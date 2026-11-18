# Bounded local nonharm refinement — 9 November 2026

The single approved comparison is complete. Local refinement satisfies the
fitting nonharm constraints but reproduces **all 756 outputs and candidate
metric records of the earlier facial-exception candidate exactly**, including
its known colour-stress harm. It fails the unchanged joint criteria and is not
adopted. The final eight-group, 24-photo holdout remains byte-unread.

## Intervention and verification

The user approved the bounded intervention after the saved separability audit.
The [protocol](local-nonharm-refinement-protocol-2026-11-09.md) was written before
fitting or new evaluation inspection. At most one split was allowed in each of
the eleven audited conflicting leaves. All ancestor splits and other leaves
were fixed; only existing fitting features/costs and the fourteen saved actions
were used. No recipe input was introduced at inference.

Feature order, ascending float32 midpoint candidates, smallest-index action
ties and the strict improvement tolerance were fixed in advance. No depth sweep
or outcome-driven retry occurred. Reserved-clean veto membership was recomputed
for the refined leaves under the same veto policy and frozen facial exception.
No new MST or target fitting occurred.

All eleven configurations added exactly one split. The independent scalar
verifier exhaustively checked 6,000 candidates, the selected child actions and
membership, exact preservation of all other nodes/traces/data, and all source
hashes. It also passed 880 repeated fitting clean constraints, 2,383 repeated
colour-only constraints, 220 reserved-clean identity checks and 756 predictions
after final postprocessing. These are repeated occurrences, not independent
photos. The aggregate is bound to its verification receipt.

Eight configurations selected `input_mean_l_star`; three selected
`scene_l_p90`. The three with overlapping blocker/beneficiary marginal ranges
still reduced the total constrained objective: the split need not perfectly
separate every exposure beneficiary to yield a lower summed fitting cost.

Four focused tests passed in 0.18 seconds. They cover colour-blocker isolation,
identical-vector conflicts, clean preservation/no gain and deterministic feature
ties. Independent native output replay checked all 756 outputs, 560 regional
metrics, 756 scene metrics, protection/zero-alpha pixels, 20,150 source hashes, summaries
and harm/benefit transitions. All checks passed.

## Results

Values are development / later. All candidate values equal the earlier
facial-exception values exactly.

| Check | Aligned acceptance comparator | Fixed-structure parent | Local refinement |
| --- | ---: | ---: | ---: |
| Usable clean edits | 2/22; 2/18 | 0/22; 0/18 | **0/22; 0/18** |
| Core RGB MAE | 8.0287 / 9.7567 | 12.0396 / 12.5411 | **9.7302 / 10.3639** |
| Core CIEDE2000 | 3.4406 / 4.1886 | 4.6684 / 4.9352 | **3.9696 / 4.2866** |
| Core benefits | 106 / 84 | 91 / 78 | **91 / 78** |
| Core RGB/DE harms | 1 / 5 | 0 / 0 | **0 / 0** |
| Stress RGB MAE | 39.2219 / 43.9462 | 38.7874 / 43.5718 | **38.7874 / 43.8632** |
| Stress CIEDE2000 | 15.2563 / 16.6843 | 15.1600 / 16.7600 | **15.1600 / 16.8414** |
| Stress benefits | 45 / 43 | 40 / 36 | **40 / 35** |
| Stress RGB/DE harms | 0 / 1 | 0 / 0 | **0 / 1** |

Core reference scoring denominators are 176 / 144; stress denominators are
110 / 90. RGB and DE benefit counts agree. The 14 failed clean measurements
remain separate no-op failures. Core error and benefit requirements fail in both
cohorts; stress benefit requirements fail in both, and later stress DE exceeds
aligned. The known stress harm equals aligned's harm count, so it does not
independently fail the unchanged "no increase versus aligned" harm-count rule;
the other failed requirements are sufficient to reject adoption.

The global nonharm candidate remains distinct: core RGB 10.1310 / 10.9828,
benefits 88 / 75, stress benefits 40 / 35, and no scored regional harms. Its
metrics and the fixed-structure/previous-exception attribution are saved in the
new private attribution file. No recent candidate meets the joint requirements.

## Why the known harm returns

This explanatory trace is explicitly outcome-selected from the previously
documented harm; it was inspected only after fitting and was not used to choose
the new split.

The full-fit local split uses facial L <= 32.3856000900. The fitting blocker
`diversity_017__stress_color_none` has L about 33.3177, taking the other child.
The known harmful evaluation condition `eval_02__stress_color_none` has L about
31.7808 and receives the old strong brightening action (gamma 0.69988194,
red gain 0.99898186, blue gain 0.99993898).

Its RGB error returns to 31.5307 versus input 6.6667; DE returns to 11.7017
versus input 4.8420. The fixed-structure parent had RGB 5.3059 / DE 4.3768 on
this condition; the global nonharm candidate had left it unchanged.

The local split protects the actual fitting blocker while routing the exposed
evaluation colour condition with exposure beneficiaries. This is a direct
counterexample to treating a fitting nonharm pass as sufficient evaluation
protection. It does not prove that every available feature or future dataset
is incapable of distinguishing the conditions.

## Output review and preserved artifacts

Thirty-seven decisions across 16 originals change versus the fixed-structure
parent: 34 have reference regions and three do not. The other 719 outputs and
candidate metric records match it exactly. Thirty-three scored changes improve
RGB versus that parent; one worsens it, the known stress case.

Viewed all 37 changed boards on all ten contact sheets using view_image. The
stronger recovery also restores visible fragmented facial/neck boundaries.
All 756 outputs and candidate metric records match the previously reviewed
facial-exception outputs exactly; that prior review is reused with parity
evidence, while every change versus the immediate parent was additionally
viewed. No new dense mask-quality or naturalness claim follows.

Implementation: isolated `src/model_training/local_nonharm_refinement.py` and
scripts 674–679. Private artifacts: `outputs/local_nonharm_refinement_models_v1`
and `outputs/local_nonharm_refinement_comparison_v1`. Prior models, partials,
comparisons and unrelated uncommitted work remain preserved. No runtime change,
DINO execution, annotation, external contact/upload, commit or push occurred.

## Disposition and next direction

Freeze this failed candidate as evidence. Do not deepen these trees, tune the
new threshold to the known harmful input, exempt the fitting blocker or relax
the acceptance rules. This comparison provides no new evaluation behaviour
beyond the previous candidate despite its improved fitting constraints.

A defensible next direction is a predeclared **colour-only fitting-coverage
expansion**, using training-role sources across their existing brightness range,
with clean/colour constraints retained. First design that coverage from fitting
sources and recipes, rather than manufacturing an example to match the exposed
harm. New preparation/targets/fitting require their own fixed protocol; none
ran here. This is a proposal, not evidence that more conditions will solve the
problem. Final holdout access and adoption remain unauthorised.
