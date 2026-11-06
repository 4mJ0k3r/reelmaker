# Phase A1 buildings

| Registered ID | Variant | Visual treatment |
| --- | --- | --- |
| `house_01` | `daylight` | Warm timber siding, cool reflected glass and slate roofing. |
| `house_01` | `dusk` | Warm window light against cooler roof and side-wall fill. |
| `house_01` | `weathered` | Boarded glazing, moss, a chipped roof patch and worn trim. |
| `shop_01` | `open` | Lit display bay, striped canopy and recessed entry. |
| `shop_01` | `closed` | Drawn roller shutter, solid door and teal canopy. |
| `shop_01` | `weathered` | Board across the shutter, patched door and worn canopy hem. |

Both buildings are upright `scene-0.1` nodes of kind `asset`, with
positive uniform scale and zero composed rotation. The local transform
accepts scales from 0.25 to 2 and the normal scene compiler applies its
composed transform bounds. The visual proofs use 0.96. Ground origin is
`(0, 0)` on the front foundation line. Keep this origin on an authored
ground plane and stage the ground before the building in painter order.
The local doorway thresholds are `(3, 0)` and `(37, 0)`, respectively.
These are staging references for future interactions.

The facades have fixed three-quarter projection, left-hand key and
authored contact shadows. The variants supply their own grade. The
opening states, lit windows and shadows are static. Choose the variant
that suits the shot's existing lighting. Dusk Farm is the demonstrated
world. Other worlds, extreme scale and new camera angles need visual review.
These IDs are selected through explicit scene manifests.

## Scene examples

Copy one of the complete validated scenes and edit its `building` node.
Use the corresponding registered ID and variant with the existing layer,
order and transform fields.

- [Gable cottage at Dusk Farm](../examples/asset-a1/house_01.scene.json)
- [Wayside storefront at Dusk Farm](../examples/asset-a1/shop_01.scene.json)

```bash
export PYTHONPATH=src
python tools/scene.py validate examples/asset-a1/shop_01.scene.json
python tools/scene.py render examples/asset-a1/shop_01.scene.json \
  --stills-only --output-dir outputs/a1-shop-stills
```

The evidence is under [the gallery](asset-gallery/index.html). Each building
has three transparent 720 × 1280 PNGs, a sheet in selector order and a Dusk Farm
image at both 720 × 1280 and 360 × 640. The showcase uses Rowan as a scale cue.
