# Stage 0A/0B engineering report

## Baseline and source audit

The target is [4mJ0k3r/reelmaker](https://github.com/4mJ0k3r/reelmaker), branch
`stage0ab-visual-library-foundation`, based on GitHub `main` at
`fd395f7f330407d67a885797d2a60b3129264ed9`. The local archive was checked against its
manifest and its Git tree matched the import tree
`72b89125e9c156d5fc3c160180a5611014fb497b`. The local workspace reconstructed that
tree from the package and used a separate local commit to track the diff.

| Authority | What the audit found |
| --- | --- |
| `scenes/assets.py` and `scenes/contract.py` | The trusted scene registry defines node kinds, variants, source dispatch, anchors, support envelopes and complexity caps. |
| `characters/registry.py`, `rowan.py`, `yellow_mellow_v2/` | Rowan and Yellow Mellow have their own draw paths and vocabularies. Both identities already exist in the scene registry. |
| `environments/` | The orchard and Frost Peak artwork is reached through the existing scene recipe adapter. No recipe was relocated. |
| `procedural/{contract,planning,compiler,recipes}.py` | Three environment families produce bounded generated geometry through ten internal recipes. Settlement façades and streets, crates and barrels, woodland paths and shelter entrances are present. Generated IDs are local to a plan. |
| `mvp/{planner,storylib}.py` and storyboard compiler | The prompt planner selects two environment families. Shot builders and variants determine actual preset use. The barn and orchard boughs are registered but absent from sampled shipped shots. Storyboard direction supplies its own cameras. |
| `run_reel.py`, `pyproject.toml`, tests and architecture docs | The one-command entry point and Python 3.12 runtime stay intact. Existing contract and planner tests can run independently of full video rendering. |
| `src/reelforge/catalog/` and GitHub workflow tree | The baseline catalog was documentation only. The baseline had no Actions workflow. |

The smallest integration is a read-only adapter over trusted Python declarations. Runtime
IDs, variants and budgets are derived. The only curated scene layer supplies labels,
families and source references, with exact coverage checks. Generated metadata is validated
against this adapter. No renderer, rig, planner vocabulary, contracts or resource limits
changed. The original checksum manifest remains import provenance.

## Inventory

| Measure | Count |
| --- | ---: |
| Distinct entries | 43 |
| Registered scene assets | 17 |
| Registered characters, included above | 2 |
| Procedural entries | 13 |
| System entries | 13 |
| Prompt-selectable | 2 |
| Used by fixed planner presets | 18 |
| Unavailable through the prompt planner | 23 |
| Candidates with no artistic assessment | 43 |
| Production ready | 0 |
| Internal recipes with no separately documented public parameter set | 10 |

Of the 17 registered scene assets, 14 are preset-only and 3 are unavailable through
the prompt planner. Family counts are nature 17, composition 15, architecture 4,
characters 2, props 2, lighting 2 and effects 1. Materials is reserved and empty.
No ambiguous identity was included. Unrecorded artwork bounds, review evidence
and performance measurements remain unknown. The catalog reports caps and known
support envelopes from the registry.

## Changed files

- `src/reelforge/catalog/` contains the adapter, CLI, package initializer and updated README.
- `src/reelforge/visual_library/` contains the initializer and seven family namespaces.
- `catalog/schema.json`, `catalog/components.json` and `catalog/components.md` define and publish the inventory.
- `AGENTS.md` and `docs/VISUAL_LIBRARY.md` document discovery, safety and readiness.
- `tests/test_visual_catalog.py` and `.github/workflows/visual-catalog.yml` exercise validation.
- This report records the audit and verification.

## Verification

Commands below use Python 3.12.14 with `PYTHONPATH=src` from the repository root.

- `python -m reelforge.catalog validate` validated all 43 entries.
- `python -m reelforge.catalog generate --check` matched both checked-in outputs.
- `python run_reel.py --no-reexec --plan-only --duration 15 --prompt 'Yellow Mellow finds an emergency signal in the snowy mountains.'` validated a five-shot plan.
- `ruff check src/reelforge/catalog tests/test_visual_catalog.py` passed.
- `git diff --check` passed.

- `python -m pytest -q tests/test_visual_catalog.py tests/test_mvp_prompt_to_reel.py tests/test_production.py` passed 45 tests in 439.31 seconds. This run preceded a catalog metadata clarification and removal of two test-only warnings.
- The final `python -m pytest -q tests/test_visual_catalog.py` passed all 11 tests in a separate Python 3.12 environment without Pycairo.
- The Actions workflow uses a smaller regression selection for routine CI. Its hosted result was pending at commit time.

## Limits and next stages

The CLI is a source-checkout interface. It requires the existing JSON Schema dependency.
Preset exposure reflects shipped shot-builder output. Individual registered IDs have no
prompt selector. Procedural subrecipes have no independent public placement API.
There is no render benchmark or artistic approval evidence in this stage.

Stage 0C can define the visual style and review rubric. Stage 1 can use that rubric to
develop and review the first reusable components through the trusted runtime interfaces.
Neither stage is part of this branch.
