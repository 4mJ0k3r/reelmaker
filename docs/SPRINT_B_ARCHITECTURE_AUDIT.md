# Sprint B architecture audit

The source checkout starts clean at `8d71ea2b582c7cf7e1f579cdc7e1c5152c4f39d5`
with tree `0c3eaffcfe9fc024d70fd1c818fadcd934570b61`. The local runtime
has Python 3.12, Pycairo 1.25.1 and FFmpeg. Keep the existing 256 MiB
process-tree cap and 64 MiB admission reserve.

The native-free Joint, Skeleton, Pose and two-bone solver can be reused.
Rowan's contact solver expects the Rowan leg lengths, naming convention and
boot pivots. Yellow Mellow has its own proportions and transition sampler.
Both existing blocking drawers and storyboard compilation have actor-specific
paths. New actors should be admitted explicitly through the scene renderer
first, with the old blocking/storyboard admission scope preserved.

Scene JSON resolves registered assets, validates parent transforms, verifies
actor ground support and compiles budget envelopes before native work.
The scene evaluator samples arbitrary frame indices, evaluates local recipes,
and applies one camera projection per layer. Props are registered in the
same trusted asset table and inherit normal painter order. Synchronized
actor/prop choreography should use a sealed director over the existing scene
path. It must keep hand and prop in the same depth projection and expose
only bounded known presets. Preserve historical manifest schemas and draws.

Character expressions require standalone proof and contact sequences need
contextual proofs. Weather and world kits also need contextual evidence
with the same camera framing across comparisons. The gallery already has
native-free metadata and can index new evidence without a new renderer.
