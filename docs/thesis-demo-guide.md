# Reproduce the current development demonstration

29 October 2026: a simple desktop demo is now available. Double-click
`run_truehue_demo.cmd` in the project root, or follow
[the short instructions](simple-python-demo.md). It runs the fixed experimental
ITA/MST/five-feature tree with clear trial-model labeling and failure handling.
[Implementation and verification](python-desktop-demo-results.md).

The commands below describe the earlier four-feature command-line demonstrator
and historical checkpoint; they are preserved for reproducibility.

28 October 2026. Run commands from the project root. No downloads or training
are required. The existing Python environment and local models must be present.

Open `outputs/thesis_checkpoint_v1/index.html` for a single offline overview.
It contains no dataset images. Copy that file and `checkpoint.json` together
for a portable results checkpoint. This is saved development evidence; the
report builder verifies summary hashes but does not rerun the full pipeline.

Build a fresh checkpoint directory:

```powershell
.\venv\Scripts\python.exe scripts/127_build_thesis_checkpoint.py --output-dir outputs/thesis_checkpoint_v2
```

Run the actual frozen core model on an image, using a new output directory:

```powershell
.\venv\Scripts\python.exe scripts/116_run_core_pipeline.py --image path/to/image.jpg --output-dir outputs/demo_case_v1
```

The per-case output includes `report.json`, corrected image, masks and a comparison
when processing succeeds. Failure retains a stage/reason; do not hide it or
replace its measurement. Exit0 denotes a development output with unavailable
MST, not a completed proposal pipeline; exit2 denotes a pipeline failure.
Initialization/I/O exceptions can use another nonzero exit code.

For existing fixed evidence, consult:

- `outputs/core_pipeline_check_v1/review.html`: all38attempts,37outputs and1failure.
- `outputs/core_control_comparison_v1/review.html`: fixed source-held-out comparison.
- `outputs/core_feature_conflict_v1/review.html`: failed-control diagnostic.
- `outputs/core_source_readiness_v1/sources.csv`:114source readiness records.

These detailed galleries use local images and are not standalone distribution
bundles. Do not distribute raw datasets with the checkpoint.

The current model can harm unchanged images; it is a development baseline.
The MST field remains null because a mapping has not been validated. Face/neck,
final dataset/split/reference requirements, expert MOS and Android are unfinished.
Paint/makeup protection remains a limitation; CPM work is deferred.

The latest full Python suite recorded555passing tests during the preceding
diagnostic. This report-packaging change was checked by actual execution,
summary/hash verification and script compilation; it changes no runtime code.
# Current reporting checkpoint — 30 October 2026

The demo still runs the older ten-source `baseline5`,fold1 failed-gate model,
not the retained endpoint research reference or either rejected successor.
The visible notice identifies that status. Saved folders now include stable
run identity, captured model provenance and a file-checksum `manifest.json`.
See [reporting update](demo-reporting-update-2026-10-30.md). These reporting
changes do not validate correction quality or switch the model.

