# Infrastructure

| ID | Variants | Placement and appearance |
| --- | --- | --- |
| `road_junction_01` | t_junction, crossroads | Decorative intersecting carriageways. The crossroads opens a second stem toward the camera. |
| `road_surface_01` | packed_dirt, worn_asphalt, cobblestone | Near edge at origin, receding toward y=-117. Dirt tracks, worn lane paint or paving joints. |
| `sidewalk_01` | stone, concrete, cracked | Near curb at y=0, with flagstones, concrete slabs or a split slab. |
| `small_bridge_01` | timber, weathered | Low timber span with deck, posts and two rails. Decorative only. |

Near road and curb edges sit at y=0. Match taper and endpoints by eye. Junction geometry has fixed branches. Bridge local origin is the near footing. Its open approaches follow the deck depth.

Use uniform positive scale and the existing scene transform bounds. Upright
objects require zero composed rotation. Road, junction, sidewalk and mist
permit the standard scene rotation. These assets provide decorative artwork.
They grant no collision surface, navigable support or actor interactions.

See the [gallery and scene examples](ASSET_GALLERY_MULTI_FAMILY.md). Native
measurements and per-variant complexity are recorded in the engineering evidence.
