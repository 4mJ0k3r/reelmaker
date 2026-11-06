# Ground atmosphere

| ID | Variants | Placement and appearance |
| --- | --- | --- |
| `ground_mist_01` | thin, dense | Static low transparent bands. Set painter order explicitly and keep below faces. |

Place mist on a low foreground or midground layer. Keep its transparent bands clear of faces. The variants are static and use three bounded translucent paths.

Use uniform positive scale and the existing scene transform bounds. Upright
objects require zero composed rotation. Road, junction, sidewalk and mist
permit the standard scene rotation. These assets provide decorative artwork.
They grant no collision surface, navigable support or actor interactions.

See the [gallery and scene examples](ASSET_GALLERY_MULTI_FAMILY.md). Native
measurements and per-variant complexity are recorded in the engineering evidence.
