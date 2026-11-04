# Padded processing-crop experiment

25 October 2026. Tested a fixed wider processing crop on32 saved inputs. The
candidate is **not adopted**: it does not recover40048's dark cheek patch, three
cohort cases are unavailable, and paint regression cannot be assessed.

The earlier cheek diagnosis was incomplete. Detector-crop clipping is one
constraint; color thresholds and the landmark face outline also exclude the
reported region. A wider crop alone does not solve all three constraints.

## Fixed rule and results

Padding is10% of the larger detection-box dimension, rounded up and clipped to
the image. Selected-face landmarks are remapped into that processing crop.
New correction pixels must pass YCrCb, predicted face/body-skin, the face oval,
the existing robust Lab check and a2-pixel anatomical-exclusion margin. A75%
oval-retention safeguard rejects inconsistent geometry. Original correction
pixels remain selected; measurement/generation masks and inputs are unchanged.

Twenty-nine of32 cases produce available proposals;28 change, adding17,940
pixels across the cohort. This is a selection count, not verified recovered skin.
Unavailable cases are67583 dark and60162 dark/color. Their original masks are
displayed for comparison only; they are not silent fallback candidates.

|40048 variation|Added pixels|Outcome|
|---|---:|---|
|Dark|0|Reported gap remains|
|Unchanged|27|Some cheek coverage added|
|Mild|18|Some cheek coverage added|

At diagnostic coordinate(202,124), the semantic prediction is face-skin in all
three versions, but YCrCb rejects the pixel and the landmark oval excludes it.
The dark version additionally has material distance3.39, above the fixed3 limit.
This one coordinate does not describe every pixel of the patch. It was excluded
from source generation and still exactly matches the source photograph in all
three inputs: the surrounding dark edit did not affect it. Simply extending
correction could therefore adjust an originally undistorted patch.

Codex inspected40048 and targeted67583/63870/7994/84364 boards. Additions include
face-side and lower-jaw strips, but their skin correctness is not established.
Body-skin predictions are not selected-person neck localization. The other
candidate boards remain available for review; no mask has been user-approved
or integrated as a result of this experiment.

## Regression and verification

The earlier83184 geometry sentinel is explicitly rejected on both clean and
globally shifted images (oval retention6.66%/6.44%). Earlier labeled regression
images also encounter unavailable geometry. All three paint points are
unavailable in both variants, so the zero selected paint count is **not a paint
safety pass**. Nine of12 skin points are assessable per variant and remain
selected; the other three are unavailable, not newly removed skin. Available
hair/other observations show no new selections. These remain reused24 labels,
not independent area annotations.

Independent checks verified all29 saved candidate unions, preservation of
original support, additions inside processing bounds, anatomical exclusions and
unchanged original input/measurement/generation/model/review/ledger hashes.
**464 tests passed.** No corrected image, regenerated dataset or fitted model
was produced; no threshold was relaxed after viewing results.

## Next implementation decision

Do not adopt padding globally or tune guards until40048 passes. The next
experiment must address source-generation coverage and the correction contour
together, with explicit reviewed facial-boundary evidence, and must make the
paint regression assessable. Otherwise we cannot distinguish a real coverage
improvement from correcting previously unedited pixels or admitting non-skin.
Keep the current failed masks and unavailable cases as regression evidence.

The32-pair cohort remains pending coverage resolution/staging.31154 stays held,
original evaluationfold4 remains empty, and the separate nine-source plan is
unexecuted. Operational MST, visible-neck support and final thesis
reference/data/evaluation requirements remain pending. The padded-crop rule is
recorded as an experimental distinction, not a proposal amendment.

[Comparison gallery](../outputs/padded_correction_crop_v1/review.html) |
[Full results](../outputs/padded_correction_crop_v1/summary.json) |
[40048 gate diagnostics](../outputs/padded_correction_crop_v1/40048_probe_diagnostics.json) |
[Verification](../outputs/padded_correction_crop_v1/verification.json)

Next evidence prepared: [three-image facial-boundary annotation set](face-boundary-review-guide.md). No labels supplied until user review.
