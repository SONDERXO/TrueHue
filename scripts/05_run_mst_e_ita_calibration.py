"""
05_run_mst_e_ita_calibration.py

Purpose:
    Run the frozen pilot pipeline over the MST-E inventory and record one row
    of ITA measurements per image, next to the *ground-truth* MST label from
    the official dataset metadata. This is preparation for ITA-to-MST
    calibration, not calibration itself.

    Per image:
        YuNet face detection
        -> largest-face BGR crop
        -> Skin Mask V2 (frozen: HSV/YCrCb, morphology, largest component,
           landmark eye/eyebrow/lip exclusion)
        -> CIELAB conversion of the selected skin pixels only
        -> mean L*, a*, b* and ITA (degrees)

    Landmark framing (crop-margin fix, recorded in docs/expirement-log.md):
    YuNet boxes are tight and MediaPipe Face Landmarker usually needs margin
    around the face to detect it. Face landmarks are therefore searched over
    progressively padded crops (tight -> 50% -> 150% -> full frame, see
    FACE_MARGIN_FRACTIONS) and remapped onto the tight YuNet crop, so the
    feature-exclusion mask, the candidate mask, and the ITA statistics all
    keep sharing the same tight crop. When no framing yields landmarks, the
    standard V1 fallback is recorded and the image is excluded as before.

    Input (built by scripts/04_build_dataset_inventory.py):
        data/manifests/mst_e_inventory.csv

    Output:
        data/manifests/mst_e_ita_calibration_results.csv

What this script deliberately does NOT do:
    - It does not map ITA onto MST categories.
    - It does not compute calibration thresholds, bins, or per-label means.
    - It does not train, evaluate, or load any correction model.
    - It never uses MST-E to train anything: MST-E is evaluation/calibration
      data only, and its intended_use stays "evaluation_only".
    - It makes no network calls and downloads nothing. The YuNet ONNX model and
      the MediaPipe face_landmarker.task model must already exist locally.
    - It does not modify any raw image.

Manual mask-quality review is a separate, human step: see
docs/mask-quality-review.md. Every row is written with quality_review="pending"
unless processing failed automatically, in which case quality_review is set to
"auto_failed" and exclusion_reason explains why.

Run from the project root:
    python scripts/05_run_mst_e_ita_calibration.py
    python scripts/05_run_mst_e_ita_calibration.py --limit 50
    python scripts/05_run_mst_e_ita_calibration.py --min-skin-pixels 1000
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

from src.data_preparation.dataset_inventory import (
    QUALITY_REVIEW_AUTO_FAILED,
    QUALITY_REVIEW_PENDING,
    load_inventory_manifest,
    validate_intended_use,
)
from src.face_detection.detect_faces import detect_largest_face_bgr
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.landmark_exclusion import (
    build_feature_exclusion_mask,
    detect_face_landmarks,
)
from src.skin_masking.skin_mask import (
    SkinMaskResult,
    compute_skin_mask_result,
    create_candidate_mask_bgr,
    keep_largest_connected_component,
)
from src.utilities.config import get_config


# -------------------------------------------------------------------
# Paths and constants
# -------------------------------------------------------------------

DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "mst_e_inventory.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "manifests" / "mst_e_ita_calibration_results.csv"
)
DEFAULT_MST_E_ROOT = PROJECT_ROOT / "data" / "raw" / "mst-e_data"

DEFAULT_YUNET_MODEL = PROJECT_ROOT / get_config().FACE_MODEL_PATH
DEFAULT_LANDMARKER_MODEL = (
    PROJECT_ROOT / get_config().FACE_LANDMARKER_MODEL_PATH
)

#: Same 1,000-pixel minimum-skin rule as scripts 01-03 and the ITA stage.
DEFAULT_MINIMUM_SKIN_PIXELS = 1000

#: Same YuNet confidence used by the pilot scripts.
DEFAULT_SCORE_THRESHOLD = 0.85

#: Pad fractions (of the larger face-box side) tried, in order, when MediaPipe
#: Face Landmarker fails on the tight YuNet crop. ``None`` means the full
#: frame. YuNet boxes are tight and the MediaPipe face detector usually needs
#: margin around the face, so landmark *detection* runs on a padded crop while
#: the mask and ITA statistics stay on the tight YuNet crop (see
#: detect_landmarks_with_margin).
FACE_MARGIN_FRACTIONS: tuple[float | None, ...] = (0.0, 0.5, 1.5, None)

#: Row states written to the ``status`` column.
STATUS_SUCCESS = "success"
STATUS_EXCLUDED = "excluded"

#: Columns required in the results CSV (order preserved in the output).
REQUIRED_RESULT_COLUMNS: tuple[str, ...] = (
    "dataset_name",
    "image_id",
    "image_path",
    "source_mst_label",
    "intended_use",
    "status",
    "reason",
    "face_detected",
    "skin_pixels",
    "skin_ratio_percent",
    "passes_minimum_skin_pixel_rule",
    "mean_l_star",
    "mean_a_star",
    "mean_b_star",
    "ita_degrees",
    "quality_review",
    "exclusion_reason",
)

#: Additional traceability columns written after the required ones.
EXTRA_RESULT_COLUMNS: tuple[str, ...] = (
    "relative_path",
    "source_pose",
    "source_lighting",
    "source_wearing_mask",
    "face_x",
    "face_y",
    "face_width",
    "face_height",
    "face_area_pixels",
    "landmarks_available",
    "mask_status",
)

RESULT_COLUMNS: tuple[str, ...] = REQUIRED_RESULT_COLUMNS + EXTRA_RESULT_COLUMNS


# -------------------------------------------------------------------
# Command-line options
# -------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(
        description=(
            "Measure masked ITA for every MST-E image listed in the dataset "
            "inventory. No thresholds, no MST mapping, no training."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Inventory CSV to read (default: {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=DEFAULT_MST_E_ROOT,
        help=(
            "Dataset folder used only as a fallback when a stored image path "
            f"no longer exists (default: {DEFAULT_MST_E_ROOT})"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Results CSV to write (default: {DEFAULT_OUTPUT})",
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
            "Local MediaPipe face_landmarker.task model used for eye, "
            f"eyebrow, and lip exclusion (default: {DEFAULT_LANDMARKER_MODEL})"
        ),
    )
    parser.add_argument(
        "--min-skin-pixels",
        type=int,
        default=DEFAULT_MINIMUM_SKIN_PIXELS,
        help=(
            "Minimum number of selected skin pixels required to compute ITA "
            f"(default: {DEFAULT_MINIMUM_SKIN_PIXELS})"
        ),
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=DEFAULT_SCORE_THRESHOLD,
        help=f"YuNet confidence threshold (default: {DEFAULT_SCORE_THRESHOLD})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N inventory rows (0 = all). For a trial.",
    )
    parser.add_argument(
        "--allow-mask-fallback",
        action="store_true",
        help=(
            "Keep results even when landmark-based feature exclusion is "
            "unavailable and the mask falls back to the V1 mask. Off by "
            "default, so a single calibration table does not mix mask "
            "versions."
        ),
    )
    return parser.parse_args()


# -------------------------------------------------------------------
# Row helpers
# -------------------------------------------------------------------


def read_text(value: object) -> str:
    """Return a stripped string for a manifest cell, or ``""`` when missing."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    return str(value).strip()


