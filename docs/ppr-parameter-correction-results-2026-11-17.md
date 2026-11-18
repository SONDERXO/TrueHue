# Fixed portrait-parameter feature comparison

17 November 2026. Numerical criteria passed; **closed/not adopted after the user's brightness concern** on the newly changed original. Exact reply: "Um i think it's a little too bright?" This is natural-language feedback, not a fabricated categorical selection or expert rating. Review stops; no tuning or further review queue. The numerical result and prior artifacts remain unchanged. No qualified next fit has been selected; the full model remains unfinished.

The user asked to continue while minimizing detours and prioritizing correction improvements. One official frozen portrait-parameter component was made usable, then tested once under the [prospective319 protocol](ppr-parameter-correction-protocol-2026-11-17.md). This extends proposal63/65 with five externally learned features; the retained ITA/MST/statistics-to-control method and renderer remain. Closed local PPR10K pair studies, synthetic316, ridge, joint4410 and fivefold studies were not reopened.

## Actual result

Primary-region equal-source means, eleven held sources per role. Each cell is RGB MAE / CIEDE2000; lower is better.

| Role | Saved WB314 | PPR319 |
|---|---:|---:|
| Already unmodified original | 3.726 / 1.471 | 5.881 / 2.110 |
| Colour only | 2.476 / 0.901 | 2.476 / 0.901 |
| Underexposure | 11.251 / 4.552 | 9.396 / 3.944 |
| Overexposure | 1.597 / 0.811 | 1.597 / 0.811 |
| Combined underexposure/colour | 7.570 / 3.743 | 8.304 / 4.186 |
| Combined overexposure/colour | 1.249 / 0.535 | 1.249 / 0.535 |

Underexposure RGB error decreased16.49%, DE13.37%. All five nonidentity role means beat both uncorrected input and fit-only constant in RGB and DE. Underexposure improved WB314 in both, and colour-only was unchanged. These satisfy the fixed numerical gate. They do **not** establish useful appearance, preservation, per-tone fairness or completion. Combined-underexposure and unmodified-original averages worsened; these regressions were explicitly reportable under the frozen protocol, not hidden or retrospectively waived.

Three original cases change:16061,39568,59807. The latter two have exactly the previous WB314 controls; their earlier ratings remain historical and have not been assigned to the new candidate. The new change is16061: neutral controls become `[1,1.4142135623730954,1,1,1]`, changing26465pixels, primary RGB0=>23.707 and DE0=>7.029. Eight originals are exactly unchanged from their inputs. Only a human can judge whether this newly brighter result is acceptable; no unwanted-change label has been invented.

Other parent regressions:49131combined-under RGB4.597=>18.352/DE3.000=>8.264;59807combined-under RGB6.247=>18.079/DE4.452=>8.120. The existing16061colour-only numerical harm versus input persists; all eleven colour-only control vectors are exactly WB314's, with the same role means. Numerical harm is not a fabricated human rating.

Of the prior three neutral exposure misses,16061under now predicts gain1.4142 (RGB21.615=>1.211), and48879combined-under now predicts gain1.4142 (RGB26.347=>8.836, with residual colour error). **48879under remains exactly unchanged** at RGB25.379/DE7.609. These changes do not justify claiming the previous eight-case usefulness failure is solved.

## What was actually run

Exactly66input-only forward calls plus one generated contract call produced330raw coefficients from the one frozen `mask_noglc_a` component. Exact314features plus five raw float32 coefficients supplied319features, with no selection/scaling or extra target training. Exactly11ordinary depth4/seed42 source-held correction trees,660fit routes and66held predictions; all fits independently verified before all controls were sealed, before reference/support pixels were decoded. The frozen features enter two splits across two models (held16061,39568). No additional head, baseline, constant or all-data fit.

All66new output arrays exactly match independent scalar RGB8 replay, with protected/outside pixels unchanged. Primary/core/feather/whole-region metrics and parent joins pass. Final independent audit checked87run-artifact hashes,155source bindings,20724prefix values,330raw coefficients,660fit/66held routes and48mean values/gates. Generated319adapter checks passed before actual fitting; failures and guards remain saved. These are implementation checks, separate from the quality outcome above.

