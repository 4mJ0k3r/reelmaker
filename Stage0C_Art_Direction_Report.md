# Stage 0C art direction report

The verified baseline is `5eac96b68d6a3db9f80fd655ac289ac559464af7` on
`stage0ab-visual-library-foundation`. The local checkout matched the approved
source tree `aa9fcdb8fe93c4ba36487e465145482925e936b0`. This work belongs on
`stage0c-cinematic-style-guide`.

## Evidence and baseline assessment

I inspected the character artwork and rigs, environment and procedural recipes,
scene and direction contracts, catalog, and visual-library namespaces. Four
existing engine frames were generated with Python 3.12, Pycairo 1.25.1 and
Cairo 1.18.0 and inspected at reduced size. The review also examined full-size
detail in the Frost Peak and barn frames. Exact sources and frame numbers
are listed in the [evidence index](docs/visual-evidence/stage0c/README.md).

| Sample | What reads | Observed limitation |
| --- | --- | --- |
| Orchard establishing | Warm horizon, layered hills and the narrowing path create depth. Yellow Mellow's hat and hoodie identify him. Tree clusters frame the corridor. | Yellow Mellow sits low and small in the frame, so expression and gesture are difficult to read. Field striping and repeated marks compete with his silhouette at phone size. |
| Frost Peak threat | The warm beacon separates from blue air and snow. The face, clothing silhouette and foot shadow read at this scale. | Similar pointed peaks repeat at nearly equal value and visual weight. The beam has a hard geometric cutoff and streaks cross the actor. Light appears concentrated in the emitter and beam, with little visible response on surrounding surfaces. |
| Rowan at the barn | The hat, jacket and boots form a coherent silhouette. The face and gesture are visible, and the barn has a clear opening, warm face and cooler return. | The fence crosses Rowan's gesture and the stripe field competes with his legs. At this framing the dominant path points to the barn more strongly than it connects Rowan to it. |
| Rowan in the settlement | The narrowing street and overlapping façades show recession. The hat and broad body shapes remain recognizable. | Repeated roof profiles and large flat gray distance shapes give the street a modular look. The road and foreground details have stronger edges than some of the actor's features. |

These are composition-specific observations. The four frames do not establish
consistency of proportions across poses, planted-foot stability, smooth parallax,
contact during motion, lighting continuity across cuts, or performance headroom.
A hypothesis for Stage 1 is that one shared scale reference, wider value spacing
and fewer repeated edge marks will improve character-to-world integration.
Test that hypothesis with matched views and a short motion review. The
Stickocalypse reference video was unavailable in the workspace, so no visual
comparison was performed.

## Direction and next work

**Cut planes, soft air** defines a strong contour and a few large value planes
close to the story action. Edges, chroma and detail recede into the air. The
four mood palettes share color roles, and material rules explain how surfaces
respond to light. Yellow Mellow and Rowan keep their identities and rigs.

The recommended first Stage 1 batch is a shared composition and ground-support
reference, a dusk sky and distant landform, a grounded path with contact
treatment, and one tree family with two distinct silhouettes. Evaluate these
in one farm approach with a character and existing landmark. Use the
[review rubric](docs/VISUAL_QUALITY_RUBRIC.md) before any promotion.

## Files and verification

- [Visual style guide](docs/VISUAL_STYLE_GUIDE.md)
- [Visual quality rubric](docs/VISUAL_QUALITY_RUBRIC.md)
- [Stage 1 World Kit priorities](docs/STAGE1_WORLD_KIT_PRIORITIES.md)
- [Evidence index](docs/visual-evidence/stage0c/README.md), original palette SVG and four 720 × 1280 JPEG stills
- This report

`PYTHONPATH=src python -m reelforge.catalog validate` validated all 43 entries.
`PYTHONPATH=src python -m reelforge.catalog generate --check` matched both
checked-in catalog outputs. Checked relative Markdown links, the SVG against
all 28 mood swatches, JPEG dimensions and the staged diff. The palette SVG
was rasterized locally for visual inspection. Production source and runtime
interfaces were unchanged. No full suite, motion benchmark or reel was run.

The stage is ready for independent review of the art direction and rubric.
Existing artwork remains unassessed for production approval.
