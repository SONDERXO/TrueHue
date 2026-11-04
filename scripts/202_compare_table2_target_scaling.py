"""Fixed five-feature target-scale comparison on fifteen source-held folds."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors

OUT=ROOT/'outputs/table2_target_scaling_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';plan=read(parent/'fit_plan.json');data=read(parent/'summary.json')
    verify=read(parent/'verification.json');assert digest(parent/'fit_plan.json')==verify['fit_plan_sha256'] and digest(parent/'summary.json')==verify['summary_sha256']
    prior={r['pair_id']:r for r in data['records']};rows={r['pair_id']:r for r in plan['rows']};names=plan['baseline_features']
    paths=[Path(__file__),ROOT/'docs/table2-target-scaling-protocol.md',ROOT/'src/model_training/target_scaled_tree.py',parent/'fit_plan.json',parent/'summary.json',parent/'verification.json']
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir();write(OUT/'plan.json',dict(status='frozen_before_fit',rows=plan['rows'],folds=plan['folds'],features=names,
        excluded=plan['excluded'],retained_holds=plan['retained_holds'],input_sha256=hashes,planned_fits=15,
        target_scaling='Fitting-only mean/populationstd;constant-axis scale1;raw target means exported',identity_tolerance=0.))
    records=[];statistics=[]
    for fold in plan['folds']:
        fid=fold['fold_id'];training=[rows[p] for p in fold['train_pair_ids']];held=[rows[p] for p in fold['inner_validation_pair_ids']]
        assert len(training)==28 and len(held)==2
        assert {r['duplicate_group_id'] for r in training}.isdisjoint(r['duplicate_group_id'] for r in held)
        payload,model,metadata=fit_target_scaled_tree([[r[k] for k in names] for r in training],[[r[k] for k in TARGETS] for r in training],names,dict(fold_id=fid))
        folder=OUT/f'fold_{fid}';folder.mkdir();write(folder/'raw_units_tree.json',payload);joblib.dump(model,folder/'standardized_target_model.joblib');write(folder/'target_statistics.json',metadata)
        tree=PortableTree(payload);clean=deepcopy(payload)
        for r in training:
            if r['variant']=='identity':clean['nodes'][tree.leaf_id([r[k] for k in names])]['values']=[1.,1.,1.]
        clean['provenance']['leaf_policy']='identity_if_any_fitting_control';write(folder/'clean_leaf_tree.json',clean)
        methods={'scaled_targets':tree,'scaled_clean_leaf':PortableTree(clean)};statistics.append(dict(fold_id=fid,**metadata))
        for row in held:
            pair=row['pair_id'];image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            record=dict(pair_id=pair,variant=row['variant'],fold_id=fid,no_correction=prior[pair]['no_correction'],
                methods={'baseline5':prior[pair]['methods']['baseline5']})
            for method,portable in methods.items():
                parameters=portable.predict_one([row[k] for k in names]);corrected=apply_correction(image,mask,parameters)
                path=OUT/(pair+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
                record['methods'][method]=dict(parameters=parameters,metrics=image_errors(reference,corrected,score),output_sha256=digest(path))
            records.append(record)
    aggregates={};gates={}
    for method in ['baseline5','scaled_targets','scaled_clean_leaf']:
        aggregates[method]={scope:dict(pairs=len(subset),no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in subset])),
            corrected=float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset])),
            target_mae={target:float(np.mean([abs(r['methods'][method]['parameters'][i]-rows[r['pair_id']][target]) for r in subset])) for i,target in enumerate(TARGETS)})
            for scope,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
        harms=[r['pair_id'] for r in records if r['variant']=='identity' and r['methods'][method]['metrics']['ciede2000_source_mask']>0]
        gate=dict(overall_improves=aggregates[method]['all']['corrected']<aggregates[method]['all']['no_correction'],identity_pass=not harms,harmed_identity_ids=harms)
        gate['passed']=gate['overall_improves'] and gate['identity_pass'];gates[method]=gate
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_experimental_target_scaling',records=records,target_statistics=statistics,aggregate=aggregates,gates=gates,
        input_sha256=hashes,new_fits=15,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(scores={m:{s:v['corrected'] for s,v in a.items()} for m,a in aggregates.items()},gates=gates),indent=2))


if __name__=='__main__':main()
