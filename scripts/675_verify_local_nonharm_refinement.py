"""Independent exhaustive scalar local-choice, structure and final policy check."""
from pathlib import Path
import copy,json,hashlib,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree,float32
OUT=ROOT/'outputs/local_nonharm_refinement_models_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not (OUT/'verification_PRIVATE.json').exists()
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/fixed_structure_nonharm_models_v1/models_PRIVATE.json')
    audit=read(ROOT/'outputs/conflicting_leaf_separability_v1/audit_PRIVATE.json')
    eligible={r['configuration']:r['leaf'] for r in audit['records']}
    assert d['facial_exception_policy']==old['facial_exception_policy'] and d['calibrations']==old['calibrations'] and d['feature_names']==old['feature_names']
    counts=dict(configurations=0,candidates=0,added_splits=0,clean_constraints=0,colour_constraints=0,reserved_clean=0,predictions=0);trees={}
    for f,p in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        for k in p:
            if k not in ('model','pre_veto_model','vetoed_leaves'):assert f[k]==p[k]
        expected=copy.deepcopy(p['pre_veto_model']);n=eligible[f['held_key']];ids=sorted(expected['trace'][n]['rows'])
        x=[[float32(v) for v in row] for row in f['training_features']];cost=expected['costs']
        def opt(rows):
            options=[]
            for a in range(len(expected['actions'])):
                if any((expected['clean'][i] and cost[i][a]!=0) or (expected['nonharm'][i] and cost[i][a]>cost[i][0]) for i in rows):continue
                options.append((math.fsum(cost[i][a] for i in sorted(rows)),a))
            return min(options)
        parent,pa=opt(ids);best=parent;choice=None;total=0
        for k in range(len(d['feature_names'])):
            ordered=sorted((x[i][k],i) for i in ids)
            for j in range(len(ordered)-1):
                low,high=ordered[j][0],ordered[j+1][0]
                if low==high:continue
                threshold=(low+high)/2.;left=sorted(i for v,i in ordered[:j+1]);right=sorted(i for v,i in ordered[j+1:])
                lc,la=opt(left);rc,ra=opt(right);total+=1
                if lc+rc<best-1e-12*max(1.,abs(parent)):
                    best=lc+rc;choice=(k,threshold,left,right,lc,la,rc,ra)
        receipt=dict(node=n,candidates=total,baseline_cost=parent,split_added=choice is not None,final_cost=best)
        if choice:
            k,t,left,right,lc,la,rc,ra=choice;li=len(expected['tree']['nodes']);ri=li+1
            expected['tree']['nodes'][n]=dict(kind='split',feature=k,threshold=t,left=li,right=ri)
            expected['tree']['nodes'] += [dict(kind='leaf',values=expected['actions'][la]),dict(kind='leaf',values=expected['actions'][ra])]
            tr=expected['trace'][n];tr.update(split_feature=k,split_threshold=t,immediate_child_cost=best,local_refinement=True)
            expected['trace'] += [dict(node=li,rows=left,depth=tr['depth']+1,action=la,cost=lc),dict(node=ri,rows=right,depth=tr['depth']+1,action=ra,cost=rc)]
            receipt.update(feature=k,threshold=t,left=li,right=ri,left_action=la,right_action=ra);counts['added_splits']+=1
        expected['tree']['provenance']['bounded_local_nonharm_refinement']=True
        assert f['local_refinement']==receipt and f['pre_veto_model']==expected
        pre=PortableTree(expected['tree'])
        for tr in expected['trace']:
            if expected['tree']['nodes'][tr['node']]['kind']=='leaf':
                assert set(tr['rows'])=={i for i,row in enumerate(x) if pre.leaf_id(row)==tr['node']}
        hits={}
        for r in f['reserved_clean_vectors']:
            leaf=pre.leaf_id(r['features'])
            if pre.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        assert f['vetoed_leaves']==hits
        for leaf in hits:expected['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        assert expected==f['model'];trees[f['held_key']]=(PortableTree(expected['tree']),pre,f)
        counts['configurations']+=1;counts['candidates']+=total
    def decide(key,x):
        post,pre,f=trees[key];bounds=d['facial_exception_policy']['fits'][key]['clean_bounds']
        outside=any(float32(x[d['feature_names'].index(k)])<v[0] or float32(x[d['feature_names'].index(k)])>v[1] for k,v in bounds.items())
        return pre.predict_one(x) if str(post.leaf_id(x)) in f['vetoed_leaves'] and outside else post.predict_one(x)
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
        key=p['subject_id'] if p['cohort']=='development' else 'full'
        assert p['parameters']==(decide(key,p['features']) if p['features'] is not None else None);counts['predictions']+=1
    assert d['added_split_fits']==counts['added_splits'] and counts['configurations']==11 and counts['predictions']==756
    for p,h in d['input_sha256'].items():assert sha(p)==h
    receipt=dict(passed=True,checks=counts,model_sha256=sha(OUT/'models_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
if __name__=='__main__':main()
