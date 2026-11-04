# Measurement-error proposal

1 November 2026. User authorised preparing this proposal after the25-attempt
additional-subject eligibility screen. This is a proposal, not implementation,
mask adoption, new calibration or permission to fit a correction model.

## Recommendation

Address the demonstrated **outside-face spill** with one geometrically bounded
measurement candidate. Treat **inside-face occluders** as a separate unresolved
validity problem. Do not promise that cropping to a face outline removes beards,
glasses or worn masks. Do not train another calibrator while these remain.

Correction coverage is a separate purpose: keep whole-face plus visible neck,
enclosed-hole filling and inward blending. Its intentional coverage of internal
features/hair must never be copied into measurement. No change to either demo.

## Findings and code mechanism

The frozen screen has25attempts/17technical successes/8failures. All17 saved
mask/feature replays passed, yet visual inspection identified neck/garment in
case4, beard in case10 and a worn mask in case14. These are diagnostic findings,
not complete hand-labelled ground truth or a population error estimate.

In semantic_face_coverage.py, select_face_skin retains an entire predicted
skin/nose connected component if any part overlaps the selected face seed.
It does not bound the retained component by that seed. Thus a misclassified
component can extend into neck or clothing. This code path permits the observed
outside-face spill; an overlap association is not a spatial containment rule.

Beard and covering pixels inside the face are different: they can have the same
predicted skin class and lie inside valid geometry. The parser has no distinct
beard class. Anatomical feature exclusions and a nasal guard cannot guarantee
removal of such pixels. Facial skin statistics can therefore be reproducible
without being valid measurements of actual skin.

## One proposed implementation, if pursued

Keep the original measurement pipeline and artifacts intact. Implement a new,
isolated candidate with the exact rule:

`candidate = current_nostril_measurement_mask AND selected_face_outline`

Use the existing original landmark polygon at square256, with no dilation,
convex-hull expansion, radius choice, hole filling, alternative face rectangle,
region search or recovery fallback. Keep the same1000-pixel minimum and existing
failure behaviour. Add no new pixels. Missing/degenerate geometry or too few
remaining pixels means unavailable features, never old-ITA substitution.

This is a defensible hard boundary for **measurement**, not a claim that the
landmark outline equals actual skin. It may remove legitimate forehead/cheek/
ear skin or remain wrong if landmarks are wrong. Record loss of coverage and
failures rather than relax the boundary to achieve favourable results.

Give it a new version and dependency-hashed measurement contract. Recompute
features only for an explicitly frozen diagnostic replay; do not load/export
any old lookup. Even a successful mask repair cannot transfer the old MST fits,
feature approvals or correction targets. The current contract remains unchanged
until a separately executed candidate exists.

## Occlusion handling: no invented automatic detector

Do not remove the lower face for everyone, pick whichever region gives a better
ITA, infer skin from brightness, or add a beard/glasses model under this proposal.
Beard-specific model work remains held. A recorded mask-status field is
development metadata, not an input available to an arbitrary gallery photo;
the screen already contains conflicting0|1 metadata.

For development eligibility, preserve explicit image-bound reviewer evidence of
selected beard/glasses/covering pixels. Such measurements remain on hold even if
the geometric candidate passes every programmed exclusion. No deletion from
denominators, relabelling, replacement or filtered refit. Manual annotation can
judge diagnostics; it is not an automatic on-device validity mechanism.

Operationally, a technical-success result cannot be described as verified skin
or reliable MST. A future validity/occlusion mechanism needs its own evidence
and scope. This proposal does not claim arbitrary-gallery reliability.

## Evaluation frozen before candidate results

Use the already frozen25attempt screen as development/regression evidence only:
all25attempts remain, including the eight previous failures. Use saved category
maps/landmarks for successful cases; do not repeat inference to chase recovery.
Unavailable saved evidence stays unavailable. Preserve current baseline bytes.

For all17 saved successes, independently reconstruct both masks and compare:

- Candidate selected pixels outside the exact geometric outline: must be0.
- Added pixels relative to current measurement: must be0.
- Selected predicted forbidden/anatomical/nasal-guard pixels: must be0.
- Source-image, correction support and rendering bytes: must stay unchanged.
- Removed pixels, retained fraction and minimum-pixel failures: report for every
  image, including failures. No retention threshold selected after results.
- Lab/ITA and endpoint features: replay exactly from saved candidate pixels;
  unavailable features must remain unavailable, not stale values.

Before comparing candidate results visually, bind the known contamination
diagnostics to image hashes and record clearly visible contamination locations
against original images/current masks. Distinguish clear non-skin, clear skin
and uncertain boundaries. Keep annotator identity and uncertainty. Sparse
diagnostic marks are not full ground truth and cannot estimate mask precision,
recall or population accuracy. Any selected clearly marked non-skin pixel is
a validity failure for that case; zero marked overlap alone is not a pass.

Inspect all saved successful cases once. Report whether the neck/garment failure
is removed and whether beard/face-covering selection remains. Do not require
this boundary-only candidate to solve internal occluders by changing its rule.
No label/ITA/MST error, reference colour or correction score selects geometry.

## Independent evaluation and stopping decision

These25photos and all four subjects are exposed development evidence. The312
unsampled photos are of the same people; they are not independent subject-level
validation. The prior15MST-E subjects are also exposed. No untouched eligible
independent-subject validation set is established by current records. Reserved
correction roles remain locked; do not repurpose them as a measurement test.

Therefore this proposal can support at most one bounded engineering diagnostic,
not a final measurement-accuracy or MST-generalisation claim. Before any broader
validation, freeze independent subject provenance, duplicate relationships,
roles and actual-skin annotations outside the evidence used to design the rule.
Existing datasets may provide that route only after eligibility and permitted
roles are established; no recruitment is required by implication.

Stop after one diagnostic replay. A containment invariant failure means reject
the implementation. Successful containment with remaining beard/covering errors
means **outside-face spill addressed, actual-skin reliability unresolved**.
Neither result authorises another radius/feature/calibrator/tree trial, automatic
cohort expansion or a fit on selected clean cases. Do not introduce alternative
boundary candidates after seeing the result.

## What this delivers and what remains

Deliverable if implemented: isolated candidate code, exact old/new mask gallery,
all-attempt ledger, feature replays, coverage/failure report and one stop decision.
No new runtime MST lookup or correction training. Retain
ITA + calibrated MST + facial statistics → decision-tree gamma/red/blue correction.

Even perfect face containment would leave three separate needs: actual-skin
validity inside the face, a reliable matching MST mapping, and adequate
reference/evaluation support. Categories7/10 still lack independent subject
support in full MST-E. A limited synthetic reconstruction study does not require
proving intrinsic skin reflectance, but it cannot quietly bypass these retained
method requirements or become a true-colour claim.

Preparing this document changed no code, settings, masks, allocations or models.
No new image processing, fitting, professional contact or participant collection.
No tests rerun for a documentation-only proposal. Last measurement checks:
7existing nostril/semantic tests passed in1.78s;17saved measurement replays passed.
