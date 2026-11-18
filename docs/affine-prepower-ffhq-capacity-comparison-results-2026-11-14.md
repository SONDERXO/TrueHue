# Matched FFHQ five-control capacity comparison: numerical screen passes

14 November2026. Completed the user-authorized fixed comparison after freezing
`affine-prepower-ffhq-capacity-comparison-protocol-2026-11-14.md` and passing its
generated-workflow barrier.66matched real cases,11existing photographic sources,
55new reference-aware five-control local fits,0baseline refits and0tree fits.
Independent verification passed every case and the prospective decision label.

## Main result

The five-control family materially improves numerical exposure/combined recovery
on these inputs compared with the saved three-control local solutions. Colour-
only improvement is small and includes individual regressions. This supports
further research on the operator; it is not a trained single-photo correction
model, visible-preference result or adoption into the paper/runtime.

Same cached input/reference, approved alpha/protection, support regions, metric
implementations, counterfactual medium setting and source weighting throughout.
No new distortion or source selection; no photographic MST labels are inferred.
RGB MAE is8-bit channel codes. DE is CIEDE2000 under assumed decoded sRGB.

| Role,11cases each | Three-control RGB MAE | Five-control RGB MAE | Three-control DE | Five-control DE |
| --- | ---: | ---: | ---: | ---: |
| Identity | 0 | 0 | 0 | 0 |
| Colour-only | 1.572 | 1.554 | 1.319 | 1.299 |
| Exposure-under | 17.363 | 7.748 | 8.136 | 3.760 |
| Exposure-over | 18.718 | 8.337 | 16.019 | 4.345 |
| Combined-under | 15.706 | 7.659 | 7.380 | 3.798 |
| Combined-over | 18.221 | 7.475 | 16.110 | 3.672 |

Exposure/combined mean RGB error reductions relative to the saved baseline are
55.38%,55.46%,51.23%and58.97%, respectively. Colour-only reduction is1.20%.
These are relative reductions on this exposed developmental sample, not model
accuracy, population improvement or percentages of physical colour recovered.

All44exposure/combined cases improve both RGB MAE and DE against the saved
baseline. For colour-only, RGB MAE regresses on29617,32685,48879,49131;
DE regresses on54632,16061,52445,32685. The largest colour-only RGB worsening
is.076912codes (29617); largest DE worsening is.005305 (16061). Their small
numeric magnitude does not turn them into beneficial or invisible corrections.
All individual values remain in the assessment. No user rerating occurred.

All11reference-aware identity outputs are exact unchanged controls. That is
identity target construction with the reference known, not evidence that a
tree will preserve an unknown acceptable portrait. No predictor was executed.

## Conditioning, bounds and remaining error

All66targets are available. Every nonidentity fit converges with numerical
rank5. All55float objectives are no worse than the embedded old local solution
within the frozen1e-12tolerance. This is an observed result; no old solution was
used as a candidate start, fallback or rescue fit.

The positive input-offset bound+.3 is active in six cases: exposure-over on
54632,39568,53146,48879 and combined-over on53146,48879. It is not expanded.
Condition numbers span13.15–2320.81 across nonidentity fits. Exposure-over
median is577.94 and combined-over median378.03, versus colour-only35.96.
These are raw numerical-Jacobian diagnostics, not a calibrated uncertainty
measure or proof of uniqueness/stability. No perturbation or bootstrap test ran.

The fitted controls are reference-informed approximations to clipped/quantized
inputs; they need not equal the analytic inverse of the unclipped forward
operator. Additional target freedom can absorb reference-specific missing-data
averages. Numerical improvement does not establish a transferable input cue.

Alpha1core mean RGB errors fall from14.217→4.208 under,16.312→4.802 over,
12.396→4.076 combined-under and15.767→3.857 combined-over. Feather errors
remain34.84–35.68codes for these four roles, versus37.40–41.06before. The
strong distortion is global and partial alpha leaves some error at edges.
No widening, opacity multiplier, protection relaxation or new mask is adopted
to improve this comparison. Nonzero core residual and clipped information remain.

## Frozen decision

Status: **NUMERIC_CAPACITY_ELIGIBLE_ONLY**. All prospective numerical checks
pass:66available matched cases, exact identities, unchanged protected/outside
pixels, every nonidentity family nonworse in mean RGB MAE and DE, and exposure
families strictly better in both. The criteria were written before candidate
fits; they are not new perceptual/usefulness or final-qualification thresholds.

This passes a modest capacity screen only. It does not solve the earlier
red/blue prediction failure, demonstrate worthwhile colour-only visual benefit,
establish stable learned five-control targets, or reduce bias against darker-
skinned people. These11references have no eligible supplied MST labels and have
been repeatedly exposed. No final predictor or independent evaluation exists
from this result. The paper's three outputs and this proposed five-output family
remain explicitly different; no manuscript or runtime method is silently changed.

The comparison stops here. It supports considering a bounded prediction-stage
proposal, but does not automatically authorize tree training, bounds expansion,
another operator, more source/annotation work or a new user-review batch. Any
prediction-stage proposal must account for conditioning/bounds, the existing
colour-routing failures, and the thesis's darker-skin qualification requirement.

## Engineering and real verification

38focused comparison/fitter tests passed in4.53seconds. Tests cover corrupt
baseline output/metrics and hashes before fitting, missing candidate handling,
exact feasible old-solution embedding, no baseline optimizer calls, gate
regressions that cannot be pooled away, identity, preservation, no overwrite
and partial-failure persistence. No full-suite claim.

`scripts/run_affine_capacity_comparison.py --generated-workflow-qa` reused
all66saved generated baseline cases, made55new candidate fits and0baseline
fits, and passed66independent scalar matched replays and frozen-gate replay.
Code/protocol/QA/dependency hashes were bound before the real run.

`--execute-fixed-real-comparison` then read only cached artifacts from the
independently verified three-control FFHQ run. Every bound baseline file was
hashed before decoding. Original identity containers, raw photographs, old
unused supports and locked files/manifests were not opened. No parser/detector,
feature extraction, source labelling or mask rebuilding occurred. All ten ear
bundles and59807manual support remained exact through the cached alpha/protection.

The old solution embedded at input_scale1/input_offset0 reproduces every saved
old output exactly and matches its float objective. It was checked separately
from the single identity-start five-control solver. Baseline arrays, files and
metrics remain unchanged. Candidate cases keep generated_fixture=false.

`scripts/verify_affine_capacity_comparison.py` imports no optimizer or target
fitter. It replays all66matched cases using the separate scalar five-control
path, old feasible solution, float objective, RGB8 output, standard-library DE
with separate conversion/aggregation, region metrics, per-case improvements,
parameter constraints/conditioning arithmetic, source-equal summaries and
prospective label. It performs0fits. Standard DE is not independently derived.
The completed bound artifacts were rehashed again after verification.

Outputs: `outputs/affine_capacity_comparison_engineering_v1/` and
`outputs/affine_capacity_comparison_v1/`, including execution/solver accounting,
candidate outputs, comparison summary, verification and per-role assessment.
All previous artifacts/closures/ratings and approved manual/ear support remain
preserved.0new user ratings,0tree fits,0new sources,0locked content/manifest,
runtime/Android or manuscript edits. Model unfinished; paper paused;
darker-skin priority and November25 deadline retained.
