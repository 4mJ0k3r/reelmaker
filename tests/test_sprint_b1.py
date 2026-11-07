import json
import math
from pathlib import Path

import pytest

from reelforge.characters import living
from reelforge.characters.living_transitions import TRANSITIONS, sample_transition
from reelforge.contracts.project import MAX_INPUT_BYTES
from reelforge.core.errors import InputError
from tools import living_worlds


@pytest.mark.parametrize("text", [
    '{"film":"a","film":"b"}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e999}',
    '{', '[1,]', '"unterminated', '['*33+'0'+']'*33,
])
def test_strict_json_rejection(tmp_path, text):
    path = tmp_path / "request.json"
    path.write_text(text)
    with pytest.raises(InputError):
        living_worlds.read_request(path)


@pytest.mark.parametrize("raw", [b"\xff", b" "* (MAX_INPUT_BYTES+1)])
def test_request_bytes_are_bounded(tmp_path, raw):
    path = tmp_path / "request.json"
    path.write_bytes(raw)
    with pytest.raises(InputError):
        living_worlds.read_request(path)


@pytest.mark.parametrize("data", [
    [], None, {"schema_version":"living-film-0.1","film":"unknown"},
    {"schema_version":"living-film-0.1","film":[]},
    {"schema_version":"living-film-0.1","film":"the_creek_crossing","extra":0},
])
def test_invalid_film_combination(data):
    with pytest.raises(ValueError):
        living_worlds.film_request(data)


def test_valid_request_uses_the_strict_loader(tmp_path):
    path = tmp_path / "request.json"
    path.write_text('{"schema_version":"living-film-0.1","film":"the_creek_crossing"}')
    assert living_worlds.film_request(living_worlds.read_request(path)) == "the_creek_crossing"


@pytest.fixture
def sequence_stubs(monkeypatch):
    def render(scene, output, **kwargs):
        output.mkdir()
        (output / "scene.mp4").write_bytes(b"shot")
        return {"frames":30, "verification":{"decoded_rgb_sha256":["hash"]}}
    def join(paths, output, cancelled):
        output.write_bytes(b"joined")
    monkeypatch.setattr(living_worlds, "render_scene", render)
    monkeypatch.setattr(living_worlds, "_concat_copy", join)
    monkeypatch.setattr(living_worlds, "verify_video",
                        lambda *a,**k: {"decoded_rgb_sha256":["hash"]*3})
    monkeypatch.setattr(living_worlds, "_verify_pts", lambda *a,**k: {"passed":True})
    return [(None,None)]*3


@pytest.mark.parametrize("point", ["begin","middle","last_shot","join","verify","timestamps","publication"])
def test_sequence_fault_cleans_only_owned_work(tmp_path, monkeypatch, sequence_stubs, point):
    parent = tmp_path / "jobs"
    parent.mkdir()
    foreign = parent / "user.txt"
    foreign.write_bytes(b"preserve")
    output = parent / "film"
    original = living_worlds.render_scene
    count = 0
    def render(scene, target, **kwargs):
        nonlocal count
        count += 1
        if count == {"begin":1,"middle":2,"last_shot":3}.get(point):
            target.mkdir()
            (target / "partial").write_bytes(b"unfinished")
            raise RuntimeError(point)
        return original(scene,target,**kwargs)
    monkeypatch.setattr(living_worlds, "render_scene", render)
    def fail(*args, **kwargs):
        raise RuntimeError(point)
    if point in ("join","verify","timestamps"):
        monkeypatch.setattr(living_worlds, {"join":"_concat_copy","verify":"verify_video",
                                          "timestamps":"_verify_pts"}[point], fail)
    if point == "publication":
        link = living_worlds.os.link
        def link_with_failure(source, destination):
            if str(destination).endswith(".json"):
                raise RuntimeError(point)
            link(source,destination)
        monkeypatch.setattr(living_worlds.os, "link", link_with_failure)
    with pytest.raises(RuntimeError, match=point):
        living_worlds.render_sequence(sequence_stubs,output)
    assert not output.exists()
    assert list(parent.iterdir()) == [foreign]
    assert foreign.read_bytes() == b"preserve"


