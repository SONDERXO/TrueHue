"""Descriptive facial-feature overlap in frozen vetoed branches; no split search."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/vetoed_branch_facial_audit_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    if OUT.exists():raise FileExistsError('Preserve audit')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    m=read('outputs/reserved_clean_veto_models_v1/models_PRIVATE.json')
    assert read('outputs/reserved_clean_veto_models_v1/verification_PRIVATE.json')['passed']
    facial=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees'];derived='input_mst_score'
    names=m['feature_names'];axes=facial+[derived];records=[]
    for f in m['folds']+[m['full']]:
        pre=f['pre_veto_model'];fittingclean=[f['training_features'][i] for i,flag in enumerate(pre['clean']) if flag]
        pooled=fittingclean+[r['features'] for r in f['reserved_clean_vectors']]
        limits={name:(min(f32(x[names.index(name)]) for x in pooled),max(f32(x[names.index(name)]) for x in pooled)) for name in axes}
        for leaf,hits in f['vetoed_leaves'].items():
            t=pre['trace'][int(leaf)];action=t['action'];assert action!=0
            targets=[]
            for i in t['rows']:
                if pre['costs'][i][action]>=pre['costs'][i][0]:continue
                x=f['training_features'][i];outside=[name for name,(lo,hi) in limits.items() if f32(x[names.index(name)])<lo or f32(x[names.index(name)])>hi]
                targets.append(dict(case_id=f['training_cases'][i],facial_values={name:f32(x[names.index(name)]) for name in axes},outside_pooled_clean_axes=outside))
            records.append(dict(fit_key=f['held_key'],leaf=int(leaf),action=action,training_rows=len(t['rows']),useful_training_rows=len(targets),
                fitting_clean_count=len(fittingclean),reserved_clean_count=len(f['reserved_clean_vectors']),reserved_clean_hits=hits,
                pooled_clean_ranges={k:list(v) for k,v in limits.items()},
                useful_outside_raw_facial=sum(any(a in facial for a in r['outside_pooled_clean_axes']) for r in targets),
                useful_outside_raw_plus_MST=sum(bool(r['outside_pooled_clean_axes']) for r in targets),targets=targets))
    summary={}
    for scope in ('full','folds'):
        rr=[r for r in records if (r['fit_key']=='full')==(scope=='full')]
        summary[scope]={name:sum(r[name] for r in rr) for name in ('training_rows','useful_training_rows','useful_outside_raw_facial','useful_outside_raw_plus_MST')}
        summary[scope]['vetoed_leaves']=len(rr)
        summary[scope]['reserved_clean_hit_occurrences']=sum(len(r['reserved_clean_hits']) for r in rr)
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();result=dict(summary=summary,records=records,input_sha256=bound,new_fits=0,new_predictions=0,holdout_image_reads=0,
        method='Fixed per-axis float32 min/max over fitting clean plus reserved clean rows. Facial Lab/ITA only; MST reported separately. Useful means the frozen pre-veto leaf action improves saved training RGB cost.',
        limitation='Pooled range overlap does not prove multivariate inseparability; outside ranges is training-only, not safety. Repeated folds are not independent. No evaluation outcomes choose ranges or policy.')
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