The comparison measures the complete319-feature fitting procedure. Only two models split on the added coefficients; changed predictions in the other models cannot be attributed to their coefficient values. A separate causal attribution experiment was not run, and no additional control fit is queued.

Source access was resolved by **new** official information: the current README Overview and [author issue23comment](https://github.com/csjliang/PPR10K/issues/23#issuecomment-2564283695) point to a replacement Drive folder while other model links remain stale. Official commit `239490b8a8e917f2c29e3016ee2f6543c3c1bfba`. ZIP ranges transferred41,698,173bytes for only `pretrained_models/mask_noglc_a/classifier_-1.pth`, not the full261,433,127byte archive, LUTs or photos. Computed checkpointSHA256 `b8a62f350e265496728ba0653da0ef9e652a30c8f14316b2e1d9a8311930488a` is not an author-published checksum. Safe weights-only strict loading,122tensors/11,179,077parameters, RGB unit scaling/bilinear224/eval/frozen, generated repeat/immutability and unchanged state passed in the existing environment. No packages/extension builds. Wrapper adaptation is not author-runtime bit parity. Code Apache2.0 and author noncommercial research notices retained; no public redistribution/commercial-app rights inferred. See [bounded acquisition contract](ppr-parameter-acquisition-contract-2026-11-17.md).

## Stopping point

**Superseding user response:** "Um i think it's a little too bright?" saved in `outputs/ppr_parameter_preservation_feedback_v1/user_reply.txt`, with interpretation and hash bindings separately. This is a tentative brightness concern and does not endorse acceptable preservation. Under the predeclared preservation stop rule, close this candidate's review and withhold adoption. No repeat question, additional ratings or savefile required. Both the unmodified16061original and its underexposed counterpart route to leaf5 of the16061held-source model, predicting the same gain1.4142. This saved-route fact locates a correction-decision error; the renderer is faithfully applying those controls. Do not lower global strength, add thresholds, change depth/features/loss, select another checkpoint, or reopen the candidate as an automatic rescue. Historical numerical pass remains unchanged. The following preparation description is historical, not a pending review request.

One newly changed original is ready for a short preservation check: [two-panel image](../outputs/ppr_parameter_preservation_check_v1/comparison.png), [local page](../outputs/ppr_parameter_preservation_check_v1/index.html). Native PNG roundtrips and source hashes pass; no browser/server needed or interactive-browser QA claimed. The assistant inspected the saved comparison. The user has been asked whether the brighter candidate is acceptable, unwanted or uncertain. **Zero new ratings collected at preparation; answer pending.** No savefile or repeat of the old eleven-case review is requested. Stop this candidate's review if unwanted/uncertain; do not tune it or transfer old ratings. An acceptable answer would still leave the remaining current-candidate preservation and exposure-usefulness checks before adoption.

Artifacts: `outputs/ppr_parameter_access_v1`, `ppr_parameter_features_v1`, `ppr_parameter_correction_engineering_v1`, `ppr_parameter_correction_design_v1`, `ppr_parameter_correction_prediction_v1` and `ppr_parameter_preservation_check_v1`. Scripts: `check_ppr_parameter_archive.py`, `check_ppr_parameter_ready.py`, `extract_ppr_parameter_features.py`, `ppr_parameter_correction_workflow.py`, `verify_ppr_parameter_correction_result.py`, `prepare_ppr_preservation_check.py`.

This is repeatedly exposed eleven-source development, not person-disjoint/MST-stratified70/15/15 qualification. External pretraining overlap is unknown. No darker-skin benefit, formal expert MOS or Android qualification follows. PIQ23 remains a separate access/use-pending stage with zero real external heads. No model variants, scale/depth/loss/source queue, new portraits/contact, raw originals, locked contents/manifests, runtime/Android or manuscript changes. Previous artifacts/ratings/manual ears remain. Full objective and actual expert feedback before Friday paper submission remain; no completion promise. Adviser remains formatting/conferences only.
