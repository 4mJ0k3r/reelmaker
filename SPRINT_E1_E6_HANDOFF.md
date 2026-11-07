# ReelMaker Sprint E1–E6 continuation handoff

The approved base is `ee1787c3fa322a88ca77c1c5bb6b0032a371f89b` with tree `2b0826c6d8aee314b604d0b859568e76798a41db`. The branch is `sprint-e1-e6-cinematic-release-candidate`. The exact exported commit, tree, history and hashes are recorded in the archive's `GIT_IDENTITY.json`.

## Recover locally

```sh
git clone --branch sprint-e1-e6-cinematic-release-candidate \
  ReelMaker_Sprint_E1_E6.bundle reelmaker-sprint-e
cd reelmaker-sprint-e
git bundle verify ../ReelMaker_Sprint_E1_E6.bundle
git status --short
git rev-parse HEAD 'HEAD^{tree}'
git merge-base --is-ancestor ee1787c3fa322a88ca77c1c5bb6b0032a371f89b HEAD
```

Run `git bundle verify` from a Git repository, or check the bundle after cloning. Match the result against `GIT_IDENTITY.json` and compare the archive entries against `SHA256_MANIFEST.json`. Install the pinned Python 3.12 renderer environment as described in `docs/REELMAKER_OPERATOR_GUIDE.md`.

The operator example is `examples/sprint-e/the_last_transmission_refined.json`. For the exact delivered plan, use the exported `evidence/operator-input.json`, which has the delivery title. Reproduce through capabilities, validate, plan, inspect, preflight, render and verify. Use a new leaf under a qualified persistent output parent and keep the existing memory policy. The archive's `films/refined/` directory is the complete verified operator package. The original and refined MP4s and before/after assets are supplied separately for review.

## Next gates

1. On the authorized constrained Ubuntu target, follow the E2 plan as an ordinary user and collect admission, codec, OOM, resource and persistent-storage evidence.
2. Ask the environment owner for permitted host-side observation of the bounded E1 reproducer. Correlate process and mount namespace with inode and creation or rename events. Preserve unexpected paths. Keep unattended deployment blocked until the ownership behavior is understood on the deployment volume.
3. Review the two 30-second films and three motion studies independently. Confirm whether the blackout, spatial transition and final payoff clear the artistic bar. The current self-assessment still marks geography, motion and overall polish as limited.
4. Review the exact local commits and reports before any publication decision. This sprint made no remote changes.

Read `REELMAKER_SPRINT_E1_E6_QUALIFICATION.md` for gate dispositions and the engineering report for exact verification and measurements.
