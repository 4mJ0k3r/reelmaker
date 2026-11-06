# Stage 1A engineering and visual report

Baseline `dc6ae67b8cf663abca1d7d17317751c892a12ccb` was verified on
`stage0c-cinematic-style-guide`. The local source tree matched
`499c5452bb6abff11b26dc6d3a8aae1bd4fba044`. Work is on
`stage1a-cinematic-world-kit`.

## Architecture

Five scene-registered components are implemented under `visual_library/nature`
and `visual_library/lighting`. The existing scene registry and dispatch in
`scenes/assets.py` resolve them as immutable vector geometry. The validated
assembly recipe lives in `visual_library/composition/farm.py`. Variant,
parameter, anchor and budget details are in the [farm kit guide](docs/STAGE1A_FARM_WORLD_KIT.md)
and generated catalog. The added IDs are `cinematic_dusk_sky_01`,
`cinematic_dusk_hills_01`, `cinematic_farm_track_01`,
`cinematic_farm_tree_01`, and `cinematic_dusk_contact_01`.

The catalog adapter now emits 48 components. All five additions remain
`candidate`, `not_assessed` and unavailable through the prompt planner.
Legacy IDs and dispatch behavior, Rowan's rig, scene/camera contracts,
production planner, encoder and admission policies are retained.

Changed areas include those asset and catalog modules, generated JSON and
Markdown catalogs, the still sampler, the visual library guide and farm kit
documentation, eight JPEG evidence files and their index, focused tests and
the existing catalog CI workflow.

## Visual evidence

Use the [evidence index](docs/visual-evidence/stage1a/README.md) for exact file
paths. Reviewed the new establishing and medium images, the matched before
view, standalone sky/landform, track and tree studies, and the annotated
depth view. Also inspected the integrated scene at 360 × 640 and the medium
composition at frames 0, 36 and 89. Rowan is stationary and looking around.
A walk and continuous camera move are outside the reviewed claim.

| Criterion | Provisional | Observations |
| --- | ---: | --- |
| Silhouette/design | 4 | The low fork and wide shoulder read differently from the tall leaning trunk and offset crown. Some canopy accents remain visibly graphic at close range. |
| Color/materials | 3 | Cool upper sky and muted warm air improve distance grouping. The ground remains broad and simplified, and the inherited barn siding is more detailed than its surroundings. |
| Depth/grounding | 4 | The road tapers toward the doorway, tree roots have compact contact cues, and the revised landforms recede. Evidence covers fixed poses and static ground marks. |
| Composition | 4 | Removing ground striping makes Rowan easier to read. The path and sun balance the barn. The medium view crops part of the right roof and tree. |
| Integration | 3 | Rowan and the barn fit the palette and scale in the proof scene. The rig, barn, tree edges and field still have different detail density. Other settings and the folded hill profile need integrated visual review. |
| Motion | N/A | Fixed views and static kit artwork. Sampled poses stayed clear of the foreground canopy. No walking, animated decals, continuous parallax or wind assessment. |
| Technical performance | 4 for the sampled scope | Bounded, deterministic scene evaluation and rasterization with ample observed RSS headroom on this host. A lower-memory production host and end-to-end encoding remain unmeasured. |

The improvement is clearest in route readability and quieter focal framing.
The art remains stylized and spare. Contact treatment is suitable for fixed
grounded subjects. Moving actors still rely on their existing rig shadows.
The candidate kit is ready for independent engineering and artistic review
within the documented scope. Material polish and cross-scene integration
remain below the provisional approval floor. There is no production approval.

## Technical evidence

The existing strict monitor sampled 12 establishing frames at 720 × 1280
on an AMD EPYC 9V74 host with an eight-vCPU cgroup quota and an 8 GiB cgroup
memory limit. Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0. One Cairo surface
was reused. Evaluation and rasterization took **0.331 s wall** and **0.349 s
process CPU**, about **27.6 ms wall per frame**. PNG writing, scene compilation
and encoding were outside the timed interval. The measured render interval
peaked at **29.94 MiB process-tree RSS**, and the whole still tool peaked at
**30.34 MiB**. The strict monitor reported no cancellation and continuous
OOM telemetry. The sample is below the unchanged 256 MiB cap with the 64 MiB
reserve policy in place. It does not establish performance on a 0.4–1 GiB host.

The sampled draw maximum was 378 paths and 2,207 operations, against a
compiled 632-path and 11,460-operation allowance. Global caps remain
4,096 and 80,000. Re-evaluating frame 36 produced the same pixel SHA-256
`3aa0a5f038ef7cce5e87dbf5c65c61e12ecc5b086a81d90c807034440068eda1`
on the recorded runtime. No full reel or audio was produced.

With `PYTHONPATH=src`, catalog `validate` and `generate --check` passed
for all 48 entries. The focused command below passed **48 tests** with
Pycairo. A separate native-free run passed 45 tests and skipped three
existing Cairo-dependent checks.

```sh
PYTHONPATH=src python -m pytest -q tests/test_stage1a_world_kit.py \
  tests/test_visual_catalog.py tests/test_snowy_mountain.py \
  'tests/test_mvp_prompt_to_reel.py::test_plan_and_manifest_compile[15-5]' \
  tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary
```

Ruff and the staged Git whitespace check passed. The existing CI workflow
now includes the Stage 1A tests in its native-free catalog job. A hosted
result was unavailable at commit time.
