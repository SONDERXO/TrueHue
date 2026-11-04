"""
13_fairface_smoke_test.py

Purpose:
    Run a small, reproducible 20-image FairFace smoke test through the *frozen*
    TrueHue pipeline and write isolated smoke-test artifacts. Nothing existing
    is overwritten, no thresholds are tuned, and no model is trained.

    Pipeline per image (unchanged, reused from scripts/11):
        YuNet face detection (single face only)
        -> largest-face BGR crop
        -> Skin Mask V2 (HSV/YCrCb + morphology + largest component +
           landmark eye/eyebrow/lip exclusion)
        -> CIELAB conversion of the selected skin pixels only
        -> mean L*, a*, b* and continuous ITA (degrees)

What this script reuses (no logic is copied):
    - scripts/12_select_fairface_candidates.py
        metadata loading, the stratified seed-42 sampler, and the output
        builder (which blanks official MST labels/groups and records
        ``pending_ita_processing`` / ``not_available_until_ita``).
    - scripts/11_prepare_training_manifests.py
        ``prepare_dataset`` / ``process_record`` (the frozen pipeline),
        ``compute_v2_skin_mask_with_margin`` (V2 feature exclusion), and
        ``resolve_image_path``.
    - src.face_detection.detect_faces._detect_face_boxes (YuNet, unchanged)
    - src.skin_masking.skin_mask.save_mask_visualization (2x2 review grid)
    - src.data_preparation.training_manifest (column contract + summaries)

What this script deliberately does NOT do:
    - No SCIN image is downloaded or processed.
    - No pipeline module (YuNet, Skin Mask V2, landmark exclusion, CIELAB,
      ITA) is modified.
    - No synthetic distortion is generated and no model is trained.
    - FairFace race/age/gender are used only for source-image diversity.
    - Official MST labels and broad MST groups are left blank; no ITA-to-group
      threshold is invented (no --estimated-group-rule is applied).
    - Rows with no estimated broad group are kept, not discarded.
    - V1 fallback masks (landmarks unavailable) are excluded from the valid
      V2 outputs and are never visualized as a V2 result.

Outputs (all smoke-test-specific; existing manifests are untouched):
    data/manifests/fairface_smoke_test_selection.csv
    data/manifests/fairface_smoke_test_processed_manifest.csv
    data/manifests/fairface_smoke_test_summary.csv
    outputs/fairface_smoke_test_visualizations/<image_id>_visualization.png

Run from the project root (point at the local FairFace copy):
    python scripts/13_fairface_smoke_test.py \
        --image-root "C:\\Users\\NYTHAN\\Downloads\\Dataset\\FairFace" \
        --train-csv "C:\\Users\\NYTHAN\\Downloads\\Dataset\\FairFace\\train_labels.csv" \
        --val-csv "C:\\Users\\NYTHAN\\Downloads\\Dataset\\FairFace\\val_labels.csv"

No network calls: the YuNet ONNX and MediaPipe face_landmarker.task models must
already exist locally (see src/utilities/config.py).
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import cv2
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
from src.face_detection.detect_faces import _detect_face_boxes  # noqa: E402
from src.skin_masking.skin_mask import save_mask_visualization  # noqa: E402
from src.utilities.config import get_config  # noqa: E402

# Reuse the existing stages instead of copying any of their logic.
select_candidates = importlib.import_module("12_select_fairface_candidates")
prepare_manifests = importlib.import_module("11_prepare_training_manifests")
mst_e_review = importlib.import_module("06_prepare_mst_e_review")

sanitise_filename = mst_e_review.sanitise_filename


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"

DEFAULT_SELECTION_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_smoke_test_selection.csv"
)
DEFAULT_PROCESSED_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_smoke_test_processed_manifest.csv"
)
DEFAULT_SUMMARY_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "fairface_smoke_test_summary.csv"
)
DEFAULT_VISUALIZATIONS_ROOT = (
    PROJECT_ROOT / "outputs" / "fairface_smoke_test_visualizations"
)

DEFAULT_YUNET_MODEL = PROJECT_ROOT / get_config().FACE_MODEL_PATH
DEFAULT_LANDMARKER_MODEL = PROJECT_ROOT / get_config().FACE_LANDMARKER_MODEL_PATH

#: Same 1,000-pixel minimum-skin rule and YuNet confidence as the pipeline.
DEFAULT_MINIMUM_SKIN_PIXELS = 1000
DEFAULT_SCORE_THRESHOLD = 0.85

#: The smoke test always selects 20 candidates with seed 42.
SMOKE_TEST_LIMIT = select_candidates.SMOKE_TEST_LIMIT
DEFAULT_SEED = select_candidates.DEFAULT_SEED

#: ``intended_use`` written for smoke-test rows so they are never mistaken for
#: real training data.
INTENDED_USE_SMOKE_TEST = "smoke_test"


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options, defaulting to the repo FairFace layout."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a reproducible 20-image FairFace smoke test through the frozen "
            "face -> Skin Mask V2 -> continuous ITA pipeline. Isolated outputs "
            "only; no training, no thresholds, no raw-image edits."
        )
    )
    parser.add_argument(
        "--image-root",
        type=Path,
        default=select_candidates.DEFAULT_IMAGE_ROOT,
        help=f"FairFace image root (default: {select_candidates.DEFAULT_IMAGE_ROOT})",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=select_candidates.DEFAULT_TRAIN_CSV,
        help=f"FairFace train metadata CSV (default: {select_candidates.DEFAULT_TRAIN_CSV})",
    )
    parser.add_argument(
        "--val-csv",
        type=Path,
        default=select_candidates.DEFAULT_VAL_CSV,
        help=f"FairFace validation metadata CSV (default: {select_candidates.DEFAULT_VAL_CSV})",
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
        default=SMOKE_TEST_LIMIT,
        help=f"Number of candidates to select (default: {SMOKE_TEST_LIMIT})",
    )
    parser.add_argument(
        "--selection-output",
        type=Path,
        default=DEFAULT_SELECTION_OUTPUT,
        help=f"Smoke-test selection CSV (default: {DEFAULT_SELECTION_OUTPUT})",
    )
    parser.add_argument(
        "--processed-output",
        type=Path,
        default=DEFAULT_PROCESSED_OUTPUT,
        help=f"Smoke-test processed manifest CSV (default: {DEFAULT_PROCESSED_OUTPUT})",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT,
        help=f"Smoke-test summary CSV (default: {DEFAULT_SUMMARY_OUTPUT})",
    )
    parser.add_argument(
        "--visualizations-root",
        type=Path,
        default=DEFAULT_VISUALIZATIONS_ROOT,
        help=(
            "Folder that receives the smoke-test review grids "
            f"(default: {DEFAULT_VISUALIZATIONS_ROOT})"
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
    return parser.parse_args()


# -------------------------------------------------------------------
# Candidate selection (reuses scripts/12)
# -------------------------------------------------------------------


def select_candidates_frame(args: argparse.Namespace) -> pd.DataFrame:
    """Return the reproducible smoke-test selection (official labels blank)."""
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
        selected, seed=args.seed, smoke_test=True
    )


def build_pipeline_records(selection: pd.DataFrame, image_root: Path) -> pd.DataFrame:
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
    records["intended_use"] = INTENDED_USE_SMOKE_TEST
    return records


# -------------------------------------------------------------------
# Visualization (reuses the frozen V2 mask + save_mask_visualization)
# -------------------------------------------------------------------


def generate_smoke_visualization(
    row: pd.Series,
    *,
    visualizations_root: Path,
    yunet_model: Path,
    landmarker_model: Path,
    score_threshold: float,
) -> bool:
    """Re-mask one valid V2 row and write its 2x2 review grid.

    Returns True when a PNG was written. Rows without a single detected face or
    without a real V2 mask (landmarks unavailable) are skipped.
    """
    image_path = Path(read_text(row.get("image_path")))
    if not image_path.is_file():
        return False

    image_id = read_text(row.get("image_id"))
    destination = (
        visualizations_root
        / f"{sanitise_filename(image_id)}_visualization.png"
    )

    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        return False

    boxes = _detect_face_boxes(image_bgr, yunet_model, score_threshold)
    if len(boxes) != 1:
        return False

    x, y, width, height = boxes[0]
    face_crop_bgr = image_bgr[y : y + height, x : x + width].copy()
    if face_crop_bgr.size == 0:
        return False

    mask_result = prepare_manifests.compute_v2_skin_mask_with_margin(
        face_crop_bgr=face_crop_bgr,
        image_bgr=image_bgr,
        face_box=(x, y, width, height),
        landmarker_model=landmarker_model,
    )
    if not mask_result.landmarks_available:
        return False
    if mask_result.mask is None or mask_result.mask.size == 0:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    save_mask_visualization(
        face_bgr=face_crop_bgr,
        candidate_mask=mask_result.candidate_mask,
        exclusion_mask=mask_result.exclusion_mask,
        final_mask=mask_result.mask,
        save_path=str(destination),
        landmarks_available=mask_result.landmarks_available,
    )
    return True


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
        label = describe_exclusion(str(value)) if value else "(none)"
        print(f"  {value if str(value) else '(blank)':<45}: {count}  {label}")


def write_summary(
    output_path: Path,
    processed: pd.DataFrame,
    counts: dict[str, int],
) -> None:
    """Write the smoke-test summary (pipeline counts + grouped tables)."""
    sections: list[pd.DataFrame] = []

    def add(section: str, frame: pd.DataFrame) -> None:
        block = frame.copy()
        block.insert(0, "section", section)
        sections.append(block)

    add(
        "smoke_test_counts",
        pd.DataFrame(
            {
                "metric": list(counts.keys()),
                "value": list(counts.values()),
            }
        ),
    )
    add("processed_by_status", summarize_processed(processed))
    add("processed_by_exclusion", summarize_by_exclusion(processed))
    add("processed_by_group", summarize_by_group(processed))

    combined = pd.concat(sections, ignore_index=True) if sections else pd.DataFrame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Run the 20-image FairFace smoke test end to end."""
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

    print("=" * 72)
    print("FairFace smoke test (20 images, frozen V2 pipeline, seed 42)")
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
        selection = select_candidates_frame(args)
    except Exception as error:  # metadata/layout problems are fatal here
        print(f"ERROR: {error}")
        sys.exit(1)

    if selection.empty:
        print(
            "ERROR: no candidates were selected. Check the FairFace paths and "
            "that the images resolve under --image-root."
        )
        sys.exit(1)

    args.selection_output.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(args.selection_output, index=False)

    records = build_pipeline_records(selection, args.image_root)

    print()
    print("-" * 72)
    print("Running the frozen pipeline (reusing scripts/11)")
    print("-" * 72)
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
    counts = {
        "attempted_images": int(len(processed)),
        "faces_detected": faced,
        "valid_v2_outputs": valid_v2,
        "ita_successes": ita_successes,
    }

    # ------------------------------------------------------------------
    # Visualizations (up to 20): only valid V2 rows, never V1 fallbacks.
    # ------------------------------------------------------------------
    args.visualizations_root.mkdir(parents=True, exist_ok=True)
    v2_rows = processed[processed["landmarks_available"] == True]  # noqa: E712
    visualizations_written = 0
    for _, row in v2_rows.iterrows():
        if generate_smoke_visualization(
            row,
            visualizations_root=args.visualizations_root,
            yunet_model=args.yunet_model,
            landmarker_model=args.landmarker_model,
            score_threshold=args.score_threshold,
        ):
            visualizations_written += 1

    # ------------------------------------------------------------------
    # Write isolated outputs
    # ------------------------------------------------------------------
    args.processed_output.parent.mkdir(parents=True, exist_ok=True)
    processed.loc[:, list(MANIFEST_COLUMNS)].to_csv(
        args.processed_output, index=False
    )
    write_summary(args.summary_output, processed, counts)

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("Smoke-test counts")
    print("=" * 72)
    print(f"Attempted images   : {counts['attempted_images']}")
    print(f"Faces detected     : {counts['faces_detected']}")
    print(f"Valid V2 outputs   : {counts['valid_v2_outputs']}")
    print(f"ITA successes      : {counts['ita_successes']}")
    print(f"Visualizations     : {visualizations_written}")

    excluded = processed[
        processed["processing_status"].astype(str) == STATUS_EXCLUDED
    ]
    print()
    print("Exclusions by reason:")
    if excluded.empty:
        print("  (none)")
    else:
        print_counts("", excluded["exclusion_reason"].value_counts())

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
    print("Outputs (existing manifests untouched):")
    print(f"  Selection            : {args.selection_output}")
    print(f"  Processed manifest   : {args.processed_output}")
    print(f"  Summary              : {args.summary_output}")
    print(f"  Visualizations root  : {args.visualizations_root}")
    print()
    print("Notes:")
    print("  - SCIN processing is paused; no SCIN image was downloaded or used.")
    print("  - Official MST labels and broad MST groups are blank; no ITA-to-")
    print("    group threshold was invented. Rows with no estimated group were")
    print("    kept, not discarded.")
    print("  - V1 fallback masks are excluded from the valid V2 outputs.")
    print("  - No detector, mask, CIELAB, or ITA code was modified; no model")
    print("    was trained and no raw image was modified.")


if __name__ == "__main__":
    main()
