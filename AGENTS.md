# ReelForge: agent operating instructions

You are operating **ReelForge**, a CPU-only tool that turns a short story request into a vertical
animated MP4 (720x1280, 30 fps, H.264, silent). Everything is drawn by code. There is no AI image,
video, voice or GPU involvement. **Your job is to run the existing one-command pipeline, not to
modify it.**

## The rule of this project

> When the user asks for a reel / animation / video / short with Yellow Mellow, treat the message
> as a **production request** and follow "Production procedure" below. Do not ask the user for
> JSON, asset IDs or technical details. Do not edit anything in `src/`.

## Production procedure (follow in order)

1. **Parse the request** (see table). Fill every gap with the defaults. Do not ask questions you
   can answer with a default.
2. **Check readiness once per session:** `python3 run_reel.py --check`
   - Exit 0 and `"rendering_available": true` -> continue.
   - Otherwise run `bash setup.sh` (Windows host: `powershell -ExecutionPolicy Bypass -File setup.ps1`),
     then `--check` again. If it still fails, report the `blockers` list to the user and **stop**.
3. **Write the prompt to a file** (avoids shell-quoting bugs): save plain English to
   `outputs/_prompt.txt`. Keep the user's story; add a location keyword and action verbs from the
   vocabulary below if they are missing but clearly implied.
4. **Plan first (fast, no video):**
   `python3 run_reel.py --prompt-file outputs/_prompt.txt --duration <15|60> --plan-only`
   - Exit 0 -> the printed `plan.beats` is the shot list. Continue.
   - Exit 2 -> unsupported. Follow "Unsupported requests". Do **not** render a substitute story.
5. **Render:** `python3 run_reel.py --prompt-file outputs/_prompt.txt --duration <15|60>`
   (15 s takes about a minute; 60 s takes several minutes. Wait for it; do not start a second job.)
6. **Check the result.** Success means exit 0, `"ok": true` and `verification_passed: true`.
   The video is `outputs/reel_<timestamp>/final.mp4`.
7. **Reply to the user** with the template at the bottom.

### Running from a Windows shell (PowerShell / cmd)
ReelForge runs in WSL2 Ubuntu 24.04. From Windows prefix every command:

```
wsl -d Ubuntu-24.04 --cd "<this folder, Windows path>" -- python3 run_reel.py --check
```

## Parsing the user's request

| Ask | Rule |
|-----|------|
| Duration | Only **15** or **60** seconds. Default **60**. "30 s" or other: use 15 if the request is <= 37 s, else 60, and tell the user. |
| Character | Yellow Mellow only (`yellow_mellow_v2`). If another character is requested, see "Unsupported requests". |
| Location | Snowy mountain ("snow", "mountain", "frost", "peak", "ridge", "blizzard", ...) or the orchard / valley ("orchard", "valley", "grove", "farm", "meadow", "dusk", ...). Both can appear in one story (mountain first, then valley). |
| Story | Understood verbs: discover/find/notice, investigate/activate/press, run/escape/flee, storm/wind, rescue/help/answer, lost/alone/journey/cross. The emergency beacon (words: beacon, signal, emergency, distress, flare) exists **only** in the snowy mountain. |
| Mood | calm, tense, storm, hopeful, warm, chosen automatically from the words above. |
| Output | Always 720x1280, 30 fps, silent. Saved under `outputs/`. |
| Audio / dialogue / music | **Not supported by the one-command workflow.** Output is silent. Say so. See `docs/AUDIO_WORKFLOW.md` for the separate registered-audio route (needs user-supplied WAV files). |

Full lists of characters, environments, actions, expressions and cameras: `docs/AGENT_CAPABILITIES.md`.

### Prompt templates that plan well
- `Yellow Mellow discovers an emergency signal in the snowy mountains, activates the beacon as a storm hits, then follows the signal down to the valley orchard where rescue answers.` (60 s, uses both locations)
- `Yellow Mellow explores an orchard, discovers something unusual, and runs to safety.` (orchard, run)
- `Yellow Mellow finds an emergency signal in the snowy mountains.` (snow, beacon)

