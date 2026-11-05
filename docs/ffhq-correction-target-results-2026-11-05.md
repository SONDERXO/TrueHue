# Photographic correction targets: core recovery works; stress failures remain

5November2026. This advances correction development from generated ramps to
the same12 actual FFHQ photographs with revised object/clear-lens masks.
**The three controls can closely restore the core synthetic cases when fitted
against the original reference. No correction tree was trained.**

[Open the original/distorted/recovered gallery](../outputs/ffhq_correction_targets_v1/review.html).
These are target-aware operator fits, not learned or automatic predictions.

## Fixed experiment

The [protocol](ffhq-correction-target-protocol-2026-11-05.md) was saved before
variants/fits. Each of all12 sources received the existing14-case matrix:
1clean,8core and5composite-stress-design cases,168total. One fit per nonclean
case:156local target fits plus12exact-neutral shortcuts. All168 produced
available targets under the existing solver checks; none was dropped or replaced.

Recipes, fit bounds.25–4, neutral start,500-evaluation maximum, tolerances1e-10
and rank3 check were unchanged. Maximum reported evaluations was12; no refits,
severity/model search or additional correction output. Three outputs remain
direct-exponent gamma, red gain and blue gain.

Every photograph used the same `medium` Table2-derived severity preset as a
common engineering condition. **This does not assign MST or skin categories.**
It is a disclosed diagnostic departure from406's future admitted-source,
MST-bound severity design, not a final augmentation/sampling policy.

Original256px RGB working images supply photographic references, not intrinsic
skin-colour truth or certified ideal lighting. Synthesis and recovery share the
exact saved revised alpha from418. Scoring uses all positive-alpha correction
pixels, including retained facial features and associated neck; not a verified
skin-only mask. Protected objects are unchanged and not scored. No detector,
parser, landmark or FaceOcc inference was rerun on distorted inputs. Results
therefore establish **conditional fixed-support operator capacity**, not final
input-derived masking/features, training readiness or end-to-end accuracy.

## Results on identical scoring support

RGB errors are mean absolute RGB8 channel differences on the0–255 scale.
CIEDE2000 is relative to the original photograph, not physical skin truth.
Means treat each fixed source/case equally within its layer.

| Layer | Cases available/attempted | RGB MAE before → after | Relative CIEDE2000 before → after |
|---|---:|---:|---:|
| Clean | 12/12 | 0 → 0 | 0 → 0 |
| Core | 96/96 | 18.665 → 0.135 | 7.044 → 0.129 |
| Composite stress design | 60/60 | 53.593 → 11.034 | 18.364 → 8.392 |

All12 clean cases remain exactly identical. Core cases have zero forward clipping;
their per-case residual MAE ranges0.012–0.395codes. These are means, not bounds
on every pixel, and recovery is not exactly lossless. RGB8 quantisation and
blended boundaries remain relevant.

53of60 stress cases have forward clipping. All60 stay in the stress layer,
including the seven with zero observed clipping. Worst fitted case MAE is38.294
codes on29863/stress_combined_under. No fit reported an active solver bound.
Lower average RGB error does not establish natural-looking colour or reliable
restoration of clipped detail.

Four stress cases worsen in relative CIEDE2000 despite lower RGB MAE:

| Source | Case | CIEDE2000 before → after |
|---|---|---:|
| 32685 | stress_exposure_over | 16.466 → 18.198 |
| 32685 | stress_combined_over | 16.902 → 18.285 |
| 48879 | stress_exposure_over | 16.240 → 23.589 |
| 48879 | stress_combined_over | 16.329 → 23.380 |

The RGB-squared fitting objective and perceptual metric need not agree. These
regressions are retained; there was no perceptual refit or favourable-only score.

## Visual findings

Before outcomes, the protocol fixed assistant inspection to combined_cool_under
and stress_combined_under on every source:24saved boards. All24 were inspected
at the256px working scale. Core recoveries appear close to their originals.
Stress-under recoveries often have conspicuous red/magenta/black patches,
posterised shadows, washed bright areas and eye/mouth remnants.29863 is severe;
49131 has dark eye/jaw patches, and39568 has dark eye/mouth regions surrounded
by overly bright colour. Clear-lens handling and object protections remain
consistent with the saved support, but that does not repair clipped detail.

These are assistant observations, not human/expert ratings or inspection of
all168 outputs. Full per-source notes and the four numerical regressions are
in the [assessment](../outputs/ffhq_correction_targets_assessment_v1/assessment.json).
All168 cases remain visible in the gallery and
[case CSV](../outputs/ffhq_correction_targets_assessment_v1/cases.csv).

## Verification and model-development decision

All168 saved outputs match the actual apply_blended renderer, and saved-recovery
replays/metric recomputation passed without refitting. Protected/outside pixels
are unchanged; clean identity is exact.168CSV/JSON rows agree.36focused tests
passed in4.95seconds for the diagnostic, target solver and reused core recipes;
not a full-suite run or scientific validation. Source images, preceding packages
and pinned historical sources/manifests remain byte-for-byte unchanged. New
experiment/assessment packages have artifact manifests; separate verification is
`outputs/ffhq_correction_targets_verification_v1/verification.json`.

This supplies real-photograph evidence for constructing approximate three-control
targets on the core recipes. It also shows why severely clipped stress fits
must not automatically become ordinary correction labels: even target-aware
fitting leaves visually poor outputs and metric regressions. No target is
admitted for tree training from this experiment, and no new acceptance cutoff
is invented. The core/stress separation remains in place without tuning.

The next substantive model requirement is distorted-input support/measurement
consistency and justified source/feature admission, followed by compatible MST
before the retained full tree can train. These12 photos still have unresolved
beard/hair measurement, neck/reference and person-grouping limitations; they
are development-exposed, not unseen final evaluation. ITA-to-MST is deferred,
not omitted or replaced with fake labels. No new model inference, tree/MST fits,
runtime switch, contacts, publication or paper edits. Panel register C09/C10/C12
records the diagnostic and its departures; no panel approval is claimed.
