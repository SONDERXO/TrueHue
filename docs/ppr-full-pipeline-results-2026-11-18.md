# Complete frozen PPR correction assessment: failed and closed

The user explicitly resumed the deferred assessment: "Okay lets continue the PPR correction then." The previously approved single full-mapping assessment is now complete. It **failed every fixed correction-role gate, the underexposure improvement gate, and the colour non-regression gate**. Do not adopt it, request image ratings, tune its strength, try another expert/style/checkpoint/backend, or reopen a closed study.

This was the complete pretrained `mask_noglc_a` predictor/five-LUT mapping, distinct from the earlier PPR319 coefficient-as-tree-feature study. The unchanged 66 cached coefficient vectors were used directly. ITA/MST did not condition this predictor. No new training, predictor calls, asset downloads, package installation, mask changes, Android integration or manuscript editing occurred.

## Native mechanics and execution

The matching five finite float32 LUT states passed safe `weights_only` CPU loading. The pinned official CPU C++ extension built successfully in **56.16 seconds**, within the 300-second limit. Exactly one native build occurred, with unchanged official source hashes. The original runner failed before compilation because its Windows command escaped the quoted developer-environment batch path incorrectly. That prelaunch failure is preserved separately; repairing the local launcher did not change the native code or introduce a backend retry. Unnecessary downloader/metrics imports were removed from stages that did not need those dependencies. No packages were installed.

Generated checks passed before portrait processing: all 256 integer codes per channel, 95 floating endpoint/near-grid samples, three generated non-square images, two exact repeats per image, all five LUT states and inputs immutable, nine invalid-input/coefficient guards before native calls. Native and independently implemented scalar float32 interpolation had **zero observed difference**. RGB8 quantization and protected alpha compositing matched exactly. No tolerance, grid, coefficient normalization or application-strength changes were made after results.

Exactly **66 full PPR mappings** (five table interpolations each) and composites were saved and hashed before any reference-image scoring. The original application alpha, manual-ear coverage and protection were retained. Mapping used only input RGB, alpha, protection and the cached raw coefficients. Scoring reused the saved input, WB314 and fitting-only constant outputs; there were no baseline refits.

Native mapping used the existing `.venv-reiqa-pilot` torch environment; scoring used the existing `venv` metrics environment. Neither environment was changed. These stages and executable paths are recorded separately, rather than claiming one environment provided both.

## Fixed numerical result

Primary-support means, RGB MAE / CIEDE2000; lower is better:

| Role | Uncorrected input | Saved WB314 | Complete PPR |
| --- | --- | --- | --- |
| Original | 0.000 / 0.000 | 3.726 / 1.471 | 20.065 / 7.414 |
| Colour only | 6.564 / 4.885 | 2.476 / 0.901 | 20.867 / 7.975 |
| Underexposure | 20.410 / 6.835 | 11.251 / 4.552 | 19.790 / 7.417 |
| Overexposure | 23.046 / 7.268 | 1.597 / 0.811 | 22.563 / 8.229 |
| Combined underexposure | 21.497 / 9.300 | 7.570 / 3.743 | 20.094 / 7.888 |
| Combined overexposure | 21.953 / 7.601 | 1.249 / 0.535 | 21.812 / 7.863 |

None of the five nonidentity means beat both input and fitting-only constant on both metrics. Pure underexposure failed the required improvement over WB314, and colour failed non-regression. All eleven originals changed. Twenty-nine of 55 nonidentity cases were worse than input on at least one primary metric. These are numerical findings, not invented human appearance labels.

Positive findings are retained: the three earlier exposure no-ops now change and improve against their inputs on both metrics:

| Case | Input RGB / DE | PPR RGB / DE |
| --- | --- | --- |
| 16061 under | 21.615 / 7.239 | 15.111 / 5.936 |
| 48879 under | 25.379 / 7.609 | 8.160 / 4.193 |
| 48879 combined under | 26.347 / 10.607 | 7.885 / 3.822 |

Those individual improvements do not rescue the combined screen. Before native RGB8 clipping, 12,928 channel values were below zero and 39,735 above one across the 66 images; clipping counts/ranges are saved per case. Five-LUT mixing coefficients have no gamma/R/B parameter-MAE targets, so that metric is explicitly inapplicable.

## Evidence and stopping point

All 66 composites were independently replayed with scalar arithmetic. All four evaluation regions were scored and parent metrics checked; scalar aggregation checked every RGB/DE result. The final read-only independent audit passed **72 artifact hashes, 81 bindings, 330 coefficient values, 66 joins and 48 role means**, with fixed gate outcomes independently recomputed. The audit made no new native calls, pixel reads, encoder calls or fits.

- Native assets/build log/receipt: `outputs/ppr_full_pipeline_assets_v1`.
- Generated verification: `outputs/ppr_full_pipeline_engineering_v1/verification.json`.
- Sealed predictions, per-case results, summary and audit: `outputs/ppr_full_pipeline_prediction_v1`.
- Implementation: `scripts/ppr_full_pipeline_assessment.py`, `scripts/run_ppr_full_mapping.py`, `scripts/score_ppr_full_mapping.py`.

**Approval fulfilled; candidate failed/closed; no jobs running.** Do not rerun build, generated QA, mapping or scoring. No current review or further fit is selected. All historical PIQ, synthetic316, PPR319 and other closures and exact user feedback remain unchanged. No demonstrated combined correction model or supported direct code repair has emerged; the correction model remains unfinished. This result does not prove all portrait correction or PPR variants are universally incapable. It authorizes no further variant assessment.

Full exposure-plus-colour/preservation/darker-skin objective, supported tone evidence, genuine expert appraisal/refinement before paper submission, adviser formatting/conferences-only role, manuscript pause, raw-original/locked-content-and-manifest restrictions, approved manual ears, rating provenance, no-contact and runtime/Android boundaries remain intact. No substitute scope or completion guarantee is adopted.
