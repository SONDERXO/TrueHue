"""Compare an experimental oval restriction on the 80 reviewed development images.

    venv/Scripts/python.exe scripts/16_compare_face_outline.py

No changes to baseline masks, source manifests, or manual decisions. All
experiment outputs are local and must not be treated as held-out evaluation.
"""
import csv
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import cv2
import numpy as np
from src.face_detection.detect_faces import _detect_face_boxes
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.utilities.config import get_config

prepare = importlib.import_module("11_prepare_training_manifests")
review_tools = importlib.import_module("15_prepare_fairface_mask_review")


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def panel(image, label):
    out = cv2.resize(image, (320, 320), interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(out, (0, 0), (320, 28), (0, 0, 0), -1)
    cv2.putText(out, label, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 255), 1)
    return out


def main():
    manifests = ROOT / "data/manifests"
    baseline_path = manifests / "fairface_candidate_processed_manifest.csv"
    master_path = manifests / "fairface_candidate_mask_quality_review.csv"
    sample_path = manifests / "fairface_random50_review_seed42.csv"
    output = ROOT / "outputs/face_outline_experiment_v1"
    if output.exists():
        raise FileExistsError("Experiment outputs already exist; refusing overwrite")
    source = {r["image_id"]: r for r in read(baseline_path)}
    reviewed = {r["image_id"]: r for r in read(master_path) if r["visual_review"] != "pending"}
    reviewed.update({r["image_id"]: r for r in read(sample_path)})
    config = get_config()
    yunet = ROOT / config.FACE_MODEL_PATH
    landmarker = ROOT / config.FACE_LANDMARKER_MODEL_PATH
    inputs = (baseline_path, master_path, sample_path, yunet, landmarker)
    for p in inputs:
        if not p.is_file():
            raise FileNotFoundError(p)
    hashes = {str(p): review_tools.digest(p) for p in inputs}
    output.mkdir()
    (output / "grids").mkdir()
    rows = []
    for index, (image_id, review) in enumerate(sorted(reviewed.items()), 1):
        stored = source[image_id]
        decision = review["visual_review"].strip().lower()
        decision = {"deny": "reject"}.get(decision, decision)
        row = dict(image_id=image_id, baseline_review=decision,
                   baseline_processing_status=stored["processing_status"],
                   baseline_review_notes=review["review_notes"], experiment_status="blocked",
                   experiment_visual_review="pending", experiment_review_notes="")
        try:
            image = cv2.imread(stored["image_path"])
            if image is None:
                raise ValueError("Unreadable source")
            boxes = _detect_face_boxes(image, yunet, .85)
            if len(boxes) != 1:
                raise ValueError("Single face required")
            x, y, w, h = boxes[0]
            crop = image[y:y+h, x:x+w].copy()
            v2 = prepare.compute_v2_skin_mask_with_margin(crop, image, boxes[0], landmarker)
            if not v2.landmarks_available:
                raise ValueError("V2 landmarks unavailable")
            before = compute_masked_lab_statistics(crop, v2.mask, 1000)
            before["skin_ratio_percent"] = round(np.count_nonzero(v2.mask) / (w*h)*100, 2)
            if stored["processing_status"] == "success":
                differences = review_tools.measurement_differences(stored, before)
                if differences:
                    raise ValueError("Baseline drift: " + ",".join(differences))
            elif int(float(stored["skin_pixels"])) != np.count_nonzero(v2.mask):
                raise ValueError("Excluded baseline mask pixel count changed")
            landmarks, _, _ = prepare.detect_landmarks_with_margin(image, boxes[0], landmarker)
            if landmarks is None:
                raise ValueError("Outline landmarks unavailable")
            # A repeated detection must reproduce the baseline exclusion geometry.
            if not np.array_equal(build_feature_exclusion_mask(crop, landmarks), v2.exclusion_mask):
                raise ValueError("Landmark geometry differs from baseline")
            after_mask, oval = restrict_to_face_outline(v2.mask, landmarks)
            after = compute_masked_lab_statistics(crop, after_mask, 1000)
            old_pixels = int(np.count_nonzero(v2.mask))
            new_pixels = int(np.count_nonzero(after_mask))
            row.update(experiment_status="compared", baseline_pixels=old_pixels,
                experiment_pixels=new_pixels, removed_pixels=old_pixels-new_pixels,
                retained_fraction=new_pixels/old_pixels if old_pixels else "",
                baseline_ita=before["ita_degrees"], experiment_ita=after["ita_degrees"],
                experiment_ita_valid=after["valid"], experiment_ita_reason=after["reason"],
                lost_minimum_pixel_validity=bool(before["valid"] and not after["valid"]))
            images = [crop, cv2.cvtColor(oval, cv2.COLOR_GRAY2BGR),
                      cv2.cvtColor(v2.mask, cv2.COLOR_GRAY2BGR),
                      cv2.cvtColor(after_mask, cv2.COLOR_GRAY2BGR)]
            grid = np.vstack([np.hstack([panel(images[0], "Original"), panel(images[1], "Face outline")]),
                              np.hstack([panel(images[2], "V2 baseline"), panel(images[3], "V2 intersect outline")])])
            path = output / "grids" / (image_id.replace("/", "_") + ".png")
            if not cv2.imwrite(str(path), grid):
                raise OSError("Grid write failed")
            row["comparison_grid"] = path.relative_to(ROOT).as_posix()
        except Exception as error:
            row["error"] = str(error)
        rows.append(row)
        if index % 20 == 0:
            print(f"Compared {index}/{len(reviewed)}", flush=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (output / "comparison.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    assert all(review_tools.digest(Path(p)) == h for p, h in hashes.items())
    summary = dict(reviewed_images=len(rows), compared=sum(r["experiment_status"] == "compared" for r in rows),
                   blocked=sum(r["experiment_status"] == "blocked" for r in rows),
                   lost_minimum_pixel_validity=sum(r.get("lost_minimum_pixel_validity", False) for r in rows),
                   baseline_accepted_losing_validity=sum(r["baseline_review"] == "accept" and r.get("lost_minimum_pixel_validity", False) for r in rows),
                   note="Development experiment only; numeric validity is not visual acceptance. V2 unchanged.",
                   input_sha256=hashes)
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    main()
