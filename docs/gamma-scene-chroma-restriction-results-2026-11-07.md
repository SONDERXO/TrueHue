# Gamma-only scene-chroma restriction: results

7 November 2026. Completed the [single frozen comparison](gamma-scene-chroma-restriction-protocol-2026-11-07.md).
Removing two scene-colour inputs from gamma fitting slightly improves the original
held-key core comparison, but does not fix the newly harmful recovered photo.
All gated outputs on the later eight-key cases are byte-identical to the previous
model; several ungated means worsen. **Not adopted.**

## Exactly one intervention

Gamma fitting sets scene_log_r_over_g and scene_log_b_over_g to constant zero.
Neither feature appears in any new gamma split. The full12feature interface stays
compatible; the other10inputs still include facial colour/ITA/contextual MST.
This is not a luminance-only model. Same unweighted standardized gamma objective,
depth3/seed42/minleaf1, fitting rows, targets, held-key folds and nested MST inputs.
Gains are reused byte-for-byte; gate decisions and every other model stay fixed.

11new photographic gamma fits:10saved development folds plus1full357row head.
No gain/gate/MST/target fits or image-model inference. Software tests use separate
generated fixtures. No repeated photographic fitting after reporting errors.

Four comparisons preserve their own supports/renderers:420held-key working256
attempts, and three336case native224 comparisons (borrowed support, actual-input
support, detector-fallback support).1428attempt records are repeated condition
comparisons on54original photos, not1428independent photos. The later eight keys
were already development-exposed. No pooled accuracy or fresh-test claim.

## Gated RGB error on each original reference region

MAE in0–255codes; previous -> restricted gamma.

| Condition | Clean | Core | Stress |
|---|---:|---:|---:|
| Held-key working256 |0.05580 ->0.05580|13.51194 ->13.19006|23.75824 ->23.75824|
| Borrowed native224 |0.02774 ->0.02774|15.42751 ->15.42751|24.11074 ->24.11074|
| Input-derived native224 |0.02774 ->0.02774|17.74503 ->17.74503|37.71315 ->37.71315|
| Detector-fallback native224 |0.02774 ->0.02774|17.42631 ->17.42631|36.22723 ->36.22723|

Held-key reference availability remains29/30clean,232/240core,145/150stress;
397feature predictions and9undefined-ITA no-ops, plus14original failures.
Native reference availability remains23/24,184/192,115/120. Feature availability
is318borrowed,275input-derived and291fallback cases. Native cases without original
reference support retain full-scene scores and remain unscored in region means.
Failures remain in attempt denominators; no fabricated zero colour scores.

Gated held-key core harm count drops9->6/232. Only3gated fold outputs change:
three exposure-over variants of one original photo, not three independent subjects.
All held-key clean and stress outputs stay byte-identical. Clean gated harm3/29
and stress harm1/145 remain. No gated native output changes at all across the
three conditions, including the existing false correction and clean harm.

## Ungated trade-offs

| Condition | Clean RGB MAE | Core RGB MAE | Stress RGB MAE |
|---|---:|---:|---:|
| Held-key working256 |1.32544 ->1.32544|3.56120 ->3.34114|22.85557 ->22.85557|
| Borrowed native224 |3.23507 ->4.61626|3.69551 ->4.04809|24.64308 ->24.84308|
| Input-derived native224 |3.23507 ->4.61626|7.43920 ->7.61530|38.17219 ->38.17219|
| Detector-fallback native224 |3.23507 ->4.61626|7.12048 ->7.29658|36.68627 ->36.68627|

Only4ungated held-key outputs change. Later ungated changes involve one clean
photo, two core variants per support condition and one borrowed-support stress
case. The fixed gate suppresses every changed native result, which explains why
gated results are unchanged while ungated means worsen. Full per-region RGB,
relative CIEDE2000, equal-key means and full-scene native diagnostics are retained
in results_PRIVATE.json; they must not be pooled across supports.

## Why the focal error survives

For the recovered mild-warm case the new gamma route still begins with scene
L*median50.1961 between43.7255 and58.6275. The third split now uses measured facial
L*29.5631 above18.9879, replacing the old scene-blue/green split. It reaches the
same87row overexposure training group and the same gamma1.427846. Focal leaf
membership is identical. All357full-training gamma predictions are unchanged,
even though some later-case routes differ. This is a saved fitting-partition
observation, not proof that the task is impossible or all feature information
is insufficient.

The focal gains1.146909/0.843193 and gate+0.338688 are frozen; all three controls
and the full output remain exact. Error on its own62predicted native pixels
stays32.2258, versus1.1129unchanged; full-scene error stays2.05803 versus2.01958.
The original reference mask remains unavailable, so the region diagnostic is
not official skin accuracy. Dropping those two inputs alone does not address
the learned exposure/colour confusion or the permissive gate for this case.

## Verification and visual review

Verified11gamma artifacts exclude both forbidden splits, frozen gain artifacts,
training membership/normalization and3570training routes/88rawleaf means;
1281feature/control/gate replays;2828exact saved render/metric replays, including
unchanged pixels outside application support.23native clean outputs are identical
across all three support conditions, allowing one visual review per clean photo.
Source/model hashes remain unchanged.35focused tests passed in5.34seconds,
including restriction/invariance/gain-freeze checks and a real failure-denominator
regression test. No verification refits.

Viewed61preselected boards:29held-key clean,23native clean and9fixed native
core/stress/focal comparisons. Additionally viewed4outcome-selected boards for
the3changed gated fold cases and1changed ungated native clean case; these are
explicitly descriptive, not independent/blind review. Existing missing skin,
forehead-only support, glasses/material uncertainty and hard correction boundaries
remain. Better selected-region numbers do not establish acceptable full-face output.

Two incomplete rendering/report packages are preserved:comparison_v1 failed while
counting changed outputs for original failures;v2 failed on the corresponding
scene-summary path. The corrected v3 retains those missing cases without numerical
scores. All three executions used the same11saved fitted artifacts; no outcome-
based model change, exclusion or extra fitting occurred. v3 is the completed result.

Private artifacts: gamma_scene_chroma_models_v1, gamma_scene_chroma_comparison_v3,
gamma_scene_chroma_assessment_v1 and gamma_scene_chroma_review_v1. v1/v2 comparisons
remain incomplete history. Scripts527–532; isolated helper
src/model_training/gamma_scene_chroma_restriction.py. Previous models/outputs retained.

Close this single feature intervention. Do not automatically remove more features,
change capacity/thresholds, repeat fitting, expand subjects or integrate this model.
Further correction work needs a separately justified intervention that distinguishes
exposure from baseline face/scene appearance; this result alone does not choose it.
All admissions/adoption flags remain false. No Android/runtime change, contact,
sharing or submission. Research/noncommercial/citation/no-redistribution terms retain.
