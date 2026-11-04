# Correction-data and validation redesign

28 October2026. User explicitly authorizes substantial data/training redesign
after repeated experiments on15sources failed reliable correction. Freeze new
candidates before image processing or fitting. Preserve all earlier results,
annotations,qualified acceptances,rejections,holds and allocations.

## New candidate design

Use local FairFace metadata and filename availability only. Exclude every source
in the historical650candidate audit, all explicit development-exposure IDs and
any additional FairFace IDs in the processed-manifest registries. Inclusion
outside those records means no recorded pipeline-development use,not proof of
never having been manually seen. Do not inspect/decode/hash image bytes for this
selection. Reading dataset labels/filenames is metadata exposure,not pixel review.

Select510original TRAIN sources by SHA256 ordering of
`truehue_redesign600_v1/train_seed42/` plus normalized imageID; first420are
training candidates,next90development-validation candidates. Select90original
validation sources separately by`truehue_redesign600_v1/test_seed42/`plus imageID
as final-test candidates. Preserve original train/validation labels. No original
validation row enters training. All source variants inherit the candidate role.
Do not relocate files or change historical74reserved/126development allocations.
The new role is a separate design for new sources only.

600is an operational candidate budget,not a power calculation or promised final
eligible count.420/90/90is an exact70/15/15candidate count,but **not** an
MST-stratified or person-verified split. No race,age,gender,appearance ranks,
ITA,MST,model predictions or correction outcomes determine selection. Official
FairFaceMST labels remain unavailable; do not infer them from demographics.
SCIN and complete MST/category coverage remain unresolved thesis requirements.

## Locks and eligibility

Validation/test are locked against image preprocessing,reference/mask screening,
distortion generation,feature extraction,model tuning or outcome inspection
during initial training development. Record access only when a declared phase
is intentionally opened. Candidate manifests and locks contain metadata only;
do not call them pixel-untouched independent final evidence after actual access.

Before any fitting, execute a documented duplicate/content-leakage audit and
quarantine conflicts across roles rather than silently reassigning sources.
Person identities are unavailable; source/group separation is not proof of
person separation. No candidate has a fabricated duplicate-group identity.
The duplicate audit's necessary image access must itself be disclosed and
kept separate from model/quality inspection; its execution protocol is pending.

Training preprocessing must use the existing square256measurement/experimental
MST contract and retain every failure,clipped input,target residual and human
decision. Source/reference and exact displayed processing approval remain
separate from numerical success. Do not promote unreviewed candidates or replace
failed IDs with favorable outcomes. Freeze all stage decisions before fitting.
Use existing source-conditioned Table2settings and exact unchanged controls;
do not add reference features at inference. Changes to augmentation/training
objective need a separate declared comparison,not retrospective selection.

The initial training queue contains all420IDs,split into fixed60source batches
for processing/review workload. This batching changes no role and promises no
replacement or accepted yield. No validation/test row enters the queue.

Only training-group resampling may guide model choices. Open the development-
validation phase after an explicit model/data-policy freeze,record its exposure,
and never reuse that result as final testing. Final-test candidates stay locked
until method/model choices and reporting rules are frozen. Report all eligibility
failures and final denominators rather than claiming600accepted sources.

Keep original quality gates,no-correction baseline,clean harm counts,distorted
intervention coverage and per-severity failures visible. An identity-only or
one-case-intervention gate pass is not a finished useful model. Existing weak
MST,photographic-reference,clipping and mask limitations remain. Photographer
opinions wait until model completion using the existing GoogleForm. Android
remains paused;CPM deferred. No model activation or dataset uploading.
