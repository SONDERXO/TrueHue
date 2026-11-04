# Review of regions added by YCrCb-only masking

23 October 2026. Follow-up to [the fixed YCrCb comparison](ycrcb-estimation-ablation.md).

## Finding and decision

The added regions contain both recovered facial skin and unwanted surrounding
material. **Do not integrate the candidate unchanged**, promote held cases, or
retrain on its new features yet. Existing runtime masks, cohorts, labels and
model remain unchanged. This review does not reject the paper's method in
general; it identifies limitations of this particular implementation.

Codex inspected all38 pair rows across eight source boards. Each row shows the
actual input, newly added support in green and removed support in red. Color
indicates change, not correctness. No new masks or inference were needed.

## Per-source observations

| Source | Recovered or uncertain additions | Concern |
| --- | --- | --- |
| 12288 | Color-shift input gains substantial upper/mid-face coverage; forehead remains incomplete. | Clear additions on yellow clothing beside the lower-right face; eye-rim changes need scrutiny. |
| 19 | Color shift regains forehead and lower-face skin. | Small eye-rim/jaw additions remain uncertain. Source stays development-only. |
| 22211 | Dark input regains side-face coverage. | Lower additions reach patterned collar/shoulder surroundings; color shift still misses some face. |
| 22454 | Dark input regains much of forehead/cheeks. | Remaining holes and uncertain hairline/eye/bindi-adjacent additions. The historical color-shift exclusion is not promoted. |
| 51739 | Color shift gains small forehead/cheek patches. | Repeated left face-box-border additions near surrounding material/another person. |
| 62331 | Color shift recovers much of the missed half-face. | Lower corners extend into neck/collar surroundings; eye-rim changes remain. |
| 6236 | Color shift gains forehead/nose skin. | Added left-jaw/outer-face strip and smaller edge regions need restriction or closer review. |
| 75027 | Mainly small edge/eye/lip-adjacent additions. | Narrow border slivers cannot be confirmed as facial skin at this preview scale. |

These are qualitative observations, not per-pixel labels or human/expert
annotations. Source-level notes apply across the board; they do not establish
the material of every component in every variant. Eye rims and hairline
boundaries are explicitly uncertain. No new paint labels were assigned.

## Quantitative context

Across all38 attempts, candidate support adds103,581 pixels and removes only2.
These are repeated image/variant pixel counts, not independent annotated areas,
false-positive counts or accuracy. The earlier selected-point paint regression
remains useful but did not cover all these new clothing/boundary regions.

Script57 records every connected addition component, its box and an interior
point. Component areas sum exactly to each added mask, and each pair satisfies:
candidate area = baseline area + added area - removed area. Saved original
inputs and masks retain their hashes. All76 change masks are256x256.

## Next implementation experiment

Completed follow-up: [lower-face boundary trial](lower-face-boundary-results.md)
reduces spill but also trims facial edges. It is not adopted. An additions-only
restriction is the next distinct hypothesis, preserving baseline support.

Test a separately versioned **input-derived facial boundary restriction** on
the unchanged YCrCb candidate. It must operate without clean-reference masks,
preserve anatomical exclusions and the material/hair checks, and evaluate
retained as well as held examples. Do not assume a face bounding box guarantees
facial-only support. An earlier face-outline experiment lost forehead coverage,
so measure regained skin and new skin loss, not just smaller support.

Use these saved additions as regression evidence for clothing/collar spill,
alongside the existing hair/paint points. Do not tune repeatedly until these
same reviewed examples pass or describe this development review as independent
final validation. No boundary fix or new model was implemented in this step.

## Evidence

- [All38 added-region previews](../outputs/added_correction_region_review_v1/review-index.md)
- [Per-pair visual findings](../outputs/added_correction_region_review_v1/visual_findings.json)
- [Exact masks/component geometry](../outputs/added_correction_region_review_v1/change_geometry.json)
- Reproduction: `venv/Scripts/python.exe scripts/57_review_added_correction_regions.py`
  (refuses overwrite; prepares geometry/previews, not automatic visual labels).

Verification for this review covered mask algebra, shapes, component accounting,
38-case coverage and unchanged hashes. Production code was unchanged; the
previous full suite result remains454 passed and was not rerun for this
read-only review artifact step.
