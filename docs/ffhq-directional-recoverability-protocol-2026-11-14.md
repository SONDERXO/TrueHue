# Current-renderer FFHQ directional recoverability test

14 November2026. A distinct bounded test is selected for engineering preparation,
not executed on photographs. No correction-tree fit or user-review batch selected.

## Unanswered question and history boundary

How much residual remains when the current direct-gamma/red/blue renderer uses
reference-aware local targets to restore the directional Table2 interpretation
on existing photographic references, with current approved support held fixed?

This is not another test of whether clipping loses information. That is already
established. The October28 six-source FairFace test used the earlier composite
with contrast pivot0.5 and freshly estimated distorted-input masks; both operator
and coverage differ. November3 tested the directional operator on a generated
ramp only. The FFHQ66review instead tested gamma/gain inputs, not this additive
brightness/contrast/red-blue composite. No completed current-directional FFHQ
photo test was found in the scoped history search.

The new question is the residual on current photographic support under this
specific operator/renderer pair. Changing sources alone would not justify a
rerun; fixing the current operator and approved support supplies the substantive
contract difference. Historical outcomes cannot be pooled as a causal before/
after claim. This does not supply a new predictor cue or repair tree routing.

## Exact roster, condition and budget

Use all11existing retained FFHQ reference lineages:54632,39568,29617,16061,
52445,32685,53146,48879,49131,59807,46795. No subset selection, new raw original,
source acquisition, replacement or excluded29863. Bind reference `input_rgb8`
keys/hashes from the existing blue-axis preparation design. Other NPZ keys may
not be decoded. Whole NPZ-container hashing is permitted and must be disclosed.

Use the current bound support selection from the blue-axis source-held design:
ten approved ear-support bundles and approved59807manual support/protection.
Verify the selected receipts and file hashes before decode; do not read old
unused support files or rebuild a mask. No parser, detector, calibration,
feature extraction or automatic-mask robustness claim is part of this test.

Freeze one common counterfactual Table2 row: gamma.70, brightness-35, contrast+8,
red offset-10, blue offset+10. This is the existing row named `medium` in code,
applied equally to every source. It is NOT a source MST assignment, a claim that
these people are medium-skinned, or a complete tone-dependent Table2 evaluation.
The earlier paper-aligned tone-assigned plan remains distinct and unexecuted.
This fixed row permits a renderer diagnostic without invented labels or a
three-severity grid. No strength selected by output appearance or residual.

Six roles/source: identity, colour-only, exposure-under, exposure-over,
combined-under and combined-over.66attempt records;55nonidentity local target
optimizations maximum;11exact identity targets. No target refits, multistarts,
failed-case replacement, tree fits, held predictions or model rescores.
These are numerical records, not66requested human judgments.

Reuse unchanged `directional_exposure_pivot_gamma_offset_rgb8_v1`.
Encoded RGB x: under=`1.08*(x**(1/.70)-1)+1-35/255`;
over=`1.08*x**.70+35/255`; colour adds`[-10,0,10]/255`.
Combined applies exposure then colour. Distortion alpha1over the full256crop,
clip once and round once using existing code. Record preclip out-of-range
channels/pixels for the whole crop and fixed primary support. Keep every clipped
case; do not admit stress cases into training if their clipping happens to be0.

## Reference-aware targets and interpretation

Use `direct_gamma_rgb_three_control_blended_target_v1` unchanged: identity start,
control bounds[.25,4], SciPyTRF linear RGB squared loss, all tolerances1e-10,
max_nfev500. Fit on the fixed alpha-positive primary region. Supplied references
are supervision for this capacity diagnostic, never inference inputs.
Correction uses direct power, red/blue gains, clipping, exact approved alpha
blend and RGB8 rounding. Identity is exactly[1,1,1] with no optimization.

Convergence/rank/finite-control failures stay unavailable, with no identity
fallback or alternate fit. Retain active bounds, evaluations, float and actual
RGB8 residuals. A bounded local solution is not the global best attainable
correction: high residual alone cannot prove all three-control solutions fail.
Low residual establishes existence for the scored case under this mask, not
that an input-only model can infer those controls. Clipping observations provide
separate direct evidence of lost input information; they do not explain all error.

## Frozen reporting and engineering checks

Primary scoring support is exactly alpha>0; do not refit on a favorable
intersection. Report core alpha1and feather regions separately, including
region sizes. Report input/reference and fitted-output/reference RGB8MAE and
CIEDE2000, paired benefits, change magnitude, and all per-case residuals.
Report whole-crop results descriptively: context outside correction remains
distorted and is not intended to match the original. Compute source-equal means
separately for each of the six roles; do not rescue any role by pooling others.

Verify exact zero-alpha/protected pixel equality to the actual distorted input,
not the reference. Fixed protection must veto application alpha. Reconstruct
float objective and actual RGB8 rendering with a separate scalar implementation;
independently replay CIEDE2000 using the existing standard implementation.
Verify identity bytes exactly, source immutability, all66role joins,55fit budget,
11support joins, every failure and all hashes. Fail closed on integrity mismatch.

No new perceptual pass cutoff, visibility threshold, adoption gate or rerating is
created. Numerical recovery and visible usefulness are separate. If residuals
are small, the conclusion is that this renderer can recover these cases under
oracle supervision. If large, report the observations and solver limits; do not
silently add contrast, offsets, more starts or another model family. Either
outcome ends this diagnostic without automatic training or another recipe queue.

## Execution boundary

First implement/check generated workflow fixtures covering formulas, clipping,
direct-versus-reciprocal gamma, protection, scalar rendering/objective parity,
unavailable fits, no overwrite and failure preservation. Bind code/dependency
versions and verify the design before any real-photo target fitting. This
specification and its metadata design do not constitute that engineering check.

After engineering checks, the only proposed real budget is the fixed66records/
55local optimizations. No candidate is adopted and no full paper model completion
follows. No official tone strata or darker-skin bias reduction can be inferred
from these unlabelled, repeatedly exposed references. Darker-skin qualification
remains a separate required evidence gap, not replaced by this diagnostic.

All historical failures, reference limitations, support assistance and source
exposures remain. No final24/older locked contents or manifests, runtime/Android,
paper edits, external contact, acquisition or new user review is authorized.
Model unfinished; paper paused; November25 deadline retained.

History evidence: table2-known-source-feasibility-results.md;
table2-target-fit-results.md; directional-exposure-revision-results-2026-11-03.md;
integrated-correction-development-plan-2026-11-03.md;
ffhq-source-eligibility-results-2026-11-05.md;
joint-colour-acceptability-review-results-2026-11-13.md;
reviewed-correction-magnitude-audit-results-2026-11-14.md.
