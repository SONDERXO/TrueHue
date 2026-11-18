# Whole-photo distortions: scene features help recovery but worsen clean preservation

6November2026. The authorized paired comparison is complete. On the same new
whole-photo distortions, adding seven scene features reduces core/stress error
substantially, but increases clean error and still changes all29available clean
photos. **Neither candidate is adopted.** This supports the usefulness of scene
information for this synthetic task, not a finished automatic correction model.

## What changed and what stayed fixed

Apply the existing14-case recipe matrix to the full original224RGB scenes before
native crop and256resize, using one common medium engineering severity. Use all
30originals/10publisher keys/420attempts. These are global photometric operations,
not physically calibrated lighting or proof that the perturbations reproduce
real camera errors. All source images remain unchanged on disk.

For29available originals, clean scene→crop→resize pixels and clean facial
features exactly replay their saved counterparts. The failed original retains
all14attempts with full-scene inputs but no fabricated facial support. Borrowed
measurement masks remain fixed for facial statistics/application/scoring.
Correction is confined to the256working measured region; no full224scene
correction or whole-face/neck runtime is delivered. Outside-mask pixels equal
the distorted input, not the undistorted reference. Known beard/object mask
contamination remains, so no guaranteed object-protection claim follows.

Scene inputs are two stabilized mean-channel log ratios, three L*percentiles
and two exact-channel endpoint fractions, as fixed in the
[protocol](whole-scene-correction-protocol-2026-11-06.md). They use only the
distorted full scene. No source score, reference colour, recipe or condition
enters inference. There is no feature selection or threshold tuning.

Compare original five facial features with the same five plus seven scene
features on identical newly fitted targets and training membership. Both use
the original unweighted target-standardized depth3/seed42/minleaf1procedure,
with no gate or earlier repair combined. Ten held-key folds per method:
**20new correction trees**. Reuse the55saved nested MST ridges after clean parity
checks; no new MST fits or source-label substitution. Both own and outer key
remain excluded from correction-training MST estimates.

## Coverage and target accounting

There are406working pairs with support and397available facial-feature vectors.
Nine stress ITAs are undefined and stay unchanged predictive fallbacks;
14original-failure attempts remain unscored. Source-score predictions clip
113of397available held estimates to1–10, a retained calibration-distribution
limitation. Each model uses the same357trainable rows.

Target construction makes377nonclean local fit calls and29clean neutral
shortcuts. Of nonclean fits328are available;49degenerate stress inputs have no
valid target and are excluded from fitting, retained in scoring/reporting as
unchanged target-fit fallbacks. They are not oracle-recovery successes. Whole
scene synthesis precedes crop interpolation, so these new targets must not be
silently replaced by old restricted-region targets.

## Matched results

| Layer | Scored / attempted | Input RGB8 MAE | Facial features only | Facial + scene features |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|0|10.3838|14.7037|
| Core |232/240|20.7301|18.8452|10.1152|
| Stress |145/150|52.5380|34.0250|25.5244|

RGB8MAE uses the0–255channel scale. Both methods harm all29scored clean photos.
Core regressions versus unchanged input fall98→63of232; stress regressions
27→26of145. Equal-key facial-only→scene MAEs are10.3968→14.7963clean,
18.9783→10.2582core and34.1710→25.2942stress. Relative CIEDE2000 means change
3.7126→5.2599clean,6.7273→3.9165core and12.8774→10.2843stress.

The target-fit-or-unchanged-fallback mean MAEs are0clean,0.2374core and20.8044
stress. These are reference-aware conditional diagnostics, not extra predictive
baselines. Mean errors include operational feature fallbacks on scored support;
missing original support has no invented error value.

Feature improvement is assessed against the matched facial-only model above,
not against earlier experiments whose synthesized inputs/support semantics
differ. No percentage accuracy, statistical significance, unseen-cohort fairness
or reliable real-world correction is inferred from these descriptive averages.

## Verification and visual findings

Script494generates the paired experiment. Script495replays all420full-scene
synthesis cases, independently checks420scene-feature vectors, verifies3213
nested training feature traces and20fitting means/stds, and replays all812
paired renderer/metric outputs without refitting. All source/prior artifact
hashes remain unchanged. An initial independent-quantile check used float32
interpolation and disagreed by about1e-6; the verifier was corrected to perform
linear interpolation in float64. Production features and fitted outputs were
not changed or refitted.

Seven new scene-feature tests plus existing target-scaling/recipe/target tests:
**23passed in5.06seconds**. Tests cover fixed RGB channel ratios/stabilizer,
constant scenes, percentile/endpoints, input immutability and invalid inputs.
This is not a full-suite, device or scientific validation result.

All90preselected boards were inspected: clean and the two predeclared core/
stress cases for all30originals, including three original-failure contexts.
Scene-informed outputs sometimes restore more of a darkened face but conspicuous
regional alterations remain, including on clean photos. Severe stress detail
loss and borrowed-mask seams remain. The original scenes also visibly contain
a chart and common studio background; global scene features include those
pixels. Their performance may depend on these acquisition cues. No dedicated
chart extraction, known chart colours or reference-image correction was used,
and transfer to arbitrary scenes has not been tested.

Private images, targets, models, features and hashes:
`outputs/whole_scene_correction_v1/`. Private independent verification and
90board review: `outputs/whole_scene_assessment_v1/`. No new mask inference,
model download, source expansion, scientific admission, Android/runtime change,
source sharing, contact or submission. Research/noncommercial, citation and
no-redistribution terms remain.

## Decision

Scene context adds useful predictive information for the imposed distortions
in this release. It does not solve clean preservation, and broader context
alone is not sufficient evidence to adopt the model. Close this paired study;
no automatic gate combination, feature/threshold/depth sweep or refit follows.
A later intervention must retain this matched whole-scene baseline, clean harm
and missed-correction reporting, and explicitly justify any new operating rule.