def read_label(value: object) -> int | None:
    """Return an integer MST label, or ``None`` when the cell is empty."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def field(record: object, name: str, default: object = "") -> object:
    """Read one field from an inventory row.

    Works with both a pandas ``Series`` and a named tuple, so the row reader is
    not tied to how the manifest is iterated.
    """
    if isinstance(record, dict):
        return record.get(name, default)
    return getattr(record, name, default)


def resolve_image_path(
    stored_path: str, relative_path: str, dataset_root: Path
) -> Path:
    """Turn a manifest path into a usable local path.

    The manifest stores absolute POSIX-style paths. If that path no longer
    exists (the project moved to another drive, for example) the
    dataset-relative path is resolved against ``dataset_root`` instead.
    """
    candidate = Path(stored_path) if stored_path else Path(relative_path)
    if candidate.is_file():
        return candidate

    fallback = dataset_root / relative_path if relative_path else candidate
    if fallback.is_file():
        return fallback

    return candidate


def base_row(record: object, image_path: Path) -> dict[str, object]:
    """Build a fully-populated result row from one inventory record.

    Every column is always present, so the CSV has a stable shape even when a
    stage fails half-way.
    """
    return {
        "dataset_name": read_text(field(record, "dataset_name")),
        "image_id": read_text(field(record, "image_id")),
        "image_path": image_path.as_posix(),
        "source_mst_label": read_label(field(record, "source_mst_label")),
        "intended_use": read_text(field(record, "intended_use")),
        "status": STATUS_EXCLUDED,
        "reason": "",
        "face_detected": None,
        "skin_pixels": None,
        "skin_ratio_percent": None,
        "passes_minimum_skin_pixel_rule": None,
        "mean_l_star": None,
        "mean_a_star": None,
        "mean_b_star": None,
        "ita_degrees": None,
        "quality_review": QUALITY_REVIEW_AUTO_FAILED,
        "exclusion_reason": "",
        "relative_path": read_text(field(record, "relative_path")),
        "source_pose": read_text(field(record, "source_pose")),
        "source_lighting": read_text(field(record, "source_lighting")),
        "source_wearing_mask": read_text(field(record, "source_wearing_mask")),
        "face_x": None,
        "face_y": None,
        "face_width": None,
        "face_height": None,
        "face_area_pixels": None,
        "landmarks_available": None,
        "mask_status": "",
    }


def exclude(row: dict[str, object], reason: str) -> dict[str, object]:
    """Mark a row as automatically failed with the given reason."""
    row["status"] = STATUS_EXCLUDED
    row["reason"] = reason
    row["quality_review"] = QUALITY_REVIEW_AUTO_FAILED
    row["exclusion_reason"] = reason
    return row


def margined_crop(
    image_bgr: np.ndarray,
    face_box: tuple[int, int, int, int],
    fraction: float | None,
) -> tuple[np.ndarray, int, int]:
    """Return a BGR crop around ``face_box`` plus its top-left offset.

    The crop is ``face_box`` enlarged by ``fraction`` of the larger face-box
    side on all sides, clamped to the image bounds. ``fraction=None`` returns
    the full frame with offset ``(0, 0)``.

    Returns
    -------
    tuple[np.ndarray, int, int]
        The crop and its (x, y) offset in the original image.
    """
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
    """Find face landmarks for ``face_box`` over progressively padded crops.

    MediaPipe Face Landmarker often needs margin around the face because YuNet
    boxes are tight. The first cropping that yields landmarks wins; the points
    are remapped from the padded crop back into tight-crop coordinates so the
    exclusion mask is built on the exact crop that the ITA statistics use.

    Returns
    -------
    tuple[np.ndarray | None, float | None, str]
        Landmarks in tight-crop pixel coordinates (or ``None``), the margin
        fraction that produced them (or ``None``), and a human-readable status.
    """
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
                f"{detection.status} "
                f"(detected on the {label} crop, remapped to the "
                "YuNet face crop)"
            )
            return landmarks_tight, fraction, status
    return None, None, "no face landmarks in any crop framing"


def compute_v2_skin_mask_with_margin(
    face_crop_bgr: np.ndarray,
    image_bgr: np.ndarray,
    face_box: tuple[int, int, int, int],
    landmarker_model: Path,
) -> SkinMaskResult:
    """Run Skin Mask V2 feature exclusion, searching landmarks on padded crops.

    Landmarks detected on a padded crop are remapped onto the tight YuNet crop,
    so the candidate mask, the exclusion mask, and the ITA statistics all share
    one crop. When no framing yields landmarks, the standard V1 fallback mask
    is returned (``landmarks_available=False``) so existing exclusion logic
    still applies unchanged.
    """
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


def process_record(
    record: object,
    yunet_model: Path,
    landmarker_model: Path,
    minimum_skin_pixels: int,
    score_threshold: float,
    allow_mask_fallback: bool,
    dataset_root: Path,
) -> dict[str, object]:
    """Run detection, masking, and ITA for one inventory row.

    A failure at any stage is recorded and the image is marked excluded; the
    remaining images are always processed.

    Parameters
    ----------
    record : object
        One row of the MST-E inventory (a pandas ``Series`` or named tuple).
    yunet_model : Path
        Local YuNet ONNX model path.
    landmarker_model : Path
        Local MediaPipe ``face_landmarker.task`` path.
    minimum_skin_pixels : int
        Minimum selected skin pixels required before ITA is computed.
    score_threshold : float
        YuNet confidence threshold.
    allow_mask_fallback : bool
        When True, a mask computed without landmark feature exclusion is kept
        instead of being excluded.
    dataset_root : Path
        Dataset folder used to re-resolve a moved image path.

    Returns
    -------
    dict
        A row with exactly the keys in :data:`RESULT_COLUMNS`.
    """
    relative_path = read_text(field(record, "relative_path"))
    image_path = resolve_image_path(
        read_text(field(record, "image_path")), relative_path, dataset_root
    )
    row = base_row(record, image_path)

    if row["source_mst_label"] is None:
        return exclude(
            row,
            "no ground-truth MST label in the inventory; resolve the label "
            "from official metadata before calibrating on this image",
        )

    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        return exclude(row, "Could not load image with OpenCV")

    face_box = detect_largest_face_bgr(
        image_bgr=image_bgr,
        model_path=yunet_model,
        score_threshold=score_threshold,
    )
    if face_box is None:
        return exclude(row, "No face detected")

    x, y, face_width, face_height = face_box
    row["face_detected"] = True
    row["face_x"] = int(x)
    row["face_y"] = int(y)
    row["face_width"] = int(face_width)
    row["face_height"] = int(face_height)
    row["face_area_pixels"] = int(face_width) * int(face_height)

    face_crop_bgr = image_bgr[y : y + face_height, x : x + face_width].copy()
    if face_crop_bgr.size == 0:
        return exclude(row, "Face crop was empty")

    # Skin Mask V2, used unchanged. Landmark detection first tries padded
    # crops (YuNet boxes are tight) and remaps the points onto this crop. A
    # fallback mask is recorded and excluded by default, as before.
    mask_result = compute_v2_skin_mask_with_margin(
        face_crop_bgr=face_crop_bgr,
        image_bgr=image_bgr,
        face_box=(x, y, face_width, face_height),
        landmarker_model=landmarker_model,
    )
    row["landmarks_available"] = bool(mask_result.landmarks_available)
    row["mask_status"] = mask_result.status

    if mask_result.mask is None or mask_result.mask.size == 0:
        return exclude(row, "Skin mask could not be created")

    if not mask_result.landmarks_available and not allow_mask_fallback:
        return exclude(
            row,
            "Skin Mask V2 feature exclusion unavailable, so the V1 fallback "
            "mask was produced instead: " + mask_result.status,
        )

    skin_pixels = int(np.count_nonzero(mask_result.mask > 0))
    face_area_pixels = int(row["face_area_pixels"] or 0)
    row["skin_pixels"] = skin_pixels
    row["skin_ratio_percent"] = (
        round((skin_pixels / face_area_pixels) * 100, 2)
        if face_area_pixels > 0
        else 0.0
    )
    row["passes_minimum_skin_pixel_rule"] = skin_pixels >= minimum_skin_pixels

    statistics = compute_masked_lab_statistics(
        face_bgr=face_crop_bgr,
        skin_mask=mask_result.mask,
        minimum_skin_pixels=minimum_skin_pixels,
    )

    row["mean_l_star"] = statistics["mean_l_star"]
    row["mean_a_star"] = statistics["mean_a_star"]
    row["mean_b_star"] = statistics["mean_b_star"]
    row["ita_degrees"] = statistics["ita_degrees"]

    if not statistics["valid"]:
        return exclude(row, statistics["reason"])

    row["status"] = STATUS_SUCCESS
    row["reason"] = statistics["reason"]
    row["quality_review"] = QUALITY_REVIEW_PENDING
    return row


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main() -> None:
    """Process every MST-E inventory row and write the results CSV."""
    args = parse_arguments()

    if args.min_skin_pixels <= 0:
        print("ERROR: --min-skin-pixels must be a positive integer.")
        sys.exit(1)

    try:
        manifest = load_inventory_manifest(args.manifest)
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    if manifest.empty:
        print(f"ERROR: the inventory manifest is empty: {args.manifest}")
        sys.exit(1)

    dataset_names = sorted(set(manifest["dataset_name"].astype(str)))
    for name in dataset_names:
        rows_for_dataset = manifest[manifest["dataset_name"].astype(str) == name]
        for use in sorted(set(rows_for_dataset["intended_use"].astype(str))):
            try:
                validate_intended_use(name, use)
            except ValueError as error:
                print(f"ERROR: {error}")
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
            f"WARNING: MediaPipe landmarker model was not found: "
            f"{args.landmarker_model}\n"
            "  Skin Mask V2 feature exclusion cannot run, so every image will "
            "be excluded as a mask-version fallback.\n"
            "  Place face_landmarker.task there, or pass "
            "--landmarker-model / --allow-mask-fallback."
        )

    records = manifest
    if args.limit and args.limit > 0:
        records = records.head(args.limit)

    print("=" * 65)
    print("MST-E ITA Calibration Preparation (measure only)")
    print("=" * 65)
    intended_uses = sorted(set(manifest["intended_use"].astype(str)))
    print(f"Manifest          : {args.manifest}")
    print(f"Dataset           : {', '.join(dataset_names)}")
    print(f"Intended use      : {', '.join(intended_uses)}")
    print(f"Images in manifest: {len(manifest)}")
    print(f"Images to process : {len(records)}")
    print(f"YuNet model       : {args.yunet_model}")
    print(f"Landmarker model  : {args.landmarker_model}")
    print(f"Min skin pixels   : {args.min_skin_pixels}")
    print(f"Score threshold   : {args.score_threshold}")
    print()

    results: list[dict[str, object]] = []

    for index, record in enumerate(records.itertuples(index=False), start=1):
        relative_path = read_text(field(record, "relative_path"))
        print(f"[{index}/{len(records)}] {relative_path}")

        try:
            row = process_record(
                record=record,
                yunet_model=args.yunet_model,
                landmarker_model=args.landmarker_model,
                minimum_skin_pixels=args.min_skin_pixels,
                score_threshold=args.score_threshold,
                allow_mask_fallback=args.allow_mask_fallback,
                dataset_root=args.dataset_root,
            )
        except Exception as error:  # one bad image must not stop the batch
            row = base_row(record, Path(relative_path or "."))
            exclude(row, f"Unexpected error: {error}")

        results.append(row)

        if row["status"] == STATUS_SUCCESS:
            print(
                f"  OK      | skin={row['skin_pixels']} px "
                f"| ITA={row['ita_degrees']} deg "
                f"| MST label={row['source_mst_label']} "
                f"| review={row['quality_review']}"
            )
        else:
            print(f"  EXCLUDED| {row['reason']}")

    results_df = pd.DataFrame(results, columns=list(RESULT_COLUMNS))
    results_df["source_mst_label"] = results_df["source_mst_label"].astype(
        "Int64"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(args.output, index=False)

    success_count = int((results_df["status"] == STATUS_SUCCESS).sum())
    excluded_count = int((results_df["status"] == STATUS_EXCLUDED).sum())

    print()
    print("=" * 65)
    print("MST-E ITA measurement complete")
    print("=" * 65)
    print(f"Rows written       : {len(results_df)}")
    print(f"Measurements OK    : {success_count}")
    print(f"Excluded           : {excluded_count}")
    pending_count = int(
        (results_df["quality_review"] == QUALITY_REVIEW_PENDING).sum()
    )
    print(f"Pending review     : {pending_count}")
    print(f"Results CSV        : {args.output}")

    if excluded_count:
        print()
        print("Exclusion reasons:")
        for reason, count in results_df.loc[
            results_df["status"] == STATUS_EXCLUDED, "reason"
        ].value_counts().items():
            print(f"  {count:>5}  {reason}")

    if not success_count and not excluded_count:
        print()
        print("WARNING: the manifest produced no rows to report.")

    fallback_failures = results_df["reason"].astype(str).str.contains(
        "feature exclusion unavailable", regex=False
    ).sum()
    if fallback_failures:
        print()
        print("=" * 65)
        print(f"WARNING: {int(fallback_failures)} of {len(results_df)} rows were "
              "excluded because")
        print("  MediaPipe found no face even after the padded-crop cascade "
              "(see FACE_MARGIN_FRACTIONS),")
        print("  so Skin Mask V2 could not exclude eyes/eyebrows/lips and fell "
              "back to the V1 mask.")
        print("  Do not raise --min-skin-pixels or --allow-mask-fallback to "
              "hide it; the remaining")
        print("  failures are individual images where the largest YuNet face "
              "was not suitable, so")
        print("  review them case by case with docs/mask-quality-review.md.")

    print()
    print("Next steps (not done here):")
    print("  1. Manual mask-quality review using docs/mask-quality-review.md;")
    print("     fill the quality_review column for this CSV.")
    print("  2. Only then decide ITA-to-MST calibration thresholds.")
    print("  3. MST-E is evaluation/calibration only: never use it to train,")
    print("     validate, or test-split the correction model.")


if __name__ == "__main__":
    main()
