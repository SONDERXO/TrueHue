# Operator review decision and generated algebra results

14 November2026. Completed the requested operator-method review and its one
predeclared arithmetic check. [Candidate and fixed stopping rule](affine-prepower-operator-candidate-2026-11-14.md).

## Decision

Do not repeat the old fixed-midpoint contrast comparison. Keep one technically
motivated candidate on record: shared positive scale and signed offset before
direct gamma, followed by the retained red/blue gains. It adds two controls to
the current three. The five-output family is a substantive thesis/runtime
method extension, not an unchanged implementation or an adopted model.

This candidate specifically addresses the scale/offset-before-inverse-power
mechanism in the directional exposure operator. It does not supply a new cue
for predicting the controls from a single photograph. Its generated success
does not qualify five-output tree training or authorize changes to the paper.

## Executed bounded check

Script `scripts/check_affine_prepower_operator_algebra.py` froze39probes and
the protocol/code hashes before evaluating them. It uses standard-library
scalar arithmetic only: no image libraries, optimizer, model, dataset reads or
new dependency. Exactly21identity/unclipped exposure,14combined and4clipped
collision records were evaluated. The output directory refuses overwrite and
preserves a failed attempt if any check fails.

| Check | Observed result |
| --- | --- |
|21ideal identity/exposure records | Maximum continuous channel error1.6653e-16, within frozen1e-12tolerance |
|Separate exposure-inverse arithmetic | Maximum discrepancy2.2204e-16 |
|Current three-control nesting | Exact0discrepancy at scale1/offset0 |
|Ideal recovery after input RGB8 quantization | Maximum normalized channel error.0019874; descriptive, not an acceptance cutoff |
|14combined records with exposure-only analytic controls | Maximum normalized channel error.0460591; no gains fitted or extra channel offsets added |
|Two clipped collision pairs | Equal observed inputs produced equal recovered outputs despite different references |

The known controls were obtained algebraically from each prescribed forward
operator. They are neither target fits nor automatic predictions. The combined
residual is for those known exposure-only controls; it is not the best possible
five-control residual or proof that no other controls could improve it. Some
combined values may clip. Quantization and clipping are retained, not tuned away.
No source-group, human preference, physical-colour or fairness evidence exists
in these artificial probes.

## Implication for model work

The bounded mechanism check passes; adoption does not follow. There are two
separate unresolved requirements: represent useful corrections and predict
appropriate controls without altering acceptable images. The new family helps
explain how an unclipped exposure inverse could be represented; it does not
resolve the failed red/blue predictions, combined additive colour inversion,
identity behavior on unseen inputs, lost clipped detail or darker-skin bias.

Proceeding beyond this result would mean deliberately pursuing a five-output
method, with a new identifiability/target-fit/safety contract and later grouped
evaluation. No solver bounds, regularization, learned roster, extra real-photo
fits or new review is selected here. If the thesis must retain exactly three
predicted controls, this candidate is incompatible with that requirement and
must not be disguised as preprocessing or silently added to Android.

The current decision is therefore a documented proposal with an ideal mechanism
pass, not approval to expand the thesis model. Do not turn it into an automatic
sequence of generated studies, target fits, feature searches or training runs.
The earlier four-control positives, regressions and closed studies remain intact.

Evidence: `outputs/affine_prepower_operator_algebra_v1/plan_PRIVATE.json`,
`records_PRIVATE.json`, `verification_PRIVATE.json`. Protocol/code hashes remained
unchanged.0optimizers,0tree fits,0photo/mask/NPZ arrays,0new ratings or sources.
No locked final24/older contents/manifests, runtime/Android or manuscript edits.
Approved manual/ear support and darker-skin priority retained; model unfinished,
paper paused, November25 deadline retained.
