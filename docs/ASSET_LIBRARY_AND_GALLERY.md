# ReelMaker visual asset gallery

Open [the gallery](asset-gallery/index.html) in a browser after downloading or
extracting the source. Keep the page and its `previews/` folder together. The
gallery works offline with browser JavaScript and relative image paths.

1. Search by component name or exact ID, or filter by category.
2. Choose a variant and select its thumbnail to see the full image.
3. Use **Copy ID** to copy the registered identifier. On browsers that restrict
   clipboard access to local pages, the gallery selects the ID for manual copy.
4. Check **Usage and limitations** and the review status before choosing a
   component. For example, ask for `house_01` with variant `dusk` in a
   `scene-0.1` manifest.
5. Inspect the component's catalog record and validate the resulting scene.

```bash
export PYTHONPATH=src
python -m reelforge.catalog show house_01
python tools/scene.py validate examples/asset-a1/house_01.scene.json
python tools/scene.py inspect examples/asset-a1/house_01.scene.json --frame 36
```

The catalog includes scene assets, characters, composition presets, procedural
recipes and controls. A catalog ID can only be used through its declared
contract. **Context image only** identifies a shared historical still or sheet.
**Dedicated preview unavailable** identifies a component or variant without
its own thumbnail. **Review not assessed** records the independent review
state separately from preview availability.

## Rebuilding

Run from the repository root with Python 3.12 and the runtime environment in
[Native setup](NATIVE_SETUP.md).

```bash
export PYTHONPATH=src
python -m reelforge.catalog validate
python -m reelforge.catalog generate
python tools/asset_gallery.py build --output-dir docs/asset-gallery
```

A full build needs Pycairo. Use `--metadata-only --output-dir outputs/gallery-data`
for the native-free workflow. It emits `assets.json` and the HTML with honest
unavailable statuses. Add `--metrics outputs/gallery-measurements.json` to a
full build to collect measured timings and pixel hashes.

The authoritative inventory generates the catalog and the gallery entries.
The gallery builder embeds the same metadata in `index.html` so local browsing
works without a JSON network request. It renders registered A1 variants and
copies any available catalog-linked historical stills into the gallery.
The build owns `index.html`, `assets.json` and the `previews/` directory within
the chosen output directory. It stages the completed render before replacing
the generated previews. Store hand-authored files elsewhere.

For a new building, add the trusted definition to the architecture profile
table. Its admitted variants, catalog metadata and gallery coverage derive
from that definition. Other asset families can supply a trusted preview
adapter or link existing verified evidence from their catalog records.
See [A1 buildings](ASSET_A1_BUILDINGS.md) for the placement contract.
