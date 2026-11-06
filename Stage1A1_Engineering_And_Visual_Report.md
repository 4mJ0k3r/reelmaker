# Stage 1A.1 engineering and visual report

Baseline `f35bb47e007a895518cf3f30c10ee18c82900775` was verified on
`stage1a-cinematic-world-kit`. The local baseline tree was
`41878ad646d56b5955170649215adb41fb45cf17`. The review branch is
`stage1a1-world-kit-polish`.

## Changes and compatibility

- `visual_library/nature/dusk.py` adds graduated warm air, subdued cloud
  edges, and separate ramp directions and palette ranges across the
  three hill planes. Both hill variants remain.
- `visual_library/nature/farm_tree.py` retains both main silhouettes
  and gives each its own branch connections, lower canopy planes, and
  broken edge highlights. It uses fewer draw paths than before.
- `visual_library/lighting/dusk_grade.py` applies a reusable material
  grade to the existing barn's paints. `scenes/assets.py` exposes it as
  `barn_01:dusk_graded`. The default barn's emitted geometry and paints
  match the baseline recipe exactly. The look stays optional.
- `visual_library/nature/farm_ground.py` adds the trusted `left_bend`
  variant. `visual_library/composition/farm.py` adds an alternate layout
  with the barn on the left, the actor on the right and a different tree
  arrangement. Ground support and subject scale remain consistent.
- `visual_library/lighting/contact.py` softens the directional cast and
  keeps the darkest value close to the base. The existing rig shadows
  remain in place. The approach view uses the existing scene camera with
  stationary Rowan, so the foot decal shares his anchor and depth throughout.
- The catalog adapter, generated inventory, still sampler, focused tests
  and documentation reflect these changes. All five kit IDs are unchanged.
  There are still 48 catalog entries. The kit remains candidate and
  not assessed, with no new planner exposure.

## Visual review

The [evidence index](docs/visual-evidence/stage1a1/README.md) lists the exact
files and reproduction command. Matched comparisons use the Stage 1A
baseline and retain layout, framing, pose, frame 36 and art-direction
inputs. The original layout and alternate layout were checked at
360 × 640. Full-resolution stills are 720 × 1280.

| Rubric criterion | Provisional | Visible findings |
| --- | ---: | --- |
| Silhouette/design | 4 | The two silhouettes remain distinct. The exposed branch forks join the trunks more naturally, and the clustered highlights follow the canopy contours. The canopy planes still have stylized, rounded edges. |
| Color/materials | 4 | Cooler upper air, a clearer warm horizon and hill-plane separation improve the depth read. Wood seams are less prominent and the trees carry warmer bark planes. Sparse ground details remain visibly graphic. |
| Depth/grounding | 4 | A concentrated root/sole contact and a softer cast attach objects to the ground. Rowan remains legible against the quiet track shoulders. Terrain physics and moving decal tracking are absent. |
| Composition | 4 | The route still leads to the door. The alternate route holds the focus with a different landmark position and framing foliage. The medium view retains the intentional crop of the right roof edge. |
| Integration | 4 | Reducing fine siding contrast brings the barn closer to the surrounding material hierarchy. The inherited character outlines remain sharper than the landscape contours. This score covers the two dusk layouts only. |
| Motion | 4 in sampled camera scope | Frames 0, 30, 60 and 89 show the same grounded pose location, contact and layer order. The camera push is restrained and the foreground shifts faster than the distance. No blocking overlap appeared in these samples. Continuous playback and walking were outside this proof. |
| Technical performance | 4 in sampled scope | Stable pixel hash and bounded RSS and geometry. Rasterization was slower in the measured sample. |

The visual change is clearest in the air, canopy structure and material
hierarchy. The improvements are incremental. The barn and Rowan keep their
original forms. Remaining artistic work includes less rounded canopy turns,
finer value transitions on the grass and review under other lighting.
The kit is ready for independent review of the documented scope.

## Render and resource measurements

Same 12 establishing frame indices and one 720 × 1280 CPU Cairo surface
as Stage 1A. The host reported AMD EPYC 9V74, an eight-vCPU quota and an
8 GiB memory limit. Python 3.12.14, Pycairo 1.25.1, Cairo 1.18.0.
The timed scope is scene frame evaluation and rasterization. It excludes
scene compilation, PNG writing and encoding.

| Measurement | Stage 1A reference | Stage 1A.1 |
| --- | ---: | ---: |
| Wall time per frame | 27.6 ms | 43.2 ms |
| Render interval peak process-tree RSS | 29.94 MiB | 30.01 MiB |
| Maximum sampled paths / operations | 378 / 2,207 | 365 / 2,124 |
| Compiled path / operation allowance | 632 / 11,460 | 632 / 11,460 |

Stage 1A.1 took 0.518 s wall and 0.549 s process CPU for the 12 frames.
The whole still tool peaked at 30.41 MiB. The strict monitor did not cancel
and maintained OOM telemetry. The raster time increased by about 57% in
this sample, so the result does not establish 30 FPS realtime rendering.
There was no access to the 0.4–1 GiB target host. The 256 MiB process-tree
cap and 64 MiB admission reserve are unchanged.

Repeated frame 36 rasterization yielded pixel SHA-256
`f398b3b35f78f90de3abaaa6437a1badc031211641c373f6ec94ac502b88fab7`.

## Verification

With `PYTHONPATH=src`, catalog `validate` and `generate --check` passed.
The focused test command below passed **51 tests** with Cairo. The first
run identified the old one-variant barn expectation. The corrected
discovery test verifies the legacy and opt-in variants. Both the catalog
and World Kit suites also passed **25 tests** in a Cairo-free environment.

```sh
PYTHONPATH=src python -m pytest -q tests/test_stage1a_world_kit.py \
  tests/test_visual_catalog.py tests/test_snowy_mountain.py \
  'tests/test_mvp_prompt_to_reel.py::test_plan_and_manifest_compile[15-5]' \
  tests/test_mvp_prompt_to_reel.py::test_supported_vocabulary
```

Ruff and the staged whitespace check passed. The still tool rejected an
existing output directory and the original image checksum was unchanged.
Verified the report and evidence links and image dimensions. The inherited
GitHub workflow already includes the catalog and World Kit tests. A hosted
result was unavailable at commit time.
