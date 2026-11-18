# Stellenbosch fixed face-crop bridge — 5 November 2026

The single [predeclared crop rule](stellenbosch-face-crop-protocol-2026-11-05.md)
improved technical availability on the same fixed30images from0/30whole-frame
measurements to18/30normalized measurements. This is a preprocessing diagnostic,
not a calibration result or qualification of the dataset. All30attempts remain.

The rule takes one native square with1.5times the saved detected face extent,
then uses the unchanged256px measurement pipeline. Native crops were46–61pixels
wide. Enlargement adds no source detail. Successful masks project to282–725
selected locations on the original pixel grid; these counts are neither
independent sample sizes nor evidence of sufficient native resolution.

## Results and retained limitations

Of30attempts,19passed parent measurement and received one CPU FaceOcc forward;
18passed the final normalized1000skin-pixel guard. Twelve failed: eight had no
predicted facial-skin overlap, two failed single-face detection, one parent had
907pixels and one final mask had404pixels. No thresholds were relaxed and no
alternative crops or replacement images were tried.

Each of the three fixed lighting conditions had6/10successes. The same six
subject keys passed all three conditions; four failed all three. Consequently,
the18technical passes cannot establish coverage across the selected score range,
lighting robustness, or an adequate calibration cohort.

The assistant inspected all30private boards with score labels hidden. Several
passing masks omit substantial central-face, cheek, chin or forehead regions,
and coverage changes with lighting. Glasses/reflections and dim low-signal faces
remain problematic. These observations are qualitative, without pixel truth or
an intrinsic-tone claim. No skin-support admissions have been made.

## Verification and scope

Scripts433–435 preserve and verify the old whole-frame package and source hashes.
All30native crops were independently checked as exact original pixel slices;
all30source decimal scores and raw types match the baseline. Nineteen saved
service replays, independent masked-statistic checks and native-grid projections
passed. No additional model inference was needed for verification.

The focused tests passed:29tests covering crop geometry/projection, deterministic
selection, decimal metadata and the FaceOcc service (3.09seconds). This is not a
new full-suite run. Effective crop preprocessing contract:
`8dbd6cb0b05728e972c66d8df005f59170df9cca934025fa62de67827ca9a374`.
Old whole-frame calibration/features cannot transfer under an equivalence claim.

Private evidence: `outputs/stellenbosch_face_crop_v1/review_PRIVATE.html` and
`outputs/stellenbosch_face_crop_assessment_v1/assessment_PRIVATE.json`. Photos,
individual scores and manifests remain ignored local files under the author's
research/noncommercial, citation and no-redistribution conditions. No dataset
content was uploaded or shared.

The bounded bridge check is complete. There were zero calibration fits, tree
fits, calibration admissions, runtime changes or rounded score categories.
Before fitting, the unresolved work is a justified native-resolution/skin-support
admission policy and subject-held evaluation scope that retains failures and
reports coverage. A crop or threshold sweep, expanded processing batch, and
clean-only calibration are not activated by these results.
