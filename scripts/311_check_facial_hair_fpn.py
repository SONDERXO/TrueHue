"""Same frozen twelve inputs/rule; compare one stronger auxiliary, no tuning."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.facial_hair_exclusion import FacialHairAuxiliary,lower_face_suggestion,apply_exclusions


def main():
    parent=ROOT/'outputs/facial_hair_suggestions_v1';out=ROOT/'outputs/facial_hair_fpn_suggestions_v1'
    if out.exists():raise FileExistsError(out)
    records=json.loads((parent/'records.json').read_text())
    model=ROOT/'models/facial_hair_fpn_auxiliary_v1/fpn_resnet50_fp_512.onnx'
    auxiliary=FacialHairAuxiliary(model,profile='fpn512',backend='onnxruntime')
    out.mkdir()
    for name in ['masks','categories','boards']:(out/name).mkdir()
    (out/'plan.json').write_text(json.dumps(dict(source_ids=[r['source_id'] for r in records],
        rule_unchanged=True,threshold_search=False,automatically_apply=False,
        source_records_sha256=hashlib.sha256((parent/'records.json').read_bytes()).hexdigest(),
        model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),backend='onnxruntime_CPU'),indent=2),encoding='utf-8')
    output=[]
    for old in records:
        sid=old['source_id'];image_path=ROOT/'outputs/correction_training_preparation_v1/images'/f'{sid}_reference.png'
        assert hashlib.sha256(image_path.read_bytes()).hexdigest()==old['image_sha256']
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(dict(image_id=old['image_id'],role='train',phase='fixed_higher_capacity_auxiliary_check'))+'\n')
        image=cv2.imread(str(image_path));base=cv2.imread(str(parent/'masks'/f'{sid}_preferred.png'),0)
        primary=cv2.imread(str(parent/'categories'/f'{sid}_primary.png'),0)
        cats=auxiliary.categories_bgr(image);veto,report=lower_face_suggestion(base,primary,cats);candidate,alpha=apply_exclusions(base,veto)
        for suffix,array in [('_suggestion',veto.astype(np.uint8)*255),('_candidate',candidate),('_alpha',alpha)]:
            cv2.imwrite(str(out/'masks'/f'{sid}{suffix}.png'),array)
        cv2.imwrite(str(out/'categories'/f'{sid}.png'),cats)
        panels=[]
        for title,mask in [('Photo',None),('Preferred full mask',base),('Suggestion (red)',veto),('If applied',candidate)]:
            shown=image.copy()
            if mask is not None:
                selected=mask>0;shown[selected]=np.rint(.5*shown[selected]+.5*np.array([0,0,255] if title=='Suggestion (red)' else [0,255,0])).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,25,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(shown,title,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.43,(255,255,255),1);panels.append(shown)
        cv2.imwrite(str(out/'boards'/f'{sid}.png'),np.hstack(panels))
        output.append(dict(old,report=report,removed_pixels=int(veto.sum()),auxiliary_profile='fpn512'))
        print(sid,report['suggested_pixels'],flush=True)
    (out/'records.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    sections=''.join('<section><h2>'+r['source_id']+' · '+r['group']+'</h2><p>Suggested exclusions: '+str(r['removed_pixels'])+'</p><img src="boards/'+r['source_id']+'.png"></section>' for r in output)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Fixed FPN auxiliary check</title><style>body{font:17px system-ui;margin:25px;background:#151923;color:#eee}img{width:100%;max-width:1300px}section{border-top:1px solid #777}</style><h1>Higher-capacity auxiliary check</h1><p>Same inputs and exclusion rule. No tuning and no default mask change.</p>'+sections,encoding='utf-8')


if __name__=='__main__':main()
