"""
12_select_fairface_candidates.py

Purpose:
    Build a small, reproducible, metadata-first FairFace candidate pool without
    processing the whole dataset.

    FairFace's race, gender, and age labels are used ONLY to spread the sample
    across visually diverse source images. They are recorded under neutral names
    (``source_race_label``, ``source_gender_label``, ``source_age_label``) and
    are never converted into Monk Skin Tone (MST) groups.

What this script deliberately does NOT do
-----------------------------------------
- It never infers official MST categories from FairFace race.
- It never writes FairFace rows as official light/medium/dark skin-tone groups.
- It never uses MST-E images.
- It never modifies YuNet, Skin Mask V2, or ITA code.
- It never generates distortions and never trains a model.

Instead, every selected row is marked as *pending* real colour measurement:
    estimated_broad_ita_group = pending_ita_processing
    group_assignment_source   = not_available_until_ita

Broad-group balancing happens later, only after Skin Mask V2 and continuous ITA
processing — never through race labels.

Inputs:
    data/raw/fairface/                            FairFace image root
    data/raw/fairface/fairface_label_train.csv    train metadata
    data/raw/fairface/fairface_label_val.csv      validation metadata

Output:
    data/manifests/fairface_candidate_selection.csv

Run from the project root:
    python scripts/12_select_fairface_candidates.py
    python scripts/12_select_fairface_candidates.py --smoke-test
    python scripts/12_select_fairface_candidates.py --limit 650 --seed 42
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation.dataset_inventory import make_image_id  # noqa: E402
from src.data_preparation.training_manifest import (  # noqa: E402
    FAIRFACE_DATASET_NAME,
    read_text,
)


# -------------------------------------------------------------------
# Paths, constants, and column contracts
# -------------------------------------------------------------------

DEFAULT_IMAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "fairface"
DEFAULT_TRAIN_CSV = DEFAULT_IMAGE_ROOT / "fairface_label_train.csv"
DEFAULT_VAL_CSV = DEFAULT_IMAGE_ROOT / "fairface_label_val.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "manifests" / "fairface_candidate_selection.csv"
)

DEFAULT_LIMIT = 650
DEFAULT_SEED = 42
SMOKE_TEST_LIMIT = 20

SPLIT_TRAIN = "train"
SPLIT_VALIDATION = "validation"

#: Columns written to the selection manifest, in order.
OUTPUT_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "image_path",
    "source_split",
    "source_race_label",
    "source_gender_label",
    "source_age_label",
    "source_mst_label",
    "source_broad_mst_group",
    "estimated_broad_ita_group",
    "group_assignment_source",
    "selection_seed",
    "selection_reason",
    "intended_use",
)

#: Fixed values documenting that MST grouping is not available yet.
ESTIMATED_BROAD_ITA_GROUP_PENDING = "pending_ita_processing"
GROUP_SOURCE_NOT_AVAILABLE = "not_available_until_ita"
INTENDED_USE_TRAINING_CANDIDATE = "training_candidate"

#: Candidate column names for each FairFace metadata field.
FILE_COLUMN_CANDIDATES: tuple[str, ...] = (
    "file",
    "image",
    "image_path",
    "path",
    "filename",
)
RACE_COLUMN_CANDIDATES: tuple[str, ...] = ("race", "race_label", "source_race")
GENDER_COLUMN_CANDIDATES: tuple[str, ...] = ("gender", "sex", "source_gender")
AGE_COLUMN_CANDIDATES: tuple[str, ...] = ("age", "age_group", "source_age")

#: Neutral field names.
RACE_FIELD = "source_race_label"
GENDER_FIELD = "source_gender_label"
AGE_FIELD = "source_age_label"

#: The dimensions used to stratify the sample.
STRATA_FIELDS: tuple[str, ...] = (RACE_FIELD, GENDER_FIELD, AGE_FIELD)


class MetadataError(Exception):
    """Raised when a FairFace metadata file or required column is missing."""


# -------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------


def detect_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    """Return the first matching candidate column, or ``None``."""
    lowered = {str(column).strip().lower(): column for column in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def normalize_split(value: object) -> str:
    """Map a split label to ``train`` or ``validation``."""
    text = read_text(value).lower()
    if text in {"train", "training"}:
        return SPLIT_TRAIN
    if text in {"val", "valid", "validation"}:
        return SPLIT_VALIDATION
    return text or SPLIT_VALIDATION


def resolve_image_path(image_root: Path, split: str, file_value: object) -> Path | None:
    """Find the local image for one metadata ``file`` value.

    Returns the first existing candidate path, or ``None`` when the file cannot
    be found in any of the common FairFace layouts.
    """
    text = read_text(file_value)
    if not text:
        return None

    raw = Path(text.replace("\\", "/"))
    name = raw.name
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    candidates.extend(
        [
            image_root / text,
            image_root / split / text,
            image_root / split / name,
            image_root / name,
        ]
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def relative_path_for(image_root: Path, image_path: Path) -> str:
    """Return a stable ``/``-joined path relative to the image root."""
    try:
        return image_path.resolve().relative_to(image_root.resolve()).as_posix()
    except ValueError:
        return image_path.name


# -------------------------------------------------------------------
# Metadata loading
# -------------------------------------------------------------------


def load_split_metadata(
    csv_path: Path,
    split: str,
    image_root: Path,
) -> tuple[pd.DataFrame, int, int]:
    """Read one FairFace split and keep only rows whose image exists locally.

    Returns
    -------
    tuple[pandas.DataFrame, int, int]
        ``(frame, total_rows, missing_rows)`` where ``frame`` has the neutral
        columns plus ``image_id`` and ``image_path``.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise MetadataError(f"FairFace metadata CSV not found: {path}")

    metadata = pd.read_csv(path)
    if metadata.empty:
        raise MetadataError(f"FairFace metadata CSV is empty: {path}")

    file_column = detect_column(list(metadata.columns), FILE_COLUMN_CANDIDATES)
    if file_column is None:
        raise MetadataError(
            "no image/file column found in "
            f"{path.name}.\n  available: {list(metadata.columns)}"
        )

    race_column = detect_column(list(metadata.columns), RACE_COLUMN_CANDIDATES)
    gender_column = detect_column(list(metadata.columns), GENDER_COLUMN_CANDIDATES)
    age_column = detect_column(list(metadata.columns), AGE_COLUMN_CANDIDATES)

    records: list[dict] = []
    missing = 0
    for row in metadata.itertuples(index=False):
        row_dict = row._asdict()
        image_path = resolve_image_path(image_root, split, row_dict.get(file_column))
        if image_path is None:
            missing += 1
            continue
        relative = relative_path_for(image_root, image_path)
        records.append(
            {
                "image_id": make_image_id(FAIRFACE_DATASET_NAME, relative),
                "image_path": image_path.as_posix(),
                "source_split": split,
                RACE_FIELD: read_text(row_dict.get(race_column)) if race_column else "",
                GENDER_FIELD: (
                    read_text(row_dict.get(gender_column)) if gender_column else ""
                ),
                AGE_FIELD: read_text(row_dict.get(age_column)) if age_column else "",
            }
        )

    frame = pd.DataFrame(records)
    return frame, len(metadata), missing


