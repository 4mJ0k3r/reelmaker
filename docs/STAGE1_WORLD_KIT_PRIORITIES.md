# Stage 1 World Kit priorities

Start with one small integrated exterior. Use a dusk farm approach because
the existing orchard and Rowan stills already give it a color and scale
baseline. The visual task is to make a character's route and destination
read through scale, overlapping depth and directional light. Use an
establishing view and a medium view of the same layout. Add a short camera or
walk sample only where necessary to review contact and parallax. This is a
future proof scene, outside Stage 0C.

## First batch in dependency order

| Order | Component or task | Reuse and gap | Demonstration and approval evidence |
| --- | --- | --- | --- |
| 1 | Composition and support reference | Reuse scene transforms, painter order, layer depth, support metadata and existing storyboard camera behavior. Author a documented horizon, playable ground corridor, anchor layout and shared scale reference. Terrain physics and automatic depth crossing are absent. | Annotated depth and scale overlay, then clean establishing and medium images. Inspect camera endpoints and any foreground crossing. Validate through the existing scene and storyboard contracts. |
| 2 | Sky and distant-landform pair | Use the existing dusk sky, hills and haze as starting evidence. Improve value spacing and silhouette cadence. Author one compatible distant landform profile first. A coherent, parameterized sky/terrain palette is a gap. | Standalone 720 × 1280 palette and horizon read, plus integrated wide view showing the character and path. Compare the same layout at full and half scale. Check seeded output and operation budgets. |
| 3 | Ground path and contact treatment | Reuse the orchard ground support convention and existing character contact cues. Upgrade recession, edge wear and ground value grouping. Shared directional contact treatment across ground, trunks and props is a gap. Start with authored vector shadows under existing contracts. | Show neutral and keyed previews at the same placement. Check foot contact at walk extremes, trunk attachment, cast direction and readability at 360 × 640. Document runtime cost. |
| 4 | One tree family with two silhouettes | Reuse existing orchard tree recipes as evidence of what already varies. Improve crown hierarchy, trunk taper, asymmetry and recession. Keep the barn, fence and a bounded existing rock recipe as reference components where the selected composition interface supports them. | Two distinct scale-matched standalone silhouettes with trunk anchors and one integrated foreground/midground pair. If wind is included, review an animated sample at maximum admitted strength. |

Use a single palette and a stable character scale in the first proof scene.
A character, path and existing landmark should establish action and distance
before adding decorative details. Keep early work within the existing registry
and composition interfaces. Document any capability gap that requires a
separate runtime decision.

After this batch, use the same composition checks on cold terrain and storm
lighting. Generalized materials, interiors, large architectural kits, new
character rigs, generalized lighting and richer weather are later work.
Bring a component to independent review only with the standalone and
integrated evidence, motion coverage where relevant and measured technical
results specified by the [quality rubric](VISUAL_QUALITY_RUBRIC.md).
