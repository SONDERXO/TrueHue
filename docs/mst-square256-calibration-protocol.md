# Square256 measurement and calibration protocol

28 October2026. User authorized the paper-consistent measurement/calibration
stage. Fixed before processing: decode with OpenCV IMREAD_COLOR, resize the
whole decoded image to configured256×256 using INTER_LINEAR, then detect and
measure in that same frame. No separate high-resolution detector, crop-first
resize, aspect-preserving fallback or transferred native-coordinate boxes.
This follows the proposed square input; stretch/codec/color-profile limitations
must be reported. Encoded images are treated as sRGB without camera calibration.

Use existing YuNet at0.85, exactly one face, complete-mouth HSV AND YCrCb
mask with existing anatomical exclusions, required landmarks and minimum1000
selected facial pixels. These are fixed baseline settings, not a threshold
search. YuNet and the detailed mask remain documented proposal differences.
All model/code/codec versions and pixel-count units enter a hashed contract.
The contract is reused across MST-E and future FairFace/SCIN input measurements.

Reprocess exactly418historically reviewed/included and metadata-matched MST-E
development images. Original reviews, native measurements and excluded sources
remain unchanged. Historical approval does not validate the new square masks.
Every attempt/failure is retained; no new source or reserved imagery. Select12
diagnostic boards by SHA256(seed42/image_id) before processing; no replacement.
MST-E is used only for this disclosed mapping-development study, never correction
tree fitting. The proposal's calibration/evaluation wording and previous exposure
prevent calling these images a fresh final test.

Calibration algorithm: one ITA median per measured subject, preserving official
MST; one median of subject medians per category. Fit decreasing isotonic centers
over categories1–10weighted by subject count, then midpoint adjacent centers.
All ten categories and nine strictly separated boundaries are required. Missing
categories or pooled/equal centers block a full ten-category lookup; never invent
epsilon gaps or unsupported category centers. This is a fixed diagnostic recipe.

Leave each measured subject out, repeat the same calibration using other subjects,
retain unsupported folds and compare available predictions to a training-subject
median-label baseline. Report support, exact/within-one accuracy, ordinal MAE and
subject-balanced results with explicit denominators. Independent category support
(at least two subjects/category), complete fold availability and better held-subject
MAE than the median baseline are necessary development checks, not final validation.
No production lookup is activated by this exposed-data diagnostic, even if those
checks pass. No threshold/feature/regularization search or correction-tree fit.

If measurement/support fails, record the concrete failure and preserve the method;
do not silently relax pixel count, reuse old ITA or switch resolutions. SCIN labels
remain separate; no annotator chosen or new images downloaded in this stage.
