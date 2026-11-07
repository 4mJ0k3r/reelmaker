import sys
from pathlib import Path

import pytest

from reelforge.core.trace import LifecycleTrace
from reelforge.core.transaction import OwnedDirectory
from reelforge.media.process import run_bounded
from reelforge.core.errors import OperationError


def test_trace_orders_owned_cleanup_and_supervised_child_exit(tmp_path):
    with LifecycleTrace() as trace:
        owner = OwnedDirectory(tmp_path, '.trace-')
        code, out, err = run_bounded([sys.executable, '-c', "print('bounded')"])
        assert code == 0 and out == b'bounded\n' and not err
        owner.cleanup()
    events = trace.report()['events']
    names = [e['event'] for e in events]
    assert names.index('child_exited') < names.index('owned_removed')
    assert events[0]['state']['inode'] > 0
    assert not events[-1]['state']['present']
    assert [e['monotonic_ns'] for e in events] == sorted(e['monotonic_ns'] for e in events)


def test_trace_never_reacquires_recreated_name(tmp_path):
    with LifecycleTrace() as trace:
        owner = OwnedDirectory(tmp_path, '.trace-')
        owner.cleanup()
        owner.path.mkdir()
        sentinel = owner.path / 'foreign'
        sentinel.write_bytes(b'keep')
        with pytest.raises(OperationError, match='reappeared'):
            owner.confirm_cleanup()
        assert sentinel.read_bytes() == b'keep'
    assert len([e for e in trace.events if e['event'] == 'cleanup_attempt']) == 1


def test_trace_is_bounded_and_rejects_unbounded_configuration():
    with LifecycleTrace(2) as trace:
        for _ in range(10):
            trace.record('observation')
    assert len(trace.events) == 2 and trace.dropped == 8
    with pytest.raises(ValueError):
        LifecycleTrace(100000)


def test_isolated_transactions_contend_without_clobbering(tmp_path):
    first = OwnedDirectory(tmp_path, '.job-')
    second = OwnedDirectory(tmp_path, '.job-')
    assert first.path != second.path
    (first.path / 'payload').write_bytes(b'first')
    (second.path / 'payload').write_bytes(b'second')
    target = tmp_path / 'finished'
    first.publish_as(target)
    with pytest.raises(OperationError) as error:
        second.publish_as(target)
    assert error.value.code == 'OUTPUT_EXISTS'
    second.cleanup()
    assert (target / 'payload').read_bytes() == b'first'
