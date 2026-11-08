#!/usr/bin/env python3
"""Unified operator CLI. Registry and destination paths are operator arguments only."""
import argparse
import json
import sys
import signal
from threading import Event
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from reelforge.contracts.project import load_project
from reelforge.core.errors import InputError, OperationError
from reelforge.unified.contract import compile_request, schema, VERSION, BACKENDS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry', type=Path, default=Path('assets/audio'))
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('capabilities')
    sub.add_parser('schema')
    for name in ('validate', 'plan', 'inspect', 'preflight', 'render'):
        s = sub.add_parser(name)
        s.add_argument('request', type=Path)
        if name in ('preflight', 'render'):
            s.add_argument('output', type=Path)
    sub.add_parser('verify').add_argument('output', type=Path)
    args = p.parse_args()
    cancellation = Event()
    if args.command in ('render', 'preflight', 'verify'):
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: cancellation.set())
    try:
        if args.command == 'capabilities':
            result = {'contract': VERSION, 'backends': BACKENDS, 'seconds': [6,60,3], 'caption_languages': ['en'],
                      'narration': 'One supplied registered PCM16 WAV; no generated voice', 'gain': [.05,.8],
                      'resources': {'budget_mib':256,'reserve_mib':64}, 'shot_frames':90}
        elif args.command == 'schema':
            result = schema()
        elif args.command == 'verify':
            from reelforge.unified.workflow import verify
            result = verify(args.output, args.registry, cancelled=cancellation)
        else:
            plan = compile_request(load_project(args.request), args.registry)
            if args.command in ('render','preflight'):
                from reelforge.unified.workflow import preflight, render
                result = preflight(plan,args.output,args.registry,cancelled=cancellation) if args.command == 'preflight' else render(plan,args.output,args.registry,cancelled=cancellation)
            else:
                result = {'valid':True,'plan_sha256':plan.timeline['plan_sha256']} if args.command == 'validate' else plan.timeline
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (InputError, OperationError) as e:
        issue = e.issue if isinstance(e, InputError) else None
        print(json.dumps({'error': issue.as_dict() if issue else {'code':e.code,'path':'','message':str(e)}}),file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({'error': {'code':'UNIFIED_INPUT','message':str(e)}}),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
