# Aligned FaceOcc appearance candidate — 5 November 2026

The single authorised recognition-input comparison improves technical measurement
availability from21/30to25/30. Four previously failing photos now pass; none of
the21previous passes becomes a technical failure. The highest sampled score
interval improves0/6→3/6, and complete subject keys improve6/10→7/10.
**This is a promising isolated recognition candidate, not skin-validation,
calibration admission, population performance or a trained correction model.**

## Exact change and execution

Scripts446–448 followed the [predeclared protocol](stellenbosch-faceocc-appearance-protocol-2026-11-05.md).
For the25available parents from the parser-only appearance candidate, original
aligned inputs were reconstructed and required to match saved pixels exactly.
The existing fixed Lab-L CLAHE clip2/grid8 helper then created a separate enhanced
aligned copy for FaceOcc recognition only, after alignment. Each received one
new pinned CPU FaceOcc forward; all25completed. No alternatives or settings were
tried. The five earlier detector/parser/parent failures remain without forwards.

Original alignment geometry, parser-derived parent masks, logit>0threshold,
validity/inverse mapping and1000normalized-pixel guard stayed unchanged. Original
crop pixels supply all final Lab/ITA and endpoint measurements. The enhanced
copy is not a physically corrected image or a colour reference; no measurement
is taken from it. This is a new preprocessing adaptation, not upstream-equivalent
preprocessing or compatibility with an old MST lookup.

## Full-denominator comparison

| Existing descriptive score interval | Original-input FaceOcc passes | Enhanced-input FaceOcc passes | Attempts |
|---|---:|---:|---:|
| [1,3) | 6 | 6 | 6 |
| [3,5) | 6 | 6 | 6 |
| [5,7) | 5 | 5 | 6 |
| [7,9) | 4 | 5 | 6 |
| [9,10] | 0 | 3 | 6 |
| All | 21 | 25 | 30 |

These are the same fixed photos, supplied decimal labels and descriptive sampling
strata, without rounded categories or replacements. The four gains are one
previously empty final mask outside the highest interval and all three available
highest-interval parents. The five remaining failures are two detector failures,
two no-skin-overlap parser failures and one parent with183pixels. No failure was
dropped from a denominator. No calibration/tree fit or admission occurred.

The candidate adds56,413and loses2,011normalized mask pixels compared with the
prior final masks. These are prediction disagreements, not counts of correctly
recovered skin or misclassified objects. No technical-pass regression does not
mean zero mask regression. Successful masks have3,285–16,996normalized pixels,
but only108–773selected locations when projected onto the original pixel grid.
Neither count establishes native adequacy or independent sample size.

## All30boards inspected

The assistant inspected every six-panel board with source scores hidden:
original image; aligned original; enhanced aligned model input; old final overlay;
candidate final overlay; candidate additions pink and losses cyan. The five
unavailable stages are blank and labelled; no output is fabricated.

Apparently visible chin and lower-face skin is restored in one warm-condition
subject, and broad cheek/chin support is restored in another. A glasses case
gains much more forehead/cheek support than its prior tiny cheek patch. These
are qualitative observations, not dense ground truth. Fine frames, reflections,
hairline and jaw boundaries remain uncertain. Small boundary losses also occur.

Some central-face parser holes persist unchanged despite improved FaceOcc
recognition. The three newly passing highest-interval photos retain only a
forehead strip in two cases and fragmented broader facial support in the third.
The source faces are very dim and low resolution; a technical pass does not
make those limited regions reliable or anatomically comparable skin samples.
No broad object-leakage absence or skin accuracy is certified from these boards.

Among seven technically complete subject keys, the saved within-person ITA
range across the three conditions is102.62–165.67degrees (median107.81). This
describes feature instability, not calibration error or a tuned rejection cutoff.
It mixes lighting, selected-region differences and the existing atan-based
feature's sign behaviour; it does not establish a single cause. The seven-key
set differs from the preceding six-key set, so their aggregate ranges are not
a paired improvement comparison. Better coverage does not by itself solve the
matching ITA-to-MST calibration problem.

## Decision and remaining work

Retain this as a promising isolated recognition candidate with all earlier
baselines/failures intact. It is not made the application default and no cohort
is admitted. Stop the fixed appearance comparison here; no enhancement sweep,
threshold relaxation, geometric fill or automatic wider batch is activated.

The next substantive requirement is actual-skin support validation and a
well-defined interpretation/evaluation of original-colour ITA under these
lighting conditions. This needs evidence beyond pass counts on the same already
exposed sample. Preserve native-detail limits, decimal source scores, subject
grouping and full failure accounting. Do not fit only the successful cases,
silently change the ITA formula or fabricate/omit the MST feature. The retained
full correction tree still requires a justified compatible calibration cohort.

## Verification and preservation

Thirty original-label/source/member/parent-report parities passed. Twenty-five
aligned-input/transform checks and exact saved service replays passed. Independent
manual warp/threshold/intersection reconstruction matches all25saved masks;
original-pixel statistics, parent-subset guards, added/lost counts and native
projections also match. All bound source, history and parent artifact hashes
remained unchanged. Verification ran no additional inference or fit.

Sixteen focused transform/coordinate/landmark-bridge/veto/service tests passed
in1.74seconds; not a full-suite, human-study or device test. New effective contract:
`a5aadb1b26072cc863ef2416a8928598ad52f075e59a3f1489592b93ab38f9f1`.

Private local gallery: `outputs/stellenbosch_faceocc_appearance_v1/review_PRIVATE.html`.
Bound checks/notes: `outputs/stellenbosch_faceocc_appearance_assessment_v1/assessment_PRIVATE.json`.
Dataset images, individual labels, identifiers and manifests remain ignored and
must not be redistributed without consent. Research/noncommercial use and source
citation conditions remain. No uploads, contacts, calibration/tree fits, admissions,
runtime/Android changes or submitted/working-thesis edits occurred.
