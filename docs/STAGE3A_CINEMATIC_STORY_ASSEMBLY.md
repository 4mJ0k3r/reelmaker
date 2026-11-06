# Stage 3A · The Other Light

An orange beacon glows in a snowy pass. Yellow Mellow approaches, slows, and
recoils during his one-handed investigation. The last cut returns to the beacon
and reveals a smaller light on the ridge beyond it. The source of the distant
light is left open.

The trusted recipe `cinematic_story("the_other_light")` in
`reelforge.visual_library.composition.cinematic_story` emits one complete
`episode-0.3` document. The recipe has one supported cast and location,
`yellow_mellow_v2` on Cold Ridge. Its world, reaction, shot order, duration and
audio choice are fixed. The prompt planner has no selector for it.

| Global frames | Source | Coverage |
| --- | --- | --- |
| 0–89 | Beacon insert, local 0–89 | A slow push onto the existing `local_signal` beacon |
| 90–111 | Stage 2C approach, local 0–21 | Full-body context locates the traveler left of the beacon |
| 112–146 | Stage 2C approach, local 22–56 | Follow through the approach and stop |
| 147–179 | Stage 2C approach, local 57–89 | A feet-cropped close-up holds through recoil and settle |
| 180–269 | Ridge reveal, local 0–89 | A pull of attention from the near beacon to the distant light |

The middle segment serializes the complete Stage 2C `direction-0.1` output.
The two inserts use the same grade, terrain, beacon position and silhouettes.
They omit the actor intentionally. At 90 the cut widens to show the walker
already in the pass. At 180 it leaves the recovered pose and shows the distant
light with the near beacon as a reference. These are editorial cuts with
independent scene clocks. The near beacon's glow phase can reset across a cut.
The light is revealed by the edit. No press, activation or confirmed answer is
shown. The episode is silent and has no captions.

`episode-0.3` accepts one of `storyboard` or `direction` per segment, with a
unique segment ID. It uses existing scene or procedural worlds and validated
blocking where applicable. It preserves the 1–10 segment bound, 90 local frames
per segment, exact 30 fps output clock, existing audio rules, 256 MiB
process-tree budget and 64 MiB admission reserve. The same transaction streams
the entire story through one sequential encoder.

## Reproduce

Run from the repository root in the Python 3.12 Cairo/FFmpeg environment. Use a
fresh manifest path and render directory inside a supported workspace.

```bash
export PYTHONPATH=src
mkdir -p outputs/stage3a
python tools/stage3a_story.py outputs/stage3a/story.json
python tools/episode.py validate outputs/stage3a/story.json
python tools/episode.py inspect outputs/stage3a/story.json
python tools/episode.py frame outputs/stage3a/story.json --frame 90
python tools/episode.py frame outputs/stage3a/story.json --frame 166
python tools/episode.py frame outputs/stage3a/story.json --frame 180
python tools/episode.py render outputs/stage3a/story.json --output-dir outputs/stage3a/review
jq '{success, media_verified, published, transaction_clean, error, cleanup_error, resource_error, frames, audio_streams: .streams.audio_streams}' outputs/stage3a/review/report.json
ffprobe -v error -count_frames -show_entries stream=codec_name,pix_fmt,width,height,avg_frame_rate,nb_read_frames,duration -of json outputs/stage3a/review/reel.mp4
```

Require exit 0, success, media verification, publication and clean transaction
flags, with 270 frames and zero audio streams. See the
[shot and continuity evidence](visual-evidence/stage3a/README.md).
