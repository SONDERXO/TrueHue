# Directional recoverability workflow: generated engineering passed

14 November2026. Completed the generated-only implementation and verification
required by `ffhq-directional-recoverability-protocol-2026-11-14.md`.
No real FFHQ reference, mask or NPZ array was decoded. No real-photo target
optimization, correction-tree fit, model prediction or user review occurred.

## Implemented workflow

- `src/evaluation/directional_recoverability.py`: six frozen roles, fixed
  counterfactual medium-setting operator, existing unchanged direct-gamma local
  fitter, clipping and region accounting, actual RGB8 rendering, unavailable
  targets without fallback, protected/outside preservation, per-role summaries
  and versioned-output failure preservation.
- `src/evaluation/directional_recoverability_loading.py`: all11source/support
  joins and whole-container/selected-receipt/file hash barrier before any array
  decoding; only the bound identity `input_rgb8` NPZ key is accessed. Supplied
  alpha/protection are checked, never reconstructed or silently repaired.
- `src/evaluation/directional_recoverability_scalar.py`: separate scalar forward
  formulas, clipping counts, direct-power correction, float fitting-objective
  residual and independent aggregation of standard-library metric replays.
- `scripts/check_directional_recoverability_generated.py`: generated-only
  entry point, persisted11-source/66-role rehearsal, code/design/environment
  binding and independent round-trip verification. This entry point cannot
  select the real source plan through a command-line switch.

Source provenance flags remain explicit. Schema/provenance tests simulate
declarations only; none is counted as an actual photograph or real admission.
Existing operator, target fitter, approved masks and runtime code are unchanged.

## Executed evidence

The focused command passed53tests in3.45seconds:

```
python -m pytest tests/test_directional_recoverability.py tests/test_directional_exposure_recipe.py tests/test_blended_recovery_targets.py -q -p no:cacheprovider --tb=short
```

Coverage includes identity with0optimization, exactly one identity-start solver
call with frozen bounds/tolerances, direct-versus-reciprocal gamma, rounding,
clipping, empty core regions, unavailable/degenerate targets, rejected invalid
controls, source immutability and protected/outside preservation. No-overwrite,
partial-failure preservation, duplicate rosters, invalid support and receipt/
container/file mismatches are checked. Corrupting the last source still fails
before any array decode. Poisoned object-valued NPZ members remain unread;
they would fail if mistakenly accessed with allow_pickle=False.

The full generated rehearsal completed11artificial12×12sources,66cases and
55actual local least-squares calls; identity uses exact neutral controls.
These55calls are the main rehearsal count, not a total including additional
small unit-test fits. All66persisted cases passed separate scalar distortion,
clipping, rendering, objective and metric checks. All six roles have11records;
source-equal summaries independently replay. Metrics include primary, core,
feather and whole-image regions, with explicit nulls for unavailable regions.

The scalar path imports no optimizer or production workflow. CIEDE2000 uses the
same established scikit-image implementation with separate full-image conversion
and aggregation; this is not an independently derived CIEDE2000 implementation.
Its metric replay tolerance is1e-10; fitting-objective tolerance is1e-12;
generated RGB8 arrays and clipping counts match exactly.

All191persisted rehearsal artifacts and all bound implementation/design hashes
were checked again after completion. Code/dependency versions are recorded:
Python3.14.7, NumPy2.5.3, SciPy1.18.1, scikit-image0.26.0;
opencv-python distribution4.10.0.84, cv2 runtime4.10.0. These are this execution's
versions, not a claim that historical experiments used identical dependencies.
No environment changes or package installations were made.

An earlier focused45-test pass preceded the loader tests; it emitted only a
pytest-cache write warning. The final53-test command disabled the cache provider
and passed without that warning. No full-suite or device-validation claim.

## Result and next execution boundary

Engineering status: PASS. Real-photo recoverability status: UNTESTED. Generated
random RGB fixtures are not skin models, official tone labels, photographic
quality evidence or darker-skin bias results. No scientific/adoption gate has
been relaxed or replaced by software checks.

The next concrete step is the single already specified real diagnostic:
exact11bound FFHQ identity references and approved support selections,
66condition records and at most55local reference-aware target optimizations.
Before that run, bind its actual entry point to the frozen roster and this QA
package, verify all whole-container/selected-support hashes before decoding,
preserve only allowed source access and perform the independent replay. The
current loader/engine are tested; no actual-record CLI execution has occurred.
No new source-selection or formula-design stage is needed.

No tree training, rerating, gain/strength sweep, extra source acquisition,
changed mask or automated continuation follows either outcome. High residual
from one bounded local fit is not a global impossibility proof; low residual
does not establish that a tree predicts the controls or that users prefer them.

Evidence: `outputs/directional_recoverability_engineering_v1/`, including
execution plan, generated source plan, generated_run, verification and focused
test receipt. Previous outputs refuse overwrite and remain preserved. No
final24/older locked contents or manifests, raw original photos, runtime/Android
or manuscript access. Approved59807manual/ear coverage and darker-skin priority
retained. Model unfinished; paper paused; November25 deadline retained.
