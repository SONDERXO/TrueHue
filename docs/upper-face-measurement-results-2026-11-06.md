# One upper-face repair candidate: partial tradeoff — 6 November 2026

The authorised single candidate recovers some omitted skin and reduces sampled
hair/beard inclusion, but **does not establish a reliable full-face repair**.
On the actual user references, skin inclusion54→58/113and unwanted inclusion
9→5/94are modest net changes:22skin points are recovered while18are lost;
seven unwanted inclusions are removed while three new ones appear. Object
inclusion specifically worsens1→2/8. Retain the result as an isolated candidate,
not the default measurement method or a calibration admission.

## Fixed candidate, no sweep

The [protocol](upper-face-measurement-protocol-2026-11-06.md) was recorded before
scoring. Script465applies one rule to all30existing new-source cases, reusing
29saved parser/landmark/enhanced-FaceOcc outputs without new inference:

- Existing face oval minus eye/brow/mouth and nostril exclusions.
- Restrict selection to integer pixel centres at/above landmark2's nasal-base y.
- Keep saved logit>0visibility with unchanged inverse/validity mapping.
- Allow parser background, skin and nose classes inside that guarded region;
  hard-veto every other class, including predicted hair/glasses/clothing.

The nasal-base cutoff deliberately removes moustache/chin/lower-cheek areas,
including genuine skin. It is a changed anatomical measurement scope, not an
equivalent estimate of full-face colour or a beard segmentation model. Allowing
background can restore missed skin but also admits material misclassified as
background. Cheek hair and missed glasses remain possible. No user marks were
added to masks or used to choose/tune a numerical cutoff.

All colour statistics use original crop pixels, with the unchanged1000pixel
guard. Original images, whole-face masks, measurements and user responses are
preserved. New effective contract:
`8da1bd2851240915e7cd978bccd322af807a49bc3752e7740b87a074e6933a78`.
Old features/lookups are not claimed compatible with this scope.

## Full-denominator results

Technical availability remains29/30, with zero technical pass regressions. The
original required-landmark failure remains unavailable, not an empty successful
mask. Across29available cases the candidate adds87,216and loses156,164normalized
pixels; these are prediction/scope differences, not verified skin counts. Native
grid counts range278–520, without a native-detail/independence/adequacy claim.

| Actual user marks with available prediction | Baseline whole-face mask | Upper-face candidate |
|---|---:|---:|
| Skin selected / original skin denominator | 54/113 (47.8%) | 58/113 (51.3%) |
| Hair/object selected / original unwanted denominator | 9/94 (9.6%) | 5/94 (5.3%) |
| Hair/beard points selected | 8/86 | 3/86 |
| Object/other points selected | 1/8 | 2/8 |

All238actual points remain, including31with unavailable predictions. These exposed
sparse development points are not full-mask accuracy or independent validation.
The improved pooled unwanted fraction hides an object regression, so it must
not be described as uniformly better object protection.

Transitions on the identical points are explicit:36skin retained,22gained,
18lost,37still excluded;2unwanted inclusions retained,3new,7removed,82still
excluded. The separate candidate-domain diagnostic contains60of the113available
skin marks,58selected. The other53are outside the candidate's declared geometric/
anatomical scope. That restricted58/60is not a replacement denominator or proof
of complete skin recovery: deliberately giving up genuine lower-face skin is
central to the tradeoff. Outside-domain points are not all neck or bad labels.

## All30boards inspected

The assistant inspected originals, old masks, candidate masks and added/lost
regions on every saved case. Upper-face support becomes more contiguous on
several dim/glasses images; nasal and upper-cheek holes are reduced. However,
the straight nasal-base boundary drops substantial genuine cheek/chin skin,
and the landmark oval removes upper forehead contours. Those are scope losses,
not corrected segmentation errors.

Some fringe/hairline areas and glasses/reflection regions remain uncertain.
The explicit hair/glasses class veto cannot protect pixels misclassified as
background. The actual unwanted-point additions confirm that geometric visibility
alone is not reliable material recognition. No mask-wide skin or beard accuracy
is certified by these visual observations.

## Disposition and boundary

Do not adopt this as the full-face repair or promote29technical passes to an
MST calibration cohort. It is an explicitly different upper-face candidate with
some measured development benefits and material/coverage regressions. No
calibration, ridge/ablation/baseline comparison, correction-tree fit, user review
task, new batch, app update or submitted-paper change occurred.

Close this one comparison; do not sweep the nasal cutoff or background settings
until the marked points improve. Future repair work must address actual material
discrimination rather than assume parser-background pixels are skin. Any use of
upper-face-only measurement would require an explicit justified scope, matched
features and evaluation contract; none is adopted here. These existing points
remain development-exposed and cannot be reused as independent final validation.

## Verification and private evidence

Twenty-nine exact saved candidate replays, independent predicate/mask
reconstructions, original-pixel Lab/ITA statistics and native projections passed.
Original point denominators and transition totals reconcile with the actual
hash-bound export. All source, prior masks, model/logit, user-export and parent
artifact hashes remain unchanged. Verification made no additional model passes.

33focused candidate/reference-import/coordinate tests passed in2.25seconds.
They include background recovery constraints, unchanged input pixels, negative
visibility, forbidden parser classes and invalid nasal geometry. This is not a
full-suite run or scientific acceptance test.

Private gallery/results: `outputs/upper_face_measurement_candidate_v1/review_PRIVATE.html`.
Assessment/verification: `outputs/upper_face_measurement_assessment_v1/assessment_PRIVATE.json`.
Dataset images, scores/identifiers, actual user marks and manifests remain ignored
local evidence under research/noncommercial+citation/no-redistribution terms.
No upload, contact, recruitment, runtime adoption or adviser approval occurred.
