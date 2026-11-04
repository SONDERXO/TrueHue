# Post-check anatomical-containment development comparison

29 October 2026. The frozen YCrCb v1 check ended4accept/16reject. Keep that
negative outcome intact; do not promote v1. Its20sources are now exposed
development examples, never an untouched check for a policy built from them.

Freeze one candidate before processing: retain every color threshold, cleanup,
detector, landmark and feature-exclusion rule, but constrain color candidates
to the frame-local landmark face oval before largest-component selection.
Apply complete anatomical exclusions afterwards. No erosion radius, threshold
tuning, hole filling, parser model, source geometry or skin-mask fallback.
The oval is a fixed existing landmark topology, not a semantic occlusion mask.

Replay the same reference and global color-probe pixels from the20source check.
Require exact replay of the old candidate reports first. Save new masks,
geometry and every failure. Report old-selected pixels outside the oval and
new containment invariants, minimum support and old-mask retention, without
calling removed pixels confirmed contamination or retention mask accuracy.
Compare four previously accepted cases separately for possible regression.

Hands, hair, beard or objects lying inside the facial contour can remain;
missing landmarks and source blur are not solved by containment. Do not
silently select favorable cases or ask the user to re-review all20 before
assessing the candidate's concrete limits. No new candidate human labels,
ITA-to-MST mapping, target fitting, tree fitting or model promotion. The new
measurement definition requires its own calibration if ever adopted.
Final validation/test remain closed; all prior notes and raw exports stay intact.
