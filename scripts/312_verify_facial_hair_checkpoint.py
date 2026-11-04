"""Replay saved auxiliary diagnostics; preserve the decision without more tuning."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.facial_hair_exclusion import lower_face_suggestion,apply_exclusions,preprocess_auxiliary


def main():
    out=ROOT/'outputs/facial_hair_brush_verification_v1'
    out.mkdir(exist_ok=True)
    destination=out/'verification.json'
    if destination.exists():raise FileExistsError(destination)
    parent=ROOT/'outputs/facial_hair_suggestions_v1'
    checks=[]
    for name in ['facial_hair_suggestions_v1','facial_hair_fpn_suggestions_v1']:
        folder=ROOT/'outputs'/name
        records=json.loads((folder/'records.json').read_text())
        assert len(records)==12
        for row in records:
            sid=row['source_id']
            base=cv2.imread(str(parent/'masks'/f'{sid}_preferred.png'),0)
            primary=cv2.imread(str(parent/'categories'/f'{sid}_primary.png'),0)
            suffix=f'{sid}_auxiliary.png' if name=='facial_hair_suggestions_v1' else f'{sid}.png'
            auxiliary=cv2.imread(str(folder/'categories'/suffix),0)
            veto,_=lower_face_suggestion(base,primary,auxiliary)
            mask,alpha=apply_exclusions(base,veto)
            for label,array in [('suggestion',veto.astype(np.uint8)*255),('candidate',mask),('alpha',alpha)]:
                assert np.array_equal(array,cv2.imread(str(folder/'masks'/f'{sid}_{label}.png'),0))
            assert not ((mask>0)&(base==0)).any()
            assert int(veto.sum())==row['removed_pixels']
        checks.append(dict(experiment=name,replayed_cases=len(records),
            clean_reference_removed_pixels={r['source_id']:r['removed_pixels'] for r in records if r['group']!='facial_hair_example'}))
    # One controlled runtime parity check, not another model/threshold trial.
    sys.path.insert(0,str(ROOT/'models/facial_hair_auxiliary_v1/runtime'))
    import onnxruntime as ort
    model=ROOT/'models/facial_hair_auxiliary_v1/fcn_mobilenetv2_fp.onnx'
    image=cv2.imread(str(ROOT/'outputs/correction_training_preparation_v1/images/63509_reference.png'))
    tensor=preprocess_auxiliary(image)
    net=cv2.dnn.readNetFromONNX(str(model));net.setInput(tensor)
    opencv=net.forward('logits')
    session=ort.InferenceSession(str(model),providers=['CPUExecutionProvider'])
    other=session.run(['logits'],{'image':tensor})[0]
    agreement=float(np.mean(opencv.argmax(1)==other.argmax(1)))
    assert agreement==1.0
    smoke=ROOT/'outputs/face_mask_editor_base_smoke_v1/mask.png'
    preferred=ROOT/'outputs/semantic_face_coverage_v1/masks/61590_occlusion_regression.png'
    assert np.array_equal(cv2.imread(str(smoke),0),cv2.imread(str(preferred),0))
    payload=dict(saved_diagnostic_replays=checks,
        runtime_parity=dict(source_id='63509',opencv=cv2.__version__,onnxruntime=ort.__version__,
            maximum_logit_difference=float(np.max(np.abs(opencv-other))),class_agreement=agreement),
        preferred_preview_mask_unchanged=True,
        default_automatic_exclusion=False,decision='Do not adopt either auxiliary; visible clean-skin loss. Manual exclusion brush only.',
        dense_beard_ground_truth_available=False,training_admitted=False,ITA_MST_calls=0,
        diagnostic_records_sha256={c['experiment']:hashlib.sha256((ROOT/'outputs'/c['experiment']/'records.json').read_bytes()).hexdigest() for c in checks})
    destination.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps(payload,indent=2))


if __name__=='__main__':main()
