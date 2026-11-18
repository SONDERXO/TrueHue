# FFHQ directional recoverability: real diagnostic complete

14 November2026. The fixed11-source/66-condition diagnostic completed with
exactly55nonidentity local target optimizations and11exact identity controls.
All66targets are available; all55approximate targets converged with rank3 and
no active bounds. Independent scalar verification passed all66cases and six
source-equal summaries, without verifier fits. No tree was trained or rescored.

## Main result

The fixed three-control renderer can numerically restore this colour-only
condition fairly closely with reference-aware controls. The exposure/combined
conditions retain substantial residuals under the same bounded local fitter.
Clipping is substantial in the fixed primary skin region. Stronger distortions
therefore do not, by themselves, supply a justified fix for the learned model's
weak visible colour improvements or wrong-axis predictions.

All rows below use the same counterfactual Table2 setting named medium in code.
It is not a complexion label or a complete tone-dependent paper evaluation.
Metrics are source-equal means over11sources, on exact approved alpha>0 support.
RGB MAE is in8-bit channel codes; DE is CIEDE2000 under assumed decoded sRGB.

| Condition | Input RGB MAE | Local-recovery RGB MAE | Input DE | Local-recovery DE | DE benefits / harms |
| --- | ---: | ---: | ---: | ---: | --- |
| Identity | 0 | 0 | 0 | 0 | 0/0;11exact unchanged |
| Colour-only | 6.666 | 1.572 | 5.179 | 1.319 | 11/0 |
| Exposure-under | 71.552 | 17.363 | 24.482 | 8.136 | 11/0 |
| Exposure-over | 70.494 | 18.718 | 22.100 | 16.019 | 9/2 |
| Combined-under | 71.944 | 15.706 | 25.346 | 7.380 | 11/0 |
| Combined-over | 71.395 | 18.221 | 22.296 | 16.110 | 9/2 |

All55nonidentity cases improve RGB MAE. This does not guarantee DE improvement:
32685 and48879 worsen DE in both exposure-over and combined-over. For
exposure-over, their DE changes are18.2965→19.6243 and17.8416→24.0429;
for combined-over,18.7387→19.7588 and18.0814→23.6216. The fitter minimizes
RGB squared error, not DE. No failed case is deleted or rescued by pooled means.

Primary output RGB MAE ranges are1.104–2.201 for colour-only,8.404–29.763
for exposure-under,11.641–25.602 for exposure-over,7.783–26.593 for
combined-under and11.675–24.524 for combined-over. These are observations,
not newly introduced visibility or acceptance thresholds.

## Clipping, feathering and interpretation limits

Source-equal fractions of primary pixels with at least one preclip out-of-range
channel are0.016%colour-only,22.398%exposure-under,39.377%exposure-over,
17.884%combined-under and28.238%combined-over. Clipping records are before
rounding and correction, not a claim that all such pixels have the same error.
Clipped inputs remain in the diagnostic; no training admission is inferred.

Feather regions retain larger errors because the strong input distortion is
global and correction is only partially applied there. However, the issue is
not restricted to feathering: alpha1core mean output RGB errors remain14.217
for exposure-under,16.312 for exposure-over,12.396 for combined-under and
15.767 for combined-over. Colour-only core mean is1.272. No mask dilation,
protection relaxation or stronger correction multiplier was attempted.

These are local reference-aware targets, not a learned model's predictions or
global optima. A large local residual alone does not prove that every possible
three-control solution fails. Clipping separately establishes input information
loss, but does not quantify how much of each residual is caused by clipping,
operator mismatch, the RGB objective or the local solver. Conversely, a small
residual does not establish that a single-photo tree can infer the controls,
that users prefer the output or that real-camera errors are modeled correctly.

The earlier review used mild gamma/gain diagnostics; this test uses a substantially
different directional additive/contrast composite with input RGB errors around
70codes for exposure. Do not present the increased numerical edit size as an
improved model, compare it causally with old review scores, reinterpret existing
ratings or use it to claim the user's original concern is solved.

## Exact execution and independent checks

Runner: `scripts/run_ffhq_directional_recoverability.py` with
`--execute-fixed-real-diagnostic`. The preceding `--check-bindings-only`
verified frozen design,191generated-QA artifacts, code and dependency bindings
without source-image access. The real adapter then used the unchanged tested
loader, operator, fitter and workflow. It has no model-training path.

All11whole identity containers and selected approved-support receipts/files
were hash-verified before any array decode. Only identity `input_rgb8` keys
were decoded; all other NPZ keys remained unread. Whole-container hashes read
all container bytes, which is disclosed separately from key decoding. The
11alpha arrays and selected protection PNGs were decoded. Source raw originals,
old unused supports, measurement/correction-mask arrays and locked sources were
not decoded. Selected mask files were hashed as bound support evidence.

The10approved-ear bundles and approved59807manual revision remained fixed.
No parser, detector, landmark, new mask or manual marking was used. All sources
remain declared real/exposed with generated_fixture=false; no provenance flag
was forged to use a generated-only fitter. All original selected file/container
hashes were rechecked unchanged after fitting.

Verifier: `scripts/verify_ffhq_directional_recoverability.py`. It reads the saved
run arrays, not the original source containers, and independently replays scalar
forward distortion, preclip counts, direct-gamma/blended rendering, float objective,
RGB8/DE metrics, region sizes/changes, target residuals, identity and exact outside/
protected equality. Standard DE uses the shared scikit-image implementation with
separate full-image conversion/aggregation; no independent DE formula is claimed.
Every RGB8 rendering matches exactly; objective tolerance is1e-12 and metric
replay tolerance1e-10. It verifies66unique source-role joins, all11saved support
array bindings,55solver starts, six source-equal summaries and the fixed budget.

Runtime/code versions match the preceding generated QA. The actual adapter was
bound before execution. The completed run and all of its bound artifacts were
rehashed after independent verification. No fresh full-suite run was warranted:
the unchanged workflow had53focused tests and the generated66-case rehearsal;
the new real execution received direct full independent replay.

Evidence: `outputs/ffhq_directional_recoverability_v1/` contains the execution
plan, solver accounting, cases, completion record, independent verification and
assessment. The versioned run refuses overwrite; no fit was repeated.

## Decision after this one test

Close the diagnostic as complete, not as model qualification. Do not start more
trees, fit starts, strengths, operators, sources or ratings from this result.
The next substantive model decision must address the mismatch between the
required distortion and what the current correction operator restores, while
keeping the existing colour-prediction failure separate. Simply feeding stronger
Table2 examples to the failed recipe is not a supported repair. No new training
recipe or renderer extension is selected here, and no paper scope change is
silently adopted.

No official tone labels exist for these11references, so this supplies no
darker-skin bias-reduction or independent qualification result. That remains
central to the thesis and an unresolved evidence requirement. No66-case human
review task, expert MOS, final predictor or Android readiness is implied.

All prior artifacts, model/review closures, approved manual/ear support and
locked final24/older contents and manifests remain preserved. Zero locked access,
new acquisition/contact, runtime/Android or manuscript edits. Model unfinished;
paper paused; November25 deadline retained.
