"""Exactly11fixed source-expansion fits; frozen MST/features/actions/settings."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.contextual_mst_experiment import predict
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.aligned_correction_support import blended_action_costs
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/expanded_correction_models_v1';P=ROOT/'outputs/expanded_correction_inputs_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed fits; no rerun')
    assert read(P/'verification_PRIVATE.json')['passed'] and read(P/'assessment_PRIVATE.json')['technical_preparation_verified']
    planpath=ROOT/'outputs/expanded_correction_training_plan_v1/plan_PRIVATE.json';plan=read(planpath)
    oldpath=ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json';old=read(oldpath)
    data=read(P/'results_PRIVATE.json');rows=[r for r in data['records'] if r['status']=='available' and r['reference_support_available']]
    assert len(rows)==890 and sum(r['recipe']=='clean' for r in rows)==80
    oldgroups={p['subject_id'] for p in old['predictions']};newgroups={r['subject_id'] for r in rows}
    assert len(newgroups)==32 and not newgroups&oldgroups and not newgroups&set(plan['closed_holdout_keys'])
    bound=dict(old['input_sha256'])
    for p,h in read(P/'final_input_sha256_PRIVATE.json').items():
        if p in bound:assert bound[p]==h
        bound[p]=h
    for p in (oldpath,P/'results_PRIVATE.json',P/'verification_PRIVATE.json',P/'assessment_PRIVATE.json',planpath,
              Path(__file__),ROOT/'docs/expanded-correction-training-protocol-2026-11-08.md'):
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir()
    # Cache all selected pixels, preserving the complete per-row scoring region.
    cache={}
    for i,r in enumerate(rows,1):
        mask=cv2.imread(r['scoring_path'],0)>0;im=rgb(r['scene_path']);ref=rgb(r['reference_path']);alpha=np.load(r['alpha_path'],allow_pickle=False)
        cache[r['case_id']]=(im[mask][:,None,:],ref[mask][:,None,:],alpha[mask][:,None],np.ones((int(mask.sum()),1),bool))
        if i%200==0:print('Cached',i,'/890complete scoring regions',flush=True)
    names=old['feature_names'];fits=[]
    for parent in old['folds']+[old['full']]:
        key=parent['held_key'];excluded=[] if key=='full' else [key]
        calibration=old['calibrations']['|'.join(excluded)];assert not set(calibration['training_keys'])&newgroups
        fit={k:copy.deepcopy(v) for k,v in parent.items() if k not in ('model','training_features','training_trace','training_cases')}
        cases=list(parent['training_cases']);features=copy.deepcopy(parent['training_features']);traces=copy.deepcopy(parent['training_trace'])
        costs=copy.deepcopy(parent['model']['costs']);flags=list(parent['model']['clean']);actions=parent['model']['actions']
        for r in rows:
            mst=predict(calibration['model'],r['raw_features']);values=dict(r['raw_features'],input_mst_score=mst['score'],**r['scene_features'])
            cases.append(r['case_id']);features.append([values[n] for n in names]);flags.append(r['recipe']=='clean')
            costs.append(blended_action_costs(*cache[r['case_id']],actions))
            traces.append(dict(case_id=r['case_id'],excluded_keys=excluded,own_key_absent_from_calibration=True,mst_prediction=mst))
        model=fit_action_tree(features,costs,flags,actions,names,max_depth=3);model.update(costs=costs,clean=flags)
        fit.update(training_cases=cases,training_features=features,training_trace=traces,model=model,
            parent_rows=len(parent['training_cases']),new_rows=890)
        fits.append(fit);(OUT/(key+'_PRIVATE.json')).write_text(json.dumps(fit,indent=2),encoding='utf-8')
        print('Fitted',key,len(cases),'rows;',sum(flags),'clean constraints',flush=True)
    bykey={f['held_key']:f for f in fits};predictions=[]
    for p in old['predictions']:
        q=copy.deepcopy(p);fit=bykey[p['subject_id']] if p['cohort']=='development' else fits[-1]
        q['parameters']=PortableTree(fit['model']['tree']).predict_one(q['features']) if q['features'] is not None else None
        predictions.append(q)
    assert len(fits)==11 and len(fits[-1]['training_cases'])==1117
    result=dict(folds=fits[:-1],full=fits[-1],calibrations=old['calibrations'],predictions=predictions,feature_names=names,
        input_sha256=bound,new_action_tree_fits=11,new_matching_MST_fits=0,new_target_fits=0,
        new_fitting_cases=[r['case_id'] for r in rows],new_publisher_groups=sorted(newgroups),
        measurement_contract_sha256=old['measurement_contract_sha256'],production_adopted=False,training_admitted=False,calibration_admitted=False,
        parent_model_sha256=sha(oldpath))
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('Completed11trees,0MSTfits; holdout closed.')

if __name__=='__main__':main()
