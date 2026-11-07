# D9.1 operator acceptance — fresh checkout, fresh inputs

A detached worktree at 93fc500 was installed with the documented
`uv sync --frozen --extra renderer` command, with no custom environment variables.
The host reused a previously built compatible pinned Pycairo wheel from the uv
cache; this is not evidence of cold native compilation on the low-memory VM.
The engine source in this checkout was not edited during the workflows.

The operator task: use CLI discovery, choose a valid request, correct a rejected
field using its JSON error, produce and verify media, preserve occupied outputs,
and recover from a real pinned-audio failure. All 20 commands, exit codes,
stdout/stderr and exact paths are retained in operator-command-log.json.

| Workflow | Fresh input | Operation and observed outcome |
| --- | --- | --- |
| A | D7A The Last Signal copy | Invalid world rejected at /beats/0/world; choose abandoned_outpost from error alternatives; validate/plan/inspect/preflight/render/verify; 450 frames; occupied target refused with unchanged video hash |
| B | The Last Transmission copy + trusted registry copy | Deliberately changed diag_fence WAV bytes fail real render; no result published; restore the pinned operator source; validate/plan/preflight/render/verify; 900 frames, registered stereo AAC |
| C | D7B Before the Storm copy | Validate/plan/inspect accepted; independently verify the approved existing long MP4/chunks; 1800 frames and assembly equality passed; no needless new 60-second render |

Typical exact command sequence, from a documented checkout:

```sh
.venv/bin/python tools/cinematic_project.py capabilities
.venv/bin/python tools/cinematic_project.py schema --version cinematic-project-0.2
.venv/bin/python tools/cinematic_project.py validate INPUT.json
.venv/bin/python tools/cinematic_project.py plan INPUT.json
.venv/bin/python tools/cinematic_project.py inspect INPUT.json
.venv/bin/python tools/cinematic_project.py preflight INPUT.json NEW_OUTPUT
.venv/bin/python tools/cinematic_project.py render INPUT.json NEW_OUTPUT
.venv/bin/python tools/cinematic_project.py verify NEW_OUTPUT
```

Expected outputs: reel.mp4, project.json, timeline.json, report.json,
verification.json, storyboard/ and engine/ evidence. The reused D7B package
predates persistent verification.json; its independently generated verification
is retained separately. The current new A/B packages contain it atomically.

No hidden module calls or source edits were needed for production. The test
orchestrator only copies operator inputs/registry, deliberately corrupts/restores
one WAV fixture, invokes documented CLI commands, and checks their JSON/hash
results. It is supplied with the evidence for audit, not required to operate
ReelMaker. Routine recovery uses the structured error, trusted input restoration,
validation/preflight and a fresh destination. Ownership uncertainty requires
investigation of preserved work and never authorizes a prefix sweep.

Decoded review identified partial non-focal partners in the first 30-second
film. The single focused refinement uses existing shared coverage, an
establishing wait and explicit Mira focus for the blackout reaction. The
refined request is produced through the same clean-checkout CLI into a new
output, with a separate command log; the first render is preserved for comparison.
Final source also validates/plans under the development checkout. The final
restored-tree smoke/plan/frame checks qualify the final commit separately.
