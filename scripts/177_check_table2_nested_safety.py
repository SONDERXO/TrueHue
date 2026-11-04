"""Nested source-held training-only selection; fixed candidate versus identity."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,export_tree
from src.data_preparation.source_group_folds import source_group_folds
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors

PARENT=ROOT/'outputs/table2_clean_leaf_policy_v1'
OUT=ROOT/'outputs/table2_nested_safety_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(PARENT/'plan.json');prior=read(PARENT/'summary.json');verify=read(PARENT/'verification.json')
    assert digest(PARENT/'summary.json')==verify['summary_sha256']
    rows={r['pair_id']:r for r in plan['rows']};columns=plan['features']
    paths=[Path(__file__),ROOT/'docs/table2-nested-safety-protocol.md',PARENT/'plan.json',PARENT/'summary.json',PARENT/'verification.json']
    paths+=list(PARENT.glob('fold_*/*'))
    paths += [ROOT/'src/model_training/development_build.py',ROOT/'src/model_training/portable_tree.py']
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_nested_evaluation',rows=list(rows.values()),outer_folds=plan['folds'],features=columns,
        settings=SETTINGS,inner_folds_per_outer=9,planned_fits=90,excluded=plan['excluded'],retained_holds=plan['retained_holds'],
        input_sha256=hashes,selection='Use conservative tree only when inner overall improvement AND zero clean harm; otherwise identity'))
    # Pixels are cached for scoring only, never passed to tree fitting or policy construction.
    images={p:rgb(ROOT/r['input_path']) for p,r in rows.items()}
    references={p:rgb(ROOT/r['reference_path']) for p,r in rows.items()}
    masks={p:cv2.imread(str(ROOT/r['input_mask_path']),0)>0 for p,r in rows.items()}
    scoring={p:cv2.imread(str(ROOT/r['reference_mask_path']),0)>0 for p,r in rows.items()}
    def evaluate(row,parameters):
        p=row['pair_id'];corrected=apply_correction(images[p],masks[p],parameters)
        return image_errors(references[p],corrected,scoring[p]),corrected
    decisions=[];outer_records=[];inner_records=[]
    for outer in plan['folds']:
        fid=outer['fold_id'];folder=OUT/f'outer_{fid}';folder.mkdir()
        pool=[rows[p] for p in outer['train_pair_ids']];held=[rows[p] for p in outer['inner_validation_pair_ids']]
        assert len(pool)==18 and len(held)==2
        inner_folds=source_group_folds(pool);assert len(inner_folds)==9
        write(folder/'inner_plan.json',dict(outer_fold_id=fid,folds=inner_folds))
        records=[]
        for inner in inner_folds:
            training=[rows[p] for p in inner['train_pair_ids']];validation=[rows[p] for p in inner['inner_validation_pair_ids']]
            assert len(training)==16 and len(validation)==2
            assert not ({r['duplicate_group_id'] for r in training}|{r['duplicate_group_id'] for r in validation})&{r['duplicate_group_id'] for r in held}
            model=DecisionTreeRegressor(**SETTINGS).fit([[r[k] for k in columns] for r in training],[[r[k] for k in TARGETS] for r in training])
            prefix=folder/f"inner_{inner['fold_id']}";joblib.dump(model,prefix.with_suffix('.joblib'))
            payload=export_tree(model,columns,TARGETS,dict(experimental=True,outer_fold=fid,inner_fold=inner['fold_id']))
            for r in training:
                if r['variant']=='identity':
                    leaf=int(model.apply([[r[k] for k in columns]])[0]);payload['nodes'][leaf]['values']=[1.,1.,1.]
            write(prefix.with_suffix('.json'),payload);portable=PortableTree(payload)
            for r in validation:
                parameters=portable.predict_one([r[k] for k in columns]);metrics,_=evaluate(r,parameters)
                baseline,_=evaluate(r,[1.,1.,1.])
                record=dict(outer_fold_id=fid,inner_fold_id=inner['fold_id'],pair_id=r['pair_id'],variant=r['variant'],
                    parameters=parameters,policy=metrics,no_correction=baseline)
                records.append(record);inner_records.append(record)
        harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['policy']['ciede2000_source_mask']>0]
        mean=float(np.mean([r['policy']['ciede2000_source_mask'] for r in records]));baseline=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in records]))
        selected=not harmed and mean<baseline
        decision=dict(outer_fold_id=fid,inner_predictions=len(records),inner_harmed_identity_ids=harmed,
            inner_policy_mean=mean,inner_no_correction_mean=baseline,inner_overall_improves=mean<baseline,
            inner_identity_pass=not harmed,selected='conservative_tree' if selected else 'identity')
        # Save decision before either outer held score is computed.
        write(folder/'selection.json',decision);decisions.append(decision)
        tree=PortableTree(read(PARENT/f'fold_{fid}/decision_tree.json'))
        for r in held:
            parameters=tree.predict_one([r[k] for k in columns]) if selected else [1.,1.,1.]
            metrics,corrected=evaluate(r,parameters);baseline,_=evaluate(r,[1.,1.,1.])
            output=OUT/(r['pair_id']+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            outer_records.append(dict(pair_id=r['pair_id'],variant=r['variant'],outer_fold_id=fid,selected=decision['selected'],
                parameters=parameters,nested=metrics,no_correction=baseline,output_sha256=digest(output)))
        print('outer',fid,decision['selected'],'inner clean harms',len(harmed),flush=True)
    aggregate={group:{method:float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','nested']}
        for group,subset in [('all',outer_records),('identity',[r for r in outer_records if r['variant']=='identity']),('distorted',[r for r in outer_records if r['variant']!='identity'])]}
    harmed=[r['pair_id'] for r in outer_records if r['variant']=='identity' and r['nested']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['nested']<aggregate['all']['no_correction'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_exposed_development',decisions=decisions,inner_records=inner_records,outer_records=outer_records,
        aggregate=aggregate,gate=gate,inner_fits=90,runtime_replaced=False,final_validated=False,input_sha256=hashes))
    print(json.dumps(dict(aggregate=aggregate,gate=gate,selected_tree_folds=sum(d['selected']=='conservative_tree' for d in decisions)),indent=2))


if __name__=='__main__':main()
