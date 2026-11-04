"""Isolated native/256-square development comparison and local SCIN check.

No correction model is loaded, no labels are assigned and no inputs are changed.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_image(path, image):
    if not cv2.imwrite(str(path), image):
        raise OSError(path)


def main():
    config = get_config()
    prepare = importlib.import_module("11_prepare_training_manifests")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/square_preprocessing_v1')
    output = parser.parse_args().output_dir
    if output.exists():
        raise FileExistsError(output)
    source = ROOT / "data/manifests/controlled_development_v1/selected_sources.csv"
    with source.open(encoding="utf-8-sig", newline="") as stream:
        sources = list(csv.DictReader(stream))
    assert len(sources) == 8
    detector = ROOT / config.FACE_MODEL_PATH
    landmarker = ROOT / config.FACE_LANDMARKER_MODEL_PATH
    tracked = [source, detector, landmarker, Path(__file__),
               ROOT / "scripts/11_prepare_training_manifests.py",
               ROOT / config.CORRECTION_PROTOTYPE_MODEL_PATH,
               ROOT / "data/manifests/controlled_training_v2/train.csv"]
    tracked += [Path(row["image_path"]) for row in sources]
    fingerprints = {str(p): digest(p) for p in tracked}
    output.mkdir(parents=True)
    (output / "run-status.json").write_text('{"status":"running"}', encoding="utf-8")
    measurements = []
    boards = []

    def measure(image, stem):
        record = {"width": image.shape[1], "height": image.shape[0]}
        mask = np.zeros(image.shape[:2], np.uint8)
        boxes = prepare._detect_face_boxes(image, detector, .85)
        record.update(face_count=len(boxes), face_boxes=[[int(v) for v in box] for box in boxes])
        if len(boxes) != 1:
            record["status"] = "expected_single_face"
        else:
            x, y, w, h = boxes[0]
            crop = image[y:y+h, x:x+w].copy()
            result = prepare.compute_versioned_skin_mask(
                crop, image, boxes[0], landmarker, "v2_complete_mouth_v1")
            mask[y:y+h, x:x+w] = result.mask
            stats = compute_masked_lab_statistics(crop, result.mask, 1000)
            record.update(stats)
            record["landmarks_available"] = bool(result.landmarks_available)
            record["status"] = ("success" if result.landmarks_available and stats["valid"]
                                else "landmarks_unavailable" if not result.landmarks_available
                                else stats["reason"])
            record["skin_fraction_of_image"] = float(np.count_nonzero(mask) / mask.size)
        write_image(output / f"{stem}_input.png", image)
        write_image(output / f"{stem}_mask.png", mask)
        return record, mask

    for row in sources:
        path = Path(row["image_path"])
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(path)
        # Explicit square resize before every detection/landmark/measurement step.
        # INTER_LINEAR is OpenCV resize's default and matches the proposal's call.
        square = cv2.resize(image, (config.IMAGE_SIZE, config.IMAGE_SIZE),
                            interpolation=cv2.INTER_LINEAR)
        stem = path.stem
        native, mask_native = measure(image, stem + "_native")
        resized, mask_square = measure(square, stem + "_square")
        mapped = cv2.resize(mask_native, (config.IMAGE_SIZE, config.IMAGE_SIZE),
                            interpolation=cv2.INTER_NEAREST) > 0
        selected = mask_square > 0
        union = np.count_nonzero(mapped | selected)
        comparison = {"image_id": row["image_id"], "source_path": str(path),
                      "partition": row["partition"], "native": native,
                      "square": resized,
                      "mapped_native_vs_recomputed_square_iou":
                          float(np.count_nonzero(mapped & selected) / union) if union else None,
                      "iou_warning": "Mask agreement, not accuracy; mapped mask is comparison-only."}
        if native["status"] == resized["status"] == "success":
            comparison["square_minus_native"] = {
                key: resized[key] - native[key] for key in
                ("mean_l_star", "mean_a_star", "mean_b_star", "ita_degrees", "skin_pixels")}
            comparison["native_minus_stored"] = {
                key: native[key] - float(row[column]) for key, column in
                (("mean_l_star", "mean_l_star"), ("mean_a_star", "mean_a_star"),
                 ("mean_b_star", "mean_b_star"), ("ita_degrees", "ita_degrees"))}
        panels = []
        for label, shown, mask in [("Native input", image, None),
                                    ("Native estimation", image, mask_native),
                                    ("256 square input", square, None),
                                    ("256 recomputed", square, mask_square)]:
            panel = shown.copy()
            if mask is not None:
                panel[mask > 0] = np.rint(.55*panel[mask > 0] + .45*np.array([0, 220, 0])).astype(np.uint8)
            panel = cv2.resize(panel, (256, 256))
            panel = cv2.copyMakeBorder(panel, 30, 0, 0, 0, cv2.BORDER_CONSTANT)
            cv2.putText(panel, label, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
            panels.append(panel)
        board = f"{stem}_comparison.png"
        write_image(output / board, np.hstack(panels))
        boards.append(board)
        measurements.append(comparison)
        print(f"{stem}: {native['status']} -> {resized['status']}", flush=True)

    evidence = ROOT / "outputs/method_alignment_v1/evidence.json"
    candidates = json.loads(evidence.read_text(encoding="utf-8"))["scin_metadata_candidates"]
    files = {p.name: p for p in (ROOT / config.DATA_RAW / "scin").rglob("*") if p.is_file()}
    availability = []
    for candidate in candidates:
        names = [f"scin__{candidate['case_id']}__{candidate['image_slot']}.png",
                 Path(candidate["image_path"]).name]
        found = next((files[name] for name in names if name in files), None)
        availability.append(dict(candidate, local_path=str(found) if found else None))
    local = sorted([r for r in availability if r["local_path"]],
                   key=lambda r: (r["case_id"], r["image_slot"]))
    # Fixed bound, one image per case; no acquisition or cohort expansion.
    scin_checks = []
    for candidate in local[:24]:
        image = cv2.imread(candidate["local_path"])
        if image is None:
            scin_checks.append(dict(candidate, status="unreadable"))
            continue
        square = cv2.resize(image, (config.IMAGE_SIZE, config.IMAGE_SIZE), interpolation=cv2.INTER_LINEAR)
        result, _ = measure(square, f"scin_{candidate['case_id']}_{candidate['image_slot']}")
        scin_checks.append(dict(candidate, **result,
                                eligibility="not_human_reviewed_not_admitted_to_training"))
    report = dict(status="complete", interpolation="INTER_LINEAR",
                  mask_version="v2_complete_mouth_v1", detection_threshold=.85,
                  minimum_skin_pixels=1000, measurement_scope="full resized image then fresh face crop",
                  source_count=len(sources), measurements=measurements,
                  native_status_counts=dict(Counter(r['native']['status'] for r in measurements)),
                  square_status_counts=dict(Counter(r['square']['status'] for r in measurements)),
                  scin_metadata_candidates=len(candidates), scin_local_available=len(local),
                  scin_check_limit=24, scin_availability=availability, scin_checks=scin_checks,
                  input_sha256={**fingerprints, str(evidence): digest(evidence)},
                  warning="Development only; mask agreement is not accuracy; no correction model fit or MST labels.")
    assert fingerprints == {str(p): digest(p) for p in tracked}, "Inputs changed"
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "review-index.md").write_text(
        "# Native versus 256-square preprocessing\n\nDevelopment masks, not corrected images.\n\n" +
        "\n".join(f"- [{name}]({name})" for name in boards), encoding="utf-8")
    (output / "run-status.json").write_text('{"status":"complete"}', encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["native_status_counts", "square_status_counts", "scin_local_available"]}))


if __name__ == "__main__":
    main()
