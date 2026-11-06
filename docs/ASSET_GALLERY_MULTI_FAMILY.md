# Multi-family asset gallery

Open [the gallery](asset-gallery/index.html) from an extracted checkout with its
relative directories intact. Search an ID, filter by family, choose a variant,
and click its image to enlarge. **Copy selection** copies a JSON object with
`asset_id` and `variant`. It is a fragment for a scene node. A complete
`scene-0.1` manifest also supplies the layer, order, transform and output settings.
Story templates and the natural-language planner have separate contracts.

Start with the validated [Village Roadside](../examples/asset-sprint/village-roadside.scene.json)
or [Woodland Crossing](../examples/asset-sprint/woodland-crossing.scene.json)
scene. Copy an existing asset node, choose a unique ID and order, paste the
selection, and position it with the documented anchor. Validate before rendering.

```bash
export PYTHONPATH=src
python -m reelforge.catalog validate
python -m reelforge.catalog generate --check
python tools/asset_gallery.py build
python tools/scene.py validate examples/asset-sprint/village-roadside.scene.json
```

The offline gallery derives its inventory from the catalog. A full build
requires Cairo and renders one surface at a time under the resource monitor.
Use `--metadata-only` with a separate output directory for native-free inventory
inspection. Historical context images retain their context labels.
