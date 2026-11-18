# Why the reviewed changes can look small: complete66-case audit

14November2026. User clarified “all cases that you had me reviewed,” then asked to continue. Preserve this as broad qualitative feedback across reviewed cases, not six isolated preferences and not66new case-level ratings. The bounded audit covers the latest66case review, including22previously judged exposure outputs carried exactly. Older trial files/results remain untouched.

[Protocol](reviewed-correction-magnitude-audit-protocol-2026-11-14.md); scripts/audit_reviewed_correction_magnitude.py; outputs/reviewed_correction_magnitude_v1. Original hashes verified for198saved PNGpanels and11selected alpha arrays. All66primaryRGB errors replay; outside-alpha pixels remain unchanged. Independent region/weighted-change accounting and review composition checks pass. No corrections were regenerated, model fitted, original review edited or new user answers inferred.

## Important review-design distinction

The latest review required44fresh judgments:11identity controls and33colour-only cases. Its22under/overexposure judgments were carried from exact matching prior outputs, and Next/Previous skipped them. Thus the latest fresh task consisted entirely of preservation controls and mild colour corrections. We should have surfaced this distinction before interpreting “all changes too small” as a general failure of the exposure model. Broad feedback is not dismissed by this finding; quantitative exposure changes and perceived strength are different observations.

| Role | Fresh/carried in latest review | Mean absolute RGB change inside selected region | Mean absolute RGB change over whole crop | Nominal full control recovered |
| --- | --- | ---: | ---: | ---: |
| Identity | 11fresh | 1.292 | 0.442 | 0/11 |
| Red-cast | 11fresh | 1.277 | 0.437 | 0/11 |
| Blue decrease | 11fresh | 1.224 | 0.417 | 0/11 |
| Blue increase | 11fresh | 1.534 | 0.525 | 11/11 |
| Underexposure | 11carried | 26.161 | 8.917 | 11/11 |
| Overexposure | 11carried | 23.935 | 8.167 | 11/11 |

Values are8bit RGB code levels, mean over channels/pixels and then equally over11sources. They are not visibility thresholds or new harm ratings. Nominal identity disagreement means some numeric change; all identity judgments had been acceptable under the recorded review. Tiny identity changes are preservation behavior, not automatically correction misses.

## Separate input strength, learning and application

**Mild colour inputs:** the diagnostics multiply ONEchannel by245/255or255/245, approximately-3.92%or+4.08%. Colour input-to-reference primaryRGB errors are only1.55..2.16mean code levels. Even correct recovery can be subtle: blue-increase output-to-reference error falls to0.081while its actual input-to-output change averages1.534. A correct inverse need not create a dramatic visual transformation. Making it stronger merely for visibility can move it away from the reference.

**Real colour-learning defect:** red-cast and blue-decrease recover no complete nominal vectors, consistent with the saved axis-mixing diagnosis. Red-cast meanRGB error increases2.162->2.510despite positive meanDE; blue-decrease drops only1.551->1.381. Mild stimulus strength does not excuse wrong-axis correction. The user explains weak perceived benefit rather than observed visible harm; do not substitute these numerical harms for new user harm reports.

**Exposure is different:** both exposure directions receive their nominal controls and show about24..26mean code-level changes inside selected skin. Input/reference error drops from25.49/27.75to1.68/1.64. This does not override the user's perception, but the saved data do not support a universal claim that all controls were uniformly suppressed. These outputs were carried rather than newly judged in the latest task.

**Application geometry:** correction occupies23.5..42.3%of each256crop, mean34.1%. The full-strength core occupies mean30.3%of thecrop, with feather mean3.79%. Aggregated across sources about88.9%of the selected region is alpha1; source-equal mean alpha inside the region is0.943. Feathering attenuates edges but is not applying a uniformly weak blend across the face. Outside pixels stay exactly input, so wholecrop changes are smaller. This is the intended local-correction condition, not permission to dilate masks or correct the background.

## Paper alignment

Read the already cached111page proposal extraction, pages62–63, without opening/modifying the proposal. Table2specifies light/medium/dark gamma0.85/0.70/0.60, brightness-20/-35/-45, contrast+5/+8/+10, red-axis-6/-10/-14andblue-axis+6/+10/+14. Page63defines original photographic references and three predicted outputs gamma/red/blue.

The current66conditions deliberately isolate identity, two gamma exposure roles and three mild single-axis casts. They are NOTthe complete tone-dependent Table2composites or a severity validation. Table2slider units/order remain a documented implementation issue: -10does not by itself establish whether to use an additive code offset, percentage multiplier or a specific editor conversion. Therefore245/255cannot simply be declared an implementation bug from the table numbers. Do not replace it with0.90or a new stronger slider setting without a declared operator/target contract. Additive/clipped composites also cannot generally be inverted exactly by the existing3controls; the historical target-fit work must be respected.

## Decision

Do not apply a global strength multiplier or start another cue/model search as the response to this feedback. Three distinct facts are now established: the fresh review concentrated on inherently small colour/preservation changes; red/blue-decrease predictions are genuinely diluted/mixed; and blending is local but mostly full-strength inside its selected region. No one strength setting addresses all three.

The next bounded decision should align ONE prospective paper-relevant condition/target/evaluation specification with the permitted source/tone evidence and exact operator definitions before more fitting. Use the paper's intended regimes rather than selecting severity to obtain a conspicuous result, and keep the isolateddiagnostic findings separate. No new severity, target optimization, correction strength, mask, acceptance rule, source admission, fit or rating batch is selected by this audit. Originalratings/NOTREADYassessments and user clarifications remain preserved; no posthocPASS or final adoption.

Whole-set feedback remains important, but no universal stronger-correction instruction follows. Skin/bias subgroup success is not established by this unlabelled11source development set. No actual user-display measurement or new visual score was produced. No NPZ/raworiginal/lockedholdout/Android/manuscript access/change; earlierbaseline/closures/approved59807manual/ears retained. Modelunfinished/paperpaused/darker-skinpriority/November25deadline/modelASAP.
