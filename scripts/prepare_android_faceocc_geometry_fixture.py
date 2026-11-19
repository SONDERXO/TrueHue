"""Stage private, hash-checked saved references for Android FaceOcc geometry parity."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

import cv2
import numpy as np
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    output = parser.parse_args().output_dir.resolve()
    if OUTPUTS.resolve() not in output.parents:
        raise ValueError("Use a new private directory under outputs")
    template_path = ROOT / "models/faceocc_candidate_v1/similarity_Lm3D_all.mat"
    template_sha = "53b83ce6e35c50ddc3e97603650cef4970320c157e75c241c844f29c1dcba65a"
    if sha(template_path) != template_sha:
        raise ValueError("Pinned FaceOcc landmark template required")
    template68 = loadmat(template_path)["lm"].astype(np.float64)
    if template68.shape != (68, 3) or not np.isfinite(template68).all():
        raise ValueError("Unexpected FaceOcc template")
    template = np.stack((template68[[36, 39]].mean(axis=0), template68[[42, 45]].mean(axis=0),
                         template68[30], template68[48], template68[54]))
    output.mkdir()
    template.astype(">f8").tofile(output / "template.bin")

    for name in ("test1", "test2"):
        source = OUTPUTS / "wb314_user_photo_check_v1" / name
        artifacts = json.loads((source / "manifest.json").read_text(encoding="utf-8"))["artifacts"]
        filenames = ("input.png", "aligned.png", "visible_face.png", "landmarks.npy", "report.json", "parent_report.json")
        if any(sha(source / filename) != artifacts[filename] for filename in filenames):
            raise ValueError(f"Saved reference bindings changed for {name}")
        frame = cv2.imread(str(source / "input.png"), cv2.IMREAD_COLOR)
        aligned = cv2.imread(str(source / "aligned.png"), cv2.IMREAD_COLOR)
        visible = cv2.imread(str(source / "visible_face.png"), cv2.IMREAD_GRAYSCALE)
        points = np.load(source / "landmarks.npy", allow_pickle=False)
        parent = json.loads((source / "parent_report.json").read_text(encoding="utf-8"))
        report = json.loads((source / "report.json").read_text(encoding="utf-8"))
        geometry = report["mask_source"]
        matrix = np.asarray(geometry["matrix"], dtype=np.float64)
        if (frame.shape, aligned.shape, visible.shape, points.shape, matrix.shape) != (
                (256, 256, 3), (256, 256, 3), (256, 256), (478, 2), (2, 3)):
            raise ValueError(f"Unexpected reference dimensions for {name}")
        margin = geometry["landmark_details"]["margin"]
        with (output / f"{name}.bin").open("xb") as stream:
            stream.write(struct.pack(">4id", *parent["face_box"], -1.0 if margin is None else margin))
            stream.write(points.astype(">f8").tobytes())
            stream.write(matrix.astype(">f8").tobytes())
            stream.write(frame.tobytes())
            stream.write(cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB).tobytes())
            stream.write(visible.tobytes())
    hashes = {path.name: sha(path) for path in sorted(output.iterdir())}
    (output / "receipt.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
