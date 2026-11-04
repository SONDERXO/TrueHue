# Preferred-region correction cycle: preparation results

31October2026. User authorized the next data/cohort/MST/comparison steps. The
mask design is fixed: facial skin for measurement; face, visible neck, brows
and lips for correction. No further region or parameter sweep was run.

## Concrete progress

**A broader source set is frozen.** Twelve candidates were selected before
their pixels were opened in this phase, from the existing training allocation.
They exclude all32completed-comparison sources, quarantine cases and sources
with collected prior review evidence. The live review-import scan confirms no
earlier accepted/rejected/uncertain judgments for the selected12. They remain
previously development-exposed images, not untouched data or verified distinct
people. Engineering groups are6light/5medium/1dark; these are not official MST
strata or proof of tone balance.

Ten new candidates processed successfully.59172had no predicted facial skin
overlapping the selected face;67581had only104selected pixels, below the existing
1000-pixel measurement minimum. Both remain
technical holds, with no replacement. Together with six migration anchors,
16reference-mask candidates are available. All16boards were inspected by the
assistant, not approved on the user's behalf. Blur, color casts, beard, other
people and instrument/occlusion concerns occur in the new candidates. The review
keeps these visible rather than admitting all technically successful images.

**A matching experimental MST artifact is packaged.** One all-row isotonic fit
on393successful exposed semantic MST-E measurements was saved and independently
replayed. Lookup SHA256:
`24c666fcea156317efc6f810a30b2e598b03d7f616ea8dd023ce421d16d2c0f2`.
Its semantic measurement contract remains
`f128f543377efab22930e5c60b4c20efd4c5f386d951a645818ca5c2a6265828`.
Only declared development-feature use is allowed in this cycle. It is not final
validated calibration, automatic runtime adoption or a correction-model result.
Poor held-subject exact accuracy, unreviewed calibration masks, missing category
support and lighting dependence are retained. Neither demo uses this artifact.

**Paired data now match the preferred correction region.** The six anchors have
six control records and30freshly generated inputs, with saved reference masks
for face, neck, brows, lips and union. ITA/MST/endpoint features use only facial
skin; generation covers the combined region.16inputs are primary candidates,
14are clipped stress candidates. All remain unreviewed and not fitting-admitted.
No old face-only pair was relabelled or scored as neck/brow/lip reconstruction.

**One comparison is specified.** The
[fixed development-cycle protocol](preferred-support-development-cycle-protocol.md)
declares source-held five-feature versus eleven-feature trees under the same
new method/data, with unchanged tree settings, clean-preservation gate, regional
metrics and no-correction baseline. It is not a causal test of masks alone or
an independent final test. It must not fall back to another six-source-only
trial. There is no correction-tree fit yet because exact reference/variant
admission has not been completed.

## Minimum next review

Open `outputs/preferred_reference_review_v1/review.html`:

- Six anchors: source/facial-mask approvals are retained. Only their NEW
  combined correction support needs a decision; no repeated old approval.
- Ten newly selected available sources: source suitability, facial measurement
  mask and combined correction mask. If a source is rejected/uncertain, its mask
  decisions may stay unchosen. At most36judgments across16photos.
- Two processing failures: visible as holds, no decisions requested.

Download `truehue_preferred_reference_decisions.json` into that review folder.
Script341 verifies membership, file hashes, notes and contract. Acceptance admits
only reference preparation, never distorted masks or model fitting. It preserves
rejects/uncertain cases; no adviser-request prerequisite is imposed.

After this review, generate the accepted new sources' combined-region pairs and
identify exact new input-mask judgments. Only then freeze actual admitted rows
and run the single comparison. No model is trained automatically from a browser
choice. The reference review cannot establish intrinsic color or fix MST
validation by itself.

## Verification and records

- Reference source selection, measurements, region masks and provisional lookup:
  `outputs/preferred_support_cohort_v1/`.
- Six-anchor combined-region pairs and generation replay:
  `outputs/preferred_support_pairs_v1/`.
- Exact-bound reference review, isolated DOM/export harness (not a live browser):
  `outputs/preferred_reference_review_v1/`.
- Independent replay:16reference feature sets, one all-row mapping refit,
  30pair measurements/target applications, source exclusion and region union
  checks. Every region is nonempty in the30anchor pairs; this is availability,
  not segmentation-quality approval.
- Six new importer tests passed, covering reference-only admission, held-source
  short-circuit, duplicates, stale binding, incomplete decisions and changed mask.
- Full Python suite: **872passed in14.25seconds**, cache disabled.
- The packaged development lookup emits1–9; no category10 endpoint was forced.
- Source-selection protocol snapshot is saved exactly. A later clarification
  distinguished facial estimation-retention from combined correction-retention
  screening before pair generation; its explicit amendment/snapshot hashes were
  verified. No source selection or calibration recipe changed.

No reserved evaluation pixels, correction-tree fit, new mask approval, beard
model, demo switch or professional-rating collection occurred. The original
appeal/thesis documents were not edited.
