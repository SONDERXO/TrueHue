"""
14_prepare_fairface_candidate_pool.py

Purpose:
    Prepare and process a reproducible 650-image FairFace candidate pool through
    the *frozen* TrueHue pipeline and write round-specific manifests. Nothing
    existing is overwritten, no threshold is tuned, and no model is trained.

    Pipeline per image (unchanged, reused from scripts/11):
        YuNet face detection (single face only)
        -> largest-face BGR crop
        -> Skin Mask V2 (HSV/YCrCb + morphology + largest component +
           landmark eye/eyebrow/lip exclusion)
        -> CIELAB conversion of the selected skin pixels only
        -> mean L*, a*, b* and continuous ITA (degrees)

    Candidate selection (unchanged, reused from scripts/12):
        FairFace train + validation metadata are read from the local repo copy,
        deduplicated by image_id, and sampled with the deterministic
        ``stratified_sample`` sampler (seed 42). The original train/validation
        split, image IDs, and FairFace source race/gender/age metadata are
        preserved exactly. Race/gender/age are used ONLY to spread the sample
        across visibly diverse source images; they are never converted to a
        skin-tone group.

    The seed-42, limit-650 selection is a deterministic superset of the 20-image
    smoke-test selection (same sampler, same seed, same pool). The 20 smoke-test
    images therefore appear inside the 650 exactly once; they are never counted
    or processed twice.

    Official MST labels and broad-group fields stay unassigned: no ITA-to-group
    rule is supplied, so every processed row keeps
    ``estimated_broad_mst_group`` blank and ``group_assignment_source`` as
    ``not_available_until_ita``. No group-based cap is applied, so successfully
    processed unassigned rows are never silently removed.

What this script reuses (no pipeline logic is copied):
    - scripts/12_select_fairface_candidates.py
        metadata loading, split normalisation, path resolution, the stratified
        seed-42 sampler, and the output builder (blanks official MST labels and
        records ``pending_ita_processing`` / ``not_available_until_ita``).
    - scripts/11_prepare_training_manifests.py
        ``prepare_dataset`` / ``process_record`` (the frozen pipeline) and
        ``compute_v2_skin_mask_with_margin`` (V2 feature exclusion).
    - scripts/13_fairface_smoke_test.py
        ``generate_smoke_visualization`` (2x2 Skin Mask V2 review grid).
    - scripts/09_diagnose_mst_e_ita_calibration.py
        ``_ita_stats`` (count / min / Q1 / median / Q3 / max for one ITA series).
    - src.data_preparation.training_manifest (column contract + summaries).

What this script deliberately does NOT do:
    - No SCIN or MST-E image is downloaded, read, or processed.
    - No pipeline module (YuNet, Skin Mask V2, landmark exclusion, CIELAB, ITA)
      is modified.
    - No synthetic distortion is generated and no model is trained.
    - No final data split is created.
    - No official MST label or broad MST group is invented; no --estimated-group
      rule is applied.
    - V1 fallback masks (landmarks unavailable) are excluded from the valid V2
      outputs even when a numerical ITA was computed.
    - Existing smoke-test outputs are left untouched.

Outputs (round-specific; existing manifests are untouched):
    data/manifests/fairface_candidate_selection.csv
    data/manifests/fairface_candidate_processed_manifest.csv
    data/manifests/fairface_candidate_summary.csv
    data/manifests/fairface_candidate_visualization_selection.csv
    outputs/fairface_candidate_visualizations/<image_id>_visualization.png

Run from the project root:
    python scripts/14_prepare_fairface_candidate_pool.py

    python scripts/14_prepare_fairface_candidate_pool.py ^
        --image-root "data/raw/FairFace" ^
        --train-csv "data/raw/FairFace/train_labels.csv" ^
        --val-csv  "data/raw/FairFace/val_labels.csv" ^
        --limit 650 --seed 42

No network calls: the YuNet ONNX and MediaPipe face_landmarker.task models must
already exist locally (see src/utilities/config.py).
"""

from __future__ import annotations

import argparse
import importlib
import random
import sys
from pathlib import Path

import pandas as pd

# Make the project root and scripts/ importable when run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for _path in (PROJECT_ROOT, SCRIPTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from src.data_preparation.training_manifest import (  # noqa: E402
    FAIRFACE_DATASET_NAME,
    MANIFEST_COLUMNS,
    STATUS_EXCLUDED,
    STATUS_SUCCESS,
    describe_exclusion,
    read_text,
    summarize_by_exclusion,
    summarize_by_group,
    summarize_processed,
)
from src.utilities.config import get_config  # noqa: E402

