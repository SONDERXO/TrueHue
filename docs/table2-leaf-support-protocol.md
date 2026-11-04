# Fixed fitting-leaf support guard experiment

28 October2026. Hypothesis: the five-feature conservative tree can route an
unseen input into a distortion-only leaf without that leaf's fitting samples
supporting its feature values. Test one fixed no-extrapolation rule, not a
special case for1398/75027 or a learned confidence threshold.

Use unchanged15source/30pairfolds, baseline5splits and the already defined
identity-if-any-fitting-control leaf outputs. Within each fold, collect each
leaf's28fitting rows and record float32 minima/maxima for all five inference
features(Lab,ITA,MST). Route the query with the original float32 contract.
If any query feature falls outside that reached leaf's closed empirical range,
output exact identity; otherwise use its existing conservative parameter vector.
No margin,ratio,depth/feature selection,reference or held-label fitting. No
new tree fits. Keep all five axes rather than selecting those that favor results.

These axis ranges are a conservative rectangular support heuristic, not a
joint-support/density guarantee, calibrated probability or validated outlier
detector. Small leaves may abstain excessively; correlated ITA/MST can make
the rule redundant or restrictive. The auxiliary ranges extend the runtime
policy beyond a bare tree; any final adoption requires an explicit methodology
decision and subsequent validation, not silent replacement of regression.

Freeze the rule before scoring. Report overall/clean/distorted fixed-reference
CIEDE2000, every abstention, original versus guarded errors and identity harm.
Do not tune the rule to obtain a gate pass or omit uncorrected distortions.
Gates remain strict overall improvement against no correction AND zero held
clean harm. Passing on these repeatedly exposed sources is development evidence
only, not independent final accuracy, and never automatic activation. Preserve
all accepted concerns,7rejectedIDs,74holds,MST/clipping/reference limitations.
