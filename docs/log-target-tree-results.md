# Multiplier-target comparison and target audit

30 October 2026. Training on logarithms of gamma/red/blue multipliers does not
resolve clean-photo overcorrection. The same two held clean sources change.
Keep the working demo and previous research baseline. This result does not
justify another target-coordinate search on these exposed sources.

The [frozen protocol](log-target-tree-protocol.md) compares ordinary direct
multipliers with their natural logarithms. Both use identical augmented fitting
rows, 26 held source/known duplicate groups, five Lab/ITA/experimental-MST input
features, depth 3, seed 42 and fitting-control protection. Log leaf values are
exponentiated before protection and export. The final operator still uses direct
gamma and red/blue gains; no log-valued parameter reaches inference.

Lower CIEDE2000 is better.

| Measure | Ordinary targets | Log targets | No correction |
|---|---:|---:|---:|
| Historical 30-pair error | 8.091 | 8.096 | 10.076 |
| Historical distorted 15 error | 16.181 | 16.192 | 20.153 |
| Historical clean changed /15 | 0 | 0 | 0 |
| Additional clean changed /11 | 2 | 2 | 0 |
| Combined 41-pair error | 7.314 | 7.302 | 7.373 |

The tiny combined reduction is not a useful safety improvement. Sources 29880
and 68073 still change; distorted performance is slightly worse. Both fail the
unchanged-clean requirement. These are reused development sources, not final
validation. The earlier historical-only protected model remains separate.

`scripts/258_compare_log_correction_targets.py --verify` passes 52 independent
refits, fitting-only log target construction, inversion/protection and exact
membership checks, source separation, 82 pixel/metric replays and ordinary-target
parent parity. Evidence and SHA256 records are in
`outputs/log_correction_targets_v1/verification.json`.

The focused pytest check of recovery targets, direct-gamma curves, protected
leaves and portable inference passes **56 tests**. Pytest reports one cache-write
permission warning; no test failed. The last full-suite result remains 780;
this run is the focused 56-test check, not a new full-suite result.

The first attempt correctly failed the runtime exporter's positive-parameter
check when raw log leaf values were supplied. It is preserved in
`outputs/log_correction_targets_failed_export_v1`. The corrected producer
converts model values back to positive multipliers before export. No exporter
validation was weakened, and the failed attempt is not a completed experiment.

## What the saved-target audit establishes

`scripts/259_audit_saved_recovery_targets.py` uses the same fifteen approved
distorted pairs. It checks the exact saved target-report hashes, independently
reconstructs legacy/direct curve equivalence, reproduces RGB fitting residuals
and quantization, and evaluates the saved target on each original application
mask. No target is re-fitted or replaced.

All fifteen saved targets improve their source-mask CIEDE2000 against unchanged
inputs. Mean error falls from **20.153 to 8.902** when these reference-informed
settings are applied directly. This is an oracle diagnostic, not learned model
accuracy: inference cannot access the reference or these per-image settings.
The target optimizer fits RGB error on mask intersection, not global CIEDE2000;
the result does not prove each parameter triple is optimal for that metric.

An additional diagnostic copies reference pixels only inside each application
mask. Facial scoring pixels outside it remain untouched. Its mean error is
**4.445**. For the fixed mask and per-pixel metric, that is the error contribution
no correction restricted to that mask can remove, even if correction inside
were perfect. This is a support-only lower bound, not the achievable result of
the three-parameter operator. It must not become a reference-informed runtime
fallback or an intersection-only replacement for full facial scoring.

Thus saved targets contain correction benefit, while learned prediction and
application support both leave substantial error. More tree depth and this
target-coordinate change have not solved the overlap between clean facial
statistics and distorted fitting examples. Future work should separately track
learned parameter errors and missing mask support; do not replace human mask
decisions, invent source exceptions or call the current model finished.

Audit output: `outputs/saved_recovery_target_audit_v1/summary.json` and
`verification.json`. No new sources, masks, reserved data, photographer forms,
MST calibration, targets or runtime behavior were introduced. Existing clipping,
approximate-target and tone-coverage limitations remain.
