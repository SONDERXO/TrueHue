# Facial evidence inside the vetoed correction branches

8 November 2026. Saved-training-record audit only; no new fit or evaluation prediction.

Some useful distorted photos differ from the clean examples in existing facial measurements. That supports testing a limited facial exception to the veto, while keeping the clean protection elsewhere.

## What we compared

For each frozen vetoed branch, we examined fitting conditions for which its original correction reduced saved RGB training error. We compared their facial Lab/ITA values against the minimum and maximum across **all fitting clean references plus the 20 reserved usable clean references** in that configuration. We used the full clean pool, rather than just the one reserved clean example that triggered that branch's veto, to avoid making separation look trivial.

No background features, new thresholds, split search, evaluation outcomes or image-source reads were used to calculate the ranges. Estimated MST was reported separately to check whether it added coverage.

| Saved training evidence | Full model | Ten folds combined |
| --- | ---: | ---: |
| Useful conditions in vetoed branches | 19 | 357 |
| Outside at least one raw facial clean range | 13 | 205 |
| Inside all raw facial clean ranges | 6 | 152 |
| Additional conditions outside when adding MST | 0 | 0 |

Fold totals repeatedly reuse originals and are not independent photos or people. The full model's 19 conditions comprise 13 cool-plus-overexposure, three exposure-only and three warm-plus-overexposure conditions. Across the 13 outside-range conditions, eight exceed a facial a* range, seven exceed facial L* and two exceed ITA. These counts overlap and must not be added. No condition exceeds the b* range.

“Useful” is defined using the saved training reference and existing leaf action. It is not a deployable usefulness estimate, visual-quality judgment or new accuracy result. Being inside all individual ranges does not prove multivariate inseparability; being outside does not prove a safe correction.

## One proposed change

Keep the clean veto, **except when a technically usable input reaching a vetoed leaf falls outside the clean range of at least one of the four facial Lab/ITA measurements**. In that case, use the frozen original leaf correction. Keep every other decision unchanged. Do not add estimated MST or tune a margin.

The [fixed comparison protocol](facial-exception-to-veto-protocol-2026-11-08.md) specifies this rule and the unchanged acceptance requirements. It reuses the existing 11 trees and needs no new fitting. No candidate evaluation has started; the private audit freezes the proposed bounds before any such evaluation.

This is a limited hypothesis. It may restore some useful corrections, but unseen clean photos can also lie outside these ranges. The tree still uses background-sensitive scene features, and masks remain unverified. The final eight-group, 24-photo holdout remains byte-unread. No model is adopted or integrated.

## Verification

Scripts 634–635 independently verify 11 vetoed branches, all 376 useful training-row occurrences, pooled float32 ranges, triggering reserved-clean routes and source hashes. All checks passed. No new fits, evaluation predictions, inference, rendering or annotation. Private artifacts: `outputs/vetoed_branch_facial_audit_v1`.
