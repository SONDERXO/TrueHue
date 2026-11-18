# SegFace fixed six-photo screening protocol

User authorised loader work and continuing until input is needed. Loader
verification passed before this protocol. Freeze this protocol before private
photo inference. This is the one selected parser comparison, not a backbone,
prompt, crop, appearance or threshold sweep.

Use the six existing completed point/patch review photos by their saved source
hash bindings. Match the current-framing raw ResNet18 baseline from script 581:
same normalized256 actual input, landmarks, anatomical/nostril exclusions,
1,000-pixel guard, native projection and cached raw FaceOcc logits. No new
detector/landmark/FaceOcc forward. Retain review_06's existing landmark failure;
do not generate a prediction or count it as successful protection. Exactly five
new SegFace CPU forwards, with no retry on private inputs.

Input is RGB, PIL bicubic512, ToTensor and ImageNet normalization as verified
in script695. Upsample logits to512 if necessary using bilinear
align_corners=False; argmax at512 then nearest-neighbour categorical projection
to the existing256 coordinate frame. Remap SegFace's class IDs by label to
TrueHue's existing nineteen-class schema before unchanged mask construction.
The complete remap for SegFace IDs0..18 is
`[0,14,1,16,7,8,2,3,4,5,10,11,13,12,17,6,18,9,15]`.
Check all nineteen synthetic class IDs before photo inference. No map inferred
from skin colour, previous annotations or the appearance of the output.

Stage artifacts and the checkpoint are hash-checked. Use restrictive
weights_only CPU load and strict key matching; disable all network fetches.
Reuse the isolated inference environment without modifying its dependencies
or the active demo. No correction controls, outputs, calibration or model fits.

Score original-source reviewed coordinates against native projected measurement
masks. Report diagnostic and technically usable results separately, all six
attempts and paired-usable denominators, per-photo gains/losses, skin points,
unwanted points, and positive-patch overlap. Retain original point/patch totals.
Flag the existing point/polygon conflicts separately; do not relabel or remove
them. Marked patches include neck and are not complete facial ground truth.

Require: more reviewed skin points AND more reviewed patch pixels in the same
diagnostic paired set; more usable reviewed skin/patch coverage overall; zero
newly included reviewed unwanted points (also report conflict-aware definite
unwanted changes); retain all previously usable measurements; coordinate,
excluded-class/anatomical/nostril and original-pixel measurement invariants pass.
Failure of any requirement rejects the candidate for adoption. Missing masks
are failures, not protected negatives. More aggregate skin or lower total
unwanted count cannot excuse a newly included unwanted point.

Independently replay saved class/logit decoding, parent masks, cached visibility,
native projections, statistics and point/patch accounting with zero extra model
forwards. View every produced comparison board, including failures. No automatic
clear-lens/rim or beard accuracy claim: there is no explicit beard label or
frame/lens split, and existing generic object points are insufficient for those
claims. This measurement screen does not validate whole-face correction support.

Stop after this fixed comparison. Do not remove vetoes, change crop or blend,
switch backbones, fine-tune six photos, or train a correction model to rescue a
failure. Passing would be a development screen requiring a separate integration/
measurement/calibration decision, not automatic adoption. All final holdout
photos remain byte-unread. No upload, external contact, commit or push.
