# Human material review results — 22 October 2026

Follow-up: [hair-removal experiment](graphcut-support-results.md) removes reviewed
hair but loses too much skin; the candidate was rejected.

All 24 labels from reviewer NJR passed validation: 12 skin, four hair, three
paint and five other; no unsure labels. All 144 cached observations were
available. The labels were applied without changing any masks or fitting models.

The color check blocks reviewed paint additions but does not solve hair or all
missed skin. Keep the candidates experimental rather than promoting a default.

## Selected-point results

Counts below describe the developer-selected 24 points, not all pixels in the
images. Skin selected is desirable; hair, paint and other selected are unwanted.

| Input | Mask | Skin selected / 12 | Hair selected / 4 | Paint selected / 3 | Other selected / 5 |
| --- | --- | ---: | ---: | ---: | ---: |
| Clean | Original | 11 | 3 | 0 | 0 |
| Clean | Guarded fill | 12 | 3 | 3 | 0 |
| Clean | Color checked | 12 | 3 | 0 | 0 |
| Color shifted | Original | 7 | 0 | 0 | 0 |
| Color shifted | Guarded fill | 11 | 1 | 3 | 0 |
| Color shifted | Color checked | 10 | 1 | 0 | 0 |

On shifted inputs the color check reduces unwanted selections from four to one
versus the guarded fill, at the cost of one additional missed skin point. The
original mask avoids these selected non-skin points but misses five skin points.
Thus neither clean coverage nor precision alone is enough to choose a mask.

## Exact remaining regression cases

- P05 and P06, clean 29962, and P15, clean val/10480: human-labeled hair is
  already selected by the original mask. An additions-only check cannot remove it.
- P06, shifted 29962: a new hair selection survives the guarded and color checks.
- P14, shifted val/10480: the guard recovers human-labeled skin, but the color
  check rejects it. This is a concrete color-filter false rejection.
- P19, shifted 62331: human-labeled skin is missed by all three masks. The
  failure occurs before the material check, so tuning that check cannot recover it.

Use these point IDs, coordinates and human labels as fixed development
regressions for a stronger input-only mask. Do not reinterpret a label to make a
candidate look better. Hair handling must address existing support as well as
new additions, while preserving the recovered skin and paint exclusion. Any
change to estimation masks requires separate feature regeneration and retraining;
this run changes neither estimation nor correction application.

## Provenance and limits

Labels: `data/manifests/material_review_v1/material_review_labels.json`.
Manifest and cached observations are alongside it. Results:
`outputs/material_point_review_v1/human_labeled_results.json`, including manifest,
label and prediction hashes, per-material counts and confusion metrics.
Reproduce with `scripts/34_score_material_point_review.py`; existing results are
protected from overwrite. Label file hash:
`504fc68c2561f24cb55126cdc4d153dcfa03047ef392d228826a375bf22370a3`.

Validation checked manifest identity, reviewer, final/non-draft status, complete
unique IDs, allowed labels and complete prediction coverage. The saved confusion
counts and material totals were cross-checked directly against the observations.
No implementation code changed during scoring; the existing 425-test verification
is documented in the review guide.

These are six previously exposed development images and a deliberately selected
set of points, reviewed once by one human. Shifted observations reuse the same
material labels and are not independent new annotations. These results do not
measure image-area segmentation accuracy, fairness, generalization, final color
correction quality or expert MOS. No reserved final-test data or training
eligibility changed. Future improvements on these fixed points are regression
checks, not fresh held-out evidence.
