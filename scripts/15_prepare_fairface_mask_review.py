"""Prepare local manual-review records and verified frozen-V2 review grids.

Run from the project root with venv/Scripts/python.exe. Existing review files
are protected; this command creates a new review package, not pipeline outputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]


def read_workbook(path):
    """Read the supplied review workbook without modifying it."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings = ["".join(n.itertext()) for n in ET.fromstring(
            archive.read("xl/sharedStrings.xml")).findall("m:si", ns)]
        rows = []
        for row in ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall("m:sheetData/m:row", ns):
            values = {}
            for cell in row:
                value = cell.find("m:v", ns)
                text = value.text if value is not None else ""
                if cell.get("t") == "s":
                    text = strings[int(text)]
                elif cell.get("t") == "inlineStr":
                    text = "".join(cell.find("m:is", ns).itertext())
                values[cell.get("r").rstrip("0123456789")] = text
            rows.append(values)
    return rows[1:]


def measurement_differences(stored, current):
    """Compare stored rounded measurements, rejecting missing/nonfinite values."""
    differences = []
    for key in ("skin_pixels", "skin_ratio_percent", "mean_l_star", "mean_a_star", "mean_b_star", "ita_degrees"):
        try:
            before, after = float(stored[key]), float(current[key])
            tolerance = 0 if key == "skin_pixels" else 0.00005
            if not (math.isfinite(before) and math.isfinite(after)) or abs(before - after) > tolerance:
                differences.append(key)
        except (ValueError, TypeError, KeyError):
            differences.append(key)
    return differences


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    args = parser.parse_args()
    source = ROOT / "data/manifests/fairface_candidate_processed_manifest.csv"
    output = ROOT / "data/manifests/fairface_candidate_mask_quality_review.csv"
    audit = ROOT / "data/manifests/fairface_mask_review_regeneration_audit.csv"
    provenance = ROOT / "data/manifests/fairface_mask_review_provenance.json"
    grids = ROOT / "outputs/fairface_mask_review"
    if any(p.exists() for p in (output, audit, provenance, grids)):
        raise FileExistsError("Review package already exists; refusing to overwrite decisions or evidence.")
    with source.open(newline="", encoding="utf-8-sig") as stream:
        records = list(csv.DictReader(stream))
    ids = [r["image_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source image IDs")
    filename_ids = {i.replace("/", "_") + "_visualization": i for i in ids}
    if len(filename_ids) != len(ids):
        raise ValueError("Ambiguous sanitized image IDs")
    reviewed = {}
    for row in read_workbook(args.workbook):
        image_id = filename_ids[row["A"]]
        if image_id in reviewed:
            raise ValueError("Duplicate workbook image ID")
        decision = {"Accept": "accept", "Deny": "reject", "Unsure": "unsure"}[row["B"]]
        note = row.get("C", "")
        if decision == "unsure":
            decision = "accept" if image_id in {"fairface__train/22057.jpg", "fairface__train/48136.jpg"} else "reject"
            note += " Final user decision on 2026-10-19: " + decision + "."
        reviewed[image_id] = (decision, note)
    if len(reviewed) != 30:
        raise ValueError("Expected the completed 30-image workbook")

    import cv2
    import numpy as np
    from src.utilities.config import get_config
    from src.face_detection.detect_faces import _detect_face_boxes
    from src.ita_estimation.compute_ita import compute_masked_lab_statistics
    from src.skin_masking.skin_mask import save_mask_visualization
    prepare = importlib.import_module("11_prepare_training_manifests")
    config = get_config()
    yunet, landmarker = ROOT / config.FACE_MODEL_PATH, ROOT / config.FACE_LANDMARKER_MODEL_PATH
    for path in (yunet, landmarker):
        if not path.is_file():
            raise FileNotFoundError(path)
    fingerprints = {str(p): digest(p) for p in (source, args.workbook, yunet, landmarker)}
    grids.mkdir(parents=True)
    provenance.write_text(json.dumps({"sha256": fingerprints, "score_threshold": 0.85,
        "minimum_skin_pixels": 1000, "protocol": "fairface_mask_review_v1",
        "review_date_note": "Original workbook review date unknown; final unsure resolutions confirmed 2026-10-19.",
        "versions": {name: importlib.import_module(name).__version__ for name in ("cv2", "numpy", "mediapipe")}}, indent=2), encoding="utf-8")
    fields = ["image_id", "processing_status", "automated_exclusion_reason", "visual_review", "reason_codes", "review_notes", "reviewer", "review_date", "review_source", "visualization_path", "review_protocol_version", "review_batch", "evidence_status"]
    audit_fields = ["image_id", "evidence_status", "details"]
    pending_index = 0
    with output.open("x", newline="", encoding="utf-8") as out, audit.open("x", newline="", encoding="utf-8") as audit_stream:
        writer, auditor = csv.DictWriter(out, fields), csv.DictWriter(audit_stream, audit_fields)
        writer.writeheader()
        auditor.writeheader()
        for record in sorted(records, key=lambda r: r["image_id"]):
            image_id = record["image_id"]
            decision, note = reviewed.get(image_id, ("pending", ""))
            row = dict.fromkeys(fields, "")
            row.update(image_id=image_id, processing_status=record["processing_status"],
                automated_exclusion_reason=record["exclusion_reason"], visual_review=decision,
                review_notes=note, review_protocol_version="fairface_mask_review_v1")
            if image_id in reviewed:
                path = ROOT / "outputs/fairface_candidate_visualizations" / (image_id.replace("/", "_") + "_visualization.png")
                if not path.is_file():
                    raise FileNotFoundError(path)
                row.update(reviewer="User", review_source=args.workbook.name + "; final decisions: docs/expirement-log.md",
                    visualization_path=path.relative_to(ROOT).as_posix(), evidence_status="existing_reviewed_grid")
            elif record["processing_status"] == "success":
                pending_index += 1
                batch = f"batch_{(pending_index - 1) // 25 + 1:03d}"
                row["review_batch"] = batch
                try:
                    image = cv2.imread(record["image_path"])
                    if image is None:
                        raise ValueError("Image unreadable")
                    boxes = _detect_face_boxes(image, yunet, 0.85)
                    if len(boxes) != 1:
                        raise ValueError(f"Expected one face, found {len(boxes)}")
                    x, y, w, h = boxes[0]
                    crop = image[y:y+h, x:x+w].copy()
                    result = prepare.compute_v2_skin_mask_with_margin(face_crop_bgr=crop,
                        image_bgr=image, face_box=(x, y, w, h), landmarker_model=landmarker)
                    if not result.landmarks_available:
                        raise ValueError("V2 landmarks unavailable")
                    current = compute_masked_lab_statistics(crop, result.mask, 1000)
                    current["skin_ratio_percent"] = round(np.count_nonzero(result.mask) / (w*h) * 100, 2)
                    differences = measurement_differences(record, current)
                    if not current["valid"] or differences:
                        raise ValueError("Baseline measurement mismatch: " + ", ".join(differences))
                    destination = grids / batch / (image_id.replace("/", "_") + "_visualization.png")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    save_mask_visualization(crop, result.candidate_mask, result.exclusion_mask,
                        result.mask, str(destination), landmarks_available=True)
                    row.update(visualization_path=destination.relative_to(ROOT).as_posix(), evidence_status="verified_measurements")
                    details = "Skin pixels, coverage, mean Lab and ITA match stored rounded measurements."
                except Exception as error:
                    row["evidence_status"] = "blocked"
                    details = str(error)
                auditor.writerow(dict(image_id=image_id, evidence_status=row["evidence_status"], details=details))
                audit_stream.flush()
                if pending_index % 25 == 0:
                    print(f"Prepared {pending_index}/510 pending-success evidence checks", flush=True)
            else:
                row["evidence_status"] = "automatically_excluded"
            writer.writerow(row)
            out.flush()
    if any(digest(Path(p)) != before for p, before in fingerprints.items()):
        raise RuntimeError("An input changed during preparation")
    print(f"Review record: {output}", flush=True)


if __name__ == "__main__":
    main()
