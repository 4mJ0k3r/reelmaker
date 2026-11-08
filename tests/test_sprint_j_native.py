"""Native unit checks only; these are not admitted production renders."""
from dataclasses import asdict
import json
from pathlib import Path
from threading import Event
import wave
import math
import struct
import pytest
from reelforge.unified.contract import compile_request
from reelforge.unified.workflow import resolve_audio
from reelforge.audio.registry import register_asset
from reelforge.audio.processing import mix_pcm, pcm_stats
ROOT=Path(__file__).resolve().parents[1]


def test_director_pixels_preserve_original_recipe():
    pytest.importorskip('cairo')
    from reelforge.rendering.backends.cairo import CairoRenderer
    from reelforge.rendering.diagnostic import color
    from reelforge.direction.sampling import direction_frame
    from reelforge.mvp.planner import Beat
    from reelforge.mvp.storylib import build_directed_shot
    from reelforge.mvp.dressing import dress_storyboard
    from reelforge.productions.contract import compile_production
    data=json.loads((ROOT/'examples/sprint-j/orchard_parcel.json').read_text())
    p=compile_request(data,ROOT/'assets/audio')
    e=data['events'][1];s=e['shots'][0]
    title='orchard_parcel shot 2'
    board=build_directed_shot(s['preset'],e['world'],title=title,description=e['label'],mood=e['mood'],variant=s['variant'],style=s['style'],weather=s['weather'],beacon=False)
    dress_storyboard(board,Beat(s['preset'],e['world'],e['mood'],title,e['label'],s['variant'],s['style'],s['weather']),forbidden=[])
    assert p.manifest['segments'][1]['storyboard']==board
    expected=compile_production(dict(schema_version='production-0.1',title='Reference',segments=[{'id':'one','storyboard':board},{'id':'two','storyboard':board}],audio=None))
    renderer=CairoRenderer()
    with renderer.surface(720,1280) as surface:
        for frame in (0,15,45,75,89):
            hashes=[]
            for direction in (p.visual.segments[1].storyboard.direction,expected.segments[0].storyboard.direction):
                renderer.draw(surface,direction_frame(direction,frame),background=color('243e49'),logical_size=(360,640))
                hashes.append(surface.pixel_sha256())
            assert hashes[0]==hashes[1]
    assert renderer.allocated_bytes==0


def test_short_narration_preserves_non_grid_tail(tmp_path):
    source=tmp_path/'source.wav'
    count=44100*2+29
    with wave.open(str(source),'wb') as w:
        w.setparams((1,2,44100,0,'NONE','not compressed'))
        w.writeframes(b''.join(struct.pack('<h',int(3000*math.sin(i*.08))) for i in range(count)))
    registry=tmp_path/'registry'
    asset=register_asset(registry,source,'timing','narration')
    data=json.loads((ROOT/'examples/sprint-j/orchard_parcel.json').read_text())
    data['narration']=dict(asset_id=asset.id,sha256=asset.sha256,start='1',trim_start='0',trim_end=None,gain=.8,provenance='synthetic_timing_fixture')
    plan=compile_request(data,registry)
    private=tmp_path/'private';private.mkdir()
    track,=resolve_audio(plan,registry,private,Event())
    assert track.output_samples==(count*48000+44099)//44100
    out=tmp_path/'reference.f32'
    mix_pcm((track,),plan.frames,{asset.id:private/asset.id/'input.wav'},out)
    assert pcm_stats(out)['samples_per_channel']==plan.frames*1600
    with out.open('rb') as f:
        assert not any(f.read(48000*8))
