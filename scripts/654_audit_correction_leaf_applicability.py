"""All756 saved predictions versus own fitting-leaf ranges; no new decisions."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/correction_leaf_applicability_v1'
RAW=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees']
def main():
    if OUT.exists():raise FileExistsError('Preserve audit')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    m=read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json');a=read('outputs/remaining_correction_failure_audit_v1/audit_PRIVATE.json')
    assert read('outputs/remaining_correction_failure_audit_v1/verification_PRIVATE.json')['passed']
    lookup={r['case_id']:r for r in a['records']};fits={f['held_key']:f for f in m['folds']+[m['full']]};names=m['feature_names'];ranges={};records=[]
    for key,f in fits.items():
        x=np.asarray(f['training_features'],np.float32)
        for t in f['model']['trace']:
            if f['model']['tree']['nodes'][t['node']]['kind']!='leaf':continue
            rows=x[t['rows']];ranges[(key,t['node'])]=(rows.min(0),rows.max(0))
    for p in m['predictions']:
        r=lookup[p['case_id']];key=p['subject_id'] if p['cohort']=='development' else 'full';outside=None;leaf=None
        if p['features'] is not None:
            leaf=PortableTree(fits[key]['model']['tree']).leaf_id(p['features']);lo,hi=ranges[key,leaf];x=np.asarray(p['features'],np.float32)
            outside=[name for j,name in enumerate(names) if x[j]<lo[j] or x[j]>hi[j]]
        flags=None if outside is None else dict(raw_facial=any(n in RAW for n in outside),derived_MST='input_mst_score' in outside,scene=any(n.startswith('scene_') for n in outside),any_feature=bool(outside))
        records.append(dict(case_id=p['case_id'],source_case=r['source_case'],cohort=r['cohort'],layer=r['layer'],fit_key=key,leaf=leaf,
            changed=r['changed_channels']>0,nonidentity_controls=p['parameters'] not in (None,[1.,1.,1.]),range_available=flags is not None,
            outside_axes=outside,outside=flags,RGB_category=r['metrics']['rgb8_mae_codes']['category'],DE_category=r['metrics']['relative_deltaE00_mean']['category']))
    summary={}
    for co in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in records if r['cohort']==co and r['layer']==layer];groups={}
            for group in ('raw_facial','derived_MST','scene','any_feature'):
                flagged=[r for r in rr if r['outside'] and r['outside'][group]];edits=[r for r in flagged if r['changed']]
                groups[group]=dict(flagged_available=len(flagged),flagged_changed=len(edits),changed_RGB_categories=dict(Counter(r['RGB_category'] for r in edits)),changed_DE_categories=dict(Counter(r['DE_category'] for r in edits)))
            summary[co+'_'+layer]=dict(attempts=len(rr),range_available=sum(r['range_available'] for r in rr),changed=sum(r['changed'] for r in rr),groups=groups)
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();(OUT/'audit_PRIVATE.json').write_text(json.dumps(dict(records=records,summary=summary,input_sha256=bound,new_fits=0,new_predictions=0,new_inference=0,holdout_image_reads=0,
        convention='Strict outside float32 min/max of all fitting rows in own routed leaf; raw facial, derived MST and scene separately. No margins, optimisation or guard applied.'),indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
