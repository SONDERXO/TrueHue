# TrueHue methods and results — evidence-based thesis draft

Current1Novemberupdates are in [the addendum](thesis-results-addendum-2026-11-01.md)
and [delivery checkpoint](delivery-checkpoint-2026-11-01.md). The30October draft
below is historical: Android is integrated experimentally with emulator evidence,
and current masking/FaceOcc development is separate from the older demo baseline.

Status at30 October2026. Draft for incorporation into the thesis, not a claim
of completed validation. Numerical tables below are taken from saved experiment
summaries. The implementation and deviations from the proposal must be described
together; the functioning software should not be described as a finished model.

## Implemented research method

TrueHue estimates correction parameters from one face photograph using the
retained sequence: face detection, facial skin selection, Lab statistics and
ITA, experimentally calibrated MST, and decision-tree regression. The output
coordinates are gamma, red gain and blue gain. Android integration remains
paused while the Python research method is evaluated.

The fixed research measurement resizes the whole decoded image to256×256 using
OpenCV INTER_LINEAR. It requires exactly one YuNet detection at confidence0.85,
required facial landmarks and at least1000 selected pixels. HSV and YCrCb rules
are combined, followed by a5×5 elliptical open/close/close sequence, component
selection and anatomical exclusions including the complete mouth. Color
statistics are calculated only on the selected region. These concrete settings
are implementation choices and must not be attributed to unspecified proposal
details. The measurement contract is
`051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73`.

OpenCV encoded Lab is converted to CIELAB before calculating masked channel
means. ITA follows the implemented degree-valued arctangent of
`(mean L* − 50) / mean b*`; undefined values or inadequate support cause an
explicit failure. The current lookup converts input ITA to a continuous ordinal
estimate through decreasing monotone knots and then half-up rounds to an MST
label. The feature index is that label minus one. The lookup is experimental,
bound to the mask contract and actually emits labels1–9; it must not be called
a validated ten-category skin-tone classifier.

The strongest retained research schema contains eleven input-only features:
mean L*,a*,b*, ITA, mapped MST index, and each R/G/B channel's selected-pixel
fractions exactly0 and255. Endpoint fractions describe encoded image values;
they are not direct sensor-clipping measurements. No reference image, true MST
label, target parameter or reference lighting metadata enters inference.

Correction experiments use a multi-output decision tree with depth3, seed42,
minimum leaf1 and no sample weighting. Fitting-control leaf protection sets
outputs to `[1,1,1]` in leaves containing a fitting identity control, without
altering splits. This does not guarantee that an unseen clean face reaches a
protected leaf. Every variant of a held source/known duplicate group is excluded
from that fold's fitting data. Such groups do not prove distinct person identity.

For normalized encoded RGB, the direct operator is
`clip([red_gain × R**gamma, G**gamma, blue_gain × B**gamma], 0, 1)`.
Values are rounded to8-bit output and written only within the input mask;
outside-mask values remain unchanged. This is an encoded-RGB engineering
operator, not a physical illumination/reflectance model. Historical code uses
reciprocal gamma; converting between conventions reciprocates gamma only.
Direct-gamma predictions must never be supplied to that legacy operator unchanged.

## Data, targets and measurement boundaries

FairFace/SCIN development sources support correction preparation under recorded
allocation/access rules. MST-E supplies mapping/evaluation only, never correction
tree fitting. The historical650-source partition is already development-exposed.
The separate600-source allocation contains420 training,90 development-validation
and90 final-test selections; duplicate screening leaves418/89/90 candidates.
These are allocation candidates, not automatically approved references or masks.
Earlier duplicate auditing decoded held-out pixels: the reserved sets are locked
against tuning, but must not be described as never opened.

The initial core comprised26 approved originals and21 admitted distorted stress
inputs. The primary cycle added58 exactly reviewed masks from25 of those sources.
The source-expansion cycle added six reviewed original controls and six saved
stress inputs; only four of fifteen newly reviewed primary inputs were accepted,
from two sources. Exact rejected masks, approval scopes and notes remain retained.

The three-variant Table2 implementation includes declared assumptions about
units/order not fully supplied by the proposal. Supplemental lightening/darkening
uses a separately declared gamma-only recipe with known inverse targets before
quantization. It is not the complete Table2 augmentation. Other saved correction
targets include approximate reference-fitted settings. Quantization, generation
clipping, mask differences and operator limitations prevent treating every target
as exact reversible ground truth. Clipped stress cases remain legitimate stress
evidence; their existence does not invalidate every pixel or every prior fit.

