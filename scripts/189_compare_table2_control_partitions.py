"""Fixed single-tree control-aware partition comparison, never runtime promotion."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.control_partition_tree import fit_control_partition_tree
from src.model_training.portable_tree import PortableTree
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors

OUT=ROOT/'outputs/table2_control_partition_v1'
PARENT=ROOT/'outputs/table2_clean_leaf_policy_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(PARENT/'plan.json');old=read(PARENT/'summary.json');verification=read(PARENT/'verification.json')
    assert digest(PARENT/'summary.json')==verification['summary_sha256']
    rows={r['pair_id']:r for r in plan['rows']};columns=plan['features'];prior={r['pair_id']:r for r in old['records']}
    paths=[Path(__file__),ROOT/'docs/table2-control-partition-protocol.md',ROOT/'src/model_training/control_partition_tree.py',
        PARENT/'plan.json',PARENT/'summary.json',PARENT/'verification.json']
    paths+=list(PARENT.glob('fold_*/*'))
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_fit',rows=list(rows.values()),features=columns,folds=plan['folds'],
        excluded=plan['excluded'],retained_holds=plan['retained_holds'],input_sha256=hashes,planned_fits=10,
        objective='Gini control/distortion partition;any fitting identity member yields identity leaf,otherwise fitting target mean',
        identity_tolerance=0.,no_runtime_promotion=True))
    records=[]
    for fold in plan['folds']:
        training=[rows[p] for p in fold['train_pair_ids']];held=[rows[p] for p in fold['inner_validation_pair_ids']]
        assert len(training)==18 and len(held)==2
        assert {r['duplicate_group_id'] for r in training}.isdisjoint(r['duplicate_group_id'] for r in held)
        payload,classifier,audit=fit_control_partition_tree([[r[k] for k in columns] for r in training],
            [[r[k] for k in TARGETS] for r in training],np.array([r['variant']=='identity' for r in training]),columns,
            dict(fold_id=fold['fold_id'],fitting_pair_ids=fold['train_pair_ids']))
        folder=OUT/f"fold_{fold['fold_id']}";folder.mkdir();write(folder/'decision_tree.json',payload)
        joblib.dump(classifier,folder/'partition_classifier.joblib')
        write(folder/'leaf_audit.json',audit);tree=PortableTree(payload)
        for row in held:
            pair=row['pair_id'];parameters=tree.predict_one([row[k] for k in columns]);image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            output=apply_correction(image,mask,parameters);path=OUT/(pair+'_corrected.png')
            assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=pair,variant=row['variant'],fold_id=fold['fold_id'],parameters=parameters,
                leaf=tree.leaf_id([row[k] for k in columns]),no_correction=prior[pair]['no_correction'],
                regression9=prior[pair]['original'],previous_clean_leaf=prior[pair]['policy'],
                candidate=image_errors(reference,output,scoring),output_sha256=digest(path)))
    aggregate={group:{method:float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','regression9','previous_clean_leaf','candidate']}
        for group,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]}
    harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['candidate']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['candidate']<aggregate['all']['no_correction'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_experimental_training_objective',records=records,aggregate=aggregate,gate=gate,
        input_sha256=hashes,fits=10,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(aggregate=aggregate,gate=gate),indent=2))


if __name__=='__main__':main()
