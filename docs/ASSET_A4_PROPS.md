# Everyday props

| ID | Variants | Placement and appearance |
| --- | --- | --- |
| `bench_01` | timber, painted, weathered | Grounded supports and visible seat plane. No sitting interaction. |
| `crate_stack_01` | neat, uneven | Braced timber boxes with either a square or shifted upper crate. |
| `signpost_01` | blank, directional, weathered | Blank board or directional silhouette, with worn timber in the weathered option. |
| `streetlamp_01` | unlit, lit, weathered | Metal lamp with localized authored glow. It does not light other assets. |

Ground props at their feet. Keep the seating area visible and place crates on an even plane. Signposts use silhouettes in place of text. Lamp glow stays local.

Use uniform positive scale and the existing scene transform bounds. Upright
objects require zero composed rotation. Road, junction, sidewalk and mist
permit the standard scene rotation. These assets provide decorative artwork.
They grant no collision surface, navigable support or actor interactions.

See the [gallery and scene examples](ASSET_GALLERY_MULTI_FAMILY.md). Native
measurements and per-variant complexity are recorded in the engineering evidence.