Clean controls specify preservation of the dataset reference, not independently
verified true skin color. Mask review assesses support, not reference illumination.
New distorted masks require their own admission rather than inheriting an
original photograph's approval.

Evaluation uses mean CIEDE2000 over the saved reference scoring mask and compares
each method with no correction on the same rows. Input application masks and
reference scoring masks are distinct. Reports include case-weighted/source-equal
means, subgroup counts, clean changed-pixel counts and excluded preparation
attempts. Paired synthetic inputs share reference geometry; this does not validate
unaligned real-lighting photographs. A correction that executes successfully or
changes pixels is not necessarily an improvement.

## MST development results

The early strict center/threshold diagnostic produced zero available held-subject
predictions. A later separately declared monotone recipe produced396 predictions
from418 attempts across15 measured subjects, retaining22 processing failures.
Both are historical development stages, not contradictory reports.

| Held-subject development metric | Monotone mapping | Same-row median baseline |
|---|---:|---:|
| Image-weighted ordinal MAE | 2.222 | 2.838 |
| Equal-subject ordinal MAE | 2.306 | 3.000 |
| Exact-category accuracy | 11.11% | 14.39% |
| Within-one accuracy | 33.84% | 22.22% |

Although ordinal-error criteria improved, exact accuracy remained weak and below
baseline.180 measured images lacked another fitting subject in the held category.
Categories4/5/7/9/10 each had only one measured subject. The existing user-reported
adviser approval covers limited evaluation scope; it is not approval of final
mapping accuracy or every subsequent method change. See the
[current MST audit](mst-evidence-checkpoint-2026-10-30.md).

## Correction results and stopping decisions

The endpoint-feature experiment on47 cases reduced mean error from8.013 for its
matched five-feature comparator to5.300, leaving25/26 clean originals unchanged.
Its remaining clean failure prevented adoption. These numbers must not be
compared as though the later105/121-case totals used the same evaluation set.

| Frozen comparison | Endpoint reference | Candidate | Clean changes: reference → candidate |
|---|---:|---:|---|
| Primary cycle:105 cases /26 groups | 6.964 | 7.561 | 1/26 → 3/26 |
| Source-expansion cycle:121 cases /32 groups | 6.613 | 7.956 | 2/32 → 4/32 |

In the primary cycle, normal-primary error improved8.312→6.629, while stress
error worsened11.279→18.000. In the broader cycle, new-primary error was5.439
versus3.782 without correction; pooled color error5.076 versus3.828 without
correction. The expanded candidate's four clean failures were62331,83205,29880
and68073. No general color-correction or clean-safety success follows from the
pooled exposure gain.

Both candidates failed their frozen gates and were not adopted. The broader
cycle used34 new fits and reused52 saved trees and210 historical predictions.
Verification checked121 feature vectors,34 tree memberships/leaf means and153
new image/metric outputs without verification refits. A reporting interruption
preserved29 already fitted trees and completed only five remaining fits; it did
not trigger a new trial. Full comparison results and all121 cases remain in the
[results report](broader-source-comparison-results.md) and its linked artifacts.

## Discussion and implementation status

The evidence supports a functioning reproducible research pipeline and useful
development improvements, but not reliable automatic skin-tone correction.
ITA and its mapped MST feature share underlying facial color information and
are not independent illumination observations. Reference quality, limited source
coverage, weak mapping accuracy and mask support are plausible contributors;
the experiments do not isolate one cause or establish mathematical impossibility.

Known operator limits include invariant zero channels and green255 under the
positive gamma/gain family, and pixels outside the application mask. The saved
RGB-MAE lower-bound audit is not a CIEDE2000 bound. Beard/glasses exclusions,
patchiness, JPEG-dependent coverage and neck correction remain unresolved.
No hidden reconstruction/smoothing operator was introduced.

The desktop demo still runs the older ten-source `baseline5`, fold1 experimental
model through script180 and the legacy operator. It does not run the retained
eleven-feature endpoint research candidate or either rejected successor. Its
experimental notice and provenance export help identify this distinction;
software tests establish implementation behavior, not scientific validity.

The fuller learned-parser preview is separate and on hold pending adviser
discussion, along with beard/moustache changes. No correction demo/model or
measurement contract has switched. Android, final MST validation, independent
correction evaluation and neck coverage remain unfinished. Photographer opinions
remain scheduled after a completed correction model using the existing Google
Form; no expert scores are invented.

The next correction cycle requires a substantive reference-data/scope decision,
not more small trials on these cases. See the
[adviser brief](adviser-decision-brief-2026-10-30.md) and
[draft collection protocol](controlled-reference-capture-proposal.md).
