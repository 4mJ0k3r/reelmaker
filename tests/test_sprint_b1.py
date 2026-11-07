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
    original_owner = living_worlds.OwnedDirectory
    class LocalOwner(original_owner):
        def __init__(self, parent, prefix):
            # The fixture selects a local parent for injected transaction faults.
            super().__init__(local_parent[0], prefix)
    local_parent = [None]
    original_sequence = living_worlds.render_sequence
    def sequence(shots, output, **kwargs):
        local_parent[0] = output.parent
        return original_sequence(shots, output, **kwargs)
    monkeypatch.setattr(living_worlds, "OwnedDirectory", LocalOwner)
    monkeypatch.setattr(living_worlds, "render_sequence", sequence)
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
        def link_with_failure(source, destination, **kwargs):
            if str(destination).endswith(".json"):
                raise RuntimeError(point)
            link(source,destination,**kwargs)
        monkeypatch.setattr(living_worlds.os, "link", link_with_failure)
    with pytest.raises(RuntimeError, match=point):
        living_worlds.render_sequence(sequence_stubs,output)
    assert not output.exists()
    assert list(parent.iterdir()) == [foreign]
    assert foreign.read_bytes() == b"preserve"


def test_sequence_success_and_no_clobber(tmp_path, sequence_stubs):
    output = tmp_path / "film"
    report = living_worlds.render_sequence(sequence_stubs,output)
    assert report["assembly_memory"]["job_budget_bytes"] == 256 * 1024**2
    assert report["assembly_memory"]["reserve_bytes"] == 64 * 1024**2
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


@pytest.mark.parametrize("failure_shot,failure_frame",[(0,0),(1,15),(2,29)])
def test_native_frame_failure_reaps_encoder(tmp_path,monkeypatch,failure_shot,failure_frame):
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
    from reelforge.media import encoder
    factory = encoder.FFmpegEncoder
    encoders = []
    def record(*args, **kwargs):
        instance = factory(*args, **kwargs)
        encoders.append(instance)
        return instance
    monkeypatch.setattr(encoder, "FFmpegEncoder", record)
    output=tmp_path / "film"
    with pytest.raises(RuntimeError,match="frame fault"):
        shots = [(scene,None)] * 3
        shots[failure_shot] = (scene,fail_at)
        living_worlds.render_sequence(shots,output)
    assert not output.exists()
    assert not list(tmp_path.glob(".reelforge-*"))
    assert encoders
    for instance in encoders:
        assert instance.proc.poll() is not None
        assert instance.proc.stdin.closed and instance.proc.stderr.closed
        assert not instance._reader.is_alive()
        instance.confirm_cleanup()
        assert not instance.output.parent.parent.exists()


def test_film_request_cli_dispatch(tmp_path, monkeypatch, capsys):
    path = tmp_path / "film.json"
    path.write_text('{"schema_version":"living-film-0.1","film":"the_forgotten_parcel"}')
    monkeypatch.setattr("sys.argv",["living_worlds","film-request",str(path),
                                   "--output-dir",str(tmp_path/"output")])
    seen=[]
    def render(shots,output):
        seen.append((shots,output))
        return {"frames":270,"verification":{"passed":True}}
    monkeypatch.setattr(living_worlds,"render_sequence",render)
    living_worlds.main()
    assert len(seen)==1 and len(seen[0][0])==3
    assert json.loads(capsys.readouterr().out)=={"frames":270,"passed":True}


def test_user_file_created_during_publication_survives(tmp_path,monkeypatch,sequence_stubs):
    output=tmp_path/"film"
    link=living_worlds.os.link
    def race(source,destination, **kwargs):
        if str(destination).endswith(".json"):
            (output / destination).write_bytes(b"user data")
        link(source,destination,**kwargs)
    monkeypatch.setattr(living_worlds.os,"link",race)
    with pytest.raises(FileExistsError):
        living_worlds.render_sequence(sequence_stubs,output)
    assert {p.name for p in output.iterdir()}=={"film_report.json"}
    assert (output/"film_report.json").read_bytes()==b"user data"
    assert not list(tmp_path.glob(".reelforge-*"))


@pytest.mark.parametrize("frame",[-1,90,True,1.5])
def test_transition_frame_range(frame):
    with pytest.raises(ValueError):
        sample_transition("scout_01","idle_to_walk",frame)


def test_offline_gallery_local_links():
    from html.parser import HTMLParser
    root=Path(__file__).resolve().parents[1]
    gallery=root/"docs/asset-gallery"
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if key in ("href","src") and value and not value.startswith("#"):
                    assert "://" not in value
                    assert (gallery/value).is_file()
    Links().feed((gallery/"index.html").read_text())
    data=json.loads((gallery/"assets.json").read_text())
    for actor in living.PROFILES:
        transitions=data["living_worlds"]["transitions"][actor]
        assert set(transitions)==set(TRANSITIONS)
        assert all((gallery/path).is_file() for path in transitions.values())


def test_replacement_during_publication_uses_original_directory(tmp_path,monkeypatch,sequence_stubs):
    output=tmp_path/"film"
    original=tmp_path/"moved"
    link=living_worlds.os.link
    def substitute(source,destination,**kwargs):
        if str(destination).endswith(".json"):
            output.rename(original)
            output.mkdir()
            (output/"user").write_bytes(b"keep")
        link(source,destination,**kwargs)
    monkeypatch.setattr(living_worlds.os,"link",substitute)
    with pytest.raises(ValueError,match="identity changed"):
        living_worlds.render_sequence(sequence_stubs,output)
    assert list(original.iterdir())==[]
    assert (output/"user").read_bytes()==b"keep"
    assert {p.name for p in output.iterdir()}=={"user"}


def test_native_single_scene_publication(tmp_path):
    pytest.importorskip("cairo")
    from reelforge.scenes.contract import validate_scene
    from reelforge.scenes.graph import compile_scene
    from reelforge.visual_library.composition.living_worlds import world_manifest
    if Path("/tmp") in tmp_path.parents:
        pytest.skip("Native workspace requires --basetemp outside /tmp")
    scene=compile_scene(validate_scene(world_manifest("village_lane","evening",frames=30)))
    report=living_worlds.render_sequence([(scene,None)],tmp_path/"scene",single_scene=True)
    assert report["verification"]["passed"] and report["frames"]==30
    assert report["sequence_memory"]["limit_reason"] is None
    assert {p.name for p in (tmp_path/"scene").iterdir()}=={"scene.mp4","render_report.json"}
    assert not list(tmp_path.glob(".reelforge-*"))


def test_sequence_cancellation_cleans_work(tmp_path,monkeypatch,sequence_stubs):
    monitor_type=living_worlds.JobMonitor
    monitors=[]
    class RecordingMonitor(monitor_type):
        def __enter__(self):
            result=super().__enter__()
            monitors.append(self)
            return result
    render=living_worlds.render_scene
    def cancel_after_shot(*args,**kwargs):
        result=render(*args,**kwargs)
        monitors[-1].cancelled.set()
        return result
    monkeypatch.setattr(living_worlds,"JobMonitor",RecordingMonitor)
    monkeypatch.setattr(living_worlds,"render_scene",cancel_after_shot)
    with pytest.raises(ValueError,match="resource guard"):
        living_worlds.render_sequence(sequence_stubs,tmp_path/"film")
    assert not (tmp_path/"film").exists()
    assert not list(tmp_path.glob(".reelforge-*"))
