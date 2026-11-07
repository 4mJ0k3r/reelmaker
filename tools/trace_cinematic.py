#!/usr/bin/env python3
"""Bounded ownership/process trace of the existing cinematic operator render command."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from reelforge.core.trace import LifecycleTrace, path_state
from reelforge.resources.monitor import procfs_pid, process_tree
from cinematic_project import main as production_main


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--observe-seconds', type=int, choices=(0, 1, 2, 5, 10), default=2)
    args = parser.parse_args()
    with args.trace.open('x') as handle, LifecycleTrace() as trace:
        original = sys.argv
        code = 2
        try:
            trace.record('production_start', project=str(args.project), output=str(args.output))
            sys.argv = ['cinematic_project.py', 'render', str(args.project), str(args.output)]
            code = production_main()
        finally:
            sys.argv = original
            trace.record('production_return', returncode=code,
                         observed_procfs_descendants=sorted(process_tree(procfs_pid()) - {procfs_pid()}))
            paths = sorted({e['path'] for e in trace.events if e['event'] == 'owned_created'})
            checkpoints = sorted({0, args.observe_seconds / 2, args.observe_seconds})
            started = time.monotonic()
            for checkpoint in checkpoints:
                time.sleep(max(0, started + checkpoint - time.monotonic()))
                for path in paths:
                    trace.record('post_return_observation', path=path, seconds=checkpoint,
                                 state=path_state(path))
            recurrence = any(e['event'] == 'post_return_observation' and e['state'].get('present')
                             for e in trace.events)
            report = {**trace.report(), 'recurrence_detected': recurrence,
                      'production_returncode': code, 'qualification': 'unresolved' if recurrence else 'observed_clear'}
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write('\n')
    return code or (3 if recurrence else 0)


if __name__ == '__main__':
    raise SystemExit(main())
