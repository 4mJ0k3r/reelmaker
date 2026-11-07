"""Opt-in bounded lifecycle observations. No tracing side effects when disabled."""
import os
import time
from contextvars import ContextVar
from pathlib import Path

_sink = ContextVar('reelforge_trace', default=None)


def path_state(path):
    try:
        s = Path(path).lstat()
        return {'present': True, 'device': s.st_dev, 'inode': s.st_ino, 'mode': s.st_mode,
                'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns,
                'birthtime_ns': getattr(s, 'st_birthtime_ns', None)}
    except FileNotFoundError:
        return {'present': False}
    except OSError as error:
        return {'observable': False, 'error': type(error).__name__}


def event(name, **fields):
    sink = _sink.get()
    if sink is not None:
        sink.record(name, **fields)


class LifecycleTrace:
    """Bounded engineering diagnostic, not a platform filesystem ownership oracle."""
    def __init__(self, limit=4096):
        if type(limit) is not int or not 1 <= limit <= 4096:
            raise ValueError('Trace limit must be 1..4096')
        self.limit = limit
        self.events = []
        self.dropped = 0

    def record(self, name, **fields):
        if len(self.events) >= self.limit:
            self.dropped += 1
            return
        self.events.append({'event': name, 'monotonic_ns': time.monotonic_ns(),
                            'wall_ns': time.time_ns(), 'pid': os.getpid(),
                            'parent_pid': os.getppid(), **fields})

    def __enter__(self):
        self.token = _sink.set(self)
        return self

    def __exit__(self, *_):
        _sink.reset(self.token)

    def report(self):
        return {'events': self.events, 'dropped': self.dropped,
                'scope': 'Instrumented owned transactions and supervised process lifecycle; '
                         'timestamps and inode observations do not identify external creators'}
