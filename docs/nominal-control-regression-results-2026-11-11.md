# Direct nominal-control regression baseline ? 11 November 2026

The paper-aligned baseline is complete: seven depth4 DecisionTreeRegressors,
24 fitting rows per publisher-held fold, 35 held predictions and all40 attempted
roles retained. Original photographic sources are evaluation-only. This changes
the learner/targets from catalogue selection to direct parameter regression; it
is not an objective-only ablation or a rerun of the old direct-gamma comparison.

| Role | Input RGB ? output RGB | Input DeltaE ? output DeltaE |
| --- | --- | --- |
| Underexposure | 26.0255 ? 10.7216 | 9.0354 ? 3.8312 |
| Overexposure | 23.6381 ? 15.2098 | 7.9137 ? 5.0196 |
| Mild cool colour | 2.4125 ? 8.8945 | 2.3226 ? 3.3228 |
| Original photographic sources | 37.6034 ? 24.9013 | 13.2417 ? 8.9573 |

Original-source means improve over the saved raw-action and relative-action
candidates. Four source images improve, two worsen and one is unchanged. This
small exposed development comparison does not establish generalization or justify
selecting a deployable winner. Mild-colour means still worsen versus input; two
cases worsen, three improve and two remain unchanged. Six of seven reference
identities are edited. All seven underexposure RGB errors improve, but three
underexposure DeltaE errors worsen. No uniform-benefit claim is supported.

Frozen coverage, original-source mean and protection checks pass. Both controlled
per-recipe checks and unchanged-reference check fail. The baseline is closed and
not adopted. Engineering checks are unchanged within this comparison; exact zero
clean edits is not retroactively presented as a verbatim paper requirement.

Known-target parameter MAE over28 controlled/identity cases is gamma0.15459184,
red0.01686797, blue0. Blue targets are all one: zero blue MAE demonstrates no
learned blue-cast recovery. Nominal inverse controls precede RGB8 rounding and
alpha blending; they are engineering targets, not exact optimized pixel targets.
No parameter truth is invented for original photographic sources.

Independent verification passes:113 nodes,6,501 split options, fitting leaf means,
recipe-derived targets, publisher exclusions,35 routes, native RGB renders and
standard CIEDE2000 metrics. Portable predictions matched sklearn exactly during
execution. All seven group boards/35 case panels were actually viewed. Visible
failures include darkening an accepted reference and colour-to-exposure confusion;
mask/detail limitations remain, especially1188. These are assistant observations,
not new user ratings. All five unavailable904 roles remain unaltered.

The16 inputs, external constant-MST map, reviewed masks, renderer and scoring
footprints remain fixed. No image models, mapper fits, original photos, locks,
runtime or Android were accessed/changed. No acquisition or contact occurred.

## Next correction evidence

The present correction experiments use only seven independent reference bases.
Changing the loss or restoring literal regression did not remove the colour and
identity failures. More depth/weights/guards on these same seven are not selected.
Broader reference diversity is a reasonable next data-readiness step, not a claim
that more data guarantees success or a new calibration requirement.

The already local twelve-source FFHQ development sample has no completed user
reference-appearance decisions. Its old automatic-support experiment remains
closed; do not rerun it or transfer its masks/contracts. A separate appearance-only
review can determine whether any existing original photographs are acceptable
synthetic-restoration targets under the paper's original-photo definition. This
requires the user's photographic judgment, not another mask annotation round.
All twelve attempts and prior concerns stay visible. Approved appearance alone
will not infer support approval, MST labels or training admission.

Use the prepared reference review guide before any further data/model work.
