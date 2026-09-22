"""
02_batch_face_and_skin_test.py

Purpose:
    Run face detection and facial skin masking on every image inside:
    data/raw/pilot_images/

Outputs:
    - A face crop for each successfully processed image
    - A skin mask for each successfully processed image
    - A visualization with original face crop, mask, and mask overlay
    - A CSV summary of all results, including failures

Run from the project root:
    python scripts/02_batch_face_and_skin_test.py
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
from src.skin_masking.skin_mask import create_skin_mask_bgr


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pilot_images"

YUNET_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "face_detector"
    / "face_detection_yunet_2023mar.onnx"
)

OUTPUT_FACE_CROPS = PROJECT_ROOT / "outputs" / "pilot_face_crops"
OUTPUT_MASKS = PROJECT_ROOT / "outputs" / "pilot_masks"
OUTPUT_VISUALIZATIONS = PROJECT_ROOT / "outputs" / "pilot_visualizations"
OUTPUT_METRICS = PROJECT_ROOT / "outputs" / "metrics"

RESULTS_CSV = OUTPUT_METRICS / "pilot_face_skin_results.csv"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def ensure_output_directories() -> None:
    """Create output directories if they do not already exist."""
    OUTPUT_FACE_CROPS.mkdir(parents=True, exist_ok=True)
    OUTPUT_MASKS.mkdir(parents=True, exist_ok=True)
    OUTPUT_VISUALIZATIONS.mkdir(parents=True, exist_ok=True)
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


def create_overlay(
    face_crop_bgr: np.ndarray,
    skin_mask: np.ndarray,
) -> np.ndarray:
    """
    Create a colored overlay to help inspect mask quality.

    Skin-mask pixels are shown in green with partial transparency.
    """
    overlay = face_crop_bgr.copy()
    green_layer = np.zeros_like(face_crop_bgr)
    green_layer[:, :, 1] = 255

    skin_area = skin_mask > 0

    overlay[skin_area] = cv2.addWeighted(
        face_crop_bgr[skin_area],
        0.45,
        green_layer[skin_area],
        0.55,
        0,
    )

    return overlay


def make_visualization(
    face_crop_bgr: np.ndarray,
    skin_mask: np.ndarray,
) -> np.ndarray:
    """
    Combine face crop, binary mask, and colored mask overlay horizontally.
    """
    mask_bgr = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR)
    overlay_bgr = create_overlay(face_crop_bgr, skin_mask)

    height, width = face_crop_bgr.shape[:2]

    # All sections should be the same size before stacking horizontally.
    mask_bgr = cv2.resize(mask_bgr, (width, height))
    overlay_bgr = cv2.resize(overlay_bgr, (width, height))

    return np.hstack([face_crop_bgr, mask_bgr, overlay_bgr])


def process_image(image_path: Path) -> dict:
    """
    Process one image and return a result record for the CSV summary.

    A failure in one image does not stop processing of the remaining images.
    """
    result = {
        "image_name": image_path.name,
        "status": "failed",
        "reason": "",
        "image_width": None,
        "image_height": None,
        "face_x": None,
        "face_y": None,
        "face_width": None,
        "face_height": None,
        "face_area_pixels": None,
        "skin_pixels": None,
        "skin_ratio_percent": None,
        "mask_passes_1000_pixel_rule": None,
    }

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

    # The actual HSV/YCrCb skin-mask step.
    skin_mask = create_skin_mask_bgr(face_crop_bgr)

    if skin_mask is None or skin_mask.size == 0:
        result["reason"] = "Skin mask could not be created"
        return result

    face_area_pixels = int(face_width * face_height)
    skin_pixels = int(np.count_nonzero(skin_mask))
    skin_ratio_percent = (
        (skin_pixels / face_area_pixels) * 100 if face_area_pixels > 0 else 0.0
    )

    result["face_area_pixels"] = face_area_pixels
    result["skin_pixels"] = skin_pixels
    result["skin_ratio_percent"] = round(skin_ratio_percent, 2)
    result["mask_passes_1000_pixel_rule"] = skin_pixels >= 1000

    image_stem = image_path.stem

    face_crop_path = OUTPUT_FACE_CROPS / f"{image_stem}_face_crop.png"
    mask_path = OUTPUT_MASKS / f"{image_stem}_mask.png"
    visualization_path = OUTPUT_VISUALIZATIONS / f"{image_stem}_visualization.png"

    cv2.imwrite(str(face_crop_path), face_crop_bgr)
    cv2.imwrite(str(mask_path), skin_mask)

    visualization = make_visualization(face_crop_bgr, skin_mask)
    cv2.imwrite(str(visualization_path), visualization)

    result["status"] = "success"
    result["reason"] = "Processed successfully"

    return result


def main() -> None:
    """Run the batch face-detection and skin-mask pilot test."""
    ensure_output_directories()

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
    print("Batch Face Detection + Skin Mask Pilot Test")
    print("=" * 65)
    print(f"Input folder: {INPUT_DIR}")
    print(f"Images found: {len(image_files)}")
    print()

    results = []

    for index, image_path in enumerate(image_files, start=1):
        print(f"[{index}/{len(image_files)}] Processing: {image_path.name}")

        try:
            result = process_image(image_path)
        except Exception as error:
            result = {
                "image_name": image_path.name,
                "status": "failed",
                "reason": f"Unexpected error: {error}",
                "image_width": None,
                "image_height": None,
                "face_x": None,
                "face_y": None,
                "face_width": None,
                "face_height": None,
                "face_area_pixels": None,
                "skin_pixels": None,
                "skin_ratio_percent": None,
                "mask_passes_1000_pixel_rule": None,
            }

        results.append(result)

        if result["status"] == "success":
            print(
                f"  SUCCESS | face={result['face_width']}x{result['face_height']} "
                f"| skin={result['skin_pixels']} pixels "
                f"| ratio={result['skin_ratio_percent']}%"
            )
        else:
            print(f"  FAILED | {result['reason']}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_CSV, index=False)

    success_count = int((results_df["status"] == "success").sum())
    failed_count = len(results_df) - success_count

    print()
    print("=" * 65)
    print("Batch test complete")
    print("=" * 65)
    print(f"Successful images: {success_count}")
    print(f"Failed images: {failed_count}")
    print(f"CSV summary: {RESULTS_CSV}")
    print(f"Face crops: {OUTPUT_FACE_CROPS}")
    print(f"Masks: {OUTPUT_MASKS}")
    print(f"Visualizations: {OUTPUT_VISUALIZATIONS}")


if __name__ == "__main__":
    main()