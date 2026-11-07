# ReelMaker Sprint E1–E6 engineering report

## Identity and scope

Repository [4mJ0k3r/reelmaker](https://github.com/4mJ0k3r/reelmaker). The approved starting branch is `sprint-d8-d9-independent-qualification`, commit `ee1787c3fa322a88ca77c1c5bb6b0032a371f89b`, tree `2b0826c6d8aee314b604d0b859568e76798a41db`. Fetch and local recovery agreed. D8–D9 and D7B history are retained. The local branch is `sprint-e1-e6-cinematic-release-candidate`. The export identifies the exact final commit, tree and checkpoint history in `GIT_IDENTITY.json` and in the standalone copy of this report.

No GitHub push, branch change, PR or release took place. No media binaries are in the Sprint E commits. The Cairo renderer, streaming encoder, transaction code, audio registry, asset library and memory policy are preserved. New work consists of strict opt-in cinematic cue semantics, a refined manifest, documentation and focused tests. Hosted workflow changes add only the new small contract tests to existing jobs.

## Staging and deployment

The standard-library control and a separate native 180-frame trial independently reproduced the workspace recurrence. Two corresponding runs at an alternate local root stayed clear during bounded observation. The published media digest was the same on both native paths. The workspace producer published its original inode, then its old staging name appeared with a different identity. No unexpected paths were removed. Logs retain writer-unattributed inotify events, inode states, the guest mount namespace, producer PIDs and supervised process lifecycle.

Host-level attribution was unavailable. The creator remains unknown. The reviewed environment exposes only UID/GID 0, so an ordinary-user execution was blocked before start. The four-vCPU, low-memory Ubuntu target was unavailable, recorded as `TARGET_VM_NOT_TESTED`. See `docs/SPRINT_E1_STAGING_RELIABILITY.md` and `docs/SPRINT_E2_DEPLOYMENT_QUALIFICATION.md`.

| Local run | Wall seconds | Render tree peak MiB | In-job verify peak MiB |
| --- | ---: | ---: | ---: |
| Workspace six-second probe | 10.83 | 100.67 | 107.12 |
| Alternate six-second probe | 9.97 | 100.80 | 107.12 |
| Original 30-second archived run | 71.24 | 103.32 | 125.17 |
| Refined 30-second operator run | 51.54 | 107.47 | 124.52 |

The refined package reports 18,146,760 staged logical bytes and CPU seconds of 22.61 parent, 49.67 children user and 1.79 children system. The archived original reports 11,866,419 staged logical bytes. Different workload and run conditions prevent attributing the timing difference to an optimization. The strict policy remains 256 MiB per process tree and 64 MiB admission reserve. Raw preflight and report evidence includes cgroup observability, counters, encoder status and resource sampling. This does not qualify the target.

## Motion and edit

The original developed weak arrival separation, a blackout and reaction split by the edit, and a single-actor payoff. The refined cut starts Mira's approach earlier, uses the existing stop and stable lanes, and holds the blackout with the actors and practical in the same composition. Matched beacon framing gives the outpost and ravine an editorial connection. The answer has staggered acting and a shared payoff without captions or narration.

The opt-in 0.2 `cue_style` admits a stationary pair using `alert` or `relief`. It decouples the bounded signal edge from the camera cut and layers a short anticipation and response over idle. Each actor's response uses its own delay and pacing anticipation. Existing rig joints and inverse kinematics hold both feet in place and preserve horizontal root position and authored facing. The recipe fades back to the base pose. Legacy cue behavior and timelines stay the same when the field is omitted. Registered interaction clocks and the fixed shot grid retain their original rules.

At the actual refined film's frames 308, 475 and 781 the practical changes state. Frames 491 and 506 expose different reaction phases for Mira and Bram. Frames 814 and 834 show the staged relief. The included decoded sheets, three side-by-side clips and ground coordinates support this comparison. Motion, geography and polish remain limited in the self-assessment. See `docs/SPRINT_E4_TRANSMISSION_STORYBOARD.md` and `docs/SPRINT_E5_OPERATOR_ACCEPTANCE.md`.

## Encoded media and operator acceptance

The operator discovered the example, copied it, changed the bounded title and validated it. Two CLI plans matched byte for byte. Inspection, preflight, one final render and separate verification succeeded. The occupied destination was refused and the MP4 hash was preserved.

| Film | Plan SHA-256 | MP4 SHA-256 |
| --- | --- | --- |
| Original | `6d954670512bd6ce11de3b9f08507dddfef52e9b1820b579bf72bb77c0806d44` | `eaaeff92563c90b205a3dec8ec5c525899c2224d68c603ca4a8e6c963690afd4` |
| Refined | `384bfb65a5aeca7a5ed97299fc259ec29a989e33ca28f33ef7f8f4bb5bcf81b2` | `30b826f42227483a563b5033f4bc7e5ae04463ea79d903cb8fad402eb95cb7bd` |

The refined film decoded to 900 exact-PTS frames over 30 seconds with H.264/yuv420p at 720×1280 and 30 fps. Faststart passed. The black-frame check flagged zero frames. Independent FFmpeg decode passed for video and 48 kHz stereo AAC. The effective audio interval is 1,440,000 samples per channel with −2 samples measured audible drift within the documented AAC tolerance. The package includes the exact delivered project, timeline, storyboard, reports and verification evidence. Audio sources are the four registered diagnostic cues.

## Regression, catalog and release recommendation

The complete local Python 3.12 suite passed **471 tests**, with zero failures, errors or skips. JUnit and the run log are included.

The overlapping focused runs passed 41 transaction and lifecycle cases, 30 acting and direction cases, and 29 acting and operator cases. Six cross-checkout plans and their sampled Cairo frame hashes match byte for byte. The 77-component catalog validation and drift check passed. Offline Chromium passed with 128 decoded images and 46 local links. The published baseline CI succeeded independently of this local acceptance.

**Production certification is blocked.** The release candidate is ready for independent film review and local engineering recovery. Complete target and ordinary-user qualification and establish the staging writer or obtain sufficient production-volume evidence before authorizing unattended deployment. Independent artistic approval remains pending.
