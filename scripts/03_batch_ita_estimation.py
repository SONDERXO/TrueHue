"""
03_batch_ita_estimation.py

Purpose:
    Run the ITA-estimation pipeline stage on every image inside:
    data/raw/pilot_images/

    Pipeline for each image:
        YuNet face detection
        -> largest-face BGR crop
        -> Skin Mask V2 (selected V2 implementation, unchanged)
        -> CIELAB conversion of selected skin pixels only
        -> mean L*, a*, b*
        -> ITA (degrees)

    This stage only converts selected pixels to CIELAB and computes ITA. It
    does **not** perform MST mapping, colour correction, model training, or
    any image editing.

Outputs:
    outputs/metrics/v2_pilot_ita_results.csv

Run from the project root:
    python scripts/03_batch_ita_estimation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

# Make the project root importable when this file is run from scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.face_detection.detect_faces import detect_largest_face_bgr
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.skin_mask import create_skin_mask_bgr


# -------------------------------------------------------------------
# Paths / constants
# -------------------------------------------------------------------

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pilot_images"

YUNET_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "face_detector"
    / "face_detection_yunet_2023mar.onnx"
)

OUTPUT_METRICS = PROJECT_ROOT / "outputs" / "metrics"
RESULTS_CSV = OUTPUT_METRICS / "v2_pilot_ita_results.csv"

# The selected pipeline is Skin Mask V2 (V3 was rejected; never used here).
MASK_VERSION = "v2"
MINIMUM_SKIN_PIXELS = 1000

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def ensure_output_directory() -> None:
    """Create the metrics output directory if it does not already exist."""
    OUTPUT_METRICS.mkdir(parents=True, exist_ok=True)


def get_image_files() -> list[Path]:
    """
    Return supported image files in the pilot-image folder.

    Images are sorted by filename so results appear in a consistent order.
    """
    return sorted(
        path
        for path in INPUT_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _empty_result(image_path: Path, status: str, reason: str) -> dict:
    """Build a fully-populated row dict for the CSV summary."""
    return {
        "image_name": image_path.name,
        "image_path": str(image_path),
        "mask_version": MASK_VERSION,
        "status": status,
        "reason": reason,
        "image_width": None,
        "image_height": None,
        "face_x": None,
        "face_y": None,
        "face_width": None,
        "face_height": None,
        "face_area_pixels": None,
        "skin_pixels": None,
        "skin_ratio_percent": None,
        "passes_minimum_skin_pixel_rule": None,
        "mean_l_star": None,
        "mean_a_star": None,
        "mean_b_star": None,
        "ita_degrees": None,
    }


def process_image(image_path: Path) -> dict:
    """
    Process one image through face detection, Skin Mask V2, and ITA.

    A failure in one image does not stop processing of the remaining images;
    every failure is recorded in the result dict with an explanatory reason.
    """
    result = _empty_result(image_path, "failed", "")

    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        result["reason"] = "Could not load image"
        return result

    image_height, image_width = image_bgr.shape[:2]
    result["image_width"] = image_width
    result["image_height"] = image_height

    face_box = detect_largest_face_bgr(
        image_bgr=image_bgr,
        model_path=YUNET_MODEL_PATH,
        score_threshold=0.85,
    )

    if face_box is None:
        result["reason"] = "No face detected"
        return result

    x, y, face_width, face_height = face_box

    result["face_x"] = x
    result["face_y"] = y
    result["face_width"] = face_width
    result["face_height"] = face_height

    face_crop_bgr = image_bgr[y : y + face_height, x : x + face_width].copy()

    if face_crop_bgr.size == 0:
        result["reason"] = "Face crop was empty"
        return result

    # Reuse the selected Skin Mask V2 implementation unchanged.
    skin_mask = create_skin_mask_bgr(face_crop_bgr)

    if skin_mask is None or skin_mask.size == 0:
        result["reason"] = "Skin mask could not be created"
        return result

    stats = compute_masked_lab_statistics(
        face_bgr=face_crop_bgr,
        skin_mask=skin_mask,
        minimum_skin_pixels=MINIMUM_SKIN_PIXELS,
    )

    face_area_pixels = int(face_width * face_height)
    skin_pixels = int(stats["skin_pixels"] or 0)
    skin_ratio_percent = (
        (skin_pixels / face_area_pixels) * 100 if face_area_pixels > 0 else 0.0
    )

    result["face_area_pixels"] = face_area_pixels
    result["skin_pixels"] = skin_pixels
    result["skin_ratio_percent"] = round(skin_ratio_percent, 2)
    result["passes_minimum_skin_pixel_rule"] = skin_pixels >= MINIMUM_SKIN_PIXELS
    result["mean_l_star"] = stats["mean_l_star"]
    result["mean_a_star"] = stats["mean_a_star"]
    result["mean_b_star"] = stats["mean_b_star"]
    result["ita_degrees"] = stats["ita_degrees"]
    result["status"] = "success" if stats["valid"] else "failed"
    result["reason"] = stats["reason"]

    return result


def main() -> None:
    """Run the batch ITA-estimation pilot test."""
    ensure_output_directory()

    if not INPUT_DIR.exists():
        print(f"ERROR: Input folder does not exist: {INPUT_DIR}")
        print("Create it and place pilot images inside.")
        sys.exit(1)

    if not YUNET_MODEL_PATH.exists():
        print(f"ERROR: YuNet model was not found: {YUNET_MODEL_PATH}")
        print("Download or move the YuNet ONNX model to that location first.")
        sys.exit(1)

    image_files = get_image_files()

    if len(image_files) == 0:
        print(f"ERROR: No .jpg, .jpeg, or .png files found in: {INPUT_DIR}")
        sys.exit(1)

    print("=" * 65)
    print("Batch ITA Estimation (Skin Mask V2)")
    print("=" * 65)
    print(f"Input folder : {INPUT_DIR}")
    print(f"Images found : {len(image_files)}")
    print(f"Min skin px  : {MINIMUM_SKIN_PIXELS}")
    print()

    results = []

    for index, image_path in enumerate(image_files, start=1):
        print(f"[{index}/{len(image_files)}] Processing: {image_path.name}")

        try:
            result = process_image(image_path)
        except Exception as error:
            result = {
                **_empty_result(image_path, "failed", ""),
                "reason": f"Unexpected error: {error}",
            }

        results.append(result)

        if result["status"] == "success":
            print(
                f"  SUCCESS | skin={result['skin_pixels']} px "
                f"| mean L*={result['mean_l_star']} "
                f"| mean b*={result['mean_b_star']} "
                f"| ITA={result['ita_degrees']} deg"
            )
        else:
            print(f"  FAILED  | {result['reason']}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_CSV, index=False)

    success_count = int((results_df["status"] == "success").sum())
    failed_count = len(results_df) - success_count

    print()
    print("=" * 65)
    print("Batch ITA estimation complete")
    print("=" * 65)
    print(f"Successful images : {success_count}")
    print(f"Failed images     : {failed_count}")
    print(f"CSV summary       : {RESULTS_CSV}")


if __name__ == "__main__":
    main()