"""
11b_select_scin_subset.py

Purpose:
    Select a small, reproducible *metadata-only* subset of the official SCIN
    dataset for the next TrueHue training-data step.

    This script reads ONLY the SCIN metadata CSVs (cases + labels) and writes a
    single selection manifest. It never touches images, never downloads the SCIN
    dataset, and never runs the TrueHue pipeline.

What it does
------------
1. Auto-detects the SCIN cases CSV and labels CSV inside
   data/raw/scin/metadata/ (filenames may be prefixed with ``dataset_``).
2. Prints the detected filenames and every column header before processing.
3. Auto-detects the case-id, image-path, and official estimated Monk Skin Tone
   (eMST) columns. The India eMST label is preferred;
   ``monk_skin_tone_label_us`` is used only as a fallback.
4. Expands each case into one row per available image path.
5. Keeps only rows whose official eMST label is a valid integer 1-10.
6. Groups those labels into light (1-3), medium (4-7), dark (8-10).
7. Selects a reproducible subset (seed 42 by default) of at most
   ``--per-group`` image rows per broad group (75 by default).
8. Prefers one image per case. Additional images from the same case are only
   taken when a group does not have enough unique cases, and every row records
   whether it is such an extra image
   (``multiple_images_from_same_case``).
9. Writes data/manifests/scin_candidate_selection.csv.

Important:
    The SCIN eMST label is an official dataset metadata field. It is used here
    only as the source of a *broad training group*. It is NOT a medical label
    and NOT an identity label, and the output is only a list of training
    candidates.

Run from the project root:
    python scripts/11b_select_scin_subset.py
    python scripts/11b_select_scin_subset.py --per-group 75 --seed 42
    python scripts/11b_select_scin_subset.py --per-group 50 --seed 7

No network access and no image files are needed.
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation.training_manifest import (  # noqa: E402
    GROUP_ORDER,
    SCIN_DATASET_NAME,
    broad_group_for_label,
    read_label,
    read_text,
)


# -------------------------------------------------------------------
# Paths, constants, and column contracts
# -------------------------------------------------------------------

DEFAULT_METADATA_DIR = PROJECT_ROOT / "data" / "raw" / "scin" / "metadata"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "manifests" / "scin_candidate_selection.csv"
)

DEFAULT_PER_GROUP = 75
DEFAULT_SEED = 42

#: Output column order (exactly what the next step expects).
OUTPUT_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "case_id",
    "image_slot",
    "image_path",
    "source_mst_label",
    "source_broad_mst_group",
    "group_assignment_source",
    "selection_seed",
    "selection_reason",
    "multiple_images_from_same_case",
    "intended_use",
)

#: Broad-group assignment sources for the two official SCIN eMST fields.
GROUP_SOURCE_EMST_INDIA = "official_scin_emst_india"
GROUP_SOURCE_EMST_US = "official_scin_emst_us"

#: ``intended_use`` written for every selected row.
INTENDED_USE_TRAINING_CANDIDATE = "training_candidate"

#: Candidate case-id columns, in preference order.
CASE_ID_CANDIDATES: tuple[str, ...] = (
    "case_id",
    "caseid",
    "case",
    "id",
)

#: Candidate official eMST columns, in preference order (India first).
EMST_INDIA_COLUMN = "monk_skin_tone_label_india"
EMST_US_COLUMN = "monk_skin_tone_label_us"

#: Matches image path columns such as ``image_1_path``.
_IMAGE_PATH_PATTERN = re.compile(r"^image_(\d+)_path$", re.IGNORECASE)


class MetadataFileError(Exception):
    """Raised when the SCIN metadata files or required columns cannot be found."""


# -------------------------------------------------------------------
# Metadata file detection
# -------------------------------------------------------------------


def detect_metadata_files(metadata_dir: Path) -> tuple[Path, Path]:
    """Find the SCIN cases CSV and labels CSV in ``metadata_dir``.

    Detection is by filename pattern so a ``dataset_`` prefix is fine:

    - cases  : the one CSV whose name contains ``case``
    - labels : the one CSV whose name contains ``label`` but not ``question``

    Parameters
    ----------
    metadata_dir : Path
        Folder holding the SCIN metadata CSVs.

    Returns
    -------
    tuple[Path, Path]
        ``(cases_path, labels_path)``.

    Raises
    ------
    MetadataFileError
        If the folder is missing/empty, or the cases/labels file is ambiguous
        or absent. The error message lists the candidate filenames.
    """
    if not metadata_dir.is_dir():
        raise MetadataFileError(f"metadata folder not found: {metadata_dir}")

    csv_files = sorted(
        path
        for path in metadata_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".csv"
    )
    if not csv_files:
        raise MetadataFileError(f"no CSV files found in: {metadata_dir}")

    case_candidates = [
        path for path in csv_files if "case" in path.stem.lower()
    ]
    label_candidates = [
        path
        for path in csv_files
        if "label" in path.stem.lower() and "question" not in path.stem.lower()
    ]

    problems: list[str] = []
    if len(case_candidates) != 1:
        listed = ", ".join(path.name for path in case_candidates) or "(none)"
        problems.append(f"cases CSV candidates: {listed}")
    if len(label_candidates) != 1:
        listed = ", ".join(path.name for path in label_candidates) or "(none)"
        problems.append(f"labels CSV candidates: {listed}")

    if problems:
        all_names = ", ".join(path.name for path in csv_files)
        raise MetadataFileError(
            "could not uniquely detect the SCIN cases/labels CSV files.\n"
            + "\n".join(f"  - {problem}" for problem in problems)
            + f"\n  all CSV files in {metadata_dir}: {all_names}\n"
            "Rename the files so the cases CSV contains 'case' and the labels "
            "CSV contains 'label' (and not 'question'), or pass explicit paths."
        )

    return case_candidates[0], label_candidates[0]


# -------------------------------------------------------------------
# Column detection
# -------------------------------------------------------------------


def _require_columns(
    available: list[str], wanted: list[str], field_name: str
) -> str:
    """Return the first available column in ``wanted`` or raise."""
    for column in wanted:
        if column in available:
            return column
    raise MetadataFileError(
        f"required {field_name} column not found.\n"
        f"  looked for : {wanted}\n"
        f"  available  : {available}"
    )


def detect_case_id_column(columns: list[str]) -> str:
    """Return the case-id column, preferring the documented name."""
    return _require_columns(columns, list(CASE_ID_CANDIDATES), "case-id")


def detect_image_path_columns(columns: list[str]) -> list[str]:
    """Return every ``image_<n>_path`` column, ordered by slot number."""
    matched = [column for column in columns if _IMAGE_PATH_PATTERN.match(column)]
    if not matched:
        raise MetadataFileError(
            "no image path columns found.\n"
            "  looked for : image_<n>_path (e.g. image_1_path, image_2_path)\n"
            f"  available  : {columns}"
        )
    return sorted(matched, key=lambda column: int(_IMAGE_PATH_PATTERN.match(column).group(1)))


def image_slot_for_column(column: str) -> int:
    """Return the integer slot (1, 2, 3, ...) encoded in an image path column."""
    match = _IMAGE_PATH_PATTERN.match(column)
    if match is None:  # pragma: no cover - guarded by detect_image_path_columns
        raise MetadataFileError(f"not an image path column: {column}")
    return int(match.group(1))


def detect_emst_column(columns: list[str]) -> tuple[str, str]:
    """Return ``(column_name, group_assignment_source)`` for the official eMST.

    The India label is preferred. The US label is accepted only as a fallback
    when the India column does not exist. If neither exists, a clear error
    listing the available headers is raised.
    """
    if EMST_INDIA_COLUMN in columns:
        return EMST_INDIA_COLUMN, GROUP_SOURCE_EMST_INDIA
    if EMST_US_COLUMN in columns:
        return EMST_US_COLUMN, GROUP_SOURCE_EMST_US
    raise MetadataFileError(
        "no official SCIN estimated Monk Skin Tone column found.\n"
        f"  preferred : {EMST_INDIA_COLUMN}\n"
        f"  fallback  : {EMST_US_COLUMN}\n"
        f"  available  : {columns}"
    )


# -------------------------------------------------------------------
# Pure selection helpers (synthetic-DataFrame friendly)
# -------------------------------------------------------------------


def expand_cases_to_image_rows(
    cases: pd.DataFrame, case_id_column: str, image_path_columns: list[str]
) -> pd.DataFrame:
    """Turn one-row-per-case into one-row-per-image.

    Columns of the returned frame: ``case_id``, ``image_slot``, ``image_path``.
    Empty image paths are dropped so only real images remain.
    """
    parts: list[pd.DataFrame] = []
    for column in image_path_columns:
        part = cases[[case_id_column, column]].rename(
            columns={case_id_column: "case_id", column: "image_path"}
        )
        part = part.copy()
        part["image_slot"] = image_slot_for_column(column)
        parts.append(part)

    if not parts:
        return pd.DataFrame(columns=["case_id", "image_slot", "image_path"])

    rows = pd.concat(parts, ignore_index=True)
    rows["case_id"] = rows["case_id"].map(read_text)
    rows["image_path"] = rows["image_path"].map(read_text)
    rows = rows[(rows["case_id"] != "") & (rows["image_path"] != "")]
    rows = rows.sort_values(["case_id", "image_slot"], kind="stable")
    return rows.reset_index(drop=True)


def attach_official_emst(
    image_rows: pd.DataFrame,
    labels: pd.DataFrame,
    case_id_label_column: str,
    emst_column: str,
) -> pd.DataFrame:
    """Attach the official eMST label and keep only valid rows (1-10).

    A broad group (light/medium/dark) is assigned from the official label. Rows
    whose label is missing or not a valid integer 1-10 are removed.
    """
    label_map = labels[[case_id_label_column, emst_column]].rename(
        columns={case_id_label_column: "case_id", emst_column: "source_mst_label"}
    )
    label_map = label_map.copy()
    label_map["case_id"] = label_map["case_id"].map(read_text)
    label_map = label_map[label_map["case_id"] != ""]
    label_map = label_map.drop_duplicates(subset="case_id", keep="first")

    merged = image_rows.merge(label_map, on="case_id", how="left")
    merged["source_mst_label"] = merged["source_mst_label"].map(read_label)
    merged["source_broad_mst_group"] = merged["source_mst_label"].map(
        broad_group_for_label
    )

    valid = merged[merged["source_broad_mst_group"].notna()].copy()
    valid["source_mst_label"] = valid["source_mst_label"].astype(int)
    return valid.reset_index(drop=True)


def select_group_candidates(
    group_rows: pd.DataFrame, per_group: int, seed: int
) -> pd.DataFrame:
    """Select up to ``per_group`` image rows from one broad group.

    One image per case is preferred. Only when a group has fewer unique cases
    than ``per_group`` are extra images taken from cases already chosen; those
    extra rows are marked ``multiple_images_from_same_case = True``.

    Selection is reproducible: rows are canonically ordered by
    ``(case_id, image_slot)`` and then a ``random.Random(seed)`` shuffle decides
    which cases are drawn.
    """
    if group_rows is None or group_rows.empty or per_group <= 0:
        return pd.DataFrame(columns=list(group_rows.columns) + ["multiple_images_from_same_case"])

    ordered = group_rows.sort_values(
        ["case_id", "image_slot"], kind="stable"
    ).reset_index(drop=True)

    unique_cases = sorted(ordered["case_id"].unique().tolist())
    rng = random.Random(seed)
    shuffled_cases = unique_cases[:]
    rng.shuffle(shuffled_cases)
    chosen_cases = shuffled_cases[:per_group]
    case_order = {case: index for index, case in enumerate(chosen_cases)}

    first_by_case = ordered.drop_duplicates(subset="case_id", keep="first")
    primary = first_by_case[first_by_case["case_id"].isin(chosen_cases)].copy()
    primary["_case_order"] = primary["case_id"].map(case_order)
    primary = primary.sort_values("_case_order", kind="stable").drop(
        columns="_case_order"
    )
    primary["multiple_images_from_same_case"] = False

    frames = [primary]

    if len(primary) < per_group:
        selected_keys = set(
            zip(primary["case_id"].tolist(), primary["image_slot"].tolist())
        )
        extra_mask = [
            (case, slot) not in selected_keys
            for case, slot in zip(ordered["case_id"], ordered["image_slot"])
        ]
        extras = ordered[extra_mask].reset_index(drop=True)
        needed = per_group - len(primary)
        extras = extras.head(needed).copy()
        extras["multiple_images_from_same_case"] = True
        frames.append(extras)

    return pd.concat(frames, ignore_index=True)


def select_candidates(
    valid_rows: pd.DataFrame, per_group: int, seed: int
) -> tuple[pd.DataFrame, list[str]]:
    """Select ``per_group`` rows per broad group and return warnings.

    Returns
    -------
    tuple[pandas.DataFrame, list[str]]
        The concatenated selection (one block per broad group, in
        light/medium/dark order) and a human-readable warning for every group
        that could not supply ``per_group`` rows.
    """
    frames: list[pd.DataFrame] = []
    warnings: list[str] = []

    for group in GROUP_ORDER:
        group_rows = valid_rows[valid_rows["source_broad_mst_group"] == group]
        selected = select_group_candidates(group_rows, per_group, seed)
        if len(selected) < per_group:
            unique_cases = group_rows["case_id"].nunique() if not group_rows.empty else 0
            warnings.append(
                f"{group}: requested {per_group} rows but only {len(selected)} "
                f"are available ({unique_cases} unique cases)"
            )
        frames.append(selected)

    non_empty = [frame for frame in frames if not frame.empty]
    combined = (
        pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    )
    return combined, warnings


def build_selection_output(
    selected: pd.DataFrame, group_source: str, seed: int
) -> pd.DataFrame:
    """Add the manifest columns required by the next pipeline step."""
    if selected.empty:
        return pd.DataFrame(columns=list(OUTPUT_COLUMNS))

    output = selected.copy()
    output["dataset_name"] = SCIN_DATASET_NAME
    output["image_id"] = (
        "scin__"
        + output["case_id"].astype(str)
        + "__"
        + output["image_slot"].astype(str)
    )
    output["group_assignment_source"] = group_source
    output["selection_seed"] = seed
    output["selection_reason"] = output["multiple_images_from_same_case"].map(
        {
            False: "one_image_per_case",
            True: "additional_image_from_same_case_shortfall",
        }
    )
    output["intended_use"] = INTENDED_USE_TRAINING_CANDIDATE
    return output.loc[:, list(OUTPUT_COLUMNS)]


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Select a small, reproducible, metadata-only SCIN subset. No images "
            "are downloaded and no pipeline stage is run."
        )
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=DEFAULT_METADATA_DIR,
        help=f"Folder holding the SCIN metadata CSVs (default: {DEFAULT_METADATA_DIR})",
    )
    parser.add_argument(
        "--cases-csv",
        type=Path,
        default=None,
        help="Explicit path to the SCIN cases CSV (skips filename auto-detection).",
    )
    parser.add_argument(
        "--labels-csv",
        type=Path,
        default=None,
        help="Explicit path to the SCIN labels CSV (skips filename auto-detection).",
    )
    parser.add_argument(
        "--per-group",
        type=int,
        default=DEFAULT_PER_GROUP,
        help=f"Image rows to select per broad group (default: {DEFAULT_PER_GROUP})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for reproducible sampling (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output selection CSV (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


# -------------------------------------------------------------------
# Reporting
# -------------------------------------------------------------------


def print_headers(title: str, columns: list[str]) -> None:
    """Print one file's name and column headers."""
    print(f"{title}:")
    for column in columns:
        print(f"  - {column}")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Run the metadata-only SCIN subset selection."""
    args = parse_arguments()

    if args.per_group <= 0:
        print("ERROR: --per-group must be a positive integer.")
        sys.exit(1)

    # -- 1/2. Detect and read the metadata files -------------------
    try:
        if args.cases_csv is not None and args.labels_csv is not None:
            cases_path = args.cases_csv
            labels_path = args.labels_csv
        else:
            cases_path, labels_path = detect_metadata_files(args.metadata_dir)
    except MetadataFileError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    for path in (cases_path, labels_path):
        if not path.is_file():
            print(f"ERROR: CSV file not found: {path}")
            sys.exit(1)

    cases = pd.read_csv(cases_path)
    labels = pd.read_csv(labels_path)

    print("=" * 72)
    print("SCIN metadata subset selection (metadata only, no images)")
    print("=" * 72)
    print(f"Metadata folder : {args.metadata_dir}")
    print(f"Cases CSV       : {cases_path.name}")
    print(f"Labels CSV      : {labels_path.name}")
    print()
    print_headers("Cases CSV columns", list(cases.columns))
    print()
    print_headers("Labels CSV columns", list(labels.columns))
    print()

    # -- 3. Detect fields -----------------------------------------
    try:
        case_id_column = detect_case_id_column(list(cases.columns))
        image_path_columns = detect_image_path_columns(list(cases.columns))
        if case_id_column not in list(labels.columns):
            raise MetadataFileError(
                f"case-id column {case_id_column!r} is missing from the labels CSV.\n"
                f"  available  : {list(labels.columns)}"
            )
        emst_column, group_source = detect_emst_column(list(labels.columns))
    except MetadataFileError as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    print(f"Detected case-id column      : {case_id_column}")
    print(f"Detected image path columns  : {', '.join(image_path_columns)}")
    print(f"Detected official eMST column: {emst_column}")
    print(f"Group assignment source      : {group_source}")
    print()

    # -- 4/5/6. Expand, filter, and group -------------------------
    image_rows = expand_cases_to_image_rows(
        cases, case_id_column, image_path_columns
    )
    valid_rows = attach_official_emst(
        image_rows, labels, case_id_column, emst_column
    )

    # -- 7/8. Reproducible, one-image-per-case selection ----------
    selected, warnings = select_candidates(
        valid_rows, args.per_group, args.seed
    )
    output = build_selection_output(selected, group_source, args.seed)

    # -- 9. Save ---------------------------------------------------
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)

    # -- 12. Console report ---------------------------------------
    total_cases = len(cases)
    total_image_rows = len(image_rows)
    total_valid_rows = len(valid_rows)

    unique_per_group = {
        group: int(
            valid_rows.loc[
                valid_rows["source_broad_mst_group"] == group, "case_id"
            ].nunique()
        )
        for group in GROUP_ORDER
    }
    selected_per_group = {
        group: int(
            (output["source_broad_mst_group"] == group).sum()
        )
        for group in GROUP_ORDER
    }

    repeated = output["case_id"].value_counts()
    repeated_cases = int((repeated > 1).sum())

    print()
    print("=" * 72)
    print("SCIN subset selection summary")
    print("=" * 72)
    print(f"Total cases read              : {total_cases}")
    print(f"Total image rows found        : {total_image_rows}")
    print(f"Total valid eMST rows (1-10)  : {total_valid_rows}")
    print()
    print("Unique cases per broad group:")
    for group in GROUP_ORDER:
        print(f"  {group:<7}: {unique_per_group[group]}")
    print()
    print(f"Selected candidates (per-group request = {args.per_group}, seed = {args.seed}):")
    for group in GROUP_ORDER:
        print(f"  {group:<7}: {selected_per_group[group]}")
    print(f"  {'total':<7}: {len(output)}")
    print()
    print(f"Repeated cases in selection   : {repeated_cases}")

    if warnings:
        print()
        print("Warnings (fewer rows than requested):")
        for warning in warnings:
            print(f"  ! {warning}")

    print()
    print(f"Output path                   : {args.output}")
    print()
    print("Notes:")
    print("  - No images were downloaded and the SCIN dataset was not fetched.")
    print("  - The official SCIN eMST field is used only as a broad training-")
    print("    group source; it is not a medical or identity label.")


if __name__ == "__main__":
    main()
