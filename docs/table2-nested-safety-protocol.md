# Training-only selection of the clean-leaf candidate

28 October2026. Freeze this evaluation procedure before calculating its results.
The existing conservative nine-feature policy still harms one held clean source.
Test whether training-only quality gates can withhold unsupported correction,
rather than adding a special rule around a known held-source failure.

Keep the same20approvedpairs and10outerheldsource/duplicategroups. Within each
outer fitting set of18pairs/ninegroups, perform nine inner held-group folds.
Each inner tree fits16pairs/eightgroups with the fixed9features/depth3/seed42/
minimumleaf1/unweighted settings. Apply the exact training-identity-leaf policy
using that inner tree's fitting controls only. No feature,threshold or policy
search. Save90inner models and180inner held predictions, including failures.

Before evaluating either outer held image, aggregate the18inner held predictions
and apply the existing gates: overall mean CIEDE2000 must be strictly less than
no correction AND every inner held unchanged control must have zero error.
If both pass, select the existing outer-fold conservative tree; otherwise select
identity for both outer held inputs. This is fold-level training-procedure
selection, not a per-image classifier or a source-ID lookup at inference time.
References are allowed for inner training-selection scores, never as prediction
features. Neither outer held targets nor scores may determine the decision.

Report all outer decisions, clean harm, distorted no-ops and overall/clean/
distorted scores. Identity-only behavior cannot satisfy the strict overall
improvement gate. A safe but ineffective result is not successful correction.
Do not relax gates to force selection or retry with an altered policy. The
representation and earlier experiment hypotheses were developed on exposed
sources; nested arithmetic does not erase that exposure or create independent
final evaluation. Retain weak MST, photographic-reference, clipping,source/
person and category limitations. No runtime or Android asset replacement.
