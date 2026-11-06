# ReelForge capabilities (what can actually be requested)

Everything below was read from the registered values in this version of the source. If something
is not listed here, the one-command workflow cannot produce it.

Live view of the planner vocabulary: `python3 run_reel.py --list-support`.

## Output specification

| Property | Value |
|----------|-------|
| Resolution / aspect | 720 x 1280, 9:16 vertical |
| Frame rate | 30 fps |
| Duration choices | **15 s** (5 shots) or **60 s** (20 shots). Each shot is exactly 3 s (90 frames). |
| Codec | H.264 (libx264), yuv420p, MP4 |
| Audio | **none** (zero audio streams) |
| Rendering | CPU only, Cairo vector drawing, streamed to FFmpeg (no PNG frame dumps) |
| Cuts | Hard editorial cut between shots (no cross-shot motion continuity) |

## Characters

| Id | Use |
|----|-----|
| `yellow_mellow_v2` | The hero of every planned reel (black head, red beanie, yellow hoodie). |
| `rowan_01` | Registered in the engine, but the prompt planner does **not** use it. |

One character per reel. No crowds, no second actor.

## Environments (both are built from code)

| Planner name | Look | Triggers (words in the prompt) | Contains |
|--------------|------|--------------------------------|----------|
| `frost_peak` | Snowy mountain ridge at twilight, aurora, peaks, pines, rocks, storm snow | snow, mountain, frost, peak, ridge, blizzard, ice, cold, alpine, glacier | Emergency **beacon** (buried, then active with beam), distant answering light |
| `orchard` | Warm dusk orchard / valley path with trees, fence, hills | orchard, tree, grove, valley, farm, field, dusk, meadow, woodland | Trees, fence, path (no beacon) |

A prompt that names no recognised location is rejected (exit code 2). Both locations in one
prompt are allowed: the reel starts in the first one mentioned and finishes in the second.

Registered scene assets: `dusk_sky_01`, `distant_hills_01`, `orchard_ground_01`, `orchard_tree_01`
(broad, lean, compact, windswept), `fence_01`, `barn_01`, `foreground_boughs_01`, `frost_sky_01`,
`frost_peaks_01` (far, mid), `frost_ridge_01`, `pine_snow_01` (tall, short, cluster),
`frost_rocks_01` (cliff, drift), `beacon_01` (buried, active), `answer_light_01`,
`frost_foreground_01` (default, storm). Prompts never name these; the planner chooses them.

## Shot types the planner can use

| Shot | What the viewer sees | Environments |
|------|----------------------|--------------|
| `establish` | Wide shot: Yellow Mellow walks in, stops, looks around | both |
| `reaction` | Large close-up of his face reacting (concern/surprise) | both |
| `investigate` | Close-up at the beacon: he approaches, crouches and presses its button | `frost_peak` only |
| `threat` | Beacon blazes in the foreground, storm snow, he is startled and steps back | `frost_peak` only |
| `travel` | Following camera while he walks across the landscape | both |
| `travel_run` | Following camera while he runs (escape) | both |
| `resolve` | Closing hero shot, relief; answering light visible on the mountain | both |

Repeated shot types are staged differently each time (three composition variants).
Story structure: discovery -> storm/decision -> journey -> resolution. A prompt controls which
beats appear (beacon words add the investigate/threat beats; "run/flee/escape/safety" adds a run;
"rescue/help/answer" adds the resolve).

## Moods
`calm`, `tense`, `storm`, `hopeful`, `warm` (set automatically; they change lighting, wind and expression).

## Expressions (Yellow Mellow V2)
`neutral`, `happy`, `excited`, `curious`, `surprised`, `concerned`, `determined`, `tired`.

## Motion

Reachable from the one-command workflow (through shots): idle, look around, walk, run, stop,
turn, surprise/flinch, crouch-and-press (`activate`).

Present in the rig code but **not reachable from a prompt** (needs hand-written storyboards or
engine work): `blink`, `confident`, `crouch`, `dance`, `hands_down`, `hands_up`, `head_tilt`,
`jump`, `jumping_jack`, `land`, `point`, `recover`, `squat`, `stretch`, `wave`, `start_walk`.

## Camera behaviours (inside shots, chosen by the planner)
`establishing`, `follow`, `push_in`, `reaction`, `object_reveal`, `suspense_hold`, `close_up`.
Scene camera presets: `locked`, `gentle_drift`, `approach`. Close-ups zoom up to 5x; other
behaviours 0.9-1.7x.

## Prompt limits

- Yellow Mellow, the two environments and the shot types above. Nothing else is invented.
- No dialogue, subtitles, on-screen text, logos, photos, other characters, vehicles, indoors,
  deserts, cities, space, weather other than the snow storm.
- Durations other than 15 or 60 are rejected by the planner.
- The planner is a keyword/rule system, not a language model: it works best with plain English
  naming the character, a location and a few story verbs (see `AGENTS.md`).

## Audio

The one-command workflow is **silent**. Sound (narration / sound effects) is a separate,
existing workflow that needs user-supplied WAV files registered first: `docs/AUDIO_WORKFLOW.md`.
`assets/audio` ships only three tiny diagnostic test tones, not music or voice.

## Resource limits (enforced by the engine, not configurable here)

- 256 MiB process-tree memory budget with a 64 MiB reserve; the job is refused if the machine cannot
  meet it. Disk preflight reserves free space. Workspaces under `/tmp` are refused.
- 60 s reels render as two chunks of 10 shots, joined losslessly (stream copy) and re-verified.
- Typical hardware: about 4 CPU cores, a few GB of RAM. Rendering is single-pipeline and CPU-bound.
