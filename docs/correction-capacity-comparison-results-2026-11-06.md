# Capacity comparison: clean fitting succeeds, held clean preservation still fails

6November2026. The user-authorized one-capacity comparison is complete.
Unlimited-depth trees preserve every clean fitting example exactly, but harm
21of29held clean photos and increase average held clean error. **The candidate
is not adopted.** Increasing fitting capacity alone does not solve this
development experiment's clean-preservation problem.

## Fixed comparison and fit accounting

The [protocol](correction-capacity-comparison-protocol-2026-11-06.md) changes only
max_depth3→None. Keep original five Lab/ITA/continuous-MST features, unweighted
target normalization, seed42/minleaf1, same357trainable rows,10outer folds,
saved nested MST predictions/targets/supports and420attempts. Neither balanced
weights nor chroma additions are included. No new MST fits, target fits,
distortions or masks. This remains restricted fixed borrowed support, not the
whole-face app pipeline or actual-input mask robustness.

The first10fits completed their fitting and rendering checks but failed while
serializing a NumPy integer leaf count. The incomplete v1directory and script487
are preserved. Script489converts depth/leaf counts to ordinary integers and
repeats the identical10fold specification in v2. Total executed correction fits:
20including the serialization-failed attempt; final saved comparison:10trees.
This is a serialization correction, not an extra depth setting or search. No
claim of bitwise repeat-model equivalence is made because initial model JSON
was not saved.

## Training capacity versus held prediction

All261clean fitting-row occurrences across the10folds predict exactly
`[1,1,1]` and render byte-identical outputs. Those occurrences repeat the same
29original photos across folds; they are not261independent observations. Fitted
depths range21–26, with310–325leaves, versus depth3/eight leaves previously.

| Layer | Scored / attempted | Unchanged input MAE | Depth3 MAE | Unlimited-depth MAE |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|0|10.3689|13.4124|
| Core |232/240|20.7385|18.8434|16.8832|
| Stress |145/150|52.5649|34.0350|28.4346|

RGB8MAE uses the0–255channel scale. Eight held clean images remain exactly
unchanged;21worsen. Although this reduces the count of harmed clean images from
29to21, the mean harm increases. Core regressions versus unchanged input reduce
98→87of232; stress regressions28→16of145. This is not a uniformly better model.
Equal-key candidate MAEs:13.4914clean,16.9392core,28.3773stress. Candidate relative
CIEDE2000 means:4.8638clean,6.4191core,11.4175stress.

All420attempts remain accounted for:14original-failure cases lack scoring
support; nine undefined-ITA stress cases are unchanged predictive fallbacks in
the145scored stress denominator. Neither availability nor target-fit membership
was changed to improve this comparison.

## Verification and visual findings

Script490checks exact baseline training membership, all10fitting means/stds,
portable held predictions and all406saved renderer/metric outputs. All bound
source and baseline hashes remain unchanged. No verification refit was used.
The final saved run includes261explicit clean fitting-control/renderer checks.

Two new capacity-fitter tests plus32target-scaled/portable tests:
**34passed in4.24seconds**. Tests show the candidate can fit more than eight
distinct target regions without changing the default max_depth3, and that
duplicate feature vectors with conflicting targets retain a mean rather than
pretend to fit perfectly. No full-suite or device result is claimed.

All29held clean original/baseline/candidate boards were inspected. Some candidate
outputs preserve the original, while others have large bright/dark patches
inside the fixed support. Lower distorted-case averages do not establish natural
appearance or clean safety. The board template's third-column caption says
"feature candidate"; in this package it is the unlimited-depth capacity candidate,
not the earlier chroma-feature experiment. No new reviewer labels were inferred.

Final private models/rows/predictions/hashes:
`outputs/correction_capacity_comparison_v2/`.
Private verification/boards: `outputs/correction_capacity_assessment_v1/`.
Incomplete first attempt: `outputs/correction_capacity_comparison_v1/`.
All admission flags remain false. No final estimator refit, Android/runtime
change, private-data sharing, external contact or submission occurred. Author
research/noncommercial, citation and no-redistribution terms remain.

## Decision

The experiment establishes that depth3contributed to fitting undercapacity;
removing that limit allows clean training identity but does not establish held
identity. The fitted capacity/generalization gap is consistent with overfitting
and unresolved input/target ambiguity; it does not prove either is the only
cause or that arbitrary deeper/pruned settings will solve it.

Close this capacity test. Do not automatically sweep depth/pruning, combine
previous failed interventions or add an outcome-tuned identity threshold. The
next design decision must address how a previously unseen clean photograph can
be distinguished from an imposed distortion using inference-available evidence,
with explicit clean-risk reporting. This result is not a completed correction
model or permission to replace the app's existing model.
