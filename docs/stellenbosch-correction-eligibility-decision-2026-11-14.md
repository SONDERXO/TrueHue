# Reviewed Stellenbosch material: correction-specific eligibility decision

14 November2026. User authorized deciding whether the already reviewed
Stellenbosch development material can support a correction-specific test.
Completed metadata-only reconciliation; no photo/mask/NPZ arrays, locked
records, target optimizations, calibration or correction-tree fits were used.

## Decision

Do not select these60captures as the next paper-aligned correction test or as
the replacement six-person portrait set. Keep them as valuable reviewed
measurement/calibration evidence. There is a distinct question one could ask
about reference-aware three-control restoration, but the present records do not
establish a suitable correction experiment and the low native face detail makes
this a poor priority for the user's visible-usefulness concern.

This is a scoped eligibility decision, not a declaration that all Stellenbosch
images are unusable or that the correction method is impossible. It does not
restart the closed calibration studies, request more marks, broaden to285
subjects or reopen the locked24/later reserved source records.

## Exact evidence established

`scripts/check_stellenbosch_correction_eligibility_metadata.py` reconciles the
fixed60-row reviewed development design with all60existing annotation JSONs
and their annotation-manifest hashes. It verifies case/source/subject/decimal-
label bindings, user-reviewed-selection status and unchanged admission flags.
Ten publisher subject keys each have all six saved conditions: F_cool, H_warm
and L_warm at600 and1200. These are60captures of10people, not60independent people.

Every original source is224×224. Saved native face boxes are only24–30pixels
wide and32–39pixels high; native context crops span48–59pixels. Their normalized
256px measurement images enlarge those samples. The dimensions are read from
saved geometry, not newly detected. This quantifies a limitation, not a new
universal minimum-face-size rule or an unperformed visual quality judgment.

The ten supplied decimal scores are2.4,2.5,3.0,4.0,5.3,6.9,7,7,9.0,9.2.
Five subjects have fractional scores; two have scores at least8. These are
descriptive supplied-score counts, not a newly invented integer-group policy.
The existing ten-person material does not furnish the previously proposed
four-dark-slot pilot without broadening the cohort. No such expansion occurred.

## What the reviews establish, and what they do not

All60 records establish reviewed skin selections for Lab/ITA measurement under
their scoped manual-assisted workflow. All retain training/calibration admission
false. That is real reviewed evidence; do not ask the user to repeat it.

Those measurement reviews do not establish acceptance of each original as a
clean photographic correction reference. They also do not bind full-face/neck
application alpha, protection vetoes or reference consistency for this proposed
correction test. A selected measurement patch can be useful without being an
appropriate correction application mask. Promoting it would change the task.
The decision records missing correction evidence; it does not assert that no
other historical mask could exist anywhere on disk.

Exact shared Lab/ITA computation does not establish current281-feature
compatibility. Scene/green/histogram descriptors on a small cropped scene and
on an FFHQ portrait have different image context. There is no verified compatible
automatic MST mapping for these new distorted inputs, and supplied reference
scores must not be inserted into inference features. No current mapping or
feature vector was copied into a new candidate.

## Distinct rationale versus a closed-experiment restart

The completed calibration experiments asked whether ITA/Lab predicts supplied
decimal MST under changing lighting. A potential correction-specific experiment
would instead ask whether the fixed gamma/red/blue renderer can approximately
restore synthetic distortions of an accepted photographic reference. That is
a different dependent variable and could isolate renderer recoverability before
learning. A failed calibration comparison alone does not answer it.

However, that distinction supplies neither accepted references nor application
support, useful native facial detail, tone-severity assignment, new information
for the learner or a justified repair to wrong-axis predictions. The earlier
paper-composite generated-ramp study already documents clipping and residual
limitations. Another small low-resolution operator study would not by itself
resolve the current weak-visible-benefit complaint or justify reopening failed
trees. No recipe or stronger correction is selected on this rationale alone.

The existing continuous-MST candidate preserves decimal scores without requiring
an integer adapter, but it was an isolated generated-interface experiment, not
a qualified real correction model. It does not resolve the separate paper-group
severity question. Conversely, no new integer adapter is imposed merely to run
an otherwise eligible renderer-only experiment; such a fit would not use MST as
an inference input at all.

## Consequence

The correction-test roster remains unbound. Zero new admitted references,
application supports, local target fits, tree fits or review tasks result.
Stellenbosch access is already resolved and is not the blocker here. Keep the
reviewed material and all calibration results; do not discard them as "bad data"
or continue waiting for a reply already received.

The dataset question is now answered: we have relevant labelled material, but
the already reviewed sample is a weak choice for the next visible photographic
correction test. Continuing model research requires a concrete learning or
reference-data decision beyond moving this sample into a different folder.
Do not initiate another serial eligibility or source-readiness queue from this
result. Any future source/annotation scope must be explicit and bounded.

## Verification and preserved state

Output: `outputs/stellenbosch_correction_eligibility_metadata_v1` contains the
complete60-row ledger, decision, input hashes and verification. All60case/source/
subject/label and annotation-manifest joins passed, each of ten subjects has
six conditions, and all read metadata remained hash-identical. This verifies
saved metadata, not image quality, actual skin accuracy or runtime compatibility.
No original/cached image arrays were decoded and no source file hash was freshly
recomputed. No locked manifest/content was accessed.

Research-only/noncommercial/citation/no-redistribution terms remain. Source
images, prior artifacts and experiment closures, approved desktop/manual ear
support, runtime/Android and manuscript remain unchanged. Darker-skin priority
retained; model unfinished; paper paused; November25 deadline retained.
