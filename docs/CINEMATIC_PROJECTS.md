# Structured cinematic projects

Use `tools/cinematic_project.py` with the repository's Python 3.12 environment. A project chooses registered recipes and exact frame intervals. One 90-frame shot is three seconds at 30 fps. The renderer draws the reel with CPU Cairo and encodes it with the existing FFmpeg workflow.

## Choose → author → validate → inspect → render → verify

From the checkout root:

```bash
.venv/bin/python tools/cinematic_project.py capabilities
.venv/bin/python tools/cinematic_project.py schema
.venv/bin/python tools/cinematic_project.py validate examples/cinematic-projects/the_last_delivery.json
.venv/bin/python tools/cinematic_project.py plan examples/cinematic-projects/the_last_delivery.json
.venv/bin/python tools/cinematic_project.py frame examples/cinematic-projects/the_last_delivery.json 270
.venv/bin/python tools/cinematic_project.py render examples/cinematic-projects/the_last_delivery.json outputs/last-delivery
.venv/bin/python tools/cinematic_project.py verify outputs/last-delivery
```

Choose an existing parent and a new package name outside `/tmp`. The CLI refuses an occupied output path. It stages and verifies the package before Linux publishes the complete directory atomically. A package contains `reel.mp4`, `project.json`, `timeline.json`, `report.json`, a decoded storyboard and the engine evidence. Each storyboard row represents the first, middle and final decoded frame of a shot. Open the `mobile-*.png` sheets at 100% to inspect the 360 × 640 views.

- **Shots.** Array order sets the timing. Frame 0 begins the first shot and every next shot begins 90 frames later. Choose from eight camera presets. Object reveal requires an active interaction, a signal or a staged prop. Interaction detail requires an interaction.
- **Beats.** Cover the full shot grid with ordered, contiguous half-open `start`/ `end` spans. A beat occupies one or two shots. Camera cuts inside a beat reuse the same acting, prop and atmosphere clocks. A new beat is an authored blocking cut. Use `frame` on each side to check root, prop and contact. Ordinary Scout or Mechanic beats can set an integer `stage_x` and a registered `expression`. Built-in transitions occupy one shot. Interactions require two shots and use the pairing, variant and staging in `capabilities`; a 150-frame interaction holds its terminal pose for the final 30 frames.
- **Worlds.** Choose a kit and a compatible mood. Optional effects use a registered ID and variant. `signal` uses a fixed streetlamp anchor and `lit` or `unlit`. `dressing` uses fixed world-specific anchors for the delivered parcel or parked cart. Rowan is available through the bench interaction.
- **Captions.** Use sorted, non-overlapping half-open spans. Each cue uses one of three styles and one or two lines of up to 32 admitted ASCII characters. Choose short lines that fit the mobile safe area. Text renders as DejaVu Sans glyph contours. Check the decoded storyboard at the cue boundaries.
- **Audio.** Projects up to ten shots accept a registered PCM16 WAV narration cue and up to four SFX cues. IDs resolve in the CLI-selected trusted registry. Starts and trims use frames, with 1,600 samples per frame at 48 kHz. Planning checks pinned metadata and gain overlap. Rendering validates and snapshots the actual WAV bytes, mixes globally and verifies stereo AAC timing. Use `audio: null` for silence. Eleven to twenty shots are silent and assemble from two verified chunks.
- **Errors.** The CLI reports a JSON Pointer for request errors. For `/beats/2/mood`, choose a mood listed under that beat's world. For `/audio`, check the duration, registered IDs, roles and trims. Unknown fields are rejected. The engine accepts selections, parameters and text in this contract. Script interpretation, TTS, arbitrary file selection and free-form choreography are outside its scope.

## Original examples

| Request | Duration | What to inspect |
| --- | --- | --- |
| [The Last Delivery](../examples/cinematic-projects/the_last_delivery.json) | 15 s | Pickup and placement at frames 269–270; caption across the cut |
| [Signal Across the Creek](../examples/cinematic-projects/signal_across_the_creek.json) | 30 s | Cart contact at 359–360; visible lamp answer and AAC cues |
| [The Empty Settlement](../examples/cinematic-projects/the_empty_settlement.json) | 60 s | Rain, wait, signal and closing shot; verified join at frame 900 |
| [Mechanic delivery](../examples/cinematic-projects/variant_mechanic_delivery.json) | 6 s | Actor, parcel variant, wind and camera edits |
| [Misty creek](../examples/cinematic-projects/variant_misty_creek.json) | 6 s | World, fog, pose and reveal edits |
| [Rowan bench](../examples/cinematic-projects/variant_rowan_bench.json) | 6 s | Rowan's registered sit/stand and painted bench |

Generate the original diagnostic test tones for the creek film or audio/caption proof. The fixtures are test signals.

```bash
.venv/bin/python tools/cinematic_fixture_audio.py outputs/cinematic-test-audio
.venv/bin/python tools/cinematic_project.py --registry outputs/cinematic-test-audio \
  render examples/cinematic-projects/signal_across_the_creek.json outputs/creek
.venv/bin/python tools/cinematic_project.py --registry outputs/cinematic-test-audio \
  verify outputs/creek
```

## Sprint D foundations and cinematic-project-0.2

Run `tools/cinematic_project.py schema --version cinematic-project-0.2` to
inspect the additive contract. Version 0.2 selects the refined actor motion
and admits `abandoned_outpost` and `forest_ravine`. Both new worlds have three
moods. Version 0.1 keeps the original validation and render path.

A beat can place Scout and Mechanic in separate swept lanes with independent
actions, expression, facing and delay. The same beat can span four camera
shots. Use `focus`, `two_shot` and the bounded `motion` values shown by
`capabilities`. The `auto` camera resolves semantic coverage from the beat
and cue. An optional lamp cue must land on an editorial cut inside a paired beat.

[The Unexpected Meeting](../examples/sprint-d/unexpected_meeting.json) is a
caption-free example. The two camera studies and actor motion studies in
`examples/sprint-d` show the new worlds and motions independently.
