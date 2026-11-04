# Explicit experimental MST pipeline integration

28 October2026. Added a separate runnable Python development path that connects
square256 preprocessing, face detection, the existing measurement mask,
Lab/ITA, experimental mapped MST, saved tree prediction and correction.
The existing four-feature default runner and active model are unchanged.

`src/correction/development_mst_pipeline.py` accepts explicit injected detector,
masker, lookup and portable tree dependencies. It checks the lookup measurement
contract, exact five- or nine-feature order and gamma/red/blue target schema.
It computes MST from actual input ITA, and chroma-distribution features only for
the nine-feature schema. No reference or fitted recovery target is accepted by
the inference API. Application uses the unchanged measurement support.

`scripts/180_run_development_mst_pipeline.py` requires explicit experiment and
fold arguments. Supported local experiments are `baseline5`, `chroma9` and
`clean-leaf`; none is a release model. The command checks saved summary and
lookup hashes, measurement contract and feature schema, and records artifact
hashes, fold identity, initialization time and input provenance. It refuses
existing output directories. It does not download assets or change defaults.

Example from project root, using the held fold for this saved source:

```powershell
.\venv\Scripts\python.exe scripts/180_run_development_mst_pipeline.py `
  --image outputs/table2_source_expansion24_v1/images/53109_input.png `
  --experiment baseline5 --fold-id 1 `
  --output-dir outputs/development_mst_example_new_run
```

The fold in this example is fixed by the saved evaluation plan, not selected
for favorable output. Running another image through an explicitly chosen fold
is a development demonstration, not held-out evaluation or a fitted final model.
Do not choose folds by viewing corrected images. The runner does not claim that
the experimental lookup is validated merely because an MST value is available.

Outputs are `report.json`, `square_input.png`, `measurement_mask.png` and, on
successful software execution, `corrected.png`. Reports explicitly retain
`experimental=true`, `proposal_complete=false` and `quality_gate_passed=false`.
Measurement failures retain their actual stage and stop before lookup/prediction;
no reference-feature or missing-MST fallback. A successfully executed correction
is not a passing model-quality result.

## Replay and checks

Script181freshly processes all20saved held inputs using their exact conservative
fold exports. All20reproduce saved input measurements, mapped MST indices,
9features, parameter vectors, masks and corrected pixels exactly. The previously
failed dark75027probe again fails face detection, returns no corrected image,
no mapped MST and no parameters. Actual CLI execution additionally reproduces
baseline5parameters and corrected pixels for53109medium.

Six new tests exercise both supported feature schemas, square resizing,
actual-input ITA-to-MST flow, protected/outside-mask pixels, input immutability,
detection failure, missing landmarks, contract/schema rejection and invalid
prediction failure. The complete suite passes **701tests in17.50seconds** using
a fresh workspace pytest temp directory and cache disabled.

Observed successful local Python pipeline calls range59.38to617.34ms, median
66.99ms over20sequential cases. These are single observations, without warmup
or repeated benchmarking; initialization is separately recorded. Measurement
timing contains nested detection/masking timings, so stage times overlap and
must not be summed. File decoding/output writing are outside these pipeline
timings. This is neither an Android latency benchmark nor a phone feasibility
claim. Do not compare against device timing as equivalent measurements.

The integration establishes software consistency only. The candidate's strict
clean gate still fails; clean75027remains severely overcorrected. The nested
selection experiment's lack of correction benefit also remains. Photographic
reference, clipping, weak MST, missing dark-group and unverified person-separation
limitations remain. No final evaluation, neck support, MOS or Android correction
completion is implied. Android stays paused; CPM deferred.

- [All replay checks and timing records](../outputs/development_mst_pipeline_replay_v1/verification.json)
- [Example actual CLI report](../outputs/development_mst_cli_baseline5_v1/report.json)
- [Example actual CLI image](../outputs/development_mst_cli_baseline5_v1/corrected.png)
