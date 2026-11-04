# Proposed Table 2 clipping-stress experiment

28 October 2026. Prepared for a methodological decision; not executed or approved
by preparation. The user approved retaining Table 2 and approximate recovery
targets. That does not establish that clipped inputs should enter training.

## Concrete proposed change

Keep the existing unclipped training path intact. Add a separate, versioned
experimental cohort allowing Table 2 clipped inputs, recording clipped pixels
and channel fractions on generation support. Call its targets approximate and
reference-informed. Report it as learning limited recovery from synthetic
distortions, including irreversible clipping, rather than exact restoration.
This would be an explicit exception to the current unclipped admission rule,
not an automatic promotion of the 18 feasibility probes.

Before any fit, freeze the source list, duplicate/source groups, source-level
outer folds, independently justified tone-group assignment, all mask-quality
decisions and all failures. No MST-E image enters correction-tree training.
The experimental lookup remains labelled weak and incomplete; its mapped input
MST comes only from distorted-input ITA. Do not invent source complexion truth
or infer that all ten categories are independently supported.

Only sources with explicit same-contract mask/source approval may enter. This
six-source diagnostic is not that approval. Keep scene-validity concerns and
previous review holds. Include clean identity controls for each fitting source;
keep every variant of each held source outside its fitting fold. Do not reuse
the historical native224 or different ten-feature cohort as square256 rows.

Use one predeclared depth3, seed42, minimum-leaf1 decision-tree regressor with
the five input Lab/ITA/experimental-MST features and three fitted parameter
targets. No hyperparameter search in this bounded experiment. Fit targets with
the existing frozen optimizer only; retain failed fits and measurements as
unavailable, with complete denominators. Fit-time references never enter input
features or inference.

Primary comparison: no correction versus learned correction on the identical
fixed reference-mask support, reported by held source and severity. Report
equal-source CIEDE2000, RGB MAE, identity-control harms, mask retention, clipping,
availability and fitted-oracle capacity separately. Do not substitute
intersection-only scores or oracle scores for learned performance. A source
reference mask remains estimated, not calibrated ground truth.

Necessary development gate: held-source mean fixed-support error improves over
no correction, with no harmful identity-control corrections beyond an explicitly
predeclared tolerance. Define that tolerance before fitting from an independently
justified criterion; do not derive it from the observed candidate results.
Passing is not final external validation or automatic deployment. Preserve all
failed candidates and unchanged runtime until a separate adoption decision.

Decision requested: allow this separately labelled clipped-input development
experiment, while retaining mask/source review and source-held evaluation gates,
or keep clipped inputs evaluation-only. No cohort is ready to fit at this point.

## User authorization and implemented preparation

The user answered “Okay lets do those” after the recommendation to allow this
separate path. This authorizes experimental clipped-input training with the
listed safeguards. No further decision on clipping permission is needed.

Implemented a separate policy `table2_clipping_stress_training_v1`; the original
unclipped validator is retained. It requires consistent support-based clipping
counts/fractions, same-contract image/mask evidence hashes, declared explicit
mask and single-person scene approval, and all common measurement, target,
input-MST and source-role invariants. Evidence files must be hash-verified by
the eventual caller, not accepted just because a row declares hashes.

The six staged sources use the experimental lookup on each reference ITA to
choose one severity. This is an explicitly estimated grouping supported by the
existing FairFace preparation convention, not independent official labels.
The lookup is frozen from MST-E development data; correction references do not
calibrate it. The actual feature still uses distorted-input ITA and mapped MST.
Result: two light and four medium sources; no dark-group training coverage.
Other severity probes remain separate diagnostics. This limited cohort cannot
support all-category model claims or a claim of validated source stratification.

Prepared 12 unadmitted candidate rows (six identities, six selected distortions)
and six provisional folds over existing source/duplicate groups. These are
source-separated folds; person identity across distinct sources is not verified.
Any review rejection requires rebuilding folds before fitting. The identity
gate is fixed before fitting at zero increase in fixed-reference-mask error:
a conservative engineering gate, not a claimed visual just-noticeable threshold.

[Offline mask and scene review](../outputs/table2_stress_review_v1/review.html)
is the next user verification. It preserves all existing reviews and does not
confer admission. Known concern: 51739 includes another partial person; substantial
distorted-mask holes are visible in other sources. No automatic acceptance from
past native224 or different256-policy reviews. No tree fitted yet.
