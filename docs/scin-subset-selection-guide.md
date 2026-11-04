# SCIN subset selection guide

This guide explains `scripts/11b_select_scin_subset.py`, which selects a small,
reproducible subset of **SCIN metadata rows** for the next TrueHue training-data
step.

## What this step does — and does not do

- It reads **only** the official SCIN metadata CSVs from
  `data/raw/scin/metadata/`:
  - the cases CSV (contains `case_id` and `image_1_path`, `image_2_path`,
    `image_3_path`)
  - the labels CSV (contains the official estimated Monk Skin Tone columns)
- It writes **only** a selection manifest.
- It does **not download any images.**
- It does **not download the full SCIN dataset.**
- It does **not** run YuNet, Skin Mask V2, CIELAB/ITA, MST-E, Android, synthetic
  distortions, or any model code. Those parts of the pipeline are untouched.

Filenames may be prefixed with `dataset_`. The script auto-detects the files by
name (`case` for cases, `label` for labels, excluding `question`). If detection
is ambiguous it stops and prints the candidate filenames.

## How the subset is chosen

1. Each case is expanded into **one row per available image path**.
2. Rows without a valid official eMST label are removed. Only integer labels
   **1–10** are kept.
3. Labels are grouped broadly:
   - `light`  = eMST 1–3
   - `medium` = eMST 4–7
   - `dark`   = eMST 8–10
4. Sampling is reproducible with a fixed **seed (default 42)**.
5. **One image per case is preferred.** Multiple images from the same case are
   only taken when a broad group does not have enough unique cases. Every row
   records this in `multiple_images_from_same_case` (True/False).

The official eMST field is an official SCIN metadata field, but it is used here
**only as a broad training-group source**. It is **not** a medical label and
**not** an identity label.

## Why only 225 candidates?

The default request is **75 rows per broad group**, i.e. **225 rows total**.
The point of this stage is to test the selection logic and the download path
with a small, balanced sample before spending time and bandwidth on the full
dataset. `--per-group` changes this (e.g. `--per-group 50`).

Groups that cannot supply the requested count are handled gracefully: the
script selects everything available for that group and prints a warning. In the
current official metadata the `dark` group has far fewer cases than `light` and
`medium`, so it is expected to under-fill.

## Output

The selection is saved to:

```
data/manifests/scin_candidate_selection.csv
```

Columns:

| Column | Meaning |
| --- | --- |
| `dataset_name` | Always `SCIN` |
| `image_id` | Stable id: `scin__<case_id>__<image_slot>` |
| `case_id` | SCIN case identifier |
| `image_slot` | 1, 2, or 3 |
| `image_path` | Path stored in the SCIN metadata (`dataset/images/...`) |
| `source_mst_label` | Official eMST 1–10 |
| `source_broad_mst_group` | `light` / `medium` / `dark` |
| `group_assignment_source` | `official_scin_emst_india`, or `official_scin_emst_us` if the India label was absent |
| `selection_seed` | Seed used (default 42) |
| `selection_reason` | `one_image_per_case` or `additional_image_from_same_case_shortfall` |
| `multiple_images_from_same_case` | `True`/`False` |
| `intended_use` | Always `training_candidate` |

## Run it

From the project root:

```powershell
python scripts/11b_select_scin_subset.py
python scripts/11b_select_scin_subset.py --per-group 75 --seed 42
python scripts/11b_select_scin_subset.py --per-group 50 --seed 7
```

## Next step

The next step is to **test-download only three selected image files** from this
manifest. Downloading a few files first verifies that the metadata paths,
access endpoints, and local folder layout are correct before fetching a larger
set. Images are intentionally not fetched by this script.
