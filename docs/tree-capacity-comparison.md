# Fixed tree-capacity comparison

24 October 2026. The unrestricted tree fit its training targets almost exactly, but performed worse on held-out sources. Keep the runtime model unchanged.

Same31 selected development pairs, eight source/known-duplicate-group folds, four Lab/ITA inputs, three inverse-parameter targets and fixed correction/scoring masks. Only maximum depth changed:3 versus unrestricted. Both used seed42 and minimum leaf size1. No depth search, external validation or reserved-test evaluation.

| Held-source probes | No correction | Depth3 | Unrestricted |
|---|---:|---:|---:|
| All31 | 5.46 | 7.80 | 8.59 |
| Shared22 | 5.16 | 8.16 | 8.03 |
| New9 | 6.20 | 6.92 | 9.95 |
| bright_warm | 8.36 | 9.91 | 10.63 |
| color_shift | 7.43 | 9.49 | 11.64 |
| dark | 12.68 | 7.91 | 5.78 |
| identity_control | 0.00 | 6.30 | 7.60 |
| mild_bright_exposure | 2.83 | 7.13 | 8.75 |

Values are mean CIEDE2000 reconstruction error relative to source photographs; lower is better. Equal-source means likewise worsened from7.77 to8.40 (no correction5.13). The shared22 probes improved slightly while the new9 worsened substantially; the result is not uniformly worse across every group.

Unrestricted trees reached depths7?12. Training parameter MAE was effectively zero (largest reported component about1.24e-17), while held-source parameter MAE increased for all three outputs. This is evidence of overfitting on this selected cohort; it does not prove that every deeper model or these features must fail.

Average unchanged-image error rose6.30?7.60, although the number harmed dropped8/8?7/8. Mild-image error rose7.13?8.75, with6/8 harmed versus5/8 at depth3. Darkened-image error improved7.91?5.78. Codex inspected all16 control comparisons: unwanted brightening/color shifts and sharp mask boundaries remain, with a severe new brightening failure on22454. These are development observations, not expert MOS or calibrated skin-color truth.

## Verification

Sixteen fold models saved,93 held-source prediction records. All depth3 parameters and image metrics reproduce the previous expanded31 experiment exactly. Saved-model training and held-source predictions independently replayed, training MAE recomputed, source/pair/duplicate groups checked disjoint, outside-support pixels preserved, original input/model hashes unchanged. Existing suite: **464 passed**. The first run finished computation but failed JSON serialization of a NumPy leaf-count integer; its incomplete artifacts were retained separately. The integer serialization was corrected and the fixed experiment rerun successfully.

## Recommended next step

Stop increasing depth on these four averages. Prepare a small, fixed input-only feature extension describing brightness distribution and spatial variation, such as skin-mask luminance percentiles/spread and regional brightness differences. Check availability and stability on the existing31 inputs first; do not use clean-reference values, source IDs, distortion labels or targets as input features. Freeze one feature schema before a source-grouped comparison with the original four features. Such measurements may help but cannot be assumed to distinguish complexion from illumination.

This feature audit is the next proposed experiment, not an implemented runtime change. Preserve failure cases and current dataset exclusions. Face-and-neck support, operational MST, broader data eligibility and final thesis evaluation remain pending. Record any feature changes as proposal-method distinctions before final thesis edits.

[Metrics, training fit and fold provenance](../outputs/tree_capacity_sourcecv_v1/summary.json) ? [Independent replay checks](../outputs/tree_capacity_sourcecv_v1/independent_verification.json) ? [All31 image comparisons](../outputs/tree_capacity_sourcecv_v1/review-index.md)

Follow-up: [completed input-only brightness feature audit](brightness-feature-audit.md). No model fitting yet.
