# Square256 measurement and MST calibration result

28October2026. Executed the fixed [protocol](mst-square256-calibration-protocol.md)
on418previously reviewed MST-E development images.396measurements succeeded;
21face-detection failures and1mask-stage failure remain without fallback.
All15previously represented subjects retain at least one measurement.

The same256frame is used for detection, masking and pixel statistics. The
hashed contract records model/code versions, square stretch, decoded-color
assumptions and pixel-count units. No old native ITA values or crop coordinates
were substituted. Twelve predetermined diagnostic boards were inspected;
fragmented/asymmetric coverage and possible hair/background/glasses selection
remain. Historical review acceptance does not approve these changed masks.

The subject-balanced calibration recipe could not create a full lookup:
decreasing isotonic centers pooled categories2–5,6–7and8–10. No arbitrary
epsilon gaps were added. Subject counts forMST1–10are2,2,2,1,1,2,1,2,1,1.
Holding singleton-category subjects out loses category support; remaining
folds also fail this recipe's separation condition. There are0available
held-out mapping predictions among396measurements; this is **unavailable
mapping**, not0%accuracy. Baseline-only ordinalMAE2.838(image)/3.0(equal-subject)
is not a paired candidate comparison because no candidate predictions exist.

No production threshold artifact was exported, no correction tree fitted and
no mask or runtime adopted. The method remains ITA→MST as requested; these
findings show that this fixed calibration design/data do not yet implement it
reliably. They do not prove all methods impossible. Further work needs an
explicit measurement/reference and independent-subject rationale, rather than
relabeling pooled thresholds as ten categories or reusing evaluation data silently.

[Measurement report](../outputs/mst_square256_measurement_v1/summary.json) ·
[Measurement verification](../outputs/mst_square256_measurement_v1/verification.json) ·
[Calibration/support report](../outputs/mst_square256_calibration_v1/summary.json).
Scripts138/139 refuse overwrites.607tests pass in11.16s. New unit tests use
synthetic fixtures, not study labels. No final accuracy, fresh independent
evaluation, expert review or calibrated complexion truth is claimed.

The measurement command's shell session reported exit1 although its complete
summary and final run-status were written; native MediaPipe stderr and PowerShell
redirection were present. The outputs and pixel arithmetic were checked rather
than treating that shell status as a clean process-exit claim. Preserve the log.
No rerun or model selection was performed to change that outcome.
