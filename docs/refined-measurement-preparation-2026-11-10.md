# Refined measurement preparation — 10 November 2026

## Result

Scripts 721 and 722 inspected the actual manual-export roots before preparing
data. Three refined exports exist: one generated GUI fixture, excluded from
photographic measurement preparation, and two revisions of **one** FFHQ source,
29863. No labelled calibration or tree-training record is admitted.

The user explicitly wants to review the latest revision before answering whether
either mask is finished. Both support-review statuses remain pending. This is
not a rejection, an approval, an MST annotation or a model-quality decision.

## Actual exports and verification

The real chain is automatic session report run `58aa72ec9201…`, then
`960f82d5d25e…`, then latest `794c247f2b7c…`. Folder names are not assumed to
equal report run IDs. All export members, byte sizes and SHA256 values passed;
parent manifest, preceding report, preserved automatic evidence and edit payload
bindings passed. Three editor jobs have result files: two photographic edits and
one generated-fixture job. No missing-result attempt was discarded.

Both photographic stroke replays exactly reproduce correction, measurement and
protected masks. First revision removes 5,786 measurement pixels; second removes
5,836 correction pixels and changes no measurement pixels. Each contains one
stroke. Both retain 8,861 selected measurement pixels, above the unchanged 1,000
guard. Recomputed statistics exactly match saved values:

| L* | a* | b* | ITA degrees |
| --- | --- | --- | --- |
| 33.9808 | 15.9771 | 12.1908 | -52.7284 |

Separate arithmetic verification confirms means and ITA, including rounding
before the ITA ratio. Separate change-count verification confirms all recorded
add/remove/unprotect counts, protected-output identity and identity outside
alpha. Captured historical controls remain unchanged; no edited features enter
the old MST lookup or tree.

The source SHA256 joins exactly to the existing FFHQ preparation metadata.
The original source file was **not reopened or hashed**. This is a metadata join,
not a fresh original-byte verification. All photographic processing here uses
already exported 256×256 images and masks.

Latest facial-measurement and correction overlays were both viewed. They show
different selected regions, including facial hair exclusions in measurement;
these views do not establish accurate skin segmentation. No source-wide,
photographic-quality or professional review is claimed.

## Method identity versus instance provenance

`outputs/refined_measurement_preparation_v1/method.json` defines research method
`truehue_manual_assisted_measurement_method_v1`, canonical SHA256
`2b1311a632997596571bbfad409567e8bd755d72eb8c56673424204d09859030`.
It binds the successful desktop current-mask workflow, 256×256 square linear
resize, automatic starting contract, implementation hashes, library versions,
explicit brush policy, facial-only measurement semantics, nonzero-mask selection,
OpenCV uint8 Lab conversion, float32 means, four-decimal rounding and ITA formula.

No image hash, source identity, stroke list or individual mask hash enters this
shared method identity. Those belong in per-instance records. Existing
`measurement_contract_sha256` values remain untouched and are checked against
their historical image/mask-dependent formula. Neither the new method identity
nor a shared inner service establishes equivalence to any previous calibration.
The method describes the intended measurement region; brush operations cannot
automatically certify that a user followed that region policy.

This is an isolated preparation artifact. Runtime exports and predictor behavior
are unchanged. A future runtime measurement consumer must explicitly adopt a
qualified method; simply attaching this hash to old coefficients is prohibited.

## Data manifest and remaining gaps

`records_PRIVATE.json` preserves every refined export, the excluded fixture,
source/image/mask/manifest hashes, history, method and instance identities,
statistics, strokes/counts, revision status and explicit eligibility reasons.
Only the latest real revision is the current candidate. Both versions remain
preserved; they are not independent samples. MST reference label, verified
subject/group, correction reference and allocation remain null. The historical
predicted MST value is **not** a reference label.

`labelled_queue_with_history_PRIVATE.json` records all 30 existing development
cases from ten publisher subjects, exact original decimal MST scores, source
hashes, conditions and historical outcomes. All nine unavailable cases remain;
the 21 historical technical passes are not admissions. No later/final source
paths are enumerated by this queue preparation. These records are **pending
ingestion design**, not ready-to-open desktop jobs: native face-context crops
are incompatible with the desktop whole-image square method. No masks,
calibration labels or approvals are silently transferred across geometry.

Next preparation for those labelled cases must reuse cached evidence without
rerunning the closed native experiment, declare an explicit coordinate method,
and supply an editor-compatible path that retains failures. Native and desktop
records must not be pooled under the method above without justification. This
queue is not evidence that the desktop can rescue failed detections/measurements.

## Calibration and bounded tree prerequisites

Actual reviewed refinements, credible measurement support and labelled coverage
are still required. Subject-disjoint fitting/validation roles must be established
before calibration; revisions, conditions, derived distortions and photographic
targets stay with their source group. Unknown groups/labels stay missing. Do not
select only technically successful or bright examples. Report measurement
unavailability separately from learned identity/no-op behavior.

Any matching calibration must bind the complete method and data lineage and be
validated without validation-subject leakage. Source and expert target features
must come from their own inputs; target-aware oracle controls are not predicted
training performance. Only after qualification should one separately frozen,
bounded decision-tree comparison be proposed with ITA, compatible calibrated MST,
explicit controls/rendering and the unchanged joint acceptance gates. No fit,
new comparison, old-coefficient transfer or automatic repair sweep is selected
by this preparation.

## Evidence and preservation

Both preparation and independent verification pass. Private output files are
under `outputs/refined_measurement_preparation_v1`; scripts refuse existing
versioned output/verification destinations. The independent verification binds
the preparation files, scripts and original labelled-history metadata. Prior
artifacts are unchanged. No original-source image bytes, model forwards, fits,
downloads, runtime changes, contacts, uploads, commit or push. Final eight groups /
24 photos and older locked allocations remain byte-unread. Script 665 and closed
experiments were not rerun.
