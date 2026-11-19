"""Pack the saved full-frame WB314 mask references for an Android parity check."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    output = parser.parse_args().output_dir.resolve()
    if OUTPUTS.resolve() not in output.parents:
        raise ValueError("Use a new local directory under outputs")
    output.mkdir()
    planes = ("categories.png", "visible_face.png", "baseline_mask.png", "measurement_mask.png", "protected_mask.png")
    for name in ("test1", "test2"):
        source = OUTPUTS / "wb314_user_photo_check_v1" / name
        artifacts = json.loads((source / "manifest.json").read_text(encoding="utf-8"))["artifacts"]
        files = ("input.png", "parent_report.json", "report.json", "application_alpha.npy", *planes)
        if any(sha(source / file) != artifacts[file] for file in files):
            raise ValueError(f"Saved reference bindings changed for {name}")
        frame = cv2.imread(str(source / "input.png"), cv2.IMREAD_COLOR)
        masks = [cv2.imread(str(source / file), cv2.IMREAD_GRAYSCALE) for file in planes]
        alpha = np.load(source / "application_alpha.npy", allow_pickle=False)
        if frame.shape != (256, 256, 3) or any(mask.shape != (256, 256) for mask in [*masks, alpha]):
            raise ValueError(f"Unexpected saved dimensions for {name}")
        parent = json.loads((source / "parent_report.json").read_text(encoding="utf-8"))
        report = json.loads((source / "report.json").read_text(encoding="utf-8"))
        with (output / f"{name}.bin").open("xb") as stream:
            stream.write(struct.pack(">4i", *parent["face_box"]))
            stream.write(bytes([("clear", "opaque", "uncertain").index(report["glasses"])]))
            stream.write(frame.tobytes())
            for mask in masks:
                stream.write(mask.tobytes())
            stream.write(alpha.astype(">f8").tobytes())
    (output / "receipt.json").write_text(json.dumps({file.name: sha(file) for file in sorted(output.iterdir())}, indent=2) + "\n",
                                         encoding="utf-8")


if __name__ == "__main__":
    main()
