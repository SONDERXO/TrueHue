"""Saved model JSON only; no sklearn, numpy, image reads, fits or rendering."""
import hashlib
import json
import math
import struct
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'outputs/wb_feature_direct_prediction_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def route(model,features):
    values=[struct.unpack('!f',struct.pack('!f',v))[0] for v in features]
    node=0;path=[]
    while model['nodes'][node]['kind']=='split':
        n=model['nodes'][node];left=values[n['feature']]<=n['threshold']
        path.append(dict(node=node,feature=n['feature'],wb_coordinate=n['feature']>=281,value=values[n['feature']],threshold=n['threshold'],branch='left' if left else 'right'))
        node=n['left'] if left else n['right']
    return node,model['nodes'][node]['values'],path

def main():
    out=ROOT/'outputs/wb_three_exposure_miss_diagnosis_v1'
    if out.exists():raise FileExistsError(out)
    proof=read(RUN/'verification.json');hashes={p.replace('\\','/'):h for p,h in proof['artifacts'].items()}
    ids=['camera_halfstop_ffhq_48879__exposure_under','camera_halfstop_ffhq_16061__exposure_under','camera_halfstop_ffhq_48879__combined_under']
    files=['rows.json','plan.json','held_controls_sealed.json','all_fits_verified.json']+[f'models/{arm}_{sid}.json' for arm in ['281','314'] for sid in ['48879','16061']]
    for p in files:assert sha(RUN/p)==hashes[p]
    rows={r['case_id']:r for r in read(RUN/'rows.json')};folds={f['held_source_id']:f for f in read(RUN/'plan.json')['folds']}
    held={p['case_id']:p for p in read(RUN/'held_controls_sealed.json')};result=[]
    for case in ids:
        row=rows[case];source=row['source_id'];entry=dict(case_id=case,arms={})
        for arm in ['281','314']:
            model=read(RUN/f'models/{arm}_{source}.json');leaf,pred,path=route(model,row['x'+arm])
            assert pred==held[case]['controls'+arm]
            fit=[rows[c] for c in folds[source]['fitting_cases']];assert len(fit)==60 and all(r['source_id']!=source for r in fit)
            members=[r for r in fit if route(model,r['x'+arm])[0]==leaf]
            assert members
            for j,v in enumerate(pred):assert math.isclose(v,math.fsum(r['y'][j] for r in members)/len(members),abs_tol=1e-12,rel_tol=1e-12)
            entry['arms'][arm]=dict(leaf=leaf,controls=pred,path=path,leaf_fitting_roles=dict(Counter(r['role'] for r in members)),leaf_fitting_cases=[r['case_id'] for r in members])
        assert entry['arms']['314']['controls']==[1.,1.,1.,1.,1.]
        result.append(entry)
    for p in files:assert sha(RUN/p)==hashes[p]
    out.mkdir();report=dict(passed=True,cases=result,source_metadata_sha256={p:sha(RUN/p) for p in files},new_fits=0,pixel_reads=0,renders=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps([{'case_id':r['case_id'],'arms':{a:{k:v[k] for k in ['controls','leaf_fitting_roles']} for a,v in r['arms'].items()}} for r in result],indent=2))

if __name__=='__main__':main()
