"""Build original/exclusion-overlay contact sheets for 45 accepted images.

Local diagnostic evidence only. Original decisions and masks stay unchanged.
"""
import csv
import importlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import cv2
import numpy as np
from src.utilities.config import get_config


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    output = ROOT / "outputs/accepted_exclusion_audit"
    if output.exists():
        raise FileExistsError("Audit package exists")
    manifest = ROOT / "data/manifests"
    reviewed = {r["image_id"]: r for r in read(manifest / "fairface_candidate_mask_quality_review.csv")}
    reviewed.update({r["image_id"]: r for r in read(manifest / "fairface_random50_review_seed42.csv")})
    accepted = sorted(k for k, v in reviewed.items() if v["visual_review"].strip().lower() == "accept")
    source = {r["image_id"]: r for r in read(manifest / "fairface_candidate_processed_manifest.csv")}
    prepare = importlib.import_module("11_prepare_training_manifests")
    check = importlib.import_module("15_prepare_fairface_mask_review")
    config = get_config()
    yunet, model = ROOT / config.FACE_MODEL_PATH, ROOT / config.FACE_LANDMARKER_MODEL_PATH
    if not yunet.is_file() or not model.is_file():
        raise FileNotFoundError("Local models required")
    output.mkdir()
    tiles, rows = [], []
    for image_id in accepted:
        stored = source[image_id]
        image = cv2.imread(stored["image_path"])
        if image is None:
            raise ValueError(image_id)
        boxes = prepare._detect_face_boxes(image, yunet, .85)
        if len(boxes) != 1:
            raise ValueError(image_id)
        x,y,w,h = boxes[0]
        crop = image[y:y+h,x:x+w].copy()
        result = prepare.compute_v2_skin_mask_with_margin(crop,image,boxes[0],model)
        stats = prepare.compute_masked_lab_statistics(crop,result.mask,1000)
        stats['skin_ratio_percent'] = round(np.count_nonzero(result.mask)/(w*h)*100,2)
        if check.measurement_differences(stored,stats):
            raise ValueError("Baseline drift: " + image_id)
        overlay = crop.copy()
        selected = result.exclusion_mask > 0
        overlay[selected] = (.45*crop[selected]+.55*np.array([0,0,255])).astype(np.uint8)
        tile = np.zeros((220,400,3),np.uint8)
        tile[20:,:200] = cv2.resize(crop,(200,200))
        tile[20:,200:] = cv2.resize(overlay,(200,200))
        cv2.putText(tile,image_id,(4,15),cv2.FONT_HERSHEY_SIMPLEX,.4,(255,255,255),1)
        tiles.append(tile)
        path = output/(image_id.replace('/','_')+'.png')
        if not cv2.imwrite(str(path),tile):
            raise OSError(path)
        rows.append(dict(image_id=image_id,evidence_path=path.relative_to(ROOT).as_posix(),
                         exclusion_audit='pending',audit_notes='',auditor='Codex visual inspection'))
    for start in range(0,len(tiles),9):
        group = tiles[start:start+9]
        group += [np.zeros_like(tiles[0])]*(9-len(group))
        sheet = np.vstack([np.hstack(group[i:i+3]) for i in (0,3,6)])
        cv2.imwrite(str(output/f'sheet_{start//9+1:02d}.png'),sheet)
    with (output/'audit.csv').open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(f'Prepared {len(rows)} verified overlays, five contact sheets. Red means excluded.')


if __name__ == '__main__':
    main()
