# Fixed facial-root repair of the image-loss action tree

7 November 2026. User approves continuing work on wrong exposure choices.
Saved traces show all 11 joint trees use scene_l_p50 at the root. Six of the
seven changed scored clean photos reach leaves whose actions harm zero fitting
members. Strengthening fitting-loss constraints alone would not address most
of these errors. This is a retrospective mechanism observation, not causal proof.

One fixed repair: the ROOT split may use only original facial mean L/a/b, ITA
or MST. Descendant splits may use all 12 original features. Keep max_depth3,
minleaf1, deterministic split ordering/ties, image-loss objective, clean
feasibility and every existing action/control/cost matrix exactly unchanged.
No action-strength, feature-deletion, capacity, library or threshold sweep.
This hierarchy makes facial evidence precede scene context; it is not a
guarantee of safe exposure inference. Facial inputs can also encode illumination
and acquisition cues. ITA/MST remain available, not forced selected features.

Fit exactly 11 trees on the same ten held-key fitting configurations and one
full configuration. Reuse the already verified per-fit 14-action libraries and
rendered cost matrices, with exact source/hash binding. No new target, MST,
gain, gate, mask or detector fits/forwards. No new pixels or annotations.
The joint candidate still has no separate gate, range check or leaf override.

Before research fitting, constructed tests must check the facial-root restriction,
permitted descendant context splits, clean preservation and correct recovery
when facial features are informative. Keep prior model/code artifacts unchanged.

Evaluate all 756 saved attempts in the two nonduplicate principal contexts:
420 working256 development and 336 native224 fallback-mask conditions. The
borrowed/input-only native variants are not rerun in this bounded comparison;
their older results remain preserved and are not new evidence for this model.
Compare identity, retained gated model, parent joint image-loss tree and facial-root
candidate. Report clean/core/stress, RGB MAE and relative CIEDE2000, photo/key
means, harms, coverage and missing/scored/attempted counts. Zero clean changes
remains required; aggregate gains cannot excuse severe errors or loss of recovery.

Verify fitting exclusions, cached library/cost identity, feasible optimal leaf
actions, all eligible greedy split alternatives with the root restriction,
every prediction, RGB8 PNG, metric, outside-mask pixel and source hash.
Review all 57 fixed boards (52 scored clean photos, first available core/stress
per context, recovered warm case), plus up to four explicitly outcome-selected
worst clean/core regressions. These are exposed development cohorts, not fresh
validation. Distortions repeat 54 originals, not independent people/conditions.

Stop after this one comparison. No automatically deeper tree, next root subset,
feature/weight/threshold/strength change, ensemble, gate attachment, new data,
annotation, admission, runtime integration, sharing, contact, commit or publication.
