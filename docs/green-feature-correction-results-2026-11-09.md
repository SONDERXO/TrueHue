# Fixed green-feature correction comparison — 9 November 2026

The single approved comparison is complete. **Adding the four facial green
features does not change any of the 756 evaluation controls, output images or
candidate metric records versus the global colour-nonharm parent.** The trees
use the new features and improve their fitting objective, but that improvement
does not transfer to this fixed evaluation. The candidate fails the unchanged
joint requirements, is not adopted and does not qualify for final-holdout access.

## What was fixed and what changed

The user explicitly approved the comparison after fitting-only preparation
passed. The pre-existing [design](green-channel-correction-design-2026-11-09.md)
specifies the entire feature family and comparison; no new choices were made
from evaluation outcomes.

Exactly four features were appended to the original twelve: facial green p10,
median, p90 and log contrast, on the same actual-input normalized measurement
image/mask. Evaluation extraction processed all 451 available inputs and retained
305 unavailable attempts, without imputation or borrowed masks. All 756 attempts
remain in the ledger. No new detector, parser, landmark or FaceOcc forward ran.

Exactly eleven depth-four colour-nonharm action trees were fitted, retaining
the exact case IDs, nested MST, fourteen actions, saved RGB cost matrices,
equal-row objective, clean/colour constraints, group roles and greedy settings.
The same twenty reserved-clean vectors recomputed veto membership, and the
same frozen facial exception bounds/rule were reapplied. No calibration,
MST/target fitting, mask change, recipe expansion, weight/depth variation or
feature-subset selection occurred.

Across all trees, green median is used in ten splits and green p90 in one;
green p10 and log contrast are not used. The full-fit summed pre-veto leaf
cost decreases from 10,951.4124 to 10,938.6914; all eleven fitting objectives
decrease. These are summed training costs, not evaluation error or independent
evidence. A changed tree and a better fitting objective do not by themselves
constitute a better correction model.

## Fixed results

Values are development / later; the candidate column equals the global nonharm
parent exactly, including its equal-publisher-group summaries.

| Check | Original aligned acceptance comparator | Green-feature candidate |
| --- | ---: | ---: |
| Usable clean edits | 2/22; 2/18 | **0/22; 0/18** |
| Core RGB MAE | 8.0287 / 9.7567 | **10.1310 / 10.9828** |
| Core CIEDE2000 | 3.4406 / 4.1886 | **4.0987 / 4.4757** |
| Core benefits | 106 / 84 | **88 / 75** |
| Core RGB/DE harms | 1 / 5 | **0 / 0** |
| Stress RGB MAE | 39.2219 / 43.9462 | **38.7874 / 43.5869** |
| Stress CIEDE2000 | 15.2563 / 16.6843 | **15.1600 / 16.7651** |
| Stress benefits | 45 / 43 | **40 / 35** |
| Stress RGB/DE harms | 0 / 1 | **0 / 0** |

Core reference scoring denominators are 176 / 144 and stress denominators
110 / 90. Benefit counts agree for RGB and CIEDE2000. The fourteen clean
measurement failures remain separate no-op failures, not learned preservation.
There are zero scored regional RGB/DE harms and zero whole-scene RGB harms
across all six cohort/layer combinations. These exposed results are not a
real-world safety guarantee or proof of intrinsic skin colour recovery.

Both cohorts fail core mean RGB/DE and benefit requirements. Stress benefit
requirements fail in both cohorts, and later stress DE exceeds aligned. The
known harmful stress case remains identity (RGB 6.6667), as in global nonharm;
the six benefits that parent lost versus the earlier facial exception remain
lost. The documented overexposure misses are also not repaired because no
evaluation decision changes.

Per-cohort clean/exposure-only/colour-only/combined breakdowns within each layer
and equal-publisher-group means are saved in `family_summary_PRIVATE.json`.
Attribution against the previous exception, global nonharm and fixed-structure
models is saved separately. Repeated conditions, folds and publisher groups
must not be described as independent people or verified identities.

## Verification and review

- Six focused feature/constraint tests passed in 0.39 seconds.
- Independent model replay passed eleven fits, 307 nodes, 327,192 split options,
  880 repeated clean constraints, 2,383 repeated colour constraints, 220 reserved
  clean identity checks and all 756 predictions after final postprocessing.
- The independent verifier checked all 1,804 evaluation feature values using
  explicit sorted-percentile/log formulas. Original twelve fitting columns,
  nested MST, appended fitting/reserved values, costs, actions, roles,
  calibrations, veto and frozen exception were checked against saved artifacts.
- Independent native replay passed all 756 output images, 560 regional and
  756 scene metric records, protected/zero-alpha pixel invariants, summaries,
  harm/benefit transitions and 21,525 bound source hashes.
- All 756 pixels/metric dictionaries exactly match the global nonharm outputs;
  743 also match the earlier facial-exception candidate exactly. There are
  **zero changed outputs to review**. Prior global-nonharm review lineage is
  reused under exact equality; zero new visual boards were viewed. No fresh
  756-board visual review or new mask-quality claim is made.

The machine-readable review receipt binds the output/metric parity and family
summary. Existing fragmented facial/neck coverage and visible boundaries remain
because the outputs are identical. Code/model correctness checks have passed;
the model-quality acceptance checks have failed. These are different outcomes.

## Artifacts and decision

Scripts 685–691 implement evaluation extraction, fitting, independent model
verification, fixed evaluation, independent output assessment, output parity
and review/family accounting. Private artifacts are:

- `outputs/evaluation_green_features_v1`
- `outputs/green_nonharm_models_v1`
- `outputs/green_nonharm_comparison_v1`

All previous artifacts, fitting preparation and unrelated uncommitted work are
preserved. No runtime adoption/integration, DINO execution, annotation, external
contact/upload, scientific admission, commit or push occurred. All 24 final
holdout photos remain byte-unread.

**Stop this model cycle as predeclared.** Do not switch channels/quantiles,
deepen the tree, change weights, expand recipes or add a guard as an automatic
rescue. This was the completion plan's bounded substantive correction comparison
and it produced no evaluation improvement. Return to the overall completion
decision with the failed result visible; do not call the working model finished
or silently substitute the conservative experimental parent. Mask qualification
and runtime compatibility remain unresolved as well. No next experiment was
started or selected by this report.
