"""Eleven fixed reserved-group depth-four fits, followed by clean-only leaf veto."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/reserved_clean_veto_models_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve existing fits')
    read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json';m=read(source)
    pp=ROOT/'outputs/reserved_clean_veto_plan_v1/plan_PRIVATE.json';plan=read(pp)
    assert read(pp.parent/'verification_PRIVATE.json')['passed'] and read(source.parent/'verification_PRIVATE.json')['passed']
    reserved=set(plan['reserved_all_available_conditions']);cleans=plan['reserved_usable_clean'];assert len(reserved)==227 and len(cleans)==20
    bound=dict(m['input_sha256'])
    for path in (source,pp,Path(__file__),ROOT/'docs/reserved-clean-veto-protocol-2026-11-08.md'):bound[str(path)]=sha(path)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();result=copy.deepcopy(m)
    for f in result['folds']+[result['full']]:
        parent=copy.deepcopy(f);indices=[i for i,c in enumerate(parent['training_cases']) if c not in reserved]
        reserved_vectors=[dict(case_id=c,features=parent['training_features'][parent['training_cases'].index(c)]) for c in cleans]
        for field in ('training_cases','training_features','training_trace'):f[field]=[parent[field][i] for i in indices]
        costs=[parent['model']['costs'][i] for i in indices];flags=[parent['model']['clean'][i] for i in indices]
        model=fit_action_tree(f['training_features'],costs,flags,parent['model']['actions'],m['feature_names'],max_depth=4);model.update(costs=costs,clean=flags)
        f.update(model=model,parent_rows=parent['parent_rows'],new_rows=parent['new_rows']-len(reserved))
        f['pre_veto_model']=copy.deepcopy(model);tree=PortableTree(model['tree']);hits={}
        for r in reserved_vectors:
            leaf=tree.leaf_id(r['features'])
            if tree.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        for leaf in hits:model['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        f.update(reserved_clean_vectors=reserved_vectors,vetoed_leaves=hits)
        # Costs/trace describe the pre-veto greedy fit; final tree has explicit replacements.
        (OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2))
        print('Fitted',f['held_key'],'rows',len(indices),'vetoed leaves',len(hits),flush=True)
    fits={f['held_key']:f for f in result['folds']}
    before=copy.deepcopy(result)
    for f in before['folds']+[before['full']]:f['model']=copy.deepcopy(f['pre_veto_model'])
    for data in (result,before):
        ff={f['held_key']:f for f in data['folds']}
        for q in data['predictions']:
            f=ff[q['subject_id']] if q['cohort']=='development' else data['full']
            q['parameters']=PortableTree(f['model']['tree']).predict_one(q['features']) if q['features'] is not None else None
        data.update(input_sha256=bound,maximum_depth=4,new_action_tree_fits=11,new_matching_MST_fits=0,new_target_fits=0,
            reserved_groups=plan['reserved_development_groups'],reserved_all_conditions=sorted(reserved),reserved_usable_clean=cleans,
            trace_note='Greedy trace/costs are pre-veto; final tree replacements listed in vetoed_leaves')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    (OUT/'pre_veto_models_PRIVATE.json').write_text(json.dumps(before,indent=2,allow_nan=False))
if __name__=='__main__':main()
