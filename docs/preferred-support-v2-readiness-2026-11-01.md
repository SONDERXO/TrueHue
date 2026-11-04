# Current-mask data readiness — 1 November 2026

The user accepted the eyebrow-area improvement and asked to continue. The mask
design is now fixed for this step. We updated the staged cohort and pairs to
the current correction-only eyebrow-area support; no calibration, source
selection or tree setting was changed.

## What is ready

- Same frozen six anchors and twelve additional candidates; sixteen available
  references and the same two technical holds. No substitution or new sources.
- Separate face, neck, brows, lips, surrounding-brow and combined masks. All
  sixteen facial measurement masks, statistics and feature values remain exact.
- The same experimental MST lookup was copied byte-for-byte, not refitted. Its
  validation limits and1–9output range remain. Correction-only mask changes do
  not change the facial measurement contract.
- Six control records and thirty regenerated anchor inputs using the NEW
  combined generation support. Sixteen primary and fourteen clipped stress
  candidates. Reference region files now include surrounding-brow skin
  separately, so it cannot disappear from later region-specific scoring.
- Thirty image-generation replays and thirty measurement/target replays passed.
  Source pixels outside generation support stay exact. No fitting admission,
  correction-tree fit, reserved evaluation access or demo change occurred.

The old version1outputs are preserved. The original version1pair builder was
reconstructed and its hash checked against the original frozen plan, then saved
as `outputs/preferred_support_pairs_v1/builder_at_v1.py`; the current builder
supports version2without losing the older execution source.

## Current review — only missing judgments

Open `outputs/preferred_reference_review_v2/review.html`.

The six anchors retain accepted source/facial-mask decisions; only their new
combined correction support needs judgment. The ten available additional
candidates need source suitability, facial measurement mask and combined mask
judgments. Rejected/uncertain sources need no further mask decisions. Two
technical failures need no review. At most36judgments, not a new21case review
or a request to redo accepted facial masks.

If you already downloaded version1reference decisions, use **load an earlier
downloaded reference decision file** at the top. Exact source-image/facial-mask
hashes were checked before enabling this carry-forward. It retains matching
source/facial decisions and prior notes, leaving the changed correction masks
unreviewed. Browser-only unsaved choices are not claimed to have been imported.
No decision export was found in the earlier review folder or Downloads at the
start of this task. Both old review and its browser state remain available.

Download `truehue_preferred_reference_decisions.json` into the VERSION2review
folder. Import with script341 using:

```powershell
venv\Scripts\python.exe scripts/341_import_preferred_reference_review.py outputs/preferred_reference_review_v2/truehue_preferred_reference_decisions.json --manifest outputs/preferred_reference_review_v2/manifest.json --output-dir outputs/preferred_reference_review_import_v2
```

The importer accepts exact reference judgments only; it does not approve
generated masks or train automatically. After these judgments, prepare pairs
for accepted new sources, identify exact new input-mask admission needs, freeze
actual rows, and run the one previously declared comparison. Do not fall back
to a six-source-only trial. No adviser request is needed for technical work.

## Verification record

Scripts345–347 refresh masks, rebuild pairs and check data. Script342 checks the
page in an isolated DOM harness, including prior-file carry-forward without
transferring correction decisions; it saves no simulated decisions. No live
browser interaction is claimed. Eight focused importer/peribrow tests passed.
Last full Python suite remains874passed in13.41seconds; no full rerun is
claimed for this versioning/preparation step.

Evidence: `outputs/preferred_support_cohort_v2/`,
`outputs/preferred_support_pairs_v2/`,
`outputs/preferred_reference_review_v2/`. Training remains pending actual
reference/input-mask admission. Beard-specific work and the current demos
remain unchanged.
