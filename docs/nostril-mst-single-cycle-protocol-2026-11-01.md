# Frozen nostril-excluded MST calibration cycle

1November2026. User adopted whole-face correction with inward blending and
explicitly retained skin-only ITA/MST exclusions, then authorized this cycle.
Freeze the correction design and current measurement contract
1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7.
No mask, radius, weighting, calibration algorithm or correction-tree search.

Attempt exactly the418previously exposed MST-E mapping-development photographs
from reviewed_included_rows.csv, preserving source IDs/subjects/official labels,
lighting and every failure. Reserved correction evaluation data stay locked.
MST-E never fits the correction tree. Reusing exposed data cannot establish an
untouched final test or new independent-subject support.

Use the actual nostril_measurement pipeline once per photo: square256, existing
YuNet/exactly-one face and required landmarks, pinned parser, existing semantic
skin/nose and hard anatomical exclusions, then conservative nasal-base guard.
Save categories, landmarks, masks and stats for independent exclusion checks.
Assert zero selected pixels in forbidden predicted classes, hard eye/brow/mouth
exclusions and the nasal guard. These are construction checks, not annotated
semantic correctness. The parser can mislabel hair/beard/occluders as skin and
the nasal guard is approximate. No selective failure retry or old-ITA fallback.

Fit the SAME decreasing subject-balanced isotonic/interpolation method in15
held-subject folds. Each fitting subject has equal total weight; keep all held
subject photos outside calibration. Derive membership from NEW successes.
Save IDs, weights, knots and predictions. Compare with the fitting-subject median
baseline and the prior semantic mapping on identical available rows. Compare
processing coverage separately; common-row scoring does not control changed
fit memberships. Report exact accuracy, within-one accuracy, image/subject MAE,
category support, lighting and unavailable/unsupported cases.

Do not invent a universal reliability threshold or category10 endpoint. A
favorable mean error does not establish reliable MST. Report observed evidence
and whether prior weaknesses remain. No all-row runtime lookup, current-demo
switch or correction-tree fitting follows automatically. If reliability remains
poor, retain the failure and stop; do not try another small calibration recipe.

Replay every successful vector from saved source/mask pixels, saved exclusion
invariants, fold membership/weights/refits and all predictions. Diagnostic board
selection is the existing fixed15attempts (one per subject), not favorable cases.
Any suggested human review must identify the actual missing judgment, not ask
the user to repeat unrelated source/mask reviews. Preserve all old artifacts.
