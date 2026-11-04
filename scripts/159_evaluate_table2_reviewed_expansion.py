"""Import the six-source review and evaluate the fixed eight-source cohort."""
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
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import export_tree,PortableTree
from src.evaluation.correction_prototype import apply_correction,image_errors

STATEMENT='40048: reject reason: captured hair on face mask edges, 42532: reject reason: captured hair on face mask, 63870: reject reason: captured hair a little bit, 67583: accept, 83205: accept, 84364: accept'
DECISIONS={'40048':('reject','captured hair on face mask edges'),'42532':('reject','captured hair on face mask'),
    '63870':('reject','captured hair a little bit'),'67583':('accept',''),'83205':('accept',''),'84364':('accept','')}


def main():
    out=ROOT/'outputs/table2_reviewed_expansion_evaluation_v1'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    old=ROOT/'outputs/table2_stress_evaluation_v2'
    prior_path=old/'fit_plan.json';prior=json.loads(prior_path.read_text())
    prior_verification=json.loads((old/'verification.json').read_text())
    assert digest(prior_path)==prior_verification['fit_plan_sha256']
    folder=ROOT/'outputs/table2_stress_expansion_v1'
    summary_path=folder/'summary.json';data=json.loads(summary_path.read_text())
    verify=json.loads((folder/'verification.json').read_text())
    assert digest(summary_path)==verify['summary_sha256'] and digest(folder/'review.html')==verify['review_sha256']
    assert digest(summary_path)==json.loads((folder/'independent_verification.json').read_text())['summary_sha256']
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    for p,h in data['evidence_sha256'].items():assert digest(folder/p)==h
    _,identity=contract(ROOT);assert identity==data['measurement_contract_sha256']
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(json.loads(artifact.read_text()),identity)
    out.mkdir(parents=True);review=out/'user_review.json'
    write(review,dict(user_statement_verbatim=STATEMENT,review_html_sha256=digest(folder/'review.html'),
        summary_sha256=digest(summary_path),decisions={k:dict(decision=v[0],reason=v[1]) for k,v in DECISIONS.items()},
        scope='Exact displayed masks/scenes only. Preserve previous reviews, rejected sources and accepted concerns. No MST accuracy approval.'))
    rows=prior['rows'].copy();excluded=prior['excluded'].copy()
    for source in data['sources']:
        name=source['source_id'];decision,reason=DECISIONS[name]
        if decision=='reject':
            excluded.extend(dict(pair_id=name+'__'+variant,reason=reason) for variant in ['identity','table2_'+source['assigned_severity']]);continue
        assert source['status']=='pending_review'
        for is_identity in [True,False]:
            variant='identity' if is_identity else 'table2_'+source['assigned_severity']
            image=folder/f'{name}_reference.png' if is_identity else folder/f'{name}_input.png'
            mask=folder/f'{name}_reference_mask.png' if is_identity else folder/f'{name}_input_mask.png'
            rm=folder/f'{name}_reference_mask.png'
            measurement=source['reference_measurement'] if is_identity else source['input_measurement']
            features=measurement['features'];mst=lookup.label(features['input_ita_degrees'])-1
            n=source['reference_measurement']['skin_pixels'];clipping=source['clipping']
            count=0 if is_identity else clipping['clipped_pixels']
            r=dict(pair_id=name+'__'+variant,source_image_id=source['image_id'],duplicate_group_id=source['duplicate_group_id'],
                partition='train',table_use='train',variant=variant,input_processing_status=measurement['status'],
                dataset_name='FairFace',training_eligible=True,admission_policy=POLICY,
                measurement_shape=[256,256,3],mask_version='v2_complete_mouth_v1',measurement_contract_sha256=identity,
                lookup_sha256=data['lookup_sha256'],mst_feature_source='distorted_input_ita_lookup',input_mst_index=mst,
                reference_mst_estimate=source['reference_mst_estimate'],severity_probe=source['assigned_severity'],
                group_assignment_source='experimental_reference_ita_lookup',reference_lookup_sha256=data['lookup_sha256'],
                mask_review_status='approved',scene_review_status='approved',mask_review_report_sha256=digest(review),review_concern='',
                clipped_pixel_count=count,clipped_channel_samples=0 if is_identity else clipping['clipped_channel_samples'],
                generation_skin_pixels=n,clipped_pixel_fraction=count/n,input_path=str(image.relative_to(ROOT)),input_sha256=digest(image),
                input_mask_path=str(mask.relative_to(ROOT)),input_mask_sha256=digest(mask),reference_mask_path=str(rm.relative_to(ROOT)),
                reference_mask_sha256=digest(rm),reference_path=str((folder/f'{name}_reference.png').relative_to(ROOT)))
            r.update(features)
            if is_identity:
                parameters=[1.,1.,1.]
                r.update(transform_version='encoded_rgb_gamma_then_gain_v1',target_method='exact_gamma_gain_inverse',
                    distortion_gamma=1.,distortion_red_gain=1.,distortion_blue_gain=1.)
            else:
                fit=source['target_fit'];fit_path=folder/f'{name}_target_fit.json';assert json.loads(fit_path.read_text())==fit
                parameters=fit['parameters']
                r.update(transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',
                    target_fit=fit,target_fit_report_sha256=digest(fit_path),target_fit_report_path=str(fit_path.relative_to(ROOT)))
            r.update(zip(TARGETS,parameters));rows.append(r)
    rows=validate_stress_rows(rows,measurement_contract_sha256=identity,lookup_sha256=data['lookup_sha256'],eligible_pair_ids=[r['pair_id'] for r in rows])
    folds=source_group_folds(rows)
    assert len(rows)==16 and len(folds)==8
    rejected={'51739','40048','42532','63870'};assert not any(r['pair_id'].split('__')[0] in rejected for r in rows)
    def verify_rows():
        for r in rows:
            for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[path])==r[key]
            review_path=old/'user_review.json' if r['pair_id'] in {p['pair_id'] for p in prior['rows']} else review
            assert digest(review_path)==r['mask_review_report_sha256']
            if 'target_fit_report_path' in r:
                assert digest(ROOT/r['target_fit_report_path'])==r['target_fit_report_sha256']
                assert json.loads((ROOT/r['target_fit_report_path']).read_text())==r['target_fit']
    verify_rows()
    tracked={p.relative_to(ROOT).as_posix():digest(p) for p in [prior_path,old/'user_review.json',summary_path,review,Path(__file__),
        ROOT/'src/data_preparation/table2_stress_contract.py',ROOT/'docs/table2-clipping-stress-design.md']}
    write(out/'fit_plan.json',dict(status='frozen_before_fit',rows=rows,excluded=excluded,folds=folds,settings=SETTINGS,
        features=MST_FEATURES,targets=TARGETS,sample_weight=None,identity_tolerance=0.,input_sha256=tracked,
        caveat='Exposed-data development comparison; eight source groups do not establish person separation or full MST coverage.'))
    def matrix(selected,columns):return np.asarray([[r[k] for k in columns] for r in selected],float)
    def rgb(path):return cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
    records=[]
    for fold in folds:
        training=[r for r in rows if r['pair_id'] in fold['train_pair_ids']];held=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert {r['source_image_id'] for r in training}.isdisjoint(r['source_image_id'] for r in held)
        model=DecisionTreeRegressor(**SETTINGS).fit(matrix(training,MST_FEATURES),matrix(training,TARGETS))
        fdir=out/f"fold_{fold['fold_id']}";fdir.mkdir();joblib.dump(model,fdir/'decision_tree.joblib')
        payload=export_tree(model,MST_FEATURES,TARGETS,dict(fold_id=fold['fold_id'],experimental=True));write(fdir/'decision_tree.json',payload)
        portable=PortableTree(payload)
        for row in held:
            x=[row[k] for k in MST_FEATURES];parameters=model.predict([x])[0]
            assert np.allclose(portable.predict_one(x),parameters,atol=1e-12,rtol=0)
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            corrected=apply_correction(image,mask,parameters);assert np.array_equal(corrected[~mask],image[~mask])
            output=out/(row['pair_id']+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            assert np.array_equal(rgb(output),corrected)
            records.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant'],fold_id=fold['fold_id'],
                parameters=parameters.tolist(),no_correction=image_errors(reference,image,scoring),learned=image_errors(reference,corrected,scoring),
                oracle=image_errors(reference,apply_correction(image,mask,[row[k] for k in TARGETS]),scoring),output_sha256=digest(output)))
    identities=[r for r in records if r['variant']=='identity'];distorted=[r for r in records if r['variant']!='identity']
    aggregate={key:{method+'_ciede2000':float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','learned','oracle']}
        for key,subset in [('all',records),('identity',identities),('distorted',distorted)]}
    harmed=[r['pair_id'] for r in identities if r['learned']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['learned_ciede2000']<aggregate['all']['no_correction_ciede2000'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    verify_rows()
    for p,h in tracked.items():assert digest(ROOT/p)==h
    write(out/'summary.json',dict(status='complete',admitted_pairs=16,sources=8,excluded=excluded,records=records,aggregate=aggregate,gate=gate,
        settings=SETTINGS,final_validated=False,runtime_replaced=False,review_sha256=digest(review)))
    print(json.dumps(dict(aggregate=aggregate,gate=gate),indent=2))


if __name__=='__main__':main()
