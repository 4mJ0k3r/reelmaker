# ReelMaker visual quality rubric

Use this gate for a specific component revision and its claimed variants, output
size and workflows. The [style guide](VISUAL_STYLE_GUIDE.md) defines the art
direction. The submitting agent supplies evidence. An independent reviewer
examines the images or animation and records a decision.

## Required evidence and hard gates

All applicable gates must pass before promotion.

| Gate | Acceptance evidence |
| --- | --- |
| Interface and metadata | Stable ID, validated parameters and variants, supported entry point, compatibility restrictions, and declared bounds, anchors or sockets where relevant. Validate catalog and contracts. |
| Regression and determinism | Record exact test commands, environment and results. Re-run the same seed and frame with a pinned environment and compare pixel hashes where applicable. Exercise boundary inputs and existing callers. |
| Standalone preview | Full-resolution 720 × 1280 reference with useful scale, neutral or representative lighting, and the claimed visual variants. Include front or relevant profile views when orientation matters. |
| Integrated preview | Full-resolution image in a representative scene with companion components, expected camera and light, and a 360 × 640 legibility check. Show contact, scale and any significant overlaps. Effects and lighting also need before/after evidence. |
| Motion where applicable | Inspect a representative animation sample at intended playback and frame by frame at contact, reversals, occlusion transitions and endpoints. Include the strongest supported effect or camera move. |
| CPU and memory | Report hardware/runtime, sample size, CPU or frame cost, process-tree peak and measurement method. Test a representative integrated case and highest-cost admitted variant. Compare against the declared path/operation caps and relevant job budget. Preserve CPU Cairo and the 256 MiB process-tree budget plus 64 MiB admission reserve where applicable. Record actual measurements and any untested cases. |
| Independent decision | Reviewer identifies the revision and evidence, scores applicable rows, records blockers and explicitly approves or requests changes. Automated checks cannot supply this decision. |

A regression, unsupported interface, nondeterministic result, missing required
evidence or over-budget case blocks promotion regardless of artistic scores.
A documented restriction can narrow the claim before review. For example, a
static profile can be approved for a specific use without implying a validated
turnaround or motion range.

## Scorecard

Score **1–5**. Use 1 for a blocking failure, 2 for recurring defects, 3 for a
credible draft with issues, 4 for consistent delivery at the intended scale
and 5 for exceptional control backed by evidence. Use N/A only with an explicit
reason and exclude it from any summary. Static components may omit motion when
they have no time-varying behavior, but their integrated preview still covers
the expected camera and spatial behavior.

| Criterion | 1 · Blocking | 3 · Draft | 5 · Strong |
| --- | --- | --- | --- |
| Silhouette/design | Form or pose is ambiguous, derivative or unrecognizable. | Identifiable in the reference view, with weak variants or tangencies. | Original form reads instantly across claimed views and poses at mobile size. |
| Color/materials | Materials merge or light direction conflicts. | Main palette works, with weak material distinctions or focal contrast. | Surfaces read through value and edge hierarchy across relevant moods. |
| Depth/grounding | Contacts float, slide or contradict perspective. | Contact reads in the hero frame, with some weak edges or secondary placements. | Scale, contact, occlusion and depth stay coherent through the tested views. |
| Composition | Focal action is obscured or cropped. | Main action is visible, with competing detail or poor spacing. | Look room, contrast and layered detail guide attention through the sequence. |
| Integration | Element clashes with approved neighbors or their staging. | Compatible in one case, with limited fit across the claimed use. | Predictable scale, light and visual fit across representative approved companions. |
| Motion | Weight, contact, easing or acting breaks readability. | Main action reads with visible timing or contact issues. | Weight, timing, planted contact and acting read at speed and on held frames. |
| Technical performance | A hard gate fails or relevant performance evidence is missing. | Evidence passes minimum caps, with unresolved cost or scaling concerns. | Repeatable, compatible runs with clear headroom in the representative worst case. |

Suggested approval floor is **4 in every applicable criterion**, plus all hard
gates and an explicit independent decision. Scores guide comparison and
revision. They do not measure artistic quality objectively. If approved
companion components are unavailable, disclose that gap and limit the decision
to candidate feedback until the integration gate can be satisfied.

## Record and catalog promotion

Use a versioned review record in future work. It should name the component ID,
asset revision, supported variants and workflows, reviewer identity and date,
test results, environment and measured resource use, standalone and integrated
preview references, relevant motion evidence, scores with short reasons,
limitations, decision and follow-up. Review new claims and materially changed
artwork against fresh evidence.

A future trusted promotion mechanism should verify the record's revision and
evidence before deriving `production_status: production_ready` and
`quality_review: approved`. Link integration and artistic evidence through
the existing catalog fields. Keep planner exposure and registry membership
separate. Stage 0C does not implement promotion, and existing entries retain
`candidate` and `not_assessed`.
