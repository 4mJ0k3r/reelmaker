"""Native-free operator metadata and lexical output validation; no second renderer."""
import os
from pathlib import Path

from reelforge.core.errors import OperationError

EXAMPLES = {
    'single_character_suspense': 'examples/cinematic-projects/variant_misty_creek.json',
    'two_character_discovery': 'examples/sprint-d8-d9/directed_discovery.json',
    'registered_prop_interaction': 'examples/sprint-d/pickup_refined.json',
    'registered_audio_30s': 'examples/sprint-d7b/the_answering_light.json',
    'grounded_signal_story_30s': 'examples/sprint-e/the_last_transmission_refined.json',
    'silent_multi_world_60s': 'examples/sprint-d7b/before_the_storm.json',
}


def output_destination(path):
    """Require a new leaf under an existing, non-symlink persistent parent.

    The transaction's retained parent/source inode checks defend publication.
    This is not a sandbox against a hostile OS administrator.
    """
    path = Path(path)
    if '..' in path.parts or not path.name or path.name in ('.', '..'):
        raise OperationError('OUTPUT_PATH', 'Choose a new named output without parent traversal')
    path = Path(os.path.abspath(path))
    for component in reversed((path, *path.parents)):
        if component.is_symlink():
            raise OperationError('OUTPUT_SYMLINK', 'Output and ancestor symlinks are forbidden')
    if os.path.lexists(path):
        raise OperationError('OUTPUT_EXISTS', 'Choose a new output directory')
    if not path.parent.is_dir():
        raise OperationError('WORKSPACE_MISSING', 'Create the persistent parent directory first')
    return path


def operator_metadata():
    return {
        'workflow': ['capabilities', 'schema', 'validate', 'plan', 'inspect', 'preflight', 'render', 'verify'],
        'primary_production_command': 'python tools/cinematic_project.py render PROJECT.json OUTPUT',
        'examples': EXAMPLES,
        'output': {'width': 720, 'height': 1280, 'fps': 30, 'codec': 'h264', 'pixel_format': 'yuv420p'},
        'resources': {'process_tree_budget_bytes': 256 * 1024**2,
                      'admission_reserve_bytes': 64 * 1024**2, 'policy': 'strict'},
        'durations': {'shot_frames': 90, 'shots': [1, 20], 'audio_max_frames': 900,
                      'long_route': '33–60 seconds, silent only'},
        'warnings': ['Registered diagnostic WAVs are not human narration',
                     'No arbitrary natural-language interpretation or choreography',
                     'Target VM qualification is separate from host admission'],
    }
