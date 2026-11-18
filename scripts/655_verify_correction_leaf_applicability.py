"""Independent scalar float32 range and category-summary checks; zero inference."""
from pathlib import Path
from collections import Counter
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/correction_leaf_applicability_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'audit_PRIVATE.json');m=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    fits={f['held_key']:f for f in m['folds']+[m['full']]};pred={p['case_id']:p for p in m['predictions']};cache={};checks=0
    for r in d['records']:
        p=pred[r['case_id']]
        if p['features'] is None:assert not r['range_available'] and r['outside'] is None;continue
        f=fits[r['fit_key']];tree=f['model']['tree'];x=list(map(f32,p['features']));node=0
        while tree['nodes'][node]['kind']=='split':
            n=tree['nodes'][node];node=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        assert node==r['leaf'];key=(r['fit_key'],node)
        if key not in cache:
            ids=f['model']['trace'][node]['rows'];cache[key]=[(min(f32(f['training_features'][i][j]) for i in ids),max(f32(f['training_features'][i][j]) for i in ids)) for j in range(12)]
        outside=[name for j,name in enumerate(m['feature_names']) if x[j]<cache[key][j][0] or x[j]>cache[key][j][1]]
        assert outside==r['outside_axes'];checks+=1
    for key,s in d['summary'].items():
        co,layer=key.split('_',1);rr=[r for r in d['records'] if r['cohort']==co and r['layer']==layer]
        for group,a in s['groups'].items():
            flagged=[r for r in rr if r['outside'] and r['outside'][group]];edited=[r for r in flagged if r['changed']]
            assert len(flagged)==a['flagged_available'] and len(edited)==a['flagged_changed']
            assert dict(Counter(r['RGB_category'] for r in edited))==a['changed_RGB_categories']
            assert dict(Counter(r['DE_category'] for r in edited))==a['changed_DE_categories']
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,attempts=len(d['records']),available_scalar_range_checks=checks,feature_comparisons=checks*12,new_fits=0,new_predictions=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
