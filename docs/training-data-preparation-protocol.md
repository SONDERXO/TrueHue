# Training Data Preparation Protocol (FairFace + SCIN)

## Purpose

The correction model is a decision-tree regression of (gamma, red gain, blue
gain). Before it can be trained, the two training datasets — **FairFace** and
**SCIN** — must be run through the *same frozen pipeline* used for the MST-E
calibration work and recorded in a reproducible, auditable manifest.

`scripts/11_prepare_training_manifests.py` does exactly that. For every
FairFace and SCIN image it runs:

```
YuNet face detection (single face only)
  -> largest-face BGR crop
  -> Skin Mask V2 (HSV/YCrCb + morphology + largest component
     + landmark eye/eyebrow/lip exclusion)
  -> CIELAB conversion of the selected skin pixels only
  -> mean L*, a*, b* and ITA (degrees)
```

Nothing is trained here. No threshold table is derived. No raw image is copied,
resized, re-encoded, or edited. No synthetic distortion is applied (that is a
later milestone).

## Dataset roles (fixed)

| Dataset  | Role              | Rule                                                |
| -------- | ----------------- | --------------------------------------------------- |
| FairFace | training source   | may be used to train the correction model           |
| SCIN     | training source   | may be used to train the correction model           |
| MST-E    | evaluation only   | must **never** appear in a training manifest        |

MST-E is rejected in code: `validate_training_dataset_names()` raises if an
MST-E name reaches a training manifest, and
`load_inventory_manifest()` refuses a manifest that marks MST-E for training.

### Licensing reminder

FairFace and SCIN are third-party datasets with their own licences and terms of
use. Raw images are **external** to this repository and must never be committed,
uploaded, or redistributed from it. This pipeline reads the datasets in place
and only ever writes derived metadata manifests. Check each dataset's licence
before any redistribution or publication of derived data.

## Inputs

Built by `scripts/04_build_dataset_inventory.py`:

```
data/manifests/fairface_inventory.csv
data/manifests/scin_inventory.csv
```

Optional, for official SCIN labels:

```
data/raw/scin/scin_metadata.csv      # official SCIN MST metadata
```

Optional, for FairFace estimated groups: a documented ITA-to-broad-group rule
JSON passed with `--estimated-group-rule` (see below). The rule is supplied
externally; it is never derived by this pipeline.

## Exclusions

