"""Trace crop-to-image landmark geometry for a local FairFace image.

Run from the project root. Diagnostic only: no baseline outputs are modified.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import cv2
import numpy as np
from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.landmark_exclusion import detect_face_landmarks
from src.utilities.config import get_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=ROOT / "data/raw/FairFace/train/83184.jpg")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/outline_landmark_trace_83184")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite diagnostic evidence")
    prepare = importlib.import_module("11_prepare_training_manifests")
    config = get_config()
    image = cv2.imread(str(args.image))
    if image is None:
        raise ValueError("Unreadable image")
    yunet, model = ROOT / config.FACE_MODEL_PATH, ROOT / config.FACE_LANDMARKER_MODEL_PATH
    if not yunet.is_file() or not model.is_file():
        raise FileNotFoundError("Local models required; no downloads")
    boxes = prepare._detect_face_boxes(image, yunet, .85)
    if len(boxes) != 1:
        raise ValueError("Expected one YuNet detection")
    x, y, w, h = map(int, boxes[0])
    args.output.mkdir(parents=True)
    records = []
    for fraction in prepare.FACE_MARGIN_FRACTIONS:
        framed, ox, oy = prepare.margined_crop(image, boxes[0], fraction)
        detection = detect_face_landmarks(framed, str(model))
        row = dict(margin=fraction, frame_shape=list(framed.shape), frame_origin=[ox, oy],
                   landmarks_available=detection.landmarks_available)
        if detection.landmarks_available:
            raw = detection.landmarks
            tight = raw - np.array([x-ox, y-oy])
            image_points = tight + np.array([x, y])
            direct_points = raw + np.array([ox, oy])
            error = float(np.max(np.abs(image_points-direct_points)))
            assert error < 1e-9
            oval = tight[list(FACE_OVAL)]
            row.update(remap_max_error_pixels=error,
                oval_crop_min=oval.min(axis=0).tolist(), oval_crop_max=oval.max(axis=0).tolist(),
                nose_crop=tight[1].tolist())
            canvas = image.copy()
            cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.polylines(canvas, [np.rint(image_points[list(FACE_OVAL)]).astype(np.int32)], True, (0, 255, 0), 1)
            destination = args.output / f"margin_{fraction}.png"
            if not cv2.imwrite(str(destination), cv2.resize(canvas, (672, 672))):
                raise OSError(destination)
        records.append(row)
    result = dict(image=str(args.image), image_shape=list(image.shape), face_box=[x,y,w,h], frames=records,
        note="Red: YuNet box. Green: oval. Zero remapping error establishes coordinate consistency, not landmark accuracy.")
    (args.output / "trace.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
