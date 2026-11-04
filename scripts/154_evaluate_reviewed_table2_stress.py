"""Import exact user review and execute the fixed source-held stress recipe."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.data_preparation.table2_stress_contract import POLICY,validate_stress_rows
from src.data_preparation.source_group_folds import source_group_folds
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors
from src.model_training.portable_tree import export_tree,PortableTree
from src.model_training.development_build import SETTINGS

USER_STATEMENT='22211: accept, 22454: accept, 51739: reject reason: accepted facial hair from another subject in photo, 62331: accept concern: a small hole below nose, 6236: accept concern: little background inclded in face mask, 75027: accept concern: a hole below nose'
DECISIONS={
 '22211':('accept',''), '22454':('accept',''),
 '51739':('reject','accepted facial hair from another subject in photo'),
 '62331':('accept','a small hole below nose'),
 '6236':('accept','little background inclded in face mask'),
 '75027':('accept','a hole below nose')}


def main():
    out=ROOT/'outputs/table2_stress_evaluation_v2'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,value):p.write_text(json.dumps(value,indent=2),encoding='utf-8')
    folder=ROOT/'outputs/table2_stress_review_v1'
    readiness=folder/'readiness.json';page=folder/'review.html'
    check=json.loads((folder/'verification.json').read_text())
    assert digest(readiness)==check['readiness_sha256'] and digest(page)==check['review_sha256']
    data=json.loads(readiness.read_text())
    evidence=ROOT/'outputs/table2_known_source_feasibility_v1'
    summary_path=evidence/'summary.json';summary=json.loads(summary_path.read_text())
    assert digest(summary_path)==data['feasibility_summary_sha256']
    for p,h in summary['input_sha256'].items():assert digest(ROOT/p)==h
    for p,h in summary['evidence_sha256'].items():assert digest(evidence/p)==h
    _,identity=contract(ROOT);assert identity==data['measurement_contract_sha256']
    tracked={str(p.relative_to(ROOT)):digest(p) for p in [readiness,page,summary_path,Path(__file__),
        ROOT/'src/data_preparation/table2_stress_contract.py',ROOT/'docs/table2-clipping-stress-design.md']}
    out.mkdir(parents=True)
    review=out/'user_review.json'
    write(review,dict(user_statement_verbatim=USER_STATEMENT,review_html_sha256=digest(page),
        readiness_sha256=digest(readiness),decisions={k:dict(decision=v[0],concern=v[1]) for k,v in DECISIONS.items()},
        scope='User accepts exact displayed masks/scenes with stated concerns; no scientific MST or calibrated-color approval. Original reviews remain unchanged.'))
    rows=[];excluded=[]
    for candidate in data['candidate_rows']:
        name=candidate['pair_id'].split('__')[0];decision,concern=DECISIONS[name]
        if decision!='accept':excluded.append(dict(pair_id=candidate['pair_id'],reason=concern));continue
        variant=candidate['variant'];is_identity=variant=='identity'
        suffix='reference' if is_identity else candidate['assigned_severity']+'_input'
        image=evidence/f'{name}_{suffix}.png'
        mask=evidence/f'{name}_reference_mask.png' if is_identity else evidence/f"{name}_{candidate['assigned_severity']}_mask.png"
        reference_mask=evidence/f'{name}_reference_mask.png'
        n=int(np.count_nonzero(cv2.imread(str(reference_mask),0)))
        clipping=candidate['clipping'];count=clipping['clipped_pixels']
        r={k:candidate[k] for k in ['pair_id','source_image_id','duplicate_group_id','partition','variant','input_processing_status']}
        r.update(candidate['experimental_input_features'])
        r.update(dataset_name='FairFace',training_eligible=True,table_use='train',admission_policy=POLICY,
            measurement_shape=[256,256,3],mask_version='v2_complete_mouth_v1',measurement_contract_sha256=identity,
            lookup_sha256=data['lookup_sha256'],mst_feature_source='distorted_input_ita_lookup',
            reference_mst_estimate=candidate['reference_mst_estimate'],severity_probe=candidate['assigned_severity'],
            group_assignment_source='experimental_reference_ita_lookup',reference_lookup_sha256=data['lookup_sha256'],
            mask_review_status='approved',scene_review_status='approved',mask_review_report_sha256=digest(review),review_concern=concern,
            clipped_pixel_count=count,clipped_channel_samples=clipping['clipped_channel_samples'],
            generation_skin_pixels=n,clipped_pixel_fraction=count/n,
            input_path=str(image.relative_to(ROOT)),input_sha256=digest(image),input_mask_path=str(mask.relative_to(ROOT)),
            input_mask_sha256=digest(mask),reference_mask_path=str(reference_mask.relative_to(ROOT)),reference_mask_sha256=digest(reference_mask),
            reference_path=str((evidence/f'{name}_reference.png').relative_to(ROOT)))
        if is_identity:
            parameters=[1.,1.,1.]
            r.update(transform_version='encoded_rgb_gamma_then_gain_v1',target_method='exact_gamma_gain_inverse',
                distortion_gamma=1.,distortion_red_gain=1.,distortion_blue_gain=1.)
        else:
            fit=candidate['target_fit'];fit_path=out/f'{name}_target_fit.json';write(fit_path,fit)
            assert json.loads(fit_path.read_text())==fit
            parameters=fit['parameters']
            r.update(transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',
                target_fit=fit,target_fit_report_sha256=digest(fit_path),target_fit_report_path=str(fit_path.relative_to(ROOT)))
        r.update(zip(TARGETS,parameters));rows.append(r)
    rows=validate_stress_rows(rows,measurement_contract_sha256=identity,lookup_sha256=data['lookup_sha256'],eligible_pair_ids=[r['pair_id'] for r in rows])
    folds=source_group_folds(rows)
    assert len(rows)==10 and len(folds)==5 and not any('51739' in r['pair_id'] for r in rows)
    write(out/'fit_plan.json',dict(status='frozen_before_fit',rows=rows,excluded=excluded,folds=folds,
        settings=SETTINGS,sample_weight=None,features=MST_FEATURES,targets=TARGETS,input_sha256=tracked,
        identity_tolerance=0.,primary_gate='Lower equal-source CIEDE2000 and zero identity error increase',
        method_limit='Limited experimental reference-MST severity assignment; no dark sources. Not final independent evaluation.'))
    def matrix(selected,columns):return np.asarray([[r[k] for k in columns] for r in selected],float)
    records=[];portable_checks=0
    for fold in folds:
        training=[r for r in rows if r['pair_id'] in fold['train_pair_ids']]
        held=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert {r['source_image_id'] for r in training}.isdisjoint(r['source_image_id'] for r in held)
        model=DecisionTreeRegressor(**SETTINGS).fit(matrix(training,MST_FEATURES),matrix(training,TARGETS))
        fold_dir=out/f"fold_{fold['fold_id']}";fold_dir.mkdir()
        joblib.dump(model,fold_dir/'decision_tree.joblib')
        exported=export_tree(model,MST_FEATURES,TARGETS,dict(fold_id=fold['fold_id'],experimental=True));write(fold_dir/'decision_tree.json',exported)
        portable=PortableTree(exported)
        for r in held:
            features=[r[k] for k in MST_FEATURES];parameters=model.predict([features])[0]
            assert np.allclose(portable.predict_one(features),parameters,rtol=0,atol=1e-12);portable_checks+=1
            image=cv2.cvtColor(cv2.imread(str(ROOT/r['input_path'])),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB)
            mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters)
            assert np.array_equal(corrected[~mask],image[~mask])
            output=out/(r['pair_id']+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            assert np.array_equal(cv2.cvtColor(cv2.imread(str(output)),cv2.COLOR_BGR2RGB),corrected)
            records.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],fold_id=fold['fold_id'],variant=r['variant'],
                parameters=parameters.tolist(),no_correction=image_errors(reference,image,scoring),
                learned=image_errors(reference,corrected,scoring),
                oracle=image_errors(reference,apply_correction(image,mask,[r[k] for k in TARGETS]),scoring),
                output_sha256=digest(output)))
    def mean(method,subset):return float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    identities=[r for r in records if r['variant']=='identity'];distorted=[r for r in records if r['variant']!='identity']
    aggregate={key:dict(no_correction_ciede2000=mean('no_correction',subset),learned_ciede2000=mean('learned',subset),oracle_ciede2000=mean('oracle',subset)) for key,subset in [('all',records),('identity',identities),('distorted',distorted)]}
    harmed=[r['pair_id'] for r in identities if r['learned']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['learned_ciede2000']<aggregate['all']['no_correction_ciede2000'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    for p,h in tracked.items():assert digest(ROOT/p)==h
    for r in rows:
        for p,h in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[p])==r[h]
        if 'target_fit_report_path' in r:assert digest(ROOT/r['target_fit_report_path'])==r['target_fit_report_sha256']
    write(out/'summary.json',dict(status='complete',review_sha256=digest(review),admitted_pairs=10,sources=5,excluded=excluded,
        records=records,aggregate=aggregate,gate=gate,settings=SETTINGS,portable_prediction_checks=portable_checks,
        final_validated=False,runtime_replaced=False,all_source_input_hashes_unchanged=True))
    print(json.dumps(dict(aggregate=aggregate,gate=gate),indent=2))


if __name__=='__main__':main()
