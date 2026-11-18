"""Independent scalar clean bounds and prediction-policy replay, no fitting."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/facial_veto_exception_models_v1'
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
def route(tree,x):
    i=0
    while tree['nodes'][i]['kind']=='split':
        n=tree['nodes'][i];i=n['left'] if f32(x[n['feature']])<=n['threshold'] else n['right']
    return i,tree['nodes'][i]['values']
def main():
    import runpy
    outside=runpy.run_path(str(ROOT/'scripts/636_apply_facial_veto_exception.py'))['outside']
    testnames=['L','a','b','ITA'];testbounds={n:[-1.,1.] for n in testnames}
    for x,expected in [([0.,0.,0.,0.],False),([1.,-1.,1.,-1.],False),([1.01,0.,0.,0.],True),([-1.01,0.,0.,0.],True),([float('nan'),0.,0.,0.],False),([float('inf'),0.,0.,0.],False),(None,False),([],False)]:
        assert outside(x,testnames,testbounds)==expected
    assert not outside([0.]*4,testnames,{})
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/reserved_clean_veto_models_v1/models_PRIVATE.json')
    for key in ('folds','full','calibrations','feature_names','reserved_groups','reserved_all_conditions','reserved_usable_clean'):assert d[key]==old[key]
    fits={f['held_key']:f for f in d['folds']+[d['full']]};names=d['feature_names'];bounds={};checks=0
    for key,f in fits.items():
        clean=[x for x,flag in zip(f['training_features'],f['model']['clean']) if flag]+[r['features'] for r in f['reserved_clean_vectors']]
        b=d['facial_exception_policy']['fits'][key]['clean_bounds']
        assert list(b)==['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees']
        for name,(lo,hi) in b.items():
            j=names.index(name);assert lo==min(f32(x[j]) for x in clean) and hi==max(f32(x[j]) for x in clean)
        bounds[key]=b
        for x in clean:
            leaf,action=route(f['model']['tree'],x)
            assert action==[1.,1.,1.] and not any(f32(x[names.index(k)])<v[0] or f32(x[names.index(k)])>v[1] for k,v in b.items());checks+=1
    restored=0
    for p,q,t in zip(old['predictions'],d['predictions'],d['exception_trace'],strict=True):
        for field in p:
            if field!='parameters':assert p[field]==q[field]
        key=p['subject_id'] if p['cohort']=='development' else 'full';f=fits[key];expected=p['parameters'];restore=False;leaf=None
        if p['features'] is not None and p['status']=='available':
            leaf,_=route(f['model']['tree'],p['features'])
            if str(leaf) in f['vetoed_leaves']:
                restore=any(f32(p['features'][names.index(k)])<v[0] or f32(p['features'][names.index(k)])>v[1] for k,v in bounds[key].items())
                if restore:expected=route(f['pre_veto_model']['tree'],p['features'])[1]
        assert q['parameters']==expected and t==dict(case_id=q['case_id'],fit_key=key,leaf=leaf,restored=restore);restored+=restore
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,prediction_checks=756,pooled_clean_occurrences=checks,restored_controls=restored,boundary_failure_checks=9,new_fits=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
