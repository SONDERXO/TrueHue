"""Frozen five-vs-nine feature comparison on reviewed ten-source folds."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.chroma_distribution import ADDITIONS,chroma_distribution_features
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,export_tree
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract
from src.evaluation.correction_prototype import apply_correction,image_errors
from src.data_preparation.controlled_training_table import TARGETS

OUT=ROOT/'outputs/table2_chroma_distribution_comparison_v1'
PARENT=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(PARENT/'fit_plan.json');baseline=read(PARENT/'summary.json');verify=read(PARENT/'verification.json')
    assert digest(PARENT/'fit_plan.json')==verify['fit_plan_sha256']
    assert digest(PARENT/'summary.json')==verify['summary_sha256']
    assert contract(ROOT)[1]==plan['rows'][0]['measurement_contract_sha256']
    assert plan['settings']==SETTINGS
    columns=tuple(MST_FEATURES)+ADDITIONS
    paths=[Path(__file__),ROOT/'docs/table2-chroma-distribution-protocol.md',ROOT/'src/model_training/chroma_distribution.py',
        ROOT/'src/ita_estimation/compute_ita.py',PARENT/'fit_plan.json',PARENT/'summary.json',PARENT/'verification.json']
    paths+=list(PARENT.glob('fold_*/*'))
    for r in plan['rows']:paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_features_and_fit',features=columns,settings=SETTINGS,
        baseline='Verified saved five-feature folds; no new baseline fitting',rows=plan['rows'],folds=plan['folds'],
        excluded=plan['excluded'],retained_holds=plan['retained_holds'],input_sha256=hashes,
        identity_tolerance=0.,planned_candidate_fits=10,eligible_pairs=20,runtime_promotion=False))
    rows={r['pair_id']:dict(r) for r in plan['rows']};feature_records=[]
    for row in rows.values():
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        features=chroma_distribution_features(image,mask)
        feature_records.append(dict(pair_id=row['pair_id'],**features))
        if not features['valid']:
            write(OUT/'unavailable.json',dict(status='stopped_before_fit',records=feature_records));raise ValueError('Unavailable candidate features; no cohort fallback')
        row.update(features['features'])
    write(OUT/'features.json',feature_records)
    records=[];base={r['pair_id']:r for r in baseline['records']}
    for fold in plan['folds']:
        training=[rows[p] for p in fold['train_pair_ids']];held=[rows[p] for p in fold['inner_validation_pair_ids']]
        assert len(training)==18 and len(held)==2
        assert {r['duplicate_group_id'] for r in training}.isdisjoint(r['duplicate_group_id'] for r in held)
        model=DecisionTreeRegressor(**SETTINGS).fit([[r[k] for k in columns] for r in training],[[r[k] for k in TARGETS] for r in training])
        folder=OUT/f"fold_{fold['fold_id']}";folder.mkdir();joblib.dump(model,folder/'decision_tree.joblib')
        payload=export_tree(model,columns,TARGETS,dict(experimental=True,fold_id=fold['fold_id']));write(folder/'decision_tree.json',payload)
        portable=PortableTree(payload)
        for row in held:
            pair=row['pair_id'];parameters=model.predict([[row[k] for k in columns]])[0]
            np.testing.assert_allclose(parameters,portable.predict_one([row[k] for k in columns]),rtol=0,atol=1e-12)
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
            scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters)
            output=OUT/(pair+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=pair,variant=row['variant'],fold_id=fold['fold_id'],parameters=parameters.tolist(),
                no_correction=base[pair]['no_correction'],baseline=base[pair]['learned'],oracle=base[pair]['oracle'],
                candidate=image_errors(reference,corrected,scoring),output_sha256=digest(output)))
    aggregate={}
    for group,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]:
        aggregate[group]={method:float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','baseline','candidate','oracle']}
    harmed=[r['pair_id'] for r in records if r['variant']=='identity' and r['candidate']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['candidate']<aggregate['all']['no_correction'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_development_only',records=records,aggregate=aggregate,gate=gate,input_sha256=hashes,
        candidate_fits=10,feature_count=9,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(aggregate=aggregate,gate=gate),indent=2))


if __name__=='__main__':main()
