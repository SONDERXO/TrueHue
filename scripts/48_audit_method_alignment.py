"""Read-only local evidence for the proposal alignment checkpoint.

Run from the project root. Writes a new JSON report; never modifies inputs,
fits a model, assigns MST labels or downloads SCIN images.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import cv2


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("outputs/method_alignment_v1/evidence.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    training_path = Path("data/manifests/controlled_training_v2/train.csv")
    cases_path = Path("data/raw/scin/metadata/dataset_scin_cases.csv")
    paths = [training_path, cases_path, Path(__file__),
             Path("scripts/11_prepare_training_manifests.py"),
             Path("src/face_detection/detect_faces.py")]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    dimensions: Counter[str] = Counter()
    image_evidence = []
    for row in read_rows(training_path):
        path = Path(row["input_path"])
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Unreadable training input: {path}")
        height, width = image.shape[:2]
        dimensions[f"{width}x{height}"] += 1
        image_evidence.append({"pair_id": row["pair_id"], "path": str(path),
                               "width": width, "height": height,
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    cases = read_rows(cases_path)
    candidates = []
    for case in cases:
        if case["body_parts_head_or_neck"] != "YES":
            continue
        for slot in (1, 2, 3):
            if (case[f"image_{slot}_path"] and
                    case[f"image_{slot}_shot_type"] == "AT_DISTANCE"):
                candidates.append({"case_id": case["case_id"], "image_slot": slot,
                                   "image_path": case[f"image_{slot}_path"]})
    report = {
        "scope": "Development evidence only; no final eligibility or approval",
        "training_dimensions": dict(dimensions), "training_images": image_evidence,
        "scin_case_count": len(cases),
        "scin_head_neck_cases": sum(c["body_parts_head_or_neck"] == "YES" for c in cases),
        "scin_head_neck_at_distance_image_count": len(candidates),
        "scin_head_neck_at_distance_case_count": len({c["case_id"] for c in candidates}),
        "scin_metadata_candidates": candidates,
        "scin_warning": "Case-level location plus shot type does not establish a visible face, image-level location, usable mask, label support or reference suitability. No new image was inspected or downloaded.",
        "input_sha256": before,
    }
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if before != after:
        raise RuntimeError("Audit inputs changed during the run")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {"training_images", "scin_metadata_candidates", "input_sha256"}}, indent=2))


if __name__ == "__main__":
    main()