def test_sequence_success_and_no_clobber(tmp_path, sequence_stubs):
    output = tmp_path / "film"
    living_worlds.render_sequence(sequence_stubs,output)
    before = (output / "film.mp4").stat()
    with pytest.raises(FileExistsError):
        living_worlds.render_sequence(sequence_stubs,output)
    assert (output / "film.mp4").stat().st_ino == before.st_ino
    assert {p.name for p in output.iterdir()} == {"film.mp4","film_report.json"}
    assert {p.name for p in tmp_path.iterdir()} == {"film"}


def test_foreign_output_content_is_preserved(tmp_path, monkeypatch, sequence_stubs):
    output = tmp_path / "film"
    def inject(*args,**kwargs):
        (output / "user.txt").write_bytes(b"preserve")
        raise RuntimeError("injected")
    monkeypatch.setattr(living_worlds,"_concat_copy",inject)
    with pytest.raises(RuntimeError):
        living_worlds.render_sequence(sequence_stubs,output)
    assert (output / "user.txt").read_bytes() == b"preserve"
    assert {p.name for p in tmp_path.iterdir()} == {"film"}


def test_replaced_output_is_preserved(tmp_path, monkeypatch, sequence_stubs):
    output = tmp_path / "film"
    def replace_output(*args,**kwargs):
        output.rename(tmp_path / "original")
        output.mkdir()
        (output / "foreign").write_bytes(b"preserve")
        raise RuntimeError("replacement")
    monkeypatch.setattr(living_worlds,"_concat_copy",replace_output)
    with pytest.raises(RuntimeError):
        living_worlds.render_sequence(sequence_stubs,output)
    assert (output / "foreign").read_bytes() == b"preserve"


@pytest.mark.parametrize("actor",living.PROFILES)
@pytest.mark.parametrize("transition",TRANSITIONS)
def test_continuous_transition_and_ground_contacts(actor,transition):
    samples=[sample_transition(actor,transition,frame) for frame in range(90)]
    poses=[living.RIGS[actor].evaluate(sample.pose) for sample in samples]
    assert sample_transition(actor,transition,32) == samples[32]
    maximum = max(math.hypot(b[key].x-a[key].x,b[key].y-a[key].y)
                  for a,b in zip(poses,poses[1:]) for key in a)
    assert maximum < 5.5
    for index,(sample,joints) in enumerate(zip(samples,poses)):
        for side,foot,planted in zip(("far","near"),sample.feet,sample.planted):
            joint=joints[f"{side}_foot"]
            assert math.hypot(joint.x-foot[0],joint.y-foot[1]) < 1e-9
            assert joint.y <= -5+1e-9
            if index and planted and samples[index-1].planted[("far","near").index(side)]:
                previous=poses[index-1][f"{side}_foot"]
                assert abs(joint.x-previous.x) < 1e-8
    if transition == "walk_to_stop":
        assert samples[-1].planted == (True,True)
        assert samples[-1].pose.root.x == samples[-5].pose.root.x


@pytest.mark.parametrize("failure_frame",[0,15,29])
def test_native_frame_failure_reaps_encoder(tmp_path,failure_frame):
    pytest.importorskip("cairo")
    from reelforge.scenes.contract import validate_scene
    from reelforge.scenes.graph import compile_scene,scene_frame
    from reelforge.visual_library.composition.living_worlds import world_manifest
    if Path("/tmp") in tmp_path.parents:
        pytest.skip("Native workspace requires --basetemp outside /tmp")
    scene=compile_scene(validate_scene(world_manifest("village_lane","evening",frames=30)))
    def fail_at(scene,frame):
        if frame==failure_frame:
            raise RuntimeError("frame fault")
        return scene_frame(scene,frame)
    output=tmp_path / "film"
    with pytest.raises(RuntimeError,match="frame fault"):
        living_worlds.render_sequence([(scene,fail_at)],output)
    assert not output.exists()
    assert not list(tmp_path.glob(".reelforge-*"))
