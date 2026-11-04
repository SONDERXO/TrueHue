# FairFace subset selection guide

`scripts/12_select_fairface_candidates.py` builds a small, reproducible,
**metadata-first** FairFace candidate pool so the full dataset does not have to
be processed.

## What it does

1. Reads the FairFace train and validation metadata CSVs.
2. Validates that each listed image actually exists on disk (missing images are
   skipped and counted).
3. Builds one candidate pool (seed **42** by default).
4. Selects **650** candidates by default (`--limit`), or **20** with
   `--smoke-test`.
5. Stratifies across the FairFace race, gender, and age columns so the sample
   spans visually diverse source images.

## What it deliberately does not do

- It does **not** infer official MST categories from FairFace race.
- It does **not** label FairFace rows as official light / medium / dark groups.
- It does **not** use MST-E images.
- It does **not** modify YuNet, Skin Mask V2, or ITA code.
- It does **not** generate distortions or train a model.

FairFace race/gender/age are used **only** for source-image diversity, and they
are recorded under neutral names: `source_race_label`, `source_gender_label`,
`source_age_label`.

## Where broad-group balancing happens

Broad-group balancing does **not** happen here and never happens through race
labels. It happens **only after** the FairFace candidates have gone through
Skin Mask V2 and continuous ITA processing. Until then every row is marked:

| Column | Value |
| --- | --- |
| `source_mst_label` | *(blank)* |
| `source_broad_mst_group` | *(blank)* |
| `estimated_broad_ita_group` | `pending_ita_processing` |
| `group_assignment_source` | `not_available_until_ita` |
| `intended_use` | `training_candidate` |
| `dataset_name` | `FairFace` |

## Inputs and output

Inputs:

```
data/raw/fairface/
data/raw/fairface/fairface_label_train.csv
data/raw/fairface/fairface_label_val.csv
```

Output:

```
data/manifests/fairface_candidate_selection.csv
```

Columns: `dataset_name`, `image_id`, `image_path`, `source_split`,
`source_race_label`, `source_gender_label`, `source_age_label`,
`source_mst_label`, `source_broad_mst_group`, `estimated_broad_ita_group`,
`group_assignment_source`, `selection_seed`, `selection_reason`,
`intended_use`. `source_split` preserves the original `train` / `validation`
split.

## Commands

```powershell
# Default: 650 candidates, seed 42
python scripts/12_select_fairface_candidates.py

# Smoke test: only 20 candidates
python scripts/12_select_fairface_candidates.py --smoke-test

# Custom size and seed
python scripts/12_select_fairface_candidates.py --limit 650 --seed 42

# Non-default folder layout
python scripts/12_select_fairface_candidates.py `
    --image-root path/to/fairface `
    --train-csv path/to/fairface_label_train.csv `
    --val-csv path/to/fairface_label_val.csv
```

## Notes

- Selection is reproducible: the same seed always yields the same candidates.
- The script prints counts by split, race, gender, and age for the selected set.
- `image_id` follows the project convention `fairface__<relative_path>`, so the
  same image keeps the same ID wherever the dataset lives.
- The next pipeline step runs Skin Mask V2 and continuous ITA on this candidate
  pool; only then can broad-group balancing be decided.
