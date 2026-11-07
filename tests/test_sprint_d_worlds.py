"""Both frontier kits admit every mood and stay inside their geometry envelopes."""

import pytest

from reelforge.environments.scene import Camera
from reelforge.scenes.assets import cost
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, evaluate_layers
from reelforge.visual_library.composition.living_worlds import MOODS, world_manifest


@pytest.mark.parametrize("kit", MOODS)
def test_frontier_world_geometry_is_distinct_bounded_and_deterministic(kit):
    rendered = []
    for mood in MOODS[kit]:
        scene = compile_scene(validate_scene(world_manifest(kit, mood, actor="scout_01")))
        view = Camera(18, 2, 1.1)
        frame = evaluate_layers(scene, 45, camera_override=view, atmosphere_frame=135)
        assert evaluate_layers(scene, 45, camera_override=view, atmosphere_frame=135) == frame
        paths, ops = cost(tuple(command for layer in frame for command in layer.commands))
        assert 95 < paths <= scene.path_allowance < 600
        assert ops <= scene.operation_allowance < 10000
        sky = next(layer for layer in frame if layer.id == "sky_plane").commands[0]
        # An oversized, depth-zero first path covers every admitted crop.
        assert sky.path[0].points[0] < -360
        assert sky.path[0].points[1] < -300
        assert sky.path[2].points[0] > 720
        assert sky.path[2].points[1] > 1000
        rendered.append(frame)
    assert rendered[0] != rendered[1] != rendered[2] != rendered[0]