def stack_candidate_pool(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Combine split frames into one candidate pool with stable ordering."""
    usable = [frame for frame in frames if frame is not None and not frame.empty]
    if not usable:
        return pd.DataFrame(
            columns=[
                "image_id",
                "image_path",
                "source_split",
                RACE_FIELD,
                GENDER_FIELD,
                AGE_FIELD,
            ]
        )
    pool = pd.concat(usable, ignore_index=True)
    pool = pool.drop_duplicates(subset="image_id", keep="first")
    return pool.sort_values("image_id", kind="stable").reset_index(drop=True)


# -------------------------------------------------------------------
# Stratified selection
# -------------------------------------------------------------------


def stratified_sample(
    frame: pd.DataFrame,
    limit: int,
    seed: int,
    strata_columns: tuple[str, ...] = STRATA_FIELDS,
) -> pd.DataFrame:
    """Select up to ``limit`` rows spread across the requested strata.

    Selection is reproducible: rows are canonically ordered, each stratum is
    shuffled with ``random.Random(seed)``, and rows are then drawn round-robin
    across strata so no single race/gender/age combination dominates.
    """
    if frame is None or frame.empty or limit <= 0:
        return frame.iloc[0:0].copy() if frame is not None else pd.DataFrame()

    present = [column for column in strata_columns if column in frame.columns]
    ordered = frame.copy()
    if present:
        ordered["_strata"] = ordered[present].astype(str).agg("|".join, axis=1)
    else:
        ordered["_strata"] = "all"

    ordered = ordered.sort_values(["_strata", "image_id"], kind="stable")
    ordered = ordered.reset_index(drop=True)

    groups: dict[str, list[int]] = {}
    for stratum, group in ordered.groupby("_strata", sort=True):
        indices = group.index.tolist()
        groups[str(stratum)] = indices

    rng = random.Random(seed)
    keys = sorted(groups.keys())
    for key in keys:
        rng.shuffle(groups[key])
    # Shuffle the stratum order too, so a small limit still spreads across
    # races/genders/ages instead of always taking the alphabetically-first ones.
    rng.shuffle(keys)

    positions = {key: 0 for key in keys}
    chosen_indices: list[int] = []
    while len(chosen_indices) < min(limit, len(ordered)):
        progressed = False
        for key in keys:
            position = positions[key]
            if position < len(groups[key]):
                chosen_indices.append(groups[key][position])
                positions[key] = position + 1
                progressed = True
                if len(chosen_indices) >= limit:
                    break
        if not progressed:
            break

    selected = ordered.loc[chosen_indices].drop(columns="_strata")
    return selected.reset_index(drop=True)


# -------------------------------------------------------------------
# Output building
# -------------------------------------------------------------------


def resolve_limit(limit: int | None, smoke_test: bool) -> int:
    """Resolve the effective selection limit.

    ``--smoke-test`` always selects :data:`SMOKE_TEST_LIMIT` (20); otherwise an
    explicit ``--limit`` wins and the default is :data:`DEFAULT_LIMIT` (650).
    """
    if smoke_test:
        return SMOKE_TEST_LIMIT
    if limit is not None:
        return int(limit)
    return DEFAULT_LIMIT


def build_output(selected: pd.DataFrame, seed: int, smoke_test: bool) -> pd.DataFrame:
    """Add the fixed manifest columns to the selected rows."""
    if selected is None or selected.empty:
        return pd.DataFrame(columns=list(OUTPUT_COLUMNS))

    output = selected.copy()
    output["dataset_name"] = FAIRFACE_DATASET_NAME
    output["source_mst_label"] = ""
    output["source_broad_mst_group"] = ""
    output["estimated_broad_ita_group"] = ESTIMATED_BROAD_ITA_GROUP_PENDING
    output["group_assignment_source"] = GROUP_SOURCE_NOT_AVAILABLE
    output["selection_seed"] = seed
    output["selection_reason"] = (
        "smoke_test_stratified_source_diversity"
        if smoke_test
        else "stratified_source_diversity"
    )
    output["intended_use"] = INTENDED_USE_TRAINING_CANDIDATE
    return output.loc[:, list(OUTPUT_COLUMNS)].reset_index(drop=True)


# -------------------------------------------------------------------
# Reporting
# -------------------------------------------------------------------


def print_counts(title: str, series: pd.Series) -> None:
    """Print a value-count table with a title."""
    print(title)
    if series is None or series.empty:
        print("  (none)")
        return
    for value, count in series.items():
        print(f"  {value if str(value) else '(blank)':<16}: {count}")


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Select a reproducible, metadata-first FairFace candidate pool. "
            "Race/gender/age are used only for source-image diversity; no MST "
            "group is inferred and nothing is downloaded or trained."
        )
    )
    parser.add_argument(
        "--image-root",
        type=Path,
        default=DEFAULT_IMAGE_ROOT,
        help=f"FairFace image root (default: {DEFAULT_IMAGE_ROOT})",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help=f"FairFace train metadata CSV (default: {DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--val-csv",
        type=Path,
        default=DEFAULT_VAL_CSV,
        help=f"FairFace validation metadata CSV (default: {DEFAULT_VAL_CSV})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output selection CSV (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=f"Candidates to select (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for reproducible sampling (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=f"Select only {SMOKE_TEST_LIMIT} candidates instead of the default.",
    )
    return parser.parse_args()


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Build the FairFace candidate selection and print a summary."""
    args = parse_arguments()

    limit = resolve_limit(args.limit, args.smoke_test)

    if limit <= 0:
        print("ERROR: --limit must be a positive integer.")
        sys.exit(1)

    print("=" * 72)
    print("FairFace metadata-first candidate selection")
    print("=" * 72)
    print(f"Image root : {args.image_root}")
    print(f"Train CSV  : {args.train_csv}")
    print(f"Val CSV    : {args.val_csv}")
    print(f"Limit      : {limit}{' (smoke test)' if args.smoke_test else ''}")
    print(f"Seed       : {args.seed}")
    print()

    frames: list[pd.DataFrame] = []
    total_meta = 0
    total_missing = 0

    for csv_path, split in (
        (args.train_csv, SPLIT_TRAIN),
        (args.val_csv, SPLIT_VALIDATION),
    ):
        try:
            frame, total_rows, missing = load_split_metadata(
                csv_path, split, args.image_root
            )
        except MetadataError as error:
            print(f"ERROR: {error}")
            sys.exit(1)
        total_meta += total_rows
        total_missing += missing
        print(
            f"{split:<11}: {total_rows} metadata rows, "
            f"{len(frame)} images found, {missing} missing"
        )
        frames.append(frame)

    pool = stack_candidate_pool(frames)
    if pool.empty:
        print()
        print(
            "ERROR: no valid FairFace images were found under "
            f"{args.image_root}. Check --image-root and the metadata CSVs."
        )
        sys.exit(1)

    selected = stratified_sample(pool, limit, args.seed)
    output = build_output(selected, args.seed, args.smoke_test)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)

    print()
    print("=" * 72)
    print("FairFace candidate selection summary")
    print("=" * 72)
    print(f"Metadata rows read     : {total_meta}")
    print(f"Missing images skipped : {total_missing}")
    print(f"Candidate pool         : {len(pool)}")
    print(f"Selected candidates    : {len(output)}")
    print()
    print_counts("Selected by split:", output["source_split"].value_counts())
    print()
    print_counts("Selected by race:", output[RACE_FIELD].value_counts())
    print()
    print_counts("Selected by gender:", output[GENDER_FIELD].value_counts())
    print()
    print_counts("Selected by age:", output[AGE_FIELD].value_counts())
    print()
    print(f"Output path            : {args.output}")
    print()
    print("Notes:")
    print("  - FairFace race/gender/age were used only for source-image")
    print("    diversity; no MST group was inferred from them.")
    print("  - source_mst_label and source_broad_mst_group are intentionally")
    print("    blank. Real grouping happens after Skin Mask V2 + continuous")
    print("    ITA processing (estimated_broad_ita_group= pending).")
    print("  - No images were processed, no distortions were generated, and no")
    print("    model was trained.")


if __name__ == "__main__":
    main()
