# Sprint D1–D6 architecture audit

GitHub and the clean starting checkout agree on Sprint C commit
`1d7bae4ef1574bbd926320e6df0baa7e54eac663` and tree
`6ac392f19a9f3755cc331fe0069e77791f3da9ae`. Sprint D uses a separate local worktree.

Sprint C independently samples pose and camera state but the project compiler admits
a single actor per beat. Existing interaction choreography expects fixed staging
and authored hand sockets. The scene evaluator accepts one trusted character override.
Contact drift appears in blended gait weights, where the contact target blends
toward the moving pelvis. Historical single-character requests need their current
schema, shot clocks and rendering path.

D1 separates native-free contract tests from short Cairo integration and keeps
the catalog drift and historical compatibility gates. D2 measures grounded ankles
before introducing opt-in actor motion refinements. D3 adds two registered world
builders and bounded geometry with extended terrain. D4 admits a narrow two-actor
contract, reusing the scene graph and project renderer. D5 adds coverage and camera
motion to the same trusted presets. D6 adds world-authored depth and light treatments.

Preserve historical manifests and component records. Keep 720 × 1280 at 30 FPS,
CPU-only Cairo and FFmpeg, no-clobber output, trusted assets and the 256 MiB budget
with 64 MiB reserve. Verify short encoded demonstrations and export the local history.
