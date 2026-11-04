# Unified core pipeline: software check complete, quality limitations retained

27 October2026. Added an input-only stage-by-stage runner around the existing
facial-mask/ITA/decision-tree components. **37outputs, one retained measurement
failure,537passing tests.** MST is explicitly unavailable; this remains a
partial development pipeline rather than the completed proposed method.

[Comparison gallery](../outputs/core_pipeline_check_v1/review.html) ·
[Per-case metrics](../outputs/core_pipeline_check_v1/metrics.csv) ·
[Software/quality status](../outputs/core_pipeline_check_v1/readiness.json) ·
[Replay verification](../outputs/core_pipeline_check_v1/verification.json).

## What changed

`src/correction/core_pipeline.py` records separate input, detection, masking,
measurement, MST and correction stages. It takes only the input image and
frozen dependencies; no clean image, inverse target or reference mask enters
prediction. The CLI loads the verified portable JSON tree and local detector/
landmark models, requiring their existing files without network downloads.

The policies remain YuNet0.85, HSV/YCrCb `v2_complete_mouth_v1`, four continuous
Lab/ITA measurements and `estimation_mask_v1` correction support. No semantic
parser, learned material model, CPM or mask expansion is introduced. Failed
geometry, unavailable landmarks, invalid/insufficient masks and invalid model
output are explicit failures. The landmark helper's fallback is not accepted.

On a successful development correction, `report.json` includes:

- Each stage's status and elapsed desktop time.
- Exact measured Lab/ITA features and predicted gamma/red/blue parameters.
- Model/input hashes, face bounds, mask version and threshold.
- `mst.status="unavailable"`, null category/index and the missing-lookup reason.
- `status="development_partial_mst_unavailable"` and `proposal_complete=false`.

Correction can run because this frozen prototype consumes continuous Lab/ITA,
not an MST category. That is an existing proposal difference, explicitly
reported rather than hidden with a guessed category. No operational mapping
was created or calibrated.

The new CLI is a separate development entry point. Existing script39and its
runtime/model/mask policies remain unchanged; no automatic final-model adoption.

## Run one image

From the project root:

```text
venv/Scripts/python.exe scripts/116_run_core_pipeline.py --image path/to/photo.jpg --output-dir outputs/my_core_run
```

An available result writes corrected image, estimation/application masks,
comparison and report. A processing failure writes stage details in both
report/failure JSON and exits2without a corrected image. An existing output
directory is refused. Initialization/I/O errors produce failure JSON. The
original file is unchanged. CLI success means development output availability,
not complete proposal execution or demonstrated image improvement.

## Frozen38-attempt check

The [protocol](core-pipeline-check-protocol.md) preceded execution. Used all
existing controlled-training-v2 attempts:30training diagnostics across seven
sources,3development probes from one source,4clipped-stress probes and the
original excluded attempt. Confirmed every source's recorded prior exposure,
partition and duplicate group before reading any image. No reserved/new source
was opened and no row was trained, promoted or reassigned.

All37 previously available cases produced outputs; all feature vectors match
saved measurements within0.00005. Original22454color-shift still fails at
measurement because too few skin pixels remain; no features, MST or corrected
output are invented. Existing eligibility remains unchanged.

The portable tree matches original sklearn predictions on all37recomputed
feature vectors. Every pixel outside the correction mask is unchanged. The
legacy estimation and correction masks match by design. These checks establish
software consistency, not mask accuracy or reference suitability.

## No-correction comparison

Mean CIEDE2000 on the same historical source-generation region, lower is better:

| Existing subset | Pairs | No correction | Frozen tree | Worsened pairs |
| --- | ---: | ---: | ---: | ---: |
| Training-source diagnostics, all variants | 30 | 6.125 | 6.488 | 13 |
| Unchanged controls, part of the30 | 7 | 0.000 | 7.429 | 7 |
| Mild controls, part of the30 | 7 | 2.746 | 7.491 | 4 |
| Development validation | 3 | 10.666 | 7.609 | 0 |
| Clipped stress | 4 | 7.227 | 13.916 | 3 |

Rows overlap as labeled; do not sum the controls with the30. Sixteen of the30
were the original model's training rows;14unchanged/mild additions were not in
that fit. Training-source diagnostics are not held-out generalization evidence.
The three development examples are variants of one source; clipped stress is
not independent and contains irreversible transforms.

The30pair-weighted mean error change is+0.362; the source-balanced change is
+0.742because source variant counts differ. Both are saved with per-variant
counts. Unchanged here means no synthetic edit, not a claim that the original
photo has perfect exposure. Worsening is relative reconstruction against that
same ordinary source photo, not a calibrated true-complexion judgment.

All eight source boards were visually inspected, covering37outputs and the
failed attempt. Dark examples often improve reconstruction, but mask holes,
hard patch boundaries and missed correction support remain. Unchanged/mild
examples22454/51739/6236show clear overcorrection; bright clipped stress can also
overcorrect. Observations are technical review, not expert MOS or new human
acceptance. No parameters or masks were adjusted after viewing results.

## Verification and remaining work

Scripts117–119retain all attempts, independently recompute saved-mask Lab/ITA,
original-model predictions, encoded-RGB transforms and reconstruction metrics,
and package the gallery/CSVs. Real CLI checks reproduce a successful unchanged
case(exit0with MST unavailable) and the retained failure(exit2). All tracked
input/source/model/reference/review/ledger hashes remain unchanged. Replay is
conditional on saved masks; it does not supply segmentation ground truth.
Final artifact/link checks pass. **537tests passed in8.62s**, including18new
orchestration tests for absent MST, invalid inputs/geometry/masks, landmark
fallback rejection, insufficient measurements and correction failure isolation.

The core software now has one auditable path through its implemented stages.
The next model-quality task is the existing control-aware, source-grouped
correction evaluation/training-design work; do not bypass the unchanged/mild
harm with an arbitrary strength cutoff or silently fit held/stress data.
Operational MST is a separate unresolved paper requirement and must retain its
measured mapping limitations. These are core-method issues; CPM stays deferred.

No final learner is adopted, no training pairs regenerated and no new correction
model fitted. Paint/makeup protection remains a limitation. Original source
holds, labels/reviews and folds remain; the requested face/visible-neck support
is still pending. Android, final data/reference/splits/evaluation and expert MOS
remain unfinished. Desktop stage times do not establish phone latency.
