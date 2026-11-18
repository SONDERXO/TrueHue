"""Independent scalar optimum, immutable splits and final policy verification."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree,float32
OUT=ROOT/'outputs/fixed_structure_nonharm_models_v1'
def main():
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    assert d['facial_exception_policy']==old['facial_exception_policy'] and d['calibrations']==old['calibrations']
    counts=dict(configurations=0,split_nodes=0,leaves=0,clean_constraints=0,colour_constraints=0,reserved_clean=0,predictions=0);trees={}
    for f,p in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        for k in ('held_key','training_cases','training_features','training_trace','reserved_clean_vectors','parent_rows','new_rows'):assert f[k]==p[k]
        m=f['pre_veto_model'];pm=p['pre_veto_model']
        for k in ('costs','clean','actions'):assert m[k]==pm[k]
        assert m['nonharm']==[c.split('__',1)[1] in ('colour_cool','colour_warm','stress_color_none') for c in f['training_cases']]
        assert len(m['tree']['nodes'])==len(pm['tree']['nodes'])
        for i,(n,pn) in enumerate(zip(m['tree']['nodes'],pm['tree']['nodes'],strict=True)):
            if pn['kind']=='split':assert n==pn;counts['split_nodes']+=1;continue
            t=m['trace'][i];assert t['rows']==pm['trace'][i]['rows'];ix=t['rows'];cost=m['costs'];feasible=[];totals=[]
            for a in range(14):
                totals.append(sum(cost[j][a] for j in ix))
                if all((not m['clean'][j] or cost[j][a]==0) and (not m['nonharm'][j] or cost[j][a]<=cost[j][0]) for j in ix):feasible.append(a)
            selected=min(feasible,key=lambda a:totals[a]);assert n['values']==m['actions'][selected] and t['action']==selected and abs(t['cost']-totals[selected])<1e-8;counts['leaves']+=1
        pre=PortableTree(m['tree']);hits={}
        for r in f['reserved_clean_vectors']:
            leaf=pre.leaf_id(r['features'])
            if pre.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        assert hits==f['vetoed_leaves'];expected=copy.deepcopy(m)
        for leaf in hits:expected['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        assert expected==f['model'];trees[f['held_key']]=(PortableTree(f['model']['tree']),pre,f);counts['configurations']+=1
    def decide(key,x):
        post,pre,f=trees[key];leaf=post.leaf_id(x);b=d['facial_exception_policy']['fits'][key]['clean_bounds']
        outside=any(float32(x[d['feature_names'].index(k)])<v[0] or float32(x[d['feature_names'].index(k)])>v[1] for k,v in b.items())
        return pre.predict_one(x) if str(leaf) in f['vetoed_leaves'] and outside else post.predict_one(x)
    for key,(_,_,f) in trees.items():
        m=f['model']
        for i,x in enumerate(f['training_features']):
            a=m['actions'].index(decide(key,x))
            if m['clean'][i]:assert m['costs'][i][a]==0;counts['clean_constraints']+=1
            if m['nonharm'][i]:assert m['costs'][i][a]<=m['costs'][i][0];counts['colour_constraints']+=1
        for r in f['reserved_clean_vectors']:assert decide(key,r['features'])==[1.,1.,1.];counts['reserved_clean']+=1
    for p,q in zip(d['predictions'],old['predictions'],strict=True):
        for k in q:
            if k!='parameters':assert p[k]==q[k]
        key=p['subject_id'] if p['cohort']=='development' else 'full';assert p['parameters']==(decide(key,p['features']) if p['features'] is not None else None);counts['predictions']+=1
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    receipt=dict(passed=True,checks=counts,new_fits=0,holdout_image_reads=0,model_sha256=hashlib.sha256((OUT/'models_PRIVATE.json').read_bytes()).hexdigest())
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
if __name__=='__main__':main()
