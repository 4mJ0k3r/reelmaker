# Gallery and agent usage

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

Open [the offline gallery](asset-gallery/index.html). Search by asset ID,
choose a family, select a registered variant and copy its selection.
Expand **Living-world presets and scene examples** to inspect mood stills,
motion previews and complete example requests. The animated WebP previews
are low-resolution browsing copies. The review archive contains the MP4s.

```sh
export PYTHONPATH=src:.
python -m tools.living_worlds list
python -m tools.asset_gallery build
```

Use scene JSON for artwork, interaction JSON for fixed contact choreography,
and the film ID contract for the two fixed proofs. Each is a separate entry
point. Catalog discovery and metadata-only builds run without Cairo.
