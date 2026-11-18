# Five-control fitter: generated engineering complete

14 November2026. User authorized pursuing the explicitly proposed five-control
research extension. Implemented and executed the fixed generated-only contract
in `affine-prepower-target-fitter-protocol-2026-11-14.md`. This is not adoption
into the three-output paper/runtime model and not a real-photo comparison.

## What is implemented

`src/model_training/affine_prepower_targets.py` provides isolated normalized-float
and RGB8 target fitting/rendering for [gamma,red_gain,blue_gain,input_scale,
input_offset]. The transform is exactly the proposed pre-power affine family;
alpha/protection and actual RGB8 rounding are explicit. The existing three-control
fitter, renderer and approved support files remain unchanged.

The single-start TRF solver uses the frozen bounds, tolerances and500evaluation
limit. No parameter search, repeated start or bounds expansion occurred.
Identity bypasses optimization. Degenerate input, failed convergence, rank
deficiency, invalid solutions and float loss worse than neutral stay unavailable.
Rank/singular values, condition number, active bounds, float residual, pre-power
flooring and output overflow are recorded. Rank5 is not a safety or stability
certificate. A finite positive control can still undesirably lift accepted skin.

`src/evaluation/affine_prepower_scalar.py` separately reconstructs scalar
rendering/objective and preservation. It imports no optimizer or production
fitter. `scripts/check_affine_prepower_targets_generated.py` freezes its14case
plan before solving, persists each case and results, refuses overwrite and
preserves failures. Generated provenance stays explicit; no actual-photo rows
are supplied or counted.

## Verification

39focused tests passed in2.27seconds:

```
python -m pytest tests/test_affine_prepower_targets.py tests/test_blended_recovery_targets.py -q -p no:cacheprovider --tb=short
```

Tests include known controls, old-three-control nesting, protected/zero-alpha
preservation, identity with0solver calls, exact frozen solver settings, constant/
near-flat input, convergence/rank/nonfinite-Jacobian/bounds/loss failures,
invalid data/controls, numeric overflow, and failure/no-overwrite behavior.
They also check that an intermediate value above1is not prematurely clipped
before a later gain brings it back into range. No full-suite claim.

The main generated rehearsal completed14records with exactly11local solver
calls, separate from additional small unit-test fits. Five noiseless known-
control records (four full-support and one spatial-support) recovered controls
within5.619e-12maximum absolute discrepancy, well inside the frozen1e-3
engineering tolerance. Maximum fitted float-RMSE among those five was
1.166e-13, inside1e-6. Separate scalar rendering matched the vector path exactly
on saved cases; objective checks use1e-12tolerance and RGB8 outputs match exactly.

Flat and near-flat records remain unavailable without an optimizer, not neutral
or fabricated successful fits. The generated identity remains exact neutral.
The quantized known-control case had actual RGB8 MAE.006944codes; its fitted
float residual remains nonzero because the objective is continuous while the
reference is RGB8. This is one engineering probe, not photographic quality.

## Descriptive stress results and limits

Six directional roles used one generated random RGB palette and the single
existing medium setting. These are not subjects, skin images or tone categories.
There is no same-palette three-control fitted comparator in this rehearsal;
do not compare these numbers to earlier FFHQ means as an improvement claim.

| Generated role | Actual RGB8 MAE after reference-aware fit | Numerical Jacobian condition number |
| --- | ---: | ---: |
| Identity | 0 | Not fitted |
| Colour-only | 2.903 | 14.73 |
| Exposure-under | 11.088 | 31.04 |
| Exposure-over | 9.806 | 575.10 |
| Combined-under | 11.201 | 28.82 |
| Combined-over | 10.428 | 574.87 |

Combined-over reaches the positive input-offset bound+.3. The bound is not
expanded and the source is not replaced. The over cases show substantially
higher condition numbers than several other fixtures; rank5 alone does not
establish robust targets under real-image perturbation. No uncertainty, repeated
capture or real-data stability study is claimed.

Nonzero stress residuals coexist with exact noiseless in-family recovery.
Clipped/quantized composite inputs and additive channel shifts differ from the
ideal inverse family. This check does not attribute all residual to one cause,
prove the global best correction, restore lost texture or repair learned
red/blue routing. No new cue or source-invariant control predictor was trained.

## Decision after the fixed check

Engineering and noiseless mechanism checks PASS. Keep the five-output family
as a research candidate, not a qualified correction model. Real five-control
target stability, visible utility, identity preservation under predicted controls
and darker-skin performance remain untested. No current paper scope, active
three-control model or Android schema is changed.

The next substantive candidate decision, if pursued, is one bounded
reference-aware capacity comparison against the saved three-control FFHQ
diagnostic on identical inputs/support/metrics, with the observed bound and
conditioning issues explicitly retained. It would require a fixed execution/
independent-replay contract before real fits; no new baseline fits, start/bound
changes, larger dataset, tree training or human review follows automatically.
An oracle improvement, if observed, still would not solve control prediction.

Evidence: `outputs/affine_prepower_target_engineering_v1/` contains protocol/code/
version bindings, case plan,14persisted input/reference/support records and
results. Python3.14.7, NumPy2.5.3, SciPy1.18.1. Bound inputs remain hash-identical.
0real-photo/mask/NPZ reads,0real target fits,0tree fits,0new ratings or sources.
No locked final24/older contents/manifests, runtime/Android or manuscript access.
Prior artifacts/closures and approved59807manual/ear support preserved.
Model unfinished; paper paused; darker-skin priority and November25 retained.