# Reuse the existing stages instead of copying any of their logic.
select_candidates = importlib.import_module("12_select_fairface_candidates")
prepare_manifests = importlib.import_module("11_prepare_training_manifests")
smoke_visuals = importlib.import_module("13_fairface_smoke_test")
diagnostics = importlib.import_module("09_diagnose_mst_e_ita_calibration")


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"

DEFAULT_IMAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "FairFace"
DEFAULT_TRAIN_CSV = DEFAULT_IMAGE_ROOT / "train_labels.csv"
DEFAULT_VAL_CSV = DEFAULT_IMAGE_ROOT / "val_labels.csv"

DEFAULT_SELECTION_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_candidate_selection.csv"
)
DEFAULT_PROCESSED_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_candidate_processed_manifest.csv"
)
DEFAULT_SUMMARY_OUTPUT = DEFAULT_MANIFEST_DIR / "fairface_candidate_summary.csv"
DEFAULT_VISUALIZATION_SELECTION_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_candidate_visualization_selection.csv"
)
DEFAULT_VISUALIZATIONS_ROOT = (
    PROJECT_ROOT / "outputs" / "fairface_candidate_visualizations"
)

#: The smoke-test selection is read only to confirm the 20 images are not
#: counted twice. Its outputs are never modified.
DEFAULT_SMOKE_SELECTION = (
    DEFAULT_MANIFEST_DIR / "fairface_smoke_test_selection.csv"
)

DEFAULT_YUNET_MODEL = PROJECT_ROOT / get_config().FACE_MODEL_PATH
DEFAULT_LANDMARKER_MODEL = PROJECT_ROOT / get_config().FACE_LANDMARKER_MODEL_PATH

#: Same 1,000-pixel minimum-skin rule and YuNet confidence as the pipeline.
DEFAULT_MINIMUM_SKIN_PIXELS = 1000
DEFAULT_SCORE_THRESHOLD = 0.85

#: Same deterministic pool size and seed as scripts/12.
DEFAULT_LIMIT = select_candidates.DEFAULT_LIMIT
DEFAULT_SEED = select_candidates.DEFAULT_SEED

#: Reproducible debug-visualization selection: a random spread plus the
#: lowest- and highest-mask-coverage cases (not every intermediate artifact).
DEFAULT_VISUALIZATION_RANDOM_COUNT = 20
DEFAULT_VISUALIZATION_EXTREME_COUNT = 5

