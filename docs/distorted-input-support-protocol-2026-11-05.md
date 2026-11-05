# Distorted-input masking and recovery: fixed protocol

5November2026. User explicitly authorises the next test: recompute correction
and measurement masks on the same fixed distorted cases and measure recovery.
Use all168 saved cases (12sources times14) from ffhq_correction_targets_v1, no
new photographs, recipe/severity changes, replacement or extra variants.

Freeze dependencies/protocol and the previous artifact/input hashes before
inference. Re-run the existing .85 YuNet single-face guard, fixed landmark helper
with its unchanged ordered fallbacks, parser and nostril measurement on every
saved distorted RGB8 image, including12clean controls. Save every stage/failure,
categories, landmarks, baseline mask, aligned input/matrix. One fixed CPU
FaceOcc forward per available alignment in the existing isolated environment;
no threshold/crop/model search, installation or retry. Keep failures unchanged.

Use the existing preferred experimental measurement service with those actual
distorted-input predictions and save masks/statistics/features, all skin validity
unverified/MSTNone. Rebuild correction support/alpha through correction_preview
using distorted-input categories, landmarks and raw mapped visibility. Retain
the prior explicit clear designation for16061/59807 and opaque sunglasses29617;
others uncertain. These are prior assistant choices, not automatic classification.
No source mask, source veto or reference features may repair the new masks.

Compare new correction/measurement masks with their saved source counterparts:
IoU, lost/added pixels, alpha difference and neck pixels. These are consistency
measures against imperfect predictions, NOT segmentation accuracy. Record any
glasses-choice uncertainty and actual-skin/occlusion limitations separately.

Recovery uses one new bounded local target fit per available case with ACTUAL
input-derived alpha. Fit only the intersection of original scoring support and
new positive alpha, because the pinned solver requires score inside application.
Do not hide missed regions: evaluate EVERY output on the original fixed positive
source-alpha scoring mask, including regions no longer correctable. Compare
with the frozen fixed-alpha oracle from422. Report fit-intersection size and
outside-alpha/reference mismatch. Empty intersection or failed fit stays failed.

Apply fitted parameters to the FULL input-derived support, without clamping to
the source mask. Report changed channels/pixels and MAE outside original support,
and changes on the source's protected region. The latter measures disagreement
with prior protection, not independently annotated true-object errors. Protected
pixels under the NEW veto must remain unchanged. Failed pipelines have no target;
report their operational unchanged-input output separately so failures stay in
all168 denominators, rather than inventing a successful correction.

Predeclare visual screen of core combined_cool_under and stress_combined_under
for ALL12 sources (24boards), regardless of results; gallery contains all168.
Report clean/core/stress separately, failures and regressions with denominators.
Verify saved masks/service replay/alpha/renderer/metrics without new model
passes or refits; clean repeat consistency, source/historical hashes preserved.
No numeric acceptance thresholds, source admission, tree/MST fit, fake MST,
professional ratings, automatic repair/refit or publication. This remains an
oracle diagnostic of input-support effects, not learned model performance.
