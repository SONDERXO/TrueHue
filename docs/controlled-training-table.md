# Controlled training-table build (2026-10-20)

## Run and scope

```text
venv/Scripts/python.exe scripts/25_build_controlled_training_table.py
```

The runner reads the eight selected sources and fixed distortion policy from
`data/manifests/controlled_development_v1/`. It generates the three configured
variants per source, verifies current-mask measurements against the source
manifest, and extracts input features from saved distorted full-frame PNGs.
No model is fitted, no new split is sampled, and no final evaluation is run.
Existing output folders are protected from overwrite. Original source images,
policies, prior review records and manifests are unchanged; hashes are checked
after generation and saved with the build summary.

The same binary source-mask simulation and operator contract as the earlier
pilot apply. Pixels outside the generation mask are checked unchanged. The
comparison images' third column uses known inverse parameters and the fixed
generation mask for display; it is not a learned or deployable correction.

## Outputs and accounting

Tables under `data/manifests/controlled_training_v1/`:

| File | Rows | Meaning |
| --- | ---: | --- |
| all_pairs_audit.csv | 24 | Every attempted variant with targets, source, split, clipping and input status |
| train.csv | 16 | Unclipped, numerically successful inputs from seven training sources |
| development_validation.csv | 3 | Unclipped, successful inputs from one development-validation source |
| clipped_stress.csv | 4 | Successful inputs with irreversible generation clipping; excluded from primary fit |
| excluded_pairs.csv | 1 | Failed input pipeline; no substitute feature vector |

`schema_and_summary.json` records counts, explicit model columns and input,
model and code hashes. All siblings keep their source partition, including
stress and failed rows. Source and duplicate-group separation is checked
before generation. No source identity independence can be claimed from this.

The failure is `fairface__train/22454.jpg`, color_shift:
`insufficient_skin_pixels`. It remains in the audit with the known target and
empty feature vector. Its successful siblings are retained. No replacement
variant or source is sampled to hide failure.

Generated inputs, generation masks and eight three-row comparison sheets are
under `outputs/controlled_training_v1/`. Columns are reference / distorted /
known-parameter correction. All eight sheets (24 variants) were inspected;
binary-mask seams and existing source limitations remain visible.

## Model feature/target contract

Consumers must explicitly select exactly these four features in this order:

```text
input_mean_l_star, input_mean_a_star, input_mean_b_star, input_ita_degrees
```

They are computed from the distorted input's newly inferred mask and face
crop, not the clean reference mask or source statistics. Numerical validity
does not imply that every newly inferred input mask is visually accurate.

Targets, in order:

```text
target_gamma, target_red_gain, target_blue_gain
```

The tables intentionally contain additional provenance columns. Do **not**
train on all numeric columns: distortion parameters would leak the targets;
paths, IDs, partitions, clipping metadata and reference information are also
not model features. No MST category, demographic attribute or invented group
label enters the feature vector. Continuous ITA is retained alongside Lab.

`pair_table_row` validates targets, routes failures/clipping, and rejects
nonfinite/missing successful-input statistics rather than imputing them from
references. Failed rows have all four model features blank. CSVs are written
with headers even if a resulting partition is empty.

## Verification and limitations

389 tests passed. New tests exercise input-only feature selection, no feature
imputation for failed inputs, clipped-stress routing, nonfinite-input handling
and rejection of metadata-supplied model features. Run-level checks verified
24 unique pair IDs, inherited source/group separation, baseline agreement,
outside-mask preservation and unchanged input hashes.

The small baseline/decision-tree development run is complete; see
[correction-prototype-results.md](correction-prototype-results.md). It uses
the explicit feature schema and separate fit/validation tables, reporting
parameter error and image reconstruction separately. Inference
correction must use the mask inferred from the distorted input, and any
fixed-source-mask diagnostic must be labelled as such. Preserve all failed
attempts when reporting reliability.

Sixteen training pairs, three fixed transform settings and one validation
source are only sufficient for an implementation smoke test. This cannot
establish generalization, fairness, real-world color correction or final thesis
performance. No model selection or final test performance is claimed here.
