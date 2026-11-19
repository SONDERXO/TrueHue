"""Prepare a local OpenCV tensor comparison from the two saved Huawei cases."""

import argparse
import hashlib
import json
import struct
from pathlib import Path
from zipfile import ZipFile

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
BUNDLE = ROOT / "models/face_landmarker/face_landmarker.task"
BUNDLE_SHA = "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"
GRAPHS = (("face_detector", 128, ("regressors", "classificators")),
          ("face_landmarks_detector", 256, ("Identity", "Identity_1", "Identity_2")))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def crop(index, expected_digest):
    saved = (OUTPUTS / "wb314_huawei_faceocc_trace_v1" / "fixture" / f"test{index}.bin").read_bytes()
    x, y, w, h = struct.unpack_from(">4i", saved)
    frame = np.frombuffer(saved, np.uint8, count=256 * 256 * 3, offset=24 + 478 * 16 + 48).reshape(256, 256, 3)
    rgb = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2RGB)
    if digest(rgb.tobytes()) != expected_digest:
        raise ValueError(f"Saved RGB binding changed for test{index}")
    return rgb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = parser.parse_args().output_dir.resolve()
    if OUTPUTS.resolve() not in destination.parents:
        raise ValueError("Choose a new private directory under outputs")
    if digest(BUNDLE.read_bytes()) != BUNDLE_SHA:
        raise ValueError("Pinned landmarker bundle required")
    prior = OUTPUTS / "wb314_huawei_landmark_input_v1" / "python.txt"
    hashes = {line.split()[0]: line.split()[1].split("=")[1]
              for line in prior.read_text(encoding="utf-8").splitlines() if line.endswith("python_vs_saved=0")}
    crops = {case: crop(i, hashes[f"test{i}"]) for i, case in enumerate(("adjusted", "preserved"), 1)}
    destination.mkdir()
    cv2.setNumThreads(1)
    with ZipFile(BUNDLE) as bundle:
        for name, side, outputs in GRAPHS:
            path = destination / f"{name}.tflite"
            path.write_bytes(bundle.read(path.name))
            net = cv2.dnn.readNetFromTFLite(str(path), cv2.dnn.ENGINE_CLASSIC)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            net.enableFusion(False)
            net.enableWinograd(False)
            for case, rgb in crops.items():
                # A fixed tensor comparison only. This resize is not MediaPipe graph geometry.
                image = cv2.resize(rgb, (side, side), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
                if name == "face_detector":
                    image = image * 2 - 1
                tensor = np.ascontiguousarray(image.transpose(2, 0, 1)[None])
                net.setInput(tensor)
                expected = net.forward(outputs)
                if len(expected) != len(outputs) or not all(np.isfinite(array).all() for array in expected):
                    raise ValueError("Missing or nonfinite tensor output")
                with (destination / f"{name}_{case}.bin").open("xb") as stream:
                    tensor.astype(">f4").tofile(stream)
                    for array in expected:
                        array.astype(">f4").tofile(stream)
    receipt = {path.name: digest(path.read_bytes()) for path in sorted(destination.iterdir())}
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