## Unsupported requests (be honest, do not fake it)

ReelForge is **not** unrestricted text-to-video. It composes a fixed library of code-drawn
characters, places and shot types. If the request needs something not listed in
`docs/AGENT_CAPABILITIES.md` (other characters, cities/deserts/space/indoors, vehicles, dialogue,
lyrics, logos, photos, other durations, text overlays, more than one character):

1. State which elements are unsupported.
2. Name the **closest truthful supported version** (for example "the same story set in the snowy
   mountains with Yellow Mellow").
3. If the user's intent is still met by that version, produce it and say what was changed. If
   not, ask **one** short question offering the supported options and wait.
4. Never present a different stock story as if it were the user's story.

New characters, places or props are an **engine-development task**, separate from making a reel.
Say it is a separate task and do not start it unless the user explicitly asks. All visuals must stay
code-authored in this repository (see `docs/ARCHITECTURE.md`).

## Exit codes of `run_reel.py`

| Code | Meaning | What to do |
|------|---------|------------|
| 0 | Success | Report the video. |
| 1 | Bad arguments | Fix the command (use `--prompt-file`). |
| 2 | Unsupported prompt/duration | "Unsupported requests" above. |
| 3 | Plan failed contract validation | Report the printed error; do not edit source. |
| 4 | Environment blocker (Python/Cairo/FFmpeg/memory) | Run setup; else report `blockers`. |
| 5 | Render failed | Report `error` and `production_report.md`. One retry only if the error names a fixable cause. |
| 6 | Output failed verification (rejected file kept as `rejected_failed_verification.mp4`) | Report; do not present it as finished. |
| 7 | `--name` folder already exists | Choose another name or omit `--name`. |

## Safety rules (never break these)

- **Never** edit `src/`, `assets/`, schemas or `uv.lock` to make a request work.
- **Never** lower or bypass memory/disk limits, set overrides, or run other heavy jobs at the same time.
  If memory admission refuses the job, report it and stop.
- **Never** overwrite or delete an existing video. Every run creates a new `outputs/reel_<timestamp>/`
  folder; `--name` refuses a name that already exists.
- **Never** run `git push`, change git settings, or send project files anywhere. No network use is needed after setup.
- Do not generate images, audio or video with AI services and do not add raster/stock assets.
- Do not render the same request twice "to check". One plan, one render.
- Keep generated files under `outputs/`. Do not place the project under `/tmp`.

## Output of a successful run

```
outputs/reel_YYYYMMDD_HHMMSS/
  final.mp4                 the video
  production_manifest.json  the validated plan that was rendered
  verification.json         ffprobe/ffmpeg checks (all must be true; "passed": true)
  production_report.md      shot plan, timing, memory
  render_report.json        engine report (transactions, frame hashes)
```

## Final reply template

```
Done: <absolute path to final.mp4>
Length: <60 s / 15 s>, 720x1280, 30 fps, silent
Story as built: <one sentence per act, from the shot list>
Verified: <N> frames decoded, H.264/yuv420p, no audio, checks passed
Adjustments/limits: <anything unsupported or changed, or "none">
```

## Where things are (read only when needed)

| Need | File |
|------|------|
| Exactly what can be requested | `docs/AGENT_CAPABILITIES.md` |
| Quick user walkthrough | `QUICK_START.md` |
| Adding sound (separate workflow) | `docs/AUDIO_WORKFLOW.md` |
| Architecture / contracts | `docs/ARCHITECTURE.md`, `docs/EPISODES.md`, `docs/STORYBOARDS.md` |
| Memory & hardware limits | `docs/HARDWARE_CONSTRAINTS.md`, `docs/MEMORY_OBSERVABILITY.md` |
| Planner source (do not edit for a normal request) | `src/reelforge/mvp/planner.py` |
