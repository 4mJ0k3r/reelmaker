# ReelForge visual library

The catalog is a read-only discovery layer for code-authored visual capabilities. The
scene and character registries still determine what runtime manifests can use.
`visual_library/` reserves namespaces for nature, architecture, props, effects, lighting,
materials and composition. Existing art and rigs keep their original module paths.

## Discover components

Use Python 3.12 from the repository root with the existing runtime dependencies installed.
The catalog uses JSON Schema and does not need Cairo, FFmpeg or network access.

```sh
PYTHONPATH=src python -m reelforge.catalog list
PYTHONPATH=src python -m reelforge.catalog list --family nature
PYTHONPATH=src python -m reelforge.catalog show barn_01
PYTHONPATH=src python -m reelforge.catalog validate
PYTHONPATH=src python -m reelforge.catalog generate --check
```

[Browse the generated inventory](../catalog/components.md). JSON contains runtime budgets,
known variants, parameter notes and implementation references. A null parameter object means
the recipe has no separately assessed public parameter set. Omitted evidence or geometry
fields indicate no verified value recorded. Declared budgets are caps, and support envelopes
describe ground support rather than artwork bounds.

## Readiness and access

- **Engine capability** means a trusted implementation is available through a known interface.
- **Registration** records scene and character registry membership separately. One entry
  represents both registrations when they share a scene asset ID.
- **Candidate** is inventoried and awaiting review. **Production ready** requires verified
  technical integration and independent artistic approval, with evidence for both.
- **Selectable** means the one-command planner can choose it from prompt vocabulary.
  **Preset only** means the planner uses it as part of a fixed shot or mood. **Unavailable**
  means the planner has no verified route to use it.
- **Quality review** tracks artistic assessment independently. Stage 0 records every entry
  as unassessed.

The procedural environment contract selects a whole environment family. Internal recipe
names and generated IDs cannot be placed as ordinary scene assets. For example, settlement
streets include façades, crates and barrels. Frost Peak's beacon is a registered scene asset
but the planner only uses it inside built-in scenes. Storyboard camera overrides are
distinct from the camera presets used by a direct scene.

## Development workflow

Add an implementation through the appropriate trusted runtime registration or procedural
interface. Extend the adapter with a human-readable label and source references when needed.
The adapter derives scene IDs, variants, declared complexity caps and character vocabulary
from the engine. It checks registry coverage and samples trusted storyboard builders to
determine preset exposure. It never imports paths from manifest data. Validate the generated
outputs and include them in the same change.

```sh
PYTHONPATH=src python -m reelforge.catalog generate
PYTHONPATH=src python -m reelforge.catalog validate
PYTHONPATH=src python -m reelforge.catalog generate --check
```

Review future assets in representative compositions, motion and lighting, with visual
evidence plus contract and budget checks. Tests establish technical evidence only.
Record review and integration evidence before marking an asset production ready.

`PACKAGE_MANIFEST_SHA256.txt` records the original package snapshot at `fd395f7`.
Its hashes are provenance for that import. Use Git to identify later tree contents.
