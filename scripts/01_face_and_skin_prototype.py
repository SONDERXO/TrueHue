"""
01_face_and_skin_prototype.py

Purpose:
- Load one sample image from data/raw/
- Detect a face
- Crop to the face region
- Create a skin mask inside the face using HSV + YCrCb
- Save:
  - Face crop
  - Skin mask
  - Optional overlay image
- Print basic stats (face detected, face size, skin pixel count, etc.)

Usage:
    python scripts/01_face_and_skin_prototype.py
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import urllib.request

# Adjust these paths if your structure is different
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # skin-tone-correction/
DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "models" / "face_detector"
OUTPUT_MASKS = PROJECT_ROOT / "outputs" / "masks"
OUTPUT_IMAGES = PROJECT_ROOT / "outputs" / "corrected_images"

# OpenCV 5 removed Haar cascades and Caffe importer; face detection uses the
# YuNet ONNX model via cv2.FaceDetectorYN.
FACE_MODEL = PROJECT_ROOT / "models" / "face_detector" / "face_detection_yunet_2023mar.onnx"
FACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
FACE_CONFIDENCE = 0.9  # min confidence to accept a detection

# Ensure output directories exist
OUTPUT_MASKS.mkdir(parents=True, exist_ok=True)
OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)


def ensure_face_detector_model() -> None:
    """Download the YuNet face detector ONNX model if not present."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not FACE_MODEL.exists():
        print(f"Downloading face detector model: {FACE_MODEL.name}")
        urllib.request.urlretrieve(FACE_MODEL_URL, FACE_MODEL)


def load_image(path: Path) -> np.ndarray:
    """
    Load an image using OpenCV in BGR format.
    """
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return img


def detect_largest_face_bgr(bgr_img: np.ndarray):
    """
    Detect faces using OpenCV's DNN face detector (YuNet ONNX, cv2.FaceDetectorYN).
    Returns the largest face bounding box (x, y, w, h) or None if no face found.
    """
    ensure_face_detector_model()

    h, w = bgr_img.shape[:2]
    detector = cv2.FaceDetectorYN.create(str(FACE_MODEL), "", (w, h), FACE_CONFIDENCE)
    detector.setInputSize((w, h))

    _, faces = detector.detect(bgr_img)

    if faces is None or len(faces) == 0:
        return None

    # YuNet returns rows of (x, y, w, h, 5 landmarks, score).
    boxes = []
    for face in faces:
        x, y, fw, fh, score = face[0], face[1], face[2], face[3], face[14]
        x = max(0, min(int(x), w))
        y = max(0, min(int(y), h))
        fw = max(1, min(int(fw), w - x))
        fh = max(1, min(int(fh), h - y))
        boxes.append((x, y, fw, fh))

    # Choose the largest face by area
    largest = max(boxes, key=lambda rect: rect[2] * rect[3])
    return tuple(largest)  # (x, y, w, h)


def create_skin_mask_bgr(bgr_img: np.ndarray) -> np.ndarray:
    """
    Create a binary skin mask from a BGR image using combined HSV and YCrCb thresholds.
    Returns a mask with same height/width as input (uint8, 0 or 255).
    This is a simple baseline; thresholds can be tuned later.
    """
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2YCrCb)

    # HSV thresholds (typical skin ranges; may need tuning)
    lower_hsv = np.array([0, 48, 0], dtype=np.uint8)
    upper_hsv = np.array([20, 255, 255], dtype=np.uint8)
    mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # YCrCb thresholds (common skin ranges)
    lower_ycrcb = np.array([0, 133, 77], dtype=np.uint8)
    upper_ycrcb = np.array([255, 173, 127], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)

    # Combine masks (logical AND)
    mask_combined = cv2.bitwise_and(mask_hsv, mask_ycrcb)

    # Optional: morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_clean = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    return mask_clean


def main():
    # 1. Define input image
    image_name = Path("sample_01.jpg")
    image_path = DATA_RAW / image_name

    if not image_path.exists():
        print(f"ERROR: Image not found at {image_path}")
        sys.exit(1)

    print(f"Loading image: {image_path}")
    img_bgr = load_image(image_path)
    h, w = img_bgr.shape[:2]
    print(f"Image size: {w} x {h}")

    # 2. Detect face
    print("Detecting face...")
    face_rect = detect_largest_face_bgr(img_bgr)

    if face_rect is None:
        print("No face detected. Stopping.")
        sys.exit(0)

    x, y, fw, fh = face_rect
    print(f"Face detected at x={x}, y={y}, w={fw}, h={fh}")

    # 3. Crop to face region
    face_crop_bgr = img_bgr[y:y+fh, x:x+fw].copy()

    # Save face crop
    face_crop_path = OUTPUT_IMAGES / f"{image_name.stem}_face_crop.png"
    cv2.imwrite(str(face_crop_path), face_crop_bgr)
    print(f"Saved face crop: {face_crop_path}")

    # 4. Create skin mask on the face crop
    print("Creating skin mask on face crop...")
    skin_mask = create_skin_mask_bgr(face_crop_bgr)

    # Save mask
    mask_path = OUTPUT_MASKS / f"{image_name.stem}_mask.png"
    cv2.imwrite(str(mask_path), skin_mask)
    print(f"Saved skin mask: {mask_path}")

    # 5. Compute stats
    total_pixels = skin_mask.size
    skin_pixels = np.count_nonzero(skin_mask)
    skin_ratio = skin_pixels / total_pixels if total_pixels > 0 else 0.0

    print("\n=== Stats ===")
    print(f"Face crop size: {fw} x {fh}")
    print(f"Total pixels in face crop: {total_pixels}")
    print(f"Skin pixels: {skin_pixels}")
    print(f"Skin ratio: {skin_ratio:.2%}")

    # 6. Optional: create overlay image (original with mask drawn)
    overlay = img_bgr.copy()
    # Draw rectangle around face
    cv2.rectangle(overlay, (x, y), (x+fw, y+fh), (0, 255, 0), 2)

    # Optionally draw mask on a separate copy for visualization
    mask_color = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR)
    # Resize mask to face size to overlay on full image if desired
    # For now, just save face crop with mask side by side
    face_mask_vis = np.hstack([face_crop_bgr, mask_color])
    vis_path = OUTPUT_IMAGES / f"{image_name.stem}_face_and_mask.png"
    cv2.imwrite(str(vis_path), face_mask_vis)
    print(f"Saved face+mask visualization: {vis_path}")

    print("\nPrototype completed successfully.")


if __name__ == "__main__":
    main()