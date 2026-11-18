# Parser-only appearance candidate — 5 November 2026

The user authorised one fixed recognition-preprocessing comparison. Technical
availability improved from18/30to21/30, with three newly passing photos and no
previous technical pass becoming a failure. **This is a partial recognition
improvement, not qualified skin measurement or a calibration-ready cohort.**

## Implementation and executed comparison

The [protocol](stellenbosch-parser-appearance-protocol-2026-11-05.md) was frozen
before inference. Helper `segmentation_appearance_probe.parser_input` creates a
separate256BGR copy, converts to encoded Lab, applies CLAHE only to L with fixed
clipLimit2.0/grid8x8, then converts back to BGR. Only the pinned parser sees this
copy. No alternative settings, models, crops or thresholds were tested.

Original saved pixels supply anatomy, nostril exclusions, FaceOcc aligned input,
masked Lab/ITA and endpoint statistics. The enhanced copy is not a corrected
photograph, physically calibrated colour or a measurement input. Lab round-trip
quantisation/gamut effects mean even its chroma is not claimed exactly preserved.

All30cases remain. Twenty-eight have saved landmarks and received one parser
forward; two original detector failures remain without replacements. Twenty-five
new parent masks pass the unchanged1000normalized-pixel guard, versus19previously.
For19cases, aligned original inputs exactly match prior FaceOcc inputs and their
hash-bound logits were reused. Only six newly available parents received one
new CPU FaceOcc pass each; all six forwards completed. No enhanced image was
passed to FaceOcc and no visibility fallback was invented.

## Full-denominator results

| Existing descriptive score interval | Baseline final passes | Candidate final passes | Attempts |
|---|---:|---:|---:|
| [1,3) | 6 | 6 | 6 |
| [3,5) | 6 | 6 | 6 |
| [5,7) | 3 | 5 | 6 |
| [7,9) | 3 | 4 | 6 |
| [9,10] | 0 | 0 | 6 |
| All | 18 | 21 | 30 |

Intervals remain descriptive sampling strata, not rounded MST classes. The
number of subject keys passing all three conditions stays **six of ten**. The
three gains are additional individual conditions for two incomplete subjects.
All nine final failures remain: two detector failures, two no-skin-overlap parser
failures, one parent with183pixels, three empty final masks, and one final mask
with907pixels. The original guard was not lowered.

On the identical anatomical probe used in script438, parser skin/nose fractions
increase81.63→93.43%,74.64→91.07%,52.47→63.74%,26.65→47.78%, and0→21.87% across
the five strata. These pool normalized pixels, not independent people or native
samples. The highest-interval denominator has four available probes; two detector
failures remain in availability counts. Geometry/class agreement is not accuracy.
More selected pixels can include additional unwanted material.

## Visual assessment and decision

The assistant inspected all30five-panel boards, source scores hidden. Several
forehead/nose/central-face holes are reduced. However, one existing cool-condition
pass loses more lower-face coverage. Glasses/reflections remain difficult; new
passes can consist of a small cheek patch or scattered forehead/cheek islands.
Hairline, eye/brow, nasal and neck additions need validation. The pink panel
shows parser additions before all guards, not confirmed skin or final accepted
measurement pixels. Absence of technical-pass regression is not proof of no
mask-quality regression.

All highest-interval cases still fail. Three of the four available parents there
now reach FaceOcc, but its original-pixel veto leaves zero,907and zero pixels;
the fourth has only183parent pixels. This isolates an additional constraint:
better parser recognition alone does not make the original-input visibility
path reliable on these images. It does not prove FaceOcc is wrong at every
removed pixel. Do not automatically feed enhanced images to FaceOcc, disable
the veto, union in geometry or lower the guard in response.

Selected native-grid counts among technical successes range37–774. Enlarged-mask
success therefore still does not establish native detail or an independent
sample size. No native cutoff is invented. Original-score/lighting coverage,
actual skin validity, decimal-compatible calibration and subject-held evaluation
remain unresolved. The calibrated-MST feature and three-output tree are retained
as the intended design; neither is fitted or replaced here.

**Disposition:** retain this as an isolated candidate and partial improvement,
without runtime/default-mask adoption or calibration admission. Close the single
comparison with the original and new failures visible. Any further method
comparison needs an explicit fixed design that validates selected skin and
visibility rather than chasing the pass count on these same30examples. No wider
batch, preprocessing sweep or clean-only fit is activated.

## Verification and local evidence

Scripts440–443 bind the fixed protocol, helper/tests, model/source/history hashes
and every parent artifact. Verification includes30source-score/membership parities,
28exact parser-copy replays,26semantic-mask/original-parent-statistics checks,
25exact saved service replays, and25independent final-statistic/native-projection
checks. All measurements use original image pixels; original sources and prior
packages remain byte-for-byte unchanged. Verification adds no model forwards.

33focused tests passed in1.81seconds, including original-buffer preservation,
invalid inputs, deterministic transform and reused geometry/measurement/service
tests; no new full-suite or device test. New effective contract:
`9c91875286f485f8988da0bab687229d776b9f1083144571338d82829daf6e16`.
Old whole-frame/crop lookups are not claimed compatible.

Private gallery: `outputs/stellenbosch_parser_appearance_v1/review_PRIVATE.html`.
Verification and observations: `outputs/stellenbosch_parser_appearance_verification_v1/`
and `outputs/stellenbosch_parser_appearance_assessment_v1/`. These ignored local
packages include dataset content/identifiers and must not be redistributed without
consent. Citation/research/noncommercial terms remain. No photos, labels or models
were uploaded; no contacts, calibration/tree fits, admissions, Android changes or
working-thesis claim updates occurred.
