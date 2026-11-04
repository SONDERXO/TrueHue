"""
11_prepare_training_manifests.py

Purpose:
    Prepare the training-dataset manifests for the correction model. For every
    FairFace and SCIN image listed in the dataset inventories, this script runs
    the *frozen* TrueHue pipeline unchanged:

        YuNet face detection (single face only)
        -> largest-face BGR crop
        -> Skin Mask V2 (HSV/YCrCb, morphology, largest component,
           landmark eye/eyebrow/lip exclusion)
        -> CIELAB conversion of the selected skin pixels only
        -> mean L*, a*, b* and ITA (degrees)

    Each image becomes one row that records its measurement, processing
    status, the reason it was excluded (if it was), and — where a documented
    source exists — its broad MST group. Nothing is trained here and no raw
    image is modified.

Exclusions (single-face, V2-only pipeline):
    - corrupt / unreadable image
    - no face detected
    - more than one face detected (the app supports a single face)
    - skin mask could not be created
    - Skin Mask V2 feature exclusion unavailable -> V1 fallback (not allowed)
    - fewer than --min-skin-pixels valid skin pixels
    - ITA could not be computed

Group assignment (never invented here):
    - SCIN: the official SCIN MST label (from --scin-metadata) is ground truth
            and maps to its documented broad group (official_scin_mst).
    - FairFace: no official MST label exists, so source_mst_label stays empty.
            A broad group is only recorded as an *estimate from ITA* when a
            documented rule file is supplied via --estimated-group-rule
            (estimated_from_ita). Otherwise it is left blank.
    Official labels and ITA estimates are kept strictly separate.

Inputs (built by scripts/04_build_dataset_inventory.py and 05):
    data/manifests/fairface_inventory.csv
    data/manifests/scin_inventory.csv
    optional: a documented ITA broad-group rule JSON (see docs)

Outputs (written to data/manifests/ by default):
    fairface_processed_manifest.csv      every processed FairFace image
    scin_processed_manifest.csv          every processed SCIN image
    training_candidates_manifest.csv     clean, capped subset for training
    training_data_preparation_summary.csv  counts for the run

Run from the project root:
    python scripts/11_prepare_training_manifests.py
    python scripts/11_prepare_training_manifests.py --limit 20
    python scripts/11_prepare_training_manifests.py --cap-per-group 500 \
        --estimated-group-rule configs/broad_group_rule.json

This script makes no network calls: the YuNet ONNX model and the MediaPipe
face_landmarker.task model must already exist locally.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation.dataset_inventory import (  # noqa: E402
    load_inventory_manifest,
    load_label_metadata,
    resolve_source_mst_label,
)
from src.data_preparation.training_manifest import (  # noqa: E402
    FAIRFACE_DATASET_NAME,
    INTENDED_USE_TRAINING,
    MANIFEST_COLUMNS,
    SCIN_DATASET_NAME,
    build_processed_manifest,
    build_processed_row,
    classify_exclusion,
    describe_exclusion,
    load_estimated_group_rule,
    read_text,
    select_training_candidates,
    summarize_by_exclusion,
    summarize_by_group,
    summarize_processed,
    validate_training_dataset_names,
)
from src.face_detection.detect_faces import _detect_face_boxes  # noqa: E402
from src.ita_estimation.compute_ita import compute_masked_lab_statistics  # noqa: E402
from src.skin_masking.landmark_exclusion import (  # noqa: E402
    build_feature_exclusion_mask,
    detect_face_landmarks,
)
from src.skin_masking.skin_mask import (  # noqa: E402
    SkinMaskResult,
    compute_skin_mask_result,
    create_candidate_mask_bgr,
    keep_largest_connected_component,
)
from src.utilities.config import get_config  # noqa: E402


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"
DEFAULT_FAIRFACE_INVENTORY = DEFAULT_MANIFEST_DIR / "fairface_inventory.csv"
DEFAULT_SCIN_INVENTORY = DEFAULT_MANIFEST_DIR / "scin_inventory.csv"

DEFAULT_FAIRFACE_ROOT = PROJECT_ROOT / "data" / "raw" / "fairface"
DEFAULT_SCIN_ROOT = PROJECT_ROOT / "data" / "raw" / "scin"
DEFAULT_SCIN_METADATA = DEFAULT_SCIN_ROOT / "scin_metadata.csv"

DEFAULT_FAIRFACE_OUTPUT = DEFAULT_MANIFEST_DIR / "fairface_processed_manifest.csv"
DEFAULT_SCIN_OUTPUT = DEFAULT_MANIFEST_DIR / "scin_processed_manifest.csv"
DEFAULT_CANDIDATES_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "training_candidates_manifest.csv"
)
DEFAULT_SUMMARY_OUTPUT = (
    DEFAULT_MANIFEST_DIR / "training_data_preparation_summary.csv"
)

DEFAULT_YUNET_MODEL = PROJECT_ROOT / get_config().FACE_MODEL_PATH
DEFAULT_LANDMARKER_MODEL = PROJECT_ROOT / get_config().FACE_LANDMARKER_MODEL_PATH

#: Same 1,000-pixel minimum-skin rule as the rest of the pipeline.
DEFAULT_MINIMUM_SKIN_PIXELS = 1000

#: Same YuNet confidence used by the pilot scripts.
DEFAULT_SCORE_THRESHOLD = 0.85

#: Pad fractions (of the larger face-box side) tried, in order, when MediaPipe
#: Face Landmarker fails on the tight YuNet crop. ``None`` means the full
#: frame. Kept identical to scripts/05.
FACE_MARGIN_FRACTIONS: tuple[float | None, ...] = (0.0, 0.5, 1.5, None)


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the frozen face -> Skin Mask V2 -> ITA pipeline over the "
            "FairFace and SCIN inventories and write the training manifests. "
            "No training, no thresholds, no raw-image edits."
        )
    )
    parser.add_argument(
        "--fairface-inventory",
        type=Path,
        default=DEFAULT_FAIRFACE_INVENTORY,
        help=f"FairFace inventory CSV (default: {DEFAULT_FAIRFACE_INVENTORY})",
    )
    parser.add_argument(
        "--scin-inventory",
        type=Path,
        default=DEFAULT_SCIN_INVENTORY,
        help=f"SCIN inventory CSV (default: {DEFAULT_SCIN_INVENTORY})",
    )
    parser.add_argument(
        "--fairface-root",
        type=Path,
        default=DEFAULT_FAIRFACE_ROOT,
        help=(
            "FairFace image folder, used only when a stored image path no "
            f"longer exists (default: {DEFAULT_FAIRFACE_ROOT})"
        ),
    )
    parser.add_argument(
        "--scin-root",
        type=Path,
        default=DEFAULT_SCIN_ROOT,
        help=(
            "SCIN image folder, used only when a stored image path no longer "
            f"exists (default: {DEFAULT_SCIN_ROOT})"
        ),
    )
    parser.add_argument(
        "--scin-metadata",
        type=Path,
        default=DEFAULT_SCIN_METADATA,
        help=(
            "Official SCIN metadata CSV holding the Monk Skin Tone label. "
            "Pass an empty string to skip official SCIN labels "
            f"(default: {DEFAULT_SCIN_METADATA})"
        ),
    )
    parser.add_argument(
        "--scin-key-column",
        default="image_id",
        help="SCIN metadata column holding the image identifier (default: image_id)",
    )
    parser.add_argument(
        "--scin-mst-column",
        default="monk_skin_tone",
        help=(
            "SCIN metadata column holding the Monk Skin Tone label 1-10 "
            "(default: monk_skin_tone)"
        ),
    )
    parser.add_argument(
        "--estimated-group-rule",
        type=Path,
        default=None,
        help=(
            "Optional documented JSON rule mapping ITA to a broad group. "
            "Without it, FairFace rows get no estimated broad group."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_MANIFEST_DIR,
        help=f"Where manifests are written (default: {DEFAULT_MANIFEST_DIR})",
    )
    parser.add_argument(
        "--fairface-output",
        type=Path,
        default=None,
        help=f"Override the FairFace processed manifest path (default: {DEFAULT_FAIRFACE_OUTPUT})",
    )
    parser.add_argument(
        "--scin-output",
        type=Path,
        default=None,
        help=f"Override the SCIN processed manifest path (default: {DEFAULT_SCIN_OUTPUT})",
    )
    parser.add_argument(
        "--candidates-output",
        type=Path,
        default=None,
        help=(
            "Override the training-candidates manifest path "
            f"(default: {DEFAULT_CANDIDATES_OUTPUT})"
        ),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=None,
        help=f"Override the summary CSV path (default: {DEFAULT_SUMMARY_OUTPUT})",
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
            "Local MediaPipe face_landmarker.task model used for feature "
            f"exclusion (default: {DEFAULT_LANDMARKER_MODEL})"
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
        "--cap-per-group",
        type=int,
        default=0,
        help=(
            "Keep at most N training candidates per dataset and broad group "
            "(0 = no cap). Selection is deterministic (dataset, then image_id)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N rows of each inventory (0 = all).",
    )
    return parser.parse_args()


# -------------------------------------------------------------------
# Inventory / metadata helpers
# -------------------------------------------------------------------


def load_split_manifest(
    csv_path: Path, dataset_name: str
) -> pd.DataFrame:
    """Read one inventory manifest and keep only its own dataset rows.

    Raises
    ------
    FileNotFoundError
        If the inventory CSV does not exist.
    ValueError
        If the CSV is empty, missing required columns, or marked for MST-E.
    """
    manifest = load_inventory_manifest(csv_path)
    if manifest.empty:
        raise ValueError(f"the inventory manifest is empty: {csv_path}")

    names = sorted(set(manifest["dataset_name"].astype(str)))
    validate_training_dataset_names(names)

    own = manifest[manifest["dataset_name"].astype(str) == dataset_name].copy()
    if own.empty:
        raise ValueError(
            f"the inventory {csv_path} contains no {dataset_name!r} rows "
            f"(dataset_name values found: {names})."
        )
    return own


def build_scin_label_lookup(metadata_path: Path | None, key_column: str, label_column: str):
    """Load the official SCIN MST labels, or ``None`` when unavailable.

    Returns the :class:`LabelMetadata` mapping used to attach official labels.
    A missing file is reported and treated as "no labels" rather than a hard
    error, so a FairFace-only run still works.
    """
    if metadata_path is None or str(metadata_path).strip() == "":
        print("SCIN metadata     : not supplied; SCIN rows will have no official MST label")
        return None

    if not Path(metadata_path).is_file():
        print(
            f"SCIN metadata     : file not found ({metadata_path}); SCIN rows "
            "will have no official MST label"
        )
        return None

    try:
        metadata = load_label_metadata(
            metadata_path,
            key_column=key_column,
            label_column=label_column,
            dataset_name=SCIN_DATASET_NAME,
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"SCIN metadata     : could not be loaded ({error})")
        return None

    print(f"SCIN metadata     : {Path(metadata_path).name}")
    return metadata


# -------------------------------------------------------------------
# Crops, landmarks, and Skin Mask V2 (identical to scripts/05)
# -------------------------------------------------------------------


def resolve_image_path(
    stored_path: str, relative_path: str, dataset_root: Path
) -> Path:
    """Turn a manifest path into a usable local path (see scripts/05)."""
    candidate = Path(stored_path) if stored_path else Path(relative_path)
    if candidate.is_file():
        return candidate
    fallback = dataset_root / relative_path if relative_path else candidate
    if fallback.is_file():
        return fallback
    return candidate


def margined_crop(
    image_bgr: np.ndarray,
    face_box: tuple[int, int, int, int],
    fraction: float | None,
) -> tuple[np.ndarray, int, int]:
    """Return a BGR crop around ``face_box`` plus its top-left offset."""
    x, y, w, h = (int(value) for value in face_box)
    if fraction is None:
        return image_bgr, 0, 0
    pad = int(fraction * max(w, h))
    ox = max(0, x - pad)
    oy = max(0, y - pad)
    right = min(image_bgr.shape[1], x + w + pad)
    bottom = min(image_bgr.shape[0], y + h + pad)
    return image_bgr[oy:bottom, ox:right], int(ox), int(oy)


def detect_landmarks_with_margin(
    image_bgr: np.ndarray,
    face_box: tuple[int, int, int, int],
    landmarker_model: Path,
) -> tuple[np.ndarray | None, float | None, str]:
    """Find landmarks over progressively padded crops (see scripts/05)."""
    x, y, w, h = (int(value) for value in face_box)
    for fraction in FACE_MARGIN_FRACTIONS:
        crop_bgr, ox, oy = margined_crop(image_bgr, (x, y, w, h), fraction)
        if crop_bgr.size == 0:
            continue
        detection = detect_face_landmarks(
            crop_bgr, model_path=str(landmarker_model)
        )
        if detection.landmarks_available and detection.landmarks is not None:
            offset = np.array([x - ox, y - oy], dtype=np.float64)
            landmarks_tight = detection.landmarks - offset
            label = (
                "full-frame"
                if fraction is None
                else f"{int(fraction * 100)}% margin"
            )
            status = (
                f"{detection.status} (detected on the {label} crop, remapped "
                "to the YuNet face crop)"
            )
            return landmarks_tight, fraction, status
    return None, None, "no face landmarks in any crop framing"


def compute_v2_skin_mask_with_margin(
    face_crop_bgr: np.ndarray,
    image_bgr: np.ndarray,
    face_box: tuple[int, int, int, int],
    landmarker_model: Path,
) -> SkinMaskResult:
    """Run Skin Mask V2 feature exclusion on padded crops (see scripts/05)."""
    landmarks, _, status = detect_landmarks_with_margin(
        image_bgr, face_box, landmarker_model
    )
    if landmarks is None:
        return compute_skin_mask_result(
            face_crop_bgr,
            exclude_features=True,
            model_path=str(landmarker_model),
            download_landmarker_if_missing=False,
        )
    candidate = create_candidate_mask_bgr(face_crop_bgr)
    largest = keep_largest_connected_component(candidate)
    exclusion = build_feature_exclusion_mask(face_crop_bgr, landmarks, dilation=0)
    final_mask = cv2.bitwise_and(largest, cv2.bitwise_not(exclusion))
    return SkinMaskResult(
        mask=final_mask,
        candidate_mask=candidate,
        exclusion_mask=exclusion,
        landmarks_available=True,
        status="skin mask computed with feature exclusion: " + status,
    )


# -------------------------------------------------------------------
# Per-image processing
# -------------------------------------------------------------------


def compute_versioned_skin_mask(face_crop_bgr, image_bgr, face_box, landmarker_model,
                                mask_version="v2", baseline=None):
    """Explicit version selection; keep the historical V2 helper unchanged."""
    if mask_version not in ("v2", "v2_complete_mouth_v1"):
        raise ValueError(f"Unsupported mask version: {mask_version}")
    if baseline is None:
        baseline = compute_v2_skin_mask_with_margin(face_crop_bgr, image_bgr, face_box, landmarker_model)
    if mask_version == "v2" or not baseline.landmarks_available:
        return baseline
    from src.skin_masking.mouth_exclusion import exclude_complete_mouth
    landmarks, _, _ = detect_landmarks_with_margin(image_bgr, face_box, landmarker_model)
    if landmarks is None or not np.array_equal(
        build_feature_exclusion_mask(face_crop_bgr, landmarks, dilation=0), baseline.exclusion_mask
    ):
        raise ValueError("Complete-mouth landmark geometry unavailable or inconsistent")
    final, mouth = exclude_complete_mouth(baseline.mask, landmarks)
    return SkinMaskResult(mask=final, candidate_mask=baseline.candidate_mask,
        exclusion_mask=cv2.bitwise_or(baseline.exclusion_mask, mouth),
        landmarks_available=True, status="v2_complete_mouth_v1: " + baseline.status)


def process_record(
    record,
    *,
    dataset_name: str,
    source_mst_label: object,
    source_label: object,
    dataset_root: Path,
    yunet_model: Path,
    landmarker_model: Path,
    minimum_skin_pixels: int,
    score_threshold: float,
    estimated_rule,
    mask_version: str = "v2",
) -> dict:
    """Run detection, masking, and ITA for one inventory row.

    A failure at any stage is recorded as an exclusion; the remaining images
    are always processed. The returned dict has exactly
    :data:`MANIFEST_COLUMNS`.
    """
    if mask_version not in ("v2", "v2_complete_mouth_v1"):
        raise ValueError(f"Unsupported mask version: {mask_version}")
    relative_path = read_text(record.get("relative_path") if isinstance(record, dict) else getattr(record, "relative_path", ""))
    stored_path = read_text(record.get("image_path") if isinstance(record, dict) else getattr(record, "image_path", ""))
    image_id = read_text(record.get("image_id") if isinstance(record, dict) else getattr(record, "image_id", ""))
    intended_use = read_text(
        record.get("intended_use") if isinstance(record, dict) else getattr(record, "intended_use", INTENDED_USE_TRAINING)
    ) or INTENDED_USE_TRAINING

    image_path = resolve_image_path(stored_path, relative_path, dataset_root)

    face_count = 0
    face_detected: object = None
    landmarks_available: object = None
    skin_pixels: object = None
    skin_ratio_percent: object = None
    mean_l = mean_a = mean_b = ita = None
    ita_valid = False
    mask_created = False

    image_bgr = cv2.imread(str(image_path))
    image_loaded = image_bgr is not None

    if image_loaded:
        boxes = _detect_face_boxes(image_bgr, yunet_model, score_threshold)
        face_count = len(boxes)
        face_detected = face_count > 0

        if face_count == 1:
            x, y, face_width, face_height = boxes[0]
            face_crop_bgr = image_bgr[
                y : y + face_height, x : x + face_width
            ].copy()
            if face_crop_bgr.size > 0:
                mask_result = compute_v2_skin_mask_with_margin(
                    face_crop_bgr=face_crop_bgr,
                    image_bgr=image_bgr,
                    face_box=(x, y, face_width, face_height),
                    landmarker_model=landmarker_model,
                )
                if mask_version != "v2":
                    mask_result = compute_versioned_skin_mask(
                        face_crop_bgr, image_bgr, (x, y, face_width, face_height),
                        landmarker_model, mask_version, baseline=mask_result,
                    )
                landmarks_available = bool(mask_result.landmarks_available)
                mask_created = (
                    mask_result.mask is not None and mask_result.mask.size > 0
                )
                if mask_created:
                    skin_pixels = int(np.count_nonzero(mask_result.mask > 0))
                    face_area_pixels = int(face_width) * int(face_height)
                    skin_ratio_percent = (
                        round((skin_pixels / face_area_pixels) * 100, 2)
                        if face_area_pixels > 0
                        else 0.0
                    )
                    statistics = compute_masked_lab_statistics(
                        face_bgr=face_crop_bgr,
                        skin_mask=mask_result.mask,
                        minimum_skin_pixels=minimum_skin_pixels,
                    )
                    mean_l = statistics["mean_l_star"]
                    mean_a = statistics["mean_a_star"]
                    mean_b = statistics["mean_b_star"]
                    ita = statistics["ita_degrees"]
                    ita_valid = bool(statistics["valid"])

    exclusion_reason = classify_exclusion(
        image_loaded=image_loaded,
        face_count=face_count,
        mask_created=mask_created,
        landmarks_available=bool(landmarks_available),
        skin_pixels=skin_pixels,
        ita_valid=ita_valid,
        minimum_skin_pixels=minimum_skin_pixels,
    )

    row = build_processed_row(
        dataset_name=dataset_name,
        image_id=image_id,
        image_path=image_path.as_posix(),
        source_label=source_label,
        source_mst_label=source_mst_label,
        estimated_rule=estimated_rule,
        face_detected=face_detected,
        landmarks_available=landmarks_available,
        skin_pixels=skin_pixels,
        skin_ratio_percent=skin_ratio_percent,
        mean_l_star=mean_l,
        mean_a_star=mean_a,
        mean_b_star=mean_b,
        ita_degrees=ita,
        exclusion_reason=exclusion_reason,
        intended_use=intended_use,
    )
    return row


def prepare_dataset(
    *,
    dataset_name: str,
    manifest: pd.DataFrame,
    dataset_root: Path,
    metadata,
    yunet_model: Path,
    landmarker_model: Path,
    minimum_skin_pixels: int,
    score_threshold: float,
    estimated_rule,
    limit: int,
) -> pd.DataFrame:
    """Process every row of one dataset inventory into manifest rows."""
    records = manifest
    if limit and limit > 0:
        records = records.head(limit)

    rows: list[dict] = []
    total = len(records)
    for index, record in enumerate(records.itertuples(index=False), start=1):
        record_dict = record._asdict() if hasattr(record, "_asdict") else dict(record)
        relative_path = read_text(record_dict.get("relative_path"))
        print(f"  [{index}/{total}] {dataset_name}: {relative_path}")

        label, _label_source, _reason, _extra = resolve_source_mst_label(
            dataset_name, relative_path, metadata
        )
        source_label = "" if label is None else str(label)

        try:
            row = process_record(
                record_dict,
                dataset_name=dataset_name,
                source_mst_label=label,
                source_label=source_label,
                dataset_root=dataset_root,
                yunet_model=yunet_model,
                landmarker_model=landmarker_model,
                minimum_skin_pixels=minimum_skin_pixels,
                score_threshold=score_threshold,
                estimated_rule=estimated_rule,
            )
        except Exception as error:  # one bad image must not stop the batch
            row = build_processed_row(
                dataset_name=dataset_name,
                image_id=read_text(record_dict.get("image_id")),
                image_path=read_text(record_dict.get("image_path")),
                source_label=source_label,
                source_mst_label=label,
                estimated_rule=estimated_rule,
                exclusion_reason=f"unexpected_error: {error}",
            )
        rows.append(row)

    return build_processed_manifest(rows)


# -------------------------------------------------------------------
# Reporting
# -------------------------------------------------------------------


def print_group_summary(title: str, summary: pd.DataFrame) -> None:
    """Print one summary table, or a note when it is empty."""
    print()
    print(title)
    if summary.empty:
        print("  (no rows)")
        return
    print(summary.to_string(index=False))


def write_summary(
    output_path: Path,
    processed: pd.DataFrame,
    candidates: pd.DataFrame,
) -> None:
    """Write the combined summary tables to one CSV with section headers."""
    sections: list[pd.DataFrame] = []

    def add(section: str, frame: pd.DataFrame) -> None:
        block = frame.copy()
        block.insert(0, "section", section)
        sections.append(block)

    add("processed_by_status", summarize_processed(processed))
    add("processed_by_exclusion", summarize_by_exclusion(processed))
    add("processed_by_group", summarize_by_group(processed))
    add("candidates_by_dataset", candidates.groupby("dataset_name").size().reset_index(name="count"))
    add("candidates_by_group", summarize_by_group(candidates))

    combined = pd.concat(sections, ignore_index=True) if sections else pd.DataFrame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Process FairFace and SCIN and write the three training manifests."""
    args = parse_arguments()

    if args.min_skin_pixels <= 0:
        print("ERROR: --min-skin-pixels must be a positive integer.")
        sys.exit(1)
    if not args.yunet_model.is_file():
        print(
            f"ERROR: YuNet model was not found: {args.yunet_model}\n"
            "Place face_detection_yunet_2023mar.onnx there, or pass "
            "--yunet-model. This script never downloads models."
        )
        sys.exit(1)
    if not args.landmarker_model.is_file():
        print(
            f"ERROR: MediaPipe landmarker model was not found: "
            f"{args.landmarker_model}\n"
            "Skin Mask V2 feature exclusion cannot run without it, and falling "
            "back to V1 would exclude every image. Place face_landmarker.task "
            "there, or pass --landmarker-model."
        )
        sys.exit(1)

    estimated_rule = None
    if args.estimated_group_rule is not None:
        try:
            estimated_rule = load_estimated_group_rule(args.estimated_group_rule)
        except (FileNotFoundError, ValueError) as error:
            print(f"ERROR: {error}")
            sys.exit(1)

    try:
        fairface_manifest = load_split_manifest(
            args.fairface_inventory, FAIRFACE_DATASET_NAME
        )
        scin_manifest = load_split_manifest(args.scin_inventory, SCIN_DATASET_NAME)
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}")
        print(
            "Build the inventories first with "
            "scripts/04_build_dataset_inventory.py."
        )
        sys.exit(1)

    scin_metadata = build_scin_label_lookup(
        args.scin_metadata, args.scin_key_column, args.scin_mst_column
    )

    print("=" * 72)
    print("Prepare training manifests (FairFace + SCIN, frozen V2 pipeline)")
    print("=" * 72)
    print(f"FairFace inventory : {args.fairface_inventory}")
    print(f"SCIN inventory     : {args.scin_inventory}")
    print(f"FairFace images    : {len(fairface_manifest)}")
    print(f"SCIN images        : {len(scin_manifest)}")
    print(f"Estimated rule     : {estimated_rule['name'] if estimated_rule else 'not provided'}")
    print(f"Cap per group      : {args.cap_per_group if args.cap_per_group > 0 else 'none'}")
    print(f"Min skin pixels    : {args.min_skin_pixels}")
    print()

    print("-" * 72)
    print(f"Processing {FAIRFACE_DATASET_NAME}")
    print("-" * 72)
    fairface_processed = prepare_dataset(
        dataset_name=FAIRFACE_DATASET_NAME,
        manifest=fairface_manifest,
        dataset_root=args.fairface_root,
        metadata=None,
        yunet_model=args.yunet_model,
        landmarker_model=args.landmarker_model,
        minimum_skin_pixels=args.min_skin_pixels,
        score_threshold=args.score_threshold,
        estimated_rule=estimated_rule,
        limit=args.limit,
    )

    print()
    print("-" * 72)
    print(f"Processing {SCIN_DATASET_NAME}")
    print("-" * 72)
    scin_processed = prepare_dataset(
        dataset_name=SCIN_DATASET_NAME,
        manifest=scin_manifest,
        dataset_root=args.scin_root,
        metadata=scin_metadata,
        yunet_model=args.yunet_model,
        landmarker_model=args.landmarker_model,
        minimum_skin_pixels=args.min_skin_pixels,
        score_threshold=args.score_threshold,
        estimated_rule=estimated_rule,
        limit=args.limit,
    )

    processed = pd.concat(
        [fairface_processed, scin_processed], ignore_index=True
    )
    candidates = select_training_candidates(processed, args.cap_per_group)

    # ------------------------------------------------------------------
    # Write outputs
    # ------------------------------------------------------------------
    output_dir: Path = args.output_dir
    fairface_output = args.fairface_output or (output_dir / DEFAULT_FAIRFACE_OUTPUT.name)
    scin_output = args.scin_output or (output_dir / DEFAULT_SCIN_OUTPUT.name)
    candidates_output = args.candidates_output or (
        output_dir / DEFAULT_CANDIDATES_OUTPUT.name
    )
    summary_output = args.summary_output or (output_dir / DEFAULT_SUMMARY_OUTPUT.name)

    for path in (fairface_output, scin_output, candidates_output, summary_output):
        path.parent.mkdir(parents=True, exist_ok=True)

    fairface_processed.loc[:, list(MANIFEST_COLUMNS)].to_csv(
        fairface_output, index=False
    )
    scin_processed.loc[:, list(MANIFEST_COLUMNS)].to_csv(scin_output, index=False)
    candidates.loc[:, list(MANIFEST_COLUMNS)].to_csv(candidates_output, index=False)
    write_summary(summary_output, processed, candidates)

    # ------------------------------------------------------------------
    # Console report
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("Training data preparation complete")
    print("=" * 72)
    print(f"FairFace processed rows : {len(fairface_processed)}")
    print(f"SCIN processed rows     : {len(scin_processed)}")
    print(f"Training candidates     : {len(candidates)}")

    print_group_summary(
        "Processing status by dataset:", summarize_processed(processed)
    )
    print_group_summary(
        "Exclusions by dataset and reason (with descriptions):",
        summarize_by_exclusion(processed),
    )
    print_group_summary(
        "Broad groups by dataset and assignment source:",
        summarize_by_group(processed),
    )

    print()
    print("Exclusion reason legend:")
    excluded = processed[
        processed["processing_status"].astype(str) == "excluded"
    ]
    if excluded.empty:
        print("  (no exclusions)")
    else:
        for reason, count in excluded["exclusion_reason"].value_counts().items():
            print(f"  {count:>6}  {reason}: {describe_exclusion(str(reason))}")

    print()
    print("Outputs:")
    print(f"  FairFace processed manifest : {fairface_output}")
    print(f"  SCIN processed manifest     : {scin_output}")
    print(f"  Training candidates manifest: {candidates_output}")
    print(f"  Summary CSV                 : {summary_output}")
    print()
    print("Notes:")
    print("  - MST-E was not processed: it is evaluation/calibration only.")
    print("  - Official labels (official_scin_mst) and ITA estimates")
    print("    (estimated_from_ita) are recorded separately and never mixed.")
    print("  - No feature was synthesised, no model was trained, and no raw")
    print("    image was modified.")


if __name__ == "__main__":
    main()
