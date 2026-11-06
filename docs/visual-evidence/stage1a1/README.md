# Stage 1A.1 review evidence

| Evidence | What it demonstrates |
| --- | --- |
| [Matched farm before and after](farm-establishing-comparison.jpg) | Stage 1A and 1A.1 at the same layout, camera, pose, frame 36, 720 × 1280 source resolution and art-direction values. The board presents 360 × 640 panels. |
| [Matched sky and hills](sky-hills-comparison.jpg) · [refined full resolution](sky-hills.jpg) | The same horizon anchor, rolling profile choice, framing, warmth and atmosphere. Only recipe treatment changes. |
| [Matched tree study](tree-silhouettes-comparison.jpg) · [refined full resolution](tree-silhouettes.jpg) | Broad and leaning at the same scale, anchors, warmth and backdrop. The tree and its contact recipe change together. |
| [Establishing](farm-establishing.jpg) · [medium](farm-medium.jpg) | The same original layout with the opt-in graded barn and unchanged Rowan rig. Both are 720 × 1280. |
| [Second layout, left bend](farm-left-bend.jpg) | A mirrored track variant with a relocated barn and character, restaged trees and folded hills. Framing is unchanged from the establishing view. |
| [Three-second camera approach](approach-sequence.jpg) | Frames 0, 30, 60 and 89 of the existing 30 FPS approach camera. Rowan looks around from a stationary position. This is a sampled frame sequence. |

The baseline panels use the published Stage 1A stills at
`f35bb47e007a895518cf3f30c10ee18c82900775`. The paired establishing views
hold staging and settings constant. The actual recipe treatments, including the
opt-in barn grade and contact marks, are the differences under review.

Generate full-resolution PNGs on the polished branch with Python 3.12 and the
existing Cairo renderer. Use a fresh directory.

```sh
PYTHONPATH=src python tools/stage1a_farm_stills.py outputs/stage1a1-review
```

The sampler also emits performance and deterministic pixel-hash evidence to
stdout. JPEGs are compact review copies. See the
[engineering and visual report](../../../Stage1A1_Engineering_And_Visual_Report.md)
for scope and limitations.
