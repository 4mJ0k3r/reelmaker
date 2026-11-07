import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from reelforge.cinematic_projects.contract import capabilities, load_cinematic_project
from reelforge.cinematic_projects.operator import EXAMPLES, output_destination
from reelforge.core.errors import OperationError

ROOT = Path(__file__).resolve().parents[1]


def cli(*args):
    return subprocess.run([sys.executable, str(ROOT / 'tools/cinematic_project.py'), *map(str, args)],
                          capture_output=True, text=True)


@pytest.mark.parametrize('path', EXAMPLES.values())
def test_machine_discovered_examples_validate(path):
    assert load_cinematic_project(ROOT / path, ROOT / 'assets/audio').frames in range(90, 1801, 90)


def test_capabilities_expose_resources_formats_and_bounded_choices():
    info = capabilities(ROOT / 'assets/audio')
    assert info['operator']['resources']['process_tree_budget_bytes'] == 256 * 1024**2
    assert info['operator']['durations']['audio_max_frames'] == 900
    assert set(info['shot_intents']) >= {'reveal', 'resolve', 'wait'}
    assert len(info['operator']['examples']) == 5


def test_cli_invalid_json_and_arguments_are_structured(tmp_path):
    p = tmp_path / 'bad.json'
    p.write_text('{"schema_version":"wrong"}')
    result = cli('validate', p)
    assert result.returncode == 2
    assert json.loads(result.stderr)['error']['path'] == '/schema_version'
    result = cli('schema', '--version', 'wrong')
    assert result.returncode == 2
    assert json.loads(result.stderr)['error']['code'] == 'CINEMATIC_ARGUMENT'


def test_inspect_keeps_plan_digest_and_reports_actual_camera_samples():
    path = ROOT / EXAMPLES['two_character_discovery']
    plan = json.loads(cli('plan', path).stdout)
    inspect = json.loads(cli('inspect', path).stdout)
    assert inspect['plan_sha256'] == plan['plan_sha256']
    assert inspect['composition_audit']['frames_sampled'] == plan['frames']


def test_output_rejects_traversal_symlinks_and_occupied_targets(tmp_path):
    foreign = tmp_path / 'foreign'
    foreign.mkdir()
    (foreign / 'keep').write_text('untouched')
    alias = tmp_path / 'alias'
    alias.symlink_to(foreign, target_is_directory=True)
    for bad in (tmp_path / '..' / 'elsewhere', alias / 'new', foreign):
        with pytest.raises(OperationError):
            output_destination(bad)
    assert (foreign / 'keep').read_text() == 'untouched'
    assert output_destination(tmp_path / 'new') == tmp_path / 'new'


def test_discovery_and_planning_do_not_import_cairo():
    script = """
import sys,json
from pathlib import Path
from reelforge.cinematic_projects.contract import load_cinematic_project
p=load_cinematic_project(Path('examples/sprint-d8-d9/directed_discovery.json'),Path('assets/audio'))
assert p.frames == 360
assert 'cairo' not in sys.modules
"""
    result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                            env={**os.environ, 'PYTHONPATH': str(ROOT / 'src')}, capture_output=True)
    assert result.returncode == 0, result.stderr
