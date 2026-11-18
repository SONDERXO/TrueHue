# Proposed fixed comparison: facial exception to the clean veto

8 November 2026. Design only. This specific comparison must be agreed before evaluation; no new fit is needed.

## Single change

Retain the frozen reserved-clean-veto models, group roles and all existing settings. For each fitting configuration, calculate float32 minimum and maximum values for **four facial measurements** across its fitting clean references plus its 20 reserved usable clean references: mean Lab L*, a*, b*, and ITA. The exact bounds are frozen in the private facial audit. Do not add MST, scene features, margins or optimised thresholds.

Use this rule only when a technically usable input reaches a leaf that was explicitly vetoed:

1. If at least one of those four measurements is strictly below its clean minimum or strictly above its clean maximum, restore that leaf's frozen pre-veto correction.
2. Otherwise retain identity.

Equality stays inside the clean range. Non-vetoed leaves retain their post-veto actions. Measurement failure retains the existing no-op policy. Use the established float32 feature contract. Invalid or missing bounds/features must not enable correction.

This exception uses facial evidence, but the underlying tree still uses scene features to route inputs. It is not a background-independent model. Falling outside a clean range is not proof that a photo needs correction.

## Frozen inputs and verification

Use the existing 11 fitted configurations; **zero new tree, gate, MST or target fits**. Keep all actions, masks, alpha, protection, feature extraction, calibrated MST, outer-group exclusions and reserved-group roles unchanged. No source-image acquisition, parser/occlusion inference or annotation is needed.

Verify bounds using only the saved clean fitting/reserved rows, exact pre-veto action restoration, unchanged non-vetoed decisions, and preservation of every fitting/reserved clean reference. These reference checks are training/model-selection checks, not independent validation. Freeze the policy and bound hashes before calculating new evaluation outcomes.

## Evaluation and decision

Replay the same 756 prepared evaluation attempts. Compare with the reserved veto (to isolate the exception), reserved pre-veto trees (recovery ceiling for this rule), and original aligned comparator (acceptance). Render native outputs and independently verify all metrics and protected pixels.

Retain the original joint requirements separately for development and later photos: zero changed usable clean photos; no increase in core/stress RGB or CIEDE2000 mean error or harm counts; no decrease in beneficial counts versus the aligned comparator. Do not adopt on clean preservation alone or merely because this improves the rejected veto candidate.

The separate eight-group, 24-photo holdout stays byte-unread. If any requirement fails, stop without a margin/feature/range-rule sweep, resampling reserve groups or relaxing criteria. Do not integrate the candidate automatically.

## Why this comparison is justified, and its limits

The fixed training audit finds 13 of 19 useful distorted conditions in the full vetoed branch outside at least one pooled clean facial range; six remain inside all four. Across folds the counts are 205 of 357 repeated useful conditions outside and 152 inside. MST adds no coverage in this audit. This suggests a limited facial exception can retain some actions while preserving the clean examples defining those bounds by construction.

The rule may miss useful corrections and may edit a different clean photo whose facial measurements fall outside the development ranges. Bounds can reflect mask contamination, population variation or acquisition effects. The study remains development-exposed and synthetic; no fairness, naturalness or real-world safety conclusion follows.
