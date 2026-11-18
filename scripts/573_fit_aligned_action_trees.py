"""Matching cross-fitted MST and one fixed blended-native joint-tree cycle."""
from pathlib import Path
from itertools import combinations
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.contextual_mst_experiment import _ridge,predict,FEATURES
from src.model_training.aligned_correction_support import blended_action_costs
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
P=ROOT/'outputs/aligned_correction_preparation_v1';OUT=ROOT/'outputs/aligned_action_tree_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')

def main():
    if OUT.exists():raise FileExistsError('Models exist; no automatic refits')
    assert read(P/'verification_PRIVATE.json')['passed']
    prepared=read(P/'results_PRIVATE.json');rows=prepared['records'];dev=[r for r in rows if r['cohort']=='development']
    parent_path=ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json';parent=read(parent_path)
    keys=sorted({r['subject_id'] for r in dev});assert keys==sorted(f['held_key'] for f in parent['folds'])
    clean=[dict(case_id=r['source_case'],subject_id=r['subject_id'],features=r['raw_features'],source_mst_exact_decimal=r['source_mst_exact_decimal']) for r in dev if r['recipe']=='clean' and r['status']=='available']
    if len({r['subject_id'] for r in clean})<4:raise ValueError('Too few clean publisher groups for nested calibration; no fitting')
    bound=read(P/'final_input_sha256_PRIVATE.json')
    for p in [P/'results_PRIVATE.json',P/'verification_PRIVATE.json',parent_path,Path(__file__),ROOT/'src/ita_estimation/contextual_mst_experiment.py',ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/aligned_correction_support.py']:
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'calibrations').mkdir();calibrations={};mst_fits=0
    exclusions=[()]+[(k,) for k in keys]+list(combinations(keys,2))
    for i,excluded in enumerate(exclusions):
        training=[r for r in clean if r['subject_id'] not in excluded]
        key='|'.join(excluded);eligible=len({r['subject_id'] for r in training})>=2
        model=_ridge(training,FEATURES) if eligible else None
        if eligible:mst_fits+=1
        record=dict(excluded_keys=list(excluded),training_cases=[r['case_id'] for r in training],training_keys=sorted({r['subject_id'] for r in training}),model=model,status='fitted' if eligible else 'insufficient',measurement_contract_sha256=prepared['measurement_contract_sha256'],calibration_admitted=False)
        calibrations[key]=record;write(OUT/'calibrations'/f'{i:03d}_PRIVATE.json',record)
    print('Saved matching MST calibrations:',mst_fits,'of',len(exclusions),'fixed exclusion sets',flush=True)
    names=parent['full_model']['tree']['feature_names']
    def vector(row,excluded):
        mapping=calibrations['|'.join(sorted(excluded))]
        if row['status']!='available' or mapping['model'] is None:return None,None
        mst=predict(mapping['model'],row['raw_features'])
        values=dict(row['raw_features'],input_mst_score=mst['score'],**row['scene_features'])
        return [values[n] for n in names],mst
    cache={}
    for r in dev:
        if r['status']=='available' and r['reference_support_available']:
            cache[r['case_id']]=(rgb(r['scene_path']),rgb(r['reference_path']),np.load(r['alpha_path'],allow_pickle=False),cv2.imread(r['scoring_path'],0)>0)
    folds=[];trees=0
    def train(key,actions):
        cases=[];features=[];costs=[];flags=[];trace=[]
        for r in dev:
            if r['subject_id']==key or r['case_id'] not in cache:continue
            excluded={r['subject_id']} if key=='full' else {key,r['subject_id']}
            x,mst=vector(r,excluded)
            if x is None:continue
            cases.append(r['case_id']);features.append(x);flags.append(r['recipe']=='clean')
            costs.append(blended_action_costs(*cache[r['case_id']],actions))
            trace.append(dict(case_id=r['case_id'],excluded_keys=sorted(excluded),mst_prediction=mst))
        if not cases or not any(flags):
            return dict(held_key=key,status='insufficient',training_cases=cases,training_features=features,model=None)
        model=fit_action_tree(features,costs,flags,actions,names,max_depth=3)
        model.update(costs=costs,clean=flags)
        return dict(held_key=key,status='fitted',training_cases=cases,training_features=features,training_trace=trace,model=model)
    for f in parent['folds']:
        record=train(f['held_key'],f['model']['actions']);record['held_cases']=[r['case_id'] for r in dev if r['subject_id']==f['held_key']]
        if record['model'] is not None:trees+=1
        folds.append(record);write(OUT/(f['held_key']+'_PRIVATE.json'),record)
        print('Aligned tree:',f['held_key'],record['status'],len(record['training_cases']),'rows',flush=True)
    full=train('full',parent['full_model']['actions']);trees+=int(full['model'] is not None);write(OUT/'full_PRIVATE.json',full)
    predictions=[];folds_by_key={f['held_key']:f for f in folds}
    for r in rows:
        excluded={r['subject_id']} if r['cohort']=='development' else set()
        x,mst=vector(r,excluded);fit=folds_by_key[r['subject_id']] if r['cohort']=='development' else full
        params=PortableTree(fit['model']['tree']).predict_one(x) if x is not None and fit['model'] is not None else None
        predictions.append(dict(case_id=r['case_id'],cohort=r['cohort'],subject_id=r['subject_id'],features=x,mst_prediction=mst,excluded_keys=sorted(excluded),parameters=params,status='available' if params is not None else 'unavailable_noop'))
    result=dict(folds=folds,full=full,calibrations=calibrations,predictions=predictions,feature_names=names,input_sha256=bound,
        new_matching_MST_fits=mst_fits,new_action_tree_fits=trees,new_target_fits=0,measurement_contract_sha256=prepared['measurement_contract_sha256'],production_adopted=False,calibration_admitted=False,training_admitted=False)
    write(OUT/'models_PRIVATE.json',result);assert all(sha(p)==h for p,h in bound.items())
    print('Completed',mst_fits,'matching MST and',trees,'aligned joint trees; no adoption.',flush=True)

if __name__=='__main__':main()
