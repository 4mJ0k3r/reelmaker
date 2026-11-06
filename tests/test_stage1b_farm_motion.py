import math

import pytest

from reelforge.blocking.contract import compile_blocking
from reelforge.blocking.sampling import blocking_layers, commands, inspect_frame, sample
from reelforge.characters.rowan import contact_shadows
from reelforge.core.errors import InputError
from reelforge.scenes.assets import _graded_barn, cost
from reelforge.scenes.graph import camera_at
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.farm_motion import farm_walk


@pytest.fixture(scope="module", params=["original", "left_bend"])
def motion(request):
    return compile_blocking(farm_walk(request.param, moving_camera=True))


def test_motion_stops_and_contacts_stay_grounded(motion):
    frames = [inspect_frame(motion, frame) for frame in range(90)]
    assert abs(frames[72]["position"][0] - frames[9]["position"][0]) == pytest.approx(56.2)
    assert frames[60]["mode"] == "stop"
    assert frames[72]["velocity"] == frames[89]["velocity"] == 0
    assert frames[72]["position"] == frames[89]["position"]
    assert motion.segments[-1].acting == "react"
    assert motion.segments[-1].expression == "surprised"
    for frame in frames:
        for foot in frame["contacts"]:
            if foot["error"] is not None:
                assert foot["error"] <= 1e-7
                assert foot["world"][1] == pytest.approx(motion.y)


def test_shadow_ownership_and_camera_continuity(motion):
    for frame in (9, 33, 58, 72, 89):
        layers = blocking_layers(motion, frame)
        assert layers == blocking_layers(motion, frame)
        assert [layer.depth for layer in layers] == [0, 0.18, 1, 1, 1.4]
        terrain, actors = layers[2:4]
        assert "rowan_contact" not in terrain.instance_ids
        assert {"barn_contact", "orchard_tree_contact", "roadside_tree_contact"} <= set(
            terrain.instance_ids
        )
        assert actors.instance_ids[-1] == "rowan"
        x, local = commands(motion, frame / 30)
        _, _, pose, *_ = sample(motion, frame / 30)
        shadow_count = len(contact_shadows(pose, position=(0, 0), scale=1))
        assert shadow_count
        projection = camera_at(motion.compiled, frame).transform(actors.depth)
        actor = Placement(projection.tx, projection.ty, projection.sx).compose(
            Placement(x, motion.y, motion.scale)
        )
        for shadow in local[:shadow_count]:
            assert actor.command(shadow) in actors.commands
        assert x == inspect_frame(motion, frame)["position"][0]
        paths, ops = cost(tuple(command for layer in layers for command in layer.commands))
        assert paths <= motion.compiled.path_allowance
        assert ops <= motion.compiled.operation_allowance
    cameras = [camera_at(motion.compiled, frame) for frame in range(90)]
    for depth in (0, 0.18, 1, 1.4):
        projections = [cam.transform(depth) for cam in cameras]
        assert all(0.9 <= value.sx <= 1.2 for value in projections)
        assert (
            max(
                math.hypot(a.tx - b.tx, a.ty - b.ty)
                for a, b in zip(projections[:-1], projections[1:], strict=True)
            )
            < 2
        )
    assert cameras[0].transform(0) == cameras[-1].transform(0)
    assert cameras[0].transform(1.4) != cameras[-1].transform(1.4)


def test_ground_still_rejects_sloped_routes():
    manifest = farm_walk()
    manifest["segments"][1]["destination"][1] += 1
    with pytest.raises(InputError, match="Only horizontal level routes"):
        compile_blocking(manifest)


def test_graded_barn_cache_is_bounded():
    for index in range(10):
        _graded_barn(index / 10, 0.52)
    info = _graded_barn.cache_info()
    assert info.currsize == info.maxsize == 8
    assert _graded_barn(0.8, 0.52) is _graded_barn(0.8, 0.52)


def test_farm_world_compiles_through_storyboard():
    from reelforge.direction.sampling import direction_frame
    from reelforge.storyboards.compiler import compile_storyboard

    motion = farm_walk()
    beat_data = (
        ("establish", 9, "actor", {"kind": "look_around", "expression": "calm"}),
        (
            "approach",
            51,
            "barn",
            {"kind": "walk_to", "expression": "calm", "end_x": 140, "end_speed": 36},
        ),
        ("discover", 12, "barn", {"kind": "stop_at", "expression": "calm", "end_x": 147.2}),
        ("react", 18, "actor", {"kind": "react", "expression": "surprised"}),
    )
    plan = compile_storyboard(
        {
            "schema_version": "storyboard-0.1",
            "title": motion["title"],
            "world": motion["base"],
            "rowan": {"actor_id": "rowan", "support_id": "ground", "start": motion["start"]},
            "subjects": [
                {"id": "actor", "target": {"kind": "actor", "id": "rowan"}},
                {"id": "barn", "target": {"kind": "node", "id": "barn"}},
                {"id": "center", "target": {"kind": "point", "position": [180, 400], "depth": 1}},
            ],
            "views": [
                {
                    "id": "wide",
                    "kind": "establishing",
                    "subject": "center",
                    "zoom": [1, 1],
                    "screen": [180, 400],
                    "offset_start": [0, 0],
                    "offset_end": [0, 0],
                    "lead_seconds": 0,
                    "hold": [0, 0],
                    "crop": "full",
                    "foreground": "clear",
                    "cut": "matched",
                }
            ],
            "pattern": "discovery_reaction",
            "beats": [
                {
                    "id": kind,
                    "type": kind,
                    "frames": frames,
                    "subject": subject,
                    "action": action,
                    "view": "wide",
                }
                for kind, frames, subject, action in beat_data
            ],
        }
    )
    assert direction_frame(plan.direction, 33)
    assert inspect_frame(plan.direction.blocking, 89)["position"] == [147.2, 524]