#: ``intended_use`` written for candidate rows (mirrors scripts/12).
INTENDED_USE_TRAINING_CANDIDATE = "training_candidate"
CANDIDATE_SELECTION_REASON = "stratified_source_diversity"


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options, defaulting to the repo FairFace layout."""
    parser = argparse.ArgumentParser(
        description=(
            "Prepare and process the reproducible 650-image FairFace candidate "
            "pool through the frozen face -> Skin Mask V2 -> continuous ITA "
            "pipeline. No thresholds, no training, no split, no raw-image edits."
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
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Reproducible sampling seed (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of unique candidates to select (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--selection-output",
        type=Path,
        default=DEFAULT_SELECTION_OUTPUT,
        help=f"Candidate selection CSV (default: {DEFAULT_SELECTION_OUTPUT})",
    )
    parser.add_argument(
        "--processed-output",
        type=Path,
        default=DEFAULT_PROCESSED_OUTPUT,
        help=f"Processed manifest CSV (default: {DEFAULT_PROCESSED_OUTPUT})",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT,
        help=f"Summary CSV (default: {DEFAULT_SUMMARY_OUTPUT})",
    )
    parser.add_argument(
        "--visualization-selection-output",
        type=Path,
        default=DEFAULT_VISUALIZATION_SELECTION_OUTPUT,
        help=(
            "CSV listing which debug visualizations were kept "
            f"(default: {DEFAULT_VISUALIZATION_SELECTION_OUTPUT})"
        ),
    )
    parser.add_argument(
        "--visualizations-root",
        type=Path,
        default=DEFAULT_VISUALIZATIONS_ROOT,
        help=(
            "Folder receiving the Skin Mask V2 review grids "
            f"(default: {DEFAULT_VISUALIZATIONS_ROOT})"
        ),
    )
    parser.add_argument(
        "--smoke-selection",
        type=Path,
        default=DEFAULT_SMOKE_SELECTION,
        help=(
            "Smoke-test selection used only to check the 20 images are not "
            f"counted twice (default: {DEFAULT_SMOKE_SELECTION})"
        ),
    )
    parser.add_argument(
        "--yunet-model",
        type=Path,
        default=DEFAULT_YUNET_MODEL,
        help=f"Local YuNet ONNX model (default: {DEFAULT_YUNET_MODEL})",
    )
    parser.add_argument(
        "--landmarker-model",
        type=Path,
        default=DEFAULT_LANDMARKER_MODEL,
        help=(
            "Local MediaPipe face_landmarker.task used for V2 feature exclusion "
            f"(default: {DEFAULT_LANDMARKER_MODEL})"
        ),
    )
    parser.add_argument(
        "--min-skin-pixels",
        type=int,
        default=DEFAULT_MINIMUM_SKIN_PIXELS,
        help=f"Minimum selected skin pixels required (default: {DEFAULT_MINIMUM_SKIN_PIXELS})",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=DEFAULT_SCORE_THRESHOLD,
        help=f"YuNet confidence threshold (default: {DEFAULT_SCORE_THRESHOLD})",
    )
    parser.add_argument(
        "--visualization-random-count",
        type=int,
        default=DEFAULT_VISUALIZATION_RANDOM_COUNT,
        help=(
            "Random V2 success rows to visualize "
            f"(default: {DEFAULT_VISUALIZATION_RANDOM_COUNT})"
        ),
    )
    parser.add_argument(
        "--visualization-extreme-count",
        type=int,
        default=DEFAULT_VISUALIZATION_EXTREME_COUNT,
        help=(
            "Lowest/highest mask-coverage rows to visualize "
            f"(default: {DEFAULT_VISUALIZATION_EXTREME_COUNT})"
        ),
    )
    return parser.parse_args()


# -------------------------------------------------------------------
# Candidate selection (reuses scripts/12)
# -------------------------------------------------------------------


def build_selection_frame(args: argparse.Namespace) -> pd.DataFrame:
    """Return the reproducible candidate selection (official labels blank)."""
    frames: list[pd.DataFrame] = []
    for csv_path, split in (
        (args.train_csv, select_candidates.SPLIT_TRAIN),
        (args.val_csv, select_candidates.SPLIT_VALIDATION),
    ):
        frame, total_rows, missing = select_candidates.load_split_metadata(
            csv_path, split, args.image_root
        )
        print(
            f"  {split:<11}: {total_rows} metadata rows, {len(frame)} images "
            f"found, {missing} missing"
        )
        frames.append(frame)

    pool = select_candidates.stack_candidate_pool(frames)
    if pool.empty:
        raise select_candidates.MetadataError(
            "no valid FairFace images were found under "
            f"{args.image_root}. Check --image-root and the metadata CSVs."
        )

    selected = select_candidates.stratified_sample(pool, args.limit, args.seed)
    return select_candidates.build_output(
        selected, seed=args.seed, smoke_test=False
    )


def build_pipeline_records(
    selection: pd.DataFrame, image_root: Path
) -> pd.DataFrame:
    """Turn the selection manifest into the rows scripts/11 expects.

    The relative path and image ID come from scripts/12, so the original split
    and identifier are preserved unchanged.
    """
    relative_paths = [
        select_candidates.relative_path_for(image_root, Path(path))
        for path in selection["image_path"].astype(str)
    ]
    records = selection[["image_id", "image_path", "intended_use"]].copy()
    records["relative_path"] = relative_paths
    records["dataset_name"] = FAIRFACE_DATASET_NAME
    records["intended_use"] = INTENDED_USE_TRAINING_CANDIDATE
    return records


def verify_smoke_overlap(
    selection: pd.DataFrame, smoke: pd.DataFrame
) -> dict[str, object]:
    """Report how the smoke-test images sit inside the candidate selection.

    The seed-42 sampler makes the 20-image selection a deterministic subset of
    the 650-image selection, so each smoke image should appear exactly once.
    """
    selected_ids = selection["image_id"].astype(str)
    smoke_ids = smoke["image_id"].astype(str) if smoke is not None else pd.Series(
        dtype=str
    )
    selected_set = set(selected_ids)
    smoke_set = set(smoke_ids)
    return {
        "selection_rows": int(len(selected_ids)),
        "selection_unique": bool(selected_ids.is_unique),
        "smoke_rows": int(len(smoke_ids)),
        "smoke_images_in_selection": int(len(smoke_set & selected_set)),
        "smoke_images_missing": int(len(smoke_set - selected_set)),
    }


# -------------------------------------------------------------------
# ITA summary and unassigned-group count
# -------------------------------------------------------------------


def ita_continuous_summary(successful: pd.DataFrame) -> dict[str, object]:
    """Return count/min/Q1/median/Q3/max for successful ITA rows (scripts/09)."""
    series = (
        successful["ita_degrees"]
        if "ita_degrees" in successful.columns
        else pd.Series(dtype=float)
    )
    return diagnostics._ita_stats(series)


def count_unassigned_broad_groups(frame: pd.DataFrame) -> int:
    """Count rows with neither an official nor an estimated broad group."""
    if frame is None or frame.empty:
        return 0
    official = frame.get("source_broad_mst_group", pd.Series(dtype=object)).map(
        read_text
    )
    estimated = frame.get(
        "estimated_broad_mst_group", pd.Series(dtype=object)
    ).map(read_text)
    return int(((official == "") & (estimated == "")).sum())


# -------------------------------------------------------------------
# Reproducible debug-visualization selection
# -------------------------------------------------------------------


def select_visualization_rows(
    processed: pd.DataFrame,
    *,
    seed: int,
    random_count: int,
    extreme_count: int,
) -> pd.DataFrame:
    """Pick a small, reproducible set of V2 success rows to visualize.

    Only valid V2 rows (landmarks available and a real mask) are eligible.
    The set is drawn from one seed so it is fully reproducible, and combines:
        - a random spread of examples,
        - the lowest mask-coverage cases,
        - the highest mask-coverage cases.
    Rows are never duplicated across the three groups.
    """
    columns = [
        "image_id",
        "image_path",
        "skin_ratio_percent",
        "ita_degrees",
        "visualization_reason",
    ]
    if processed is None or processed.empty:
        return pd.DataFrame(columns=columns)

    v2 = processed[
        (processed["landmarks_available"] == True)  # noqa: E712
        & processed["skin_ratio_percent"].notna()
    ].copy()
    if v2.empty:
        return pd.DataFrame(columns=columns)
    v2 = v2.sort_values("image_id", kind="stable").reset_index(drop=True)

    chosen: list[int] = []
    reasons: dict[int, str] = {}

    def take(index: int, reason: str) -> None:
        if index not in reasons:
            chosen.append(index)
            reasons[index] = reason

    rng = random.Random(seed)
    random_indices = list(range(len(v2)))
    rng.shuffle(random_indices)
    for index in random_indices[: max(random_count, 0)]:
        take(index, f"random_example_seed{seed}")

    ordered = v2.sort_values(
        ["skin_ratio_percent", "image_id"], kind="stable"
    ).index.tolist()
    for index in ordered[: max(extreme_count, 0)]:
        take(index, "lowest_mask_coverage")
    for index in ordered[::-1][: max(extreme_count, 0)]:
        take(index, "highest_mask_coverage")

    records = []
    for index in chosen:
        row = v2.loc[index]
        records.append(
            {
                "image_id": read_text(row.get("image_id")),
                "image_path": read_text(row.get("image_path")),
                "skin_ratio_percent": row.get("skin_ratio_percent"),
                "ita_degrees": row.get("ita_degrees"),
                "visualization_reason": reasons[index],
            }
        )
    return pd.DataFrame(records, columns=columns)


# -------------------------------------------------------------------
# Reporting
# -------------------------------------------------------------------


def print_counts(title: str, series: pd.Series, with_legend: bool = False) -> None:
    """Print a value-count table with a title."""
    print(title)
    if series is None or series.empty:
        print("  (none)")
        return
    for value, count in series.items():
        label = (
            describe_exclusion(str(value))
            if with_legend and value
            else ""
        )
        suffix = f"  {label}" if label else ""
        print(f"  {(value if str(value) else '(blank)'):<45}: {count}{suffix}")


def write_summary(
    output_path: Path,
    processed: pd.DataFrame,
    counts: dict[str, object],
    ita_stats: dict[str, object],
    visualization_selection: pd.DataFrame,
) -> None:
    """Write the candidate-pool summary (counts + grouped + ITA tables)."""
    sections: list[pd.DataFrame] = []

    def add(section: str, frame: pd.DataFrame) -> None:
        block = frame.copy()
        block.insert(0, "section", section)
        sections.append(block)

    add(
        "candidate_pool_counts",
        pd.DataFrame(
            {
                "metric": list(counts.keys()),
                "value": [str(value) for value in counts.values()],
            }
        ),
    )
    add("processed_by_status", summarize_processed(processed))
    add("processed_by_exclusion", summarize_by_exclusion(processed))
    add("processed_by_group", summarize_by_group(processed))
    add(
        "ita_continuous_summary",
        pd.DataFrame(
            {
                "metric": list(ita_stats.keys()),
                "value": [str(value) for value in ita_stats.values()],
            }
        ),
    )
    if visualization_selection is not None and not visualization_selection.empty:
        add("visualization_selection", visualization_selection)

    combined = pd.concat(sections, ignore_index=True) if sections else pd.DataFrame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Prepare the 650-image FairFace candidate pool end to end."""
    args = parse_arguments()

    if args.limit <= 0:
        print("ERROR: --limit must be a positive integer.")
        sys.exit(1)
    if not args.yunet_model.is_file():
        print(f"ERROR: YuNet model was not found: {args.yunet_model}")
        sys.exit(1)
    if not args.landmarker_model.is_file():
        print(
            f"ERROR: MediaPipe landmarker model was not found: "
            f"{args.landmarker_model}\nWithout it, V2 feature exclusion cannot "
            "run and every image would fall back to V1."
        )
        sys.exit(1)
    if not args.smoke_selection.is_file():
        print(
            f"ERROR: smoke-test selection was not found: {args.smoke_selection}\n"
            "It is needed only to confirm the 20 smoke-test images are not "
            "counted twice. Pass --smoke-selection if it is stored elsewhere."
        )
        sys.exit(1)

    print("=" * 72)
    print("FairFace candidate pool (frozen V2 pipeline, seed 42)")
    print("=" * 72)
    print(f"Image root  : {args.image_root}")
    print(f"Train CSV   : {args.train_csv}")
    print(f"Val CSV     : {args.val_csv}")
    print(f"Limit       : {args.limit}")
    print(f"Seed        : {args.seed}")
    print(f"Min skin px : {args.min_skin_pixels}")
    print()
    print("Selecting candidates (reusing scripts/12):")

    try:
        selection = build_selection_frame(args)
    except Exception as error:  # metadata/layout problems are fatal here
        print(f"ERROR: {error}")
        sys.exit(1)

    if selection.empty:
        print(
            "ERROR: no candidates were selected. Check the FairFace paths and "
            "that the images resolve under --image-root."
        )
        sys.exit(1)

    try:
        smoke_selection = pd.read_csv(args.smoke_selection)
    except Exception as error:
        print(f"ERROR: could not read the smoke-test selection ({error})")
        sys.exit(1)

    overlap = verify_smoke_overlap(selection, smoke_selection)
    if not overlap["selection_unique"]:
        print("ERROR: the candidate selection contains duplicate image IDs.")
        sys.exit(1)

    args.selection_output.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(args.selection_output, index=False)

    records = build_pipeline_records(selection, args.image_root)

    print()
    print("-" * 72)
    print("Smoke-test overlap check (do not count the 20 images twice):")
    print(f"  Selected candidates         : {overlap['selection_rows']}")
    print(f"  Selection unique by image_id: {overlap['selection_unique']}")
    print(f"  Smoke-test images           : {overlap['smoke_rows']}")
    print(
        f"  Smoke images inside the pool: "
        f"{overlap['smoke_images_in_selection']} (each exactly once)"
    )
    print(f"  Smoke images missing        : {overlap['smoke_images_missing']}")
    print("-" * 72)

    print()
    print("Running the frozen pipeline (reusing scripts/11)")
    processed = prepare_manifests.prepare_dataset(
        dataset_name=FAIRFACE_DATASET_NAME,
        manifest=records,
        dataset_root=args.image_root,
        metadata=None,
        yunet_model=args.yunet_model,
        landmarker_model=args.landmarker_model,
        minimum_skin_pixels=args.min_skin_pixels,
        score_threshold=args.score_threshold,
        estimated_rule=None,
        limit=0,
    )

    faced = int((processed["face_detected"] == True).sum())  # noqa: E712
    valid_v2 = int((processed["landmarks_available"] == True).sum())  # noqa: E712
    ita_successes = int(
        (processed["processing_status"].astype(str) == STATUS_SUCCESS).sum()
    )
    excluded = processed[
        processed["processing_status"].astype(str) == STATUS_EXCLUDED
    ]
    unassigned = count_unassigned_broad_groups(processed)

    counts: dict[str, object] = {
        "attempted_images": int(len(processed)),
        "faces_detected": faced,
        "valid_v2_outputs": valid_v2,
        "ita_successes": ita_successes,
        "exclusions_total": int(len(excluded)),
        "unassigned_broad_group_rows": unassigned,
    }

    successful = processed[
        processed["processing_status"].astype(str) == STATUS_SUCCESS
    ]
    ita_stats = ita_continuous_summary(successful)

    # ------------------------------------------------------------------
    # Reproducible debug visualizations (a selection, never every image).
    # ------------------------------------------------------------------
    visualization_selection = select_visualization_rows(
        processed,
        seed=args.seed,
        random_count=args.visualization_random_count,
        extreme_count=args.visualization_extreme_count,
    )
    args.visualizations_root.mkdir(parents=True, exist_ok=True)
    visualizations_written = 0
    for _, row in visualization_selection.iterrows():
        if smoke_visuals.generate_smoke_visualization(
            row,
            visualizations_root=args.visualizations_root,
            yunet_model=args.yunet_model,
            landmarker_model=args.landmarker_model,
            score_threshold=args.score_threshold,
        ):
            visualizations_written += 1

    # ------------------------------------------------------------------
    # Write outputs
    # ------------------------------------------------------------------
    args.processed_output.parent.mkdir(parents=True, exist_ok=True)
    processed.loc[:, list(MANIFEST_COLUMNS)].to_csv(
        args.processed_output, index=False
    )
    args.visualization_selection_output.parent.mkdir(parents=True, exist_ok=True)
    visualization_selection.to_csv(
        args.visualization_selection_output, index=False
    )
    write_summary(
        args.summary_output, processed, counts, ita_stats, visualization_selection
    )

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("Candidate-pool counts")
    print("=" * 72)
    print(f"Attempted images            : {counts['attempted_images']}")
    print(f"Faces detected              : {counts['faces_detected']}")
    print(f"Valid V2 outputs            : {counts['valid_v2_outputs']}")
    print(f"ITA successes               : {counts['ita_successes']}")
    print(f"Exclusions (all reasons)    : {counts['exclusions_total']}")
    print(f"Unassigned broad-group rows : {counts['unassigned_broad_group_rows']}")

    print()
    print("Exclusions by reason:")
    if excluded.empty:
        print("  (none)")
    else:
        print_counts("", excluded["exclusion_reason"].value_counts(), True)

    print()
    print("Continuous ITA (successful V2 rows only):")
    print(f"  count  : {ita_stats['count']}")
    print(f"  min    : {ita_stats['minimum_ita']}")
    print(f"  Q1     : {ita_stats['q1_ita']}")
    print(f"  median : {ita_stats['median_ita']}")
    print(f"  Q3     : {ita_stats['q3_ita']}")
    print(f"  max    : {ita_stats['maximum_ita']}")

    print()
    print("Debug visualizations (reproducible selection):")
    print(f"  Eligible V2 rows     : {int(len(visualization_selection))} selected")
    print(f"  PNGs written         : {visualizations_written}")
    if not visualization_selection.empty:
        for reason, count in (
            visualization_selection["visualization_reason"]
            .value_counts()
            .items()
        ):
            print(f"    {reason:<24}: {count}")

    print()
    print("Selected source diversity (used ONLY for sampling, not labels):")
    for column in (
        select_candidates.RACE_FIELD,
        select_candidates.GENDER_FIELD,
        select_candidates.AGE_FIELD,
    ):
        if column in selection.columns:
            print(f"  {column}:")
            for value, count in selection[column].value_counts().items():
                print(f"    {value if str(value) else '(blank)':<16}: {count}")

    print()
    print("Outputs (existing smoke-test outputs untouched):")
    print(f"  Selection                : {args.selection_output}")
    print(f"  Processed manifest       : {args.processed_output}")
    print(f"  Summary                  : {args.summary_output}")
    print(f"  Visualization selection  : {args.visualization_selection_output}")
    print(f"  Visualizations root      : {args.visualizations_root}")
    print()
    print("Notes:")
    print("  - FairFace race/gender/age were used only for source-image")
    print("    diversity; no MST group was inferred from them.")
    print("  - Official MST labels and broad MST groups are blank; no ITA-to-")
    print("    group threshold was invented. Rows with no estimated group were")
    print("    kept, not discarded, and no group-based cap was applied.")
    print("  - V1 fallback masks are excluded from the valid V2 outputs even")
    print("    when a numerical ITA was computed.")
    print("  - SCIN/MST-E were not processed; no distortion, split, or model")
    print("    was created; no raw image or pipeline module was modified.")


if __name__ == "__main__":
    main()
