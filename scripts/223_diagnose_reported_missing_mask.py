"""Reproduce source31367's detector failure without changing thresholds."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
from src.utilities.config import get_config
from src.face_detection.detect_faces import _detect_face_boxes


def main():
    parent=ROOT/'outputs/correction_training_preparation_v1'
    out=ROOT/'outputs/reported_missing_mask_31367_v1'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    rows=[json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    row=next(r for r in rows if r['source_id']=='31367')
    image_path=parent/'images/31367_reference.png';config=get_config()
    image=cv2.imread(str(image_path))
    assert image.shape==(256,256,3)
    expected=json.loads((parent/'verification.json').read_text(encoding='utf-8'))['evidence_sha256']
    assert digest(image_path)==expected['images/31367_reference.png']
    boxes=_detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    assert len(boxes)==row['reference_measurement']['face_count']==0
    result=dict(image_id=row['image_id'],status='excluded_face_detection_failure',
        user_report='Very bad. No face mask detected',detector_threshold=.85,detected_faces=len(boxes),
        stage='face_detection',mask_computation_attempted=False,
        user_message='No reliable face detected. Use a clear, unobstructed photo containing one face.',
        baseline_failure_reproduced=True,forced_mask_generated=False,training_eligible=False,
        source_reference_sha256=digest(image_path),detector_model_sha256=digest(ROOT/config.FACE_MODEL_PATH))
    out.mkdir();(out/'diagnosis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>31367: face detection failed</title><style>body{font:18px system-ui;background:#151923;color:#eee;max-width:900px;margin:32px auto;padding:16px}img{width:320px;max-width:100%}</style><h1>31367 — face detection failed</h1><p>No reliable face detected at the unchanged 0.85 threshold. Masking was not attempted; an empty mask is not a successful result.</p><img src="../correction_training_preparation_v1/images/31367_reference.png"><p>This source remains excluded. A clear, unobstructed single-face photograph is required. No replacement source or forced mask has been selected.</p>',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
