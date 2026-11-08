#!/usr/bin/env python3
"""Run the existing unified CLI against a pinned, synthetic-only qualification packet.

No rendering implementation, resource override, installation, or Git publication.
Windows execution is NOT QUALIFIED. Use a persistent Ubuntu output parent.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def checked_path(value):
    p=Path(os.path.abspath(value))
    if '..' in Path(value).parts or any(x.is_symlink() for x in (p,*p.parents)):
        raise ValueError('Use direct non-symlink paths without traversal')
    return p


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()


def run_packet(engine,packet,output_root,python,*,check_only=False):
    engine,packet,output_root=map(checked_path,(engine,packet,output_root))
    if not output_root.is_dir() or output_root.is_relative_to(engine):
        raise ValueError('Create an output parent outside the engine checkout')
    data=json.loads((packet/'packet.json').read_text())
    if data['schema_version']!='sprint-j-qualification-packet-0.1':
        raise ValueError('Unsupported qualification packet')
    for ref,key in (('HEAD','engine_commit'),('HEAD^{tree}','engine_tree')):
        actual=subprocess.check_output(['git','-C',str(engine),'rev-parse',ref],text=True).strip()
        if actual!=data[key]:raise ValueError(f'Engine {ref} differs from pinned packet identity')
    dirty=subprocess.check_output(['git','-C',str(engine),'status','--porcelain','--untracked-files=no'],text=True)
    if dirty:raise ValueError('Tracked engine changes must be checkpointed before qualification')
    # Verify every packet member before native commands. This packet contains technical tones only.
    for name,digest in data['sha256'].items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe packet member')
        target=checked_path(packet/relative)
        if sha(target)!=digest:raise ValueError(f'Packet file changed: {name}')
    for name in data['requests']:
        if not name.isidentifier() or not name.isascii():raise ValueError('Invalid request name')
        req=json.loads((packet/'productions'/f'{name}.json').read_text())
        if req['narration']['provenance']!='synthetic_timing_fixture':
            raise ValueError('Qualification packet must contain explicitly synthetic timing signals')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    evidence=output_root/f'qualification_{stamp}'
    evidence.mkdir(exist_ok=False)
    result={'success':False,'check_only':check_only,'engine_commit':data['engine_commit'],
            'audio_provenance':'synthetic_timing_fixture','evidence':str(evidence),'completed_films':[]}
    environment=os.environ.copy();environment['PYTHONPATH']=str(engine/'src')
    cli=[str(python),str(engine/'tools/reel_production.py'),'--registry',str(packet/'productions/synthetic_registry')]
    active=None
    old_handlers={}
    def forward(sig, _frame):
        if active is not None:active.send_signal(sig)
        raise KeyboardInterrupt('Qualification cancelled; preserve completed outputs and logs')
    for sig in (signal.SIGINT,signal.SIGTERM):
        old_handlers[sig]=signal.signal(sig,forward)
    def command(label,args):
        nonlocal active
        # Child CLI owns resource supervision and cooperative native cancellation.
        with (evidence/(label+'.stdout')).open('xb') as out, (evidence/(label+'.stderr')).open('xb') as err:
            active=subprocess.Popen(args,cwd=engine,env=environment,stdout=out,stderr=err)
            try:rc=active.wait()
            finally:
                if active.poll() is None:
                    active.send_signal(signal.SIGTERM)
                    try:active.wait(timeout=60)
                    except subprocess.TimeoutExpired:
                        # Do not signal an uncertain native grandchild group; operator must investigate.
                        raise RuntimeError('CLI shutdown uncertain; preserve work and investigate native ownership')
                active=None
        if rc:raise RuntimeError(f'{label} failed (exit {rc}); inspect {evidence}. No next render started.')
    try:
        command('capabilities',cli+['capabilities'])
        for name in data['requests']:
            req=str(packet/'productions'/f'{name}.json')
            for phase in ('validate','plan','inspect'):
                command(f'{name}_{phase}',cli+[phase,req])
            generated=json.loads((evidence/f'{name}_plan.stdout').read_text())
            if generated['plan_sha256']!=data['plan_sha256'][name]:
                raise ValueError(f'{name}: plan fingerprint differs from approved packet')
        # ALL preflights must pass before the first film starts. A refusal stops here.
        for name in data['requests']:
            target=evidence/name
            command(f'{name}_preflight',cli+['preflight',str(packet/'productions'/f'{name}.json'),str(target)])
        if not check_only:
            for name in data['requests']:
                target=evidence/name
                command(f'{name}_render',cli+['render',str(packet/'productions'/f'{name}.json'),str(target)])
                command(f'{name}_verify',cli+['verify',str(target)])
                if not (target/'verification.json').is_file():raise RuntimeError('Complete verification package missing')
                result['completed_films'].append(str(target/'reel.mp4'))
        result['success']=True
        return result
    except BaseException as e:
        result['error']=str(e)
        raise
    finally:
        for sig,handler in old_handlers.items():signal.signal(sig,handler)
        (evidence/'packet_result.json').write_text(json.dumps(result,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('engine','packet','output-root'):p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--python',type=Path,default=Path(sys.executable))
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args()
    try:
        result=run_packet(a.engine,a.packet,a.output_root,a.python,check_only=a.check_only)
        print(json.dumps(result,indent=2));return 0
    except (OSError,ValueError,RuntimeError,KeyboardInterrupt) as e:
        print(json.dumps({'success':False,'error':str(e)}),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
