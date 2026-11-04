# SCIN image download guide (Google Cloud Storage)

`scripts/11c_download_scin_candidates.py` downloads **only** the SCIN images
listed in `data/manifests/scin_candidate_selection.csv` (the 184 rows chosen by
`scripts/11b_select_scin_subset.py`) from the official public Google Cloud
Storage bucket. It never downloads the full SCIN dataset, an archive, or the
entire bucket.

## Where the images live

- Bucket: `dx-scin-public-data`
- Object-path format: `dataset/images/<filename>.png`
- Full object URI:
  `gs://dx-scin-public-data/dataset/images/<filename>.png`

Each image is fetched with:

```powershell
gcloud storage cp gs://dx-scin-public-data/<image_path> <local_path>
```

`--recursive` is never used, so only the listed objects are copied.

## Path normalization

The script normalizes each `image_path` before building the URI:

- If `image_path` already begins with `dataset/images/`, it is preserved.
- Otherwise the file name is taken and placed under `dataset/images/`; a
  missing extension becomes `.png`.

Examples:

| `image_path` in the CSV | object path used |
| --- | --- |
| `dataset/images/4716341186591937478.png` | `dataset/images/4716341186591937478.png` |
| `4716341186591937478.png` | `dataset/images/4716341186591937478.png` |
| `4716341186591937478` | `dataset/images/4716341186591937478.png` |

## Prerequisites

Install the Google Cloud SDK so `gcloud` is on PATH. The bucket is public, so
no authentication is required.

## Outputs

- Images: `data/raw/scin/selected_candidates/`
- Log: `data/manifests/scin_download_log.csv`

The log has one row per candidate: `image_id`, `case_id`, `image_path`,
`source_mst_label`, `source_broad_mst_group`, `local_path`, `remote_url`
(the `gs://` URI), `download_status` (`downloaded` / `skipped` / `failed`),
`error_message`, `file_size_bytes`.

Each download is validated with OpenCV before it is moved into place, so a
corrupt or failed download never leaves a usable-looking file behind. Files
that already exist and load correctly are reported as `skipped`.

## Build the candidate list first

```powershell
python scripts/11b_select_scin_subset.py
```

## 1. Dry run (no gcloud call, no files written)

```powershell
python scripts/11c_download_scin_candidates.py --dry-run
```

Prints the first 5 `image_path` values and the planned `gs://` URI and local
destination for every candidate, then exits.

## 2. One-image test (always do this first)

```powershell
python scripts/11c_download_scin_candidates.py --limit 1 --yes
```

In `--limit 1` mode, if the object fails the script prints the full `gs://` URI
it attempted and stops, so a wrong path or bucket is caught after one request.

## 3. Full selected-subset download (184 images)

```powershell
python scripts/11c_download_scin_candidates.py --yes
```

Without `--yes`, the script asks:

```
Download 184 selected SCIN images to data/raw/scin/selected_candidates/? [y/N]
```

An empty answer means no. Re-running the command is safe: already-downloaded
files are skipped.

## Options

| Option | Meaning |
| --- | --- |
| `--bucket-name` | GCS bucket (default `dx-scin-public-data`) |
| `--candidates` | Candidate CSV (default `data/manifests/scin_candidate_selection.csv`) |
| `--output-dir` | Where images are saved (default `data/raw/scin/selected_candidates/`) |
| `--log` | Log CSV (default `data/manifests/scin_download_log.csv`) |
| `--limit` | Only process the first N candidates (0 = all) |
| `--timeout` | Per-command timeout in seconds (default 120) |
| `--dry-run` | Print the plan and exit; no gcloud call |
| `--yes` | Skip the confirmation prompt |

## Notes

- Only files present in the candidate CSV are ever requested; the bucket is
  never listed or copied recursively.
- This step does not run the TrueHue pipeline, does not train a model, and does
  not modify Skin Mask V2, ITA, FairFace, or MST-E code.
- The candidate `source_broad_mst_group` is an official SCIN metadata grouping
  used only to balance the training set; it is not a medical or identity label.
