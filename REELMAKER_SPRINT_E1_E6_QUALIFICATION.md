# ReelMaker Sprint E1–E6 qualification

**Local release candidate. Production certification is blocked.** The engine and refined film passed the local operator and media gates. The staging recurrence has no identified writer, the constrained target VM is unavailable and independent artistic approval is pending.

| Gate | Result | Basis |
| --- | --- | --- |
| Baseline identity | Pass | Approved local and fetched SHA and tree match. D8–D9 and D7B are ancestors. |
| Historical compatibility | Pass | Six cross-checkout plan and sampled-pixel comparisons match. Historical D7B golden plans are covered by tests. |
| Character motion | Limitation | New opt-in planted response and staggered timing verified. The existing cutout gait and pose vocabulary remain visible. |
| Cinematic pacing | Pass | Three in-shot signal events, independent reactions and unchanged 90-frame grid. |
| Story clarity | Limitation | Same-frame blackout and shared answer improve causality. The route between locations and the purpose of the signal stay implicit. |
| Media verification | Pass | 900 exact-PTS H.264/yuv420p frames, 720×1280, 30 fps, registered stereo AAC, full decode and zero flagged black frames. |
| Memory admission | Pass on review host | 124.52 MiB maximum sampled process-tree RSS across render and in-job verification. Existing 256 MiB budget and 64 MiB reserve. |
| Transaction safety | Pass for tested cases | 41 focused transaction and fault cases passed. Occupied output was preserved. Recurrence attribution is a separate gate. |
| Staging recurrence attribution | Unresolved | Workspace native run and independent filesystem-only control reproduced. Alternate controls stayed clear within their observation windows. |
| Target VM | Not tested | `TARGET_VM_NOT_TESTED`. No authorized target session. Ordinary-user check was blocked before execution by the review guest's UID/GID mapping. |
| Weak-agent workflow | Pass | Discover, copy, validate, deterministic plan, inspect, preflight, render, verify and occupied-output check through the documented CLI. |
| Catalog | Pass | 77 components, no drift. |
| Offline gallery | Pass | Offline Chromium, 77 cards, 128 images, 46 links, keyboard and filter controls, manual clipboard fallback, zero errors or external page requests. |
| Independent artistic approval | Pending | Self-review shows improvements, while motion, geography and polish remain below 4/5. |
| Production certification | Blocked | Actual target-VM and ordinary-user qualification, recurrence attribution and artistic approval are open. |

## Test accounting

The complete local Python 3.12 suite passed **471 tests**, with zero failures, errors or skips. JUnit and the run log are included.

The E1, E3 and E4 focused runs passed 41, 30 and 29 cases respectively. These selections overlap the final suite and each other. The published baseline's hosted run succeeded. No Sprint E hosted CI run is claimed.

## Evidence

See the E1 staging report, E2 deployment report, E4 storyboard and E5 operator and visual assessment under `docs/`. The review ZIP also includes both encoded films, compared frames and motion clips, raw telemetry, the operator manifest, checksummed evidence, the tracked source and the Git recovery bundle.
