"""
04_build_dataset_inventory.py

Purpose:
    Build the local dataset inventory (manifest CSVs) for the three datasets
    used in this thesis. Each manifest lists every image below a dataset folder
    together with its stable image ID, the ground-truth MST label when that
    label is officially documented, the role the dataset may play, and the
    mask-quality review state.

    This script is READ-ONLY with respect to the raw data: it lists file names
    and reads at most the dataset's own metadata CSV. It never copies, edits,
    resizes, re-encodes, or deletes an image.

Outputs (written to data/manifests/ by default):
    fairface_inventory.csv    intended_use = training
    scin_inventory.csv        intended_use = training
    mst_e_inventory.csv       intended_use = evaluation_only

Dataset roles (fixed for this thesis):
    FairFace  -> training source
    SCIN      -> training source
    MST-E     -> evaluation/calibration ONLY. It must never enter a
                 model-training, validation, or test split. The inventory
                 records this in the intended_use column, and
                 src.data_preparation.dataset_inventory.load_inventory_manifest
                 refuses a manifest that marks MST-E for training.

Where to place the datasets locally (defaults, override with the flags below):
    data/raw/fairface/        extracted FairFace images
    data/raw/scin/            extracted SCIN images
    data/raw/mst-e_data/      extracted MST-E images, including the official
                              mst-e_image_details.csv (ground-truth MST labels)

Run from the project root:
    python scripts/04_build_dataset_inventory.py
    python scripts/04_build_dataset_inventory.py --only mst_e
    python scripts/04_build_dataset_inventory.py --strict

No network access is performed: download the datasets yourself and point the
scripts at the local folders.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation.dataset_inventory import (
    FAIRFACE_DATASET_NAME,
    INTENDED_USE_EVALUATION_ONLY,
    INTENDED_USE_TRAINING,
    MST_E_DATASET_NAME,
    MST_E_DETAIL_COLUMNS,
    SCIN_DATASET_NAME,
    build_inventory,
    load_label_metadata,
    summarize_inventory,
)


# -------------------------------------------------------------------
# Local dataset layout
# -------------------------------------------------------------------

DEFAULT_FAIRFACE_ROOT = PROJECT_ROOT / "data" / "raw" / "fairface"
DEFAULT_SCIN_ROOT = PROJECT_ROOT / "data" / "raw" / "scin"
DEFAULT_MST_E_ROOT = PROJECT_ROOT / "data" / "raw" / "mst-e_data"
DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"

#: Official MST-E metadata: ``image_ID, pose, lighting, mask, subject_name, MST``.
DEFAULT_MST_E_METADATA = (
    DEFAULT_MST_E_ROOT / "mst-e_image_details.csv"
)

MANIFEST_FILENAMES = {
    "fairface": "fairface_inventory.csv",
    "scin": "scin_inventory.csv",
    "mst_e": "mst_e_inventory.csv",
}

DATASET_CHOICES = ("fairface", "scin", "mst_e")


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Build metadata-only dataset inventory CSVs. Raw images are only "
            "listed, never modified."
        )
    )
    parser.add_argument(
        "--fairface-root",
        type=Path,
        default=DEFAULT_FAIRFACE_ROOT,
        help=f"FairFace image folder (default: {DEFAULT_FAIRFACE_ROOT})",
    )
    parser.add_argument(
        "--scin-root",
        type=Path,
        default=DEFAULT_SCIN_ROOT,
        help=f"SCIN image folder (default: {DEFAULT_SCIN_ROOT})",
    )
    parser.add_argument(
        "--mst-e-root",
        type=Path,
        default=DEFAULT_MST_E_ROOT,
        help=f"MST-E image folder (default: {DEFAULT_MST_E_ROOT})",
    )
    parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=DEFAULT_MANIFEST_DIR,
        help=(
            "Where the inventory CSVs are written "
            f"(default: {DEFAULT_MANIFEST_DIR})"
        ),
    )
    parser.add_argument(
        "--mst-e-metadata",
        type=Path,
        default=DEFAULT_MST_E_METADATA,
        help=(
            "Official MST-E metadata CSV holding the ground-truth MST label. "
            "Pass an empty string to read labels from folder names only "
            f"(default: {DEFAULT_MST_E_METADATA})"
        ),
    )
    parser.add_argument(
        "--only",
        choices=DATASET_CHOICES,
        action="append",
        default=None,
        help=(
            "Build only the named dataset (repeatable: --only fairface "
            "--only mst_e). Default: build all three."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with an error if a requested dataset folder is missing.",
    )
    return parser.parse_args()


def load_mst_e_metadata(metadata_path: Path | None) -> object | None:
    """Load the official MST-E label mapping, if the CSV is available.

    Parameters
    ----------
    metadata_path : Path | None
        Path to ``mst-e_image_details.csv``, or ``None``/empty to rely on
        label folder names only.

    Returns
    -------
    LabelMetadata | None
        The parsed mapping, or ``None`` when no CSV was supplied.
    """
    if metadata_path is None or str(metadata_path).strip() == "":
        print("MST-E metadata: not supplied, labels come from folder names")
        return None

    if not Path(metadata_path).is_file():
        print(
            f"MST-E metadata file not found: {metadata_path}\n"
            "  Labels will come from folder names only, so images inside "
            "'subject_*' folders will have no label."
        )
        return None

    metadata = load_label_metadata(
        metadata_path,
        key_column="image_ID",
        label_column="MST",
        dataset_name=MST_E_DATASET_NAME,
        detail_columns=MST_E_DETAIL_COLUMNS,
    )
    print(
        f"MST-E metadata: {metadata_path.name} "
        f"({len(metadata.labels)} keys including image-ID forms)"
    )
    return metadata


def build_one_dataset(
    dataset_name: str,
    dataset_root: Path,
    intended_use: str,
    manifest_path: Path,
    metadata: object | None = None,
) -> pd.DataFrame | None:
    """Build and write one dataset inventory CSV.

    Parameters
    ----------
    dataset_name : str
        Name written into the ``dataset_name`` column.
    dataset_root : Path
        Folder scanned recursively for images.
    intended_use : str
        ``training`` or ``evaluation_only``.
    manifest_path : Path
        Destination CSV.
    metadata : LabelMetadata | None
        Optional official label mapping.

    Returns
    -------
    pd.DataFrame | None
        The written inventory, or ``None`` when the dataset folder is missing.
    """
    print("-" * 65)
    print(f"Dataset        : {dataset_name}")
    print(f"Folder         : {dataset_root}")
    print(f"Intended use   : {intended_use}")

    if not dataset_root.exists():
        print(
            f"  SKIPPED: folder not found. Extract {dataset_name} into this "
            "location, or pass the correct path with the matching --*-root "
            "flag."
        )
        return None
    if not dataset_root.is_dir():
        print(f"  SKIPPED: {dataset_root} is not a folder.")
        return None

    frame = build_inventory(
        dataset_name=dataset_name,
        dataset_root=dataset_root,
        intended_use=intended_use,
        metadata=metadata,
    )

    if frame.empty:
        print("  WARNING: no .jpg, .jpeg, or .png images found in this folder.")

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(manifest_path, index=False)

    summary = summarize_inventory(frame)
    print(f"Images found   : {summary['images']}")
    print(f"Labelled       : {summary['labelled']}")
    print(f"Unlabelled     : {summary['unlabelled']}")
    print(f"Flagged rows   : {summary['flagged']}")
    print(f"Manifest       : {manifest_path}")

    if int(summary["flagged"]) > 0:
        print(
            "  NOTE: flagged rows have no documented MST label. They stay in "
            "the manifest with exclusion_reason set; resolve the label from "
            "official metadata before using them."
        )

    if dataset_name == MST_E_DATASET_NAME:
        print(
            "  NOTE: MST-E is evaluation/calibration only and must not be "
            "used to train the correction model."
        )

    return frame


def main() -> None:
    """Build every requested dataset inventory and print a summary."""
    args = parse_arguments()

    requested = args.only or list(DATASET_CHOICES)
    manifest_dir: Path = args.manifest_dir

    mst_e_metadata = load_mst_e_metadata(args.mst_e_metadata)

    plans = [
        (
            "fairface",
            FAIRFACE_DATASET_NAME,
            args.fairface_root,
            INTENDED_USE_TRAINING,
            manifest_dir / MANIFEST_FILENAMES["fairface"],
            None,
        ),
        (
            "scin",
            SCIN_DATASET_NAME,
            args.scin_root,
            INTENDED_USE_TRAINING,
            manifest_dir / MANIFEST_FILENAMES["scin"],
            None,
        ),
        (
            "mst_e",
            MST_E_DATASET_NAME,
            args.mst_e_root,
            INTENDED_USE_EVALUATION_ONLY,
            manifest_dir / MANIFEST_FILENAMES["mst_e"],
            mst_e_metadata,
        ),
    ]

    print("=" * 65)
    print("Build Dataset Inventory (metadata only, raw images untouched)")
    print("=" * 65)

    built: dict[str, pd.DataFrame] = {}
    missing: list[str] = []

    for key, name, root, use, manifest_path, metadata in plans:
        if key not in requested:
            continue
        frame = build_one_dataset(
            dataset_name=name,
            dataset_root=root,
            intended_use=use,
            manifest_path=manifest_path,
            metadata=metadata,
        )
        if frame is None:
            missing.append(name)
        else:
            built[key] = frame

    print("=" * 65)
    print("Total images found per dataset")
    print("=" * 65)

    for key in requested:
        frame = built.get(key)
        if frame is None:
            print(f"  {key:<9} : not built (folder missing)")
        else:
            summary = summarize_inventory(frame)
            print(f"  {key:<9} : {summary['images']} images")

    if built:
        print()
        print(f"Manifests written to: {manifest_dir}")
        print("Next step: python scripts/05_run_mst_e_ita_calibration.py")

    if missing and args.strict:
        print()
        print(f"ERROR: missing dataset folder(s): {', '.join(missing)}")
        sys.exit(1)

    if not built:
        print()
        print(
            "ERROR: no dataset folder was found. Extract at least one dataset "
            "(see the docstring at the top of this script) and run again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