For the current FairFace 650-candidate pool, automated `success` means only
that computation completed. Before downstream candidate selection, apply the
separate [FairFace mask-screening procedure](mask-quality-review.md#fairface-candidate-screening-procedure-2026-10-19).
Keep visual decisions separate from `processing_status` and `exclusion_reason`.
The current manifest-generation scripts do not enforce this manual review
gate; their success-only candidate outputs are not visually validated or
automatically training-ready. SCIN processing remains paused per the
2026-10-15 decision log entry.

An image is excluded (recorded, never silently dropped) when **any** of the
following holds. Checks run in this fixed order, so every image gets exactly one
stable reason:

| Order | `exclusion_reason`                                  | Meaning                                                        |
| ----- | --------------------------------------------------- | -------------------------------------------------------------- |
| 1     | `corrupt_or_unreadable_image`                        | OpenCV could not read the file                                 |
| 2     | `no_face_detected`                                   | YuNet found no face                                            |
| 3     | `multiple_faces_detected`                            | more than one face; the app supports a single face             |
| 4     | `skin_mask_unavailable`                              | the skin mask could not be created                             |
| 5     | `skin_mask_v1_fallback_landmarks_unavailable`        | Skin Mask V2 feature exclusion failed -> V1 fallback not allowed |
| 6     | `insufficient_skin_pixels`                           | fewer than `--min-skin-pixels` (default 1000) valid skin pixels |
| 7     | `ita_estimation_failed`                              | ITA could not be computed from the selected skin               |

The V1 fallback is **never** kept: a single manifest must not mix mask versions.
The detector, Skin Mask V2, CIELAB conversion, and the ITA formula are frozen and
must not be modified to "rescue" an image.

## Group assignment (official vs estimated)

`group_assignment_source` records exactly where a row's broad group came from:

- `official_scin_mst` — SCIN rows with an official MST label from
  `--scin-metadata`. The label is ground truth and is mapped to its documented
  broad group. The wide, overlapping ten-level label set is deliberately pooled:

  | broad group | MST labels |
  | ----------- | ---------- |
  | `light`     | 1, 2, 3    |
  | `medium`    | 4, 5, 6, 7 |
  | `dark`      | 8, 9, 10   |

- `estimated_from_ita` — a broad group **estimated** from ITA using a
  documented, externally supplied rule. This is used for FairFace, which has no
  official MST label. An estimate is not ground truth and is stored in a
  separate column (`estimated_broad_mst_group`), never in
  `source_broad_mst_group`.

- `none` — no group could be assigned.

Official labels always win over estimates, and the two are never mixed. ITA
remains a **continuous** feature; no ten-level ITA-to-MST threshold table is
created anywhere in this pipeline.

### The estimated-group rule file

An estimate is only ever produced when a human supplies a documented rule. The
JSON format is half-open intervals `[min_ita, max_ita)` (`null` = unbounded):

```json
{
  "name": "documented_broad_group_rule_v1",
  "source": "docs/training-data-preparation-protocol.md",
  "notes": "Example only. Replace with a rule you can defend and cite.",
  "intervals": [
    { "broad_group": "dark",   "min_ita": null,  "max_ita": -30.0 },
    { "broad_group": "medium", "min_ita": -30.0, "max_ita": 10.0  },
    { "broad_group": "light",  "min_ita": 10.0,  "max_ita": null  }
  ]
}
```

The loader validates that intervals do not overlap, that each broad group appears
at most once, and that `min_ita < max_ita`. The example values above are
**illustrative only** — do not treat them as validation-derived thresholds.

## Outputs

Written to `data/manifests/` by default:

| File                                  | Contents                                              |
| ------------------------------------- | ----------------------------------------------------- |
| `fairface_processed_manifest.csv`     | every processed FairFace image (usable + excluded)    |
| `scin_processed_manifest.csv`         | every processed SCIN image (usable + excluded)        |
| `training_candidates_manifest.csv`    | clean, excluded-free, optionally capped training subset |
| `training_data_preparation_summary.csv` | run summary counts (see below)                      |

### Manifest columns

```
dataset_name, image_id, image_path, source_label, source_mst_label,
source_broad_mst_group, estimated_broad_mst_group, group_assignment_source,
face_detected, landmarks_available, skin_pixels, skin_ratio_percent,
mean_l_star, mean_a_star, mean_b_star, ita_degrees, processing_status,
exclusion_reason, intended_use
```

- `source_label` is the dataset's own raw label text (for SCIN, the official MST
  value as written); `source_mst_label` is the normalised integer 1-10, empty for
  FairFace.
- `processing_status` is `success` or `excluded`.
- `intended_use` is `training` for both datasets.

### Training candidates and stratified cap

`training_candidates_manifest.csv` contains only rows with
`processing_status = success`, drawn from both datasets. `--cap-per-group N`
keeps at most `N` rows per **dataset and** broad group (official group if
present, else estimate, else `unassigned`), so a large dataset cannot dominate
and each dataset keeps its own balance. Selection is deterministic: rows are
ordered by `dataset_name` and `image_id` before the cap, and the output is
ordered by `dataset_name`, broad group (`light`, `medium`, `dark`, then
`unassigned`), and `image_id`.

## Summary counts

`training_data_preparation_summary.csv` holds, with a leading `section` column:

- `processed_by_status` — rows per dataset and `processing_status`
- `processed_by_exclusion` — excluded rows per dataset and `exclusion_reason`
- `processed_by_group` — rows per dataset, `group_assignment_source`, broad group
- `candidates_by_dataset` — candidate rows per dataset
- `candidates_by_group` — candidate rows per dataset and broad group

## Running

From the project root (the frozen models must already exist locally — this
script never downloads anything):

```powershell
python scripts/11_prepare_training_manifests.py
python scripts/11_prepare_training_manifests.py --limit 20
python scripts/11_prepare_training_manifests.py --cap-per-group 500
python scripts/11_prepare_training_manifests.py --estimated-group-rule rule.json
```

Verification: `pytest tests/test_training_manifest.py -v` (pure, synthetic data;
no real images or models required).

## What this protocol deliberately does not do

- It does not map ITA onto ten MST categories or create a threshold table.
- It does not apply synthetic distortions (a later milestone).
- It does not train, load, or evaluate any correction model.
- It does not process or include MST-E in any form.
- It does not modify face detection, Skin Mask V2, CIELAB conversion, or ITA.
- It does not modify, copy, or re-encode any raw image.
