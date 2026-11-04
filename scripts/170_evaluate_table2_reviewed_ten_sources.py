"""Import exact shortlist decisions and evaluate fixed ten-source development folds."""
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

STATEMENT='51803: accept concern: a minor hole in the mask, 53109: accept, 713: reject reason: captures hair in mask, Continue the next step'
OUT=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    old=ROOT/'outputs/table2_reviewed_expansion_evaluation_v1';folder=ROOT/'outputs/table2_source_expansion24_v1'
    prior=read(old/'fit_plan.json');pv=read(old/'verification.json')
    assert digest(old/'fit_plan.json')==pv['fit_plan_sha256']
    data=read(folder/'summary.json');verify=read(folder/'verification.json');screen=read(folder/'screen_verification.json')
    assert digest(folder/'summary.json')==verify['summary_sha256']
    assert digest(folder/'shortlist_review.html')==screen['shortlist_review_sha256']
    assert digest(folder/'codex_source_screen.json')==screen['source_screen_sha256']
    for p,h in verify['evidence_sha256'].items():assert digest(folder/p)==h
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    _,identity=contract(ROOT);assert identity==data['measurement_contract_sha256']
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    OUT.mkdir();review=OUT/'user_review.json'
    write(review,dict(user_statement_verbatim=STATEMENT,decisions={
        '51803':dict(decision='accept',concern='a minor hole in the mask'),
        '53109':dict(decision='accept',concern=''),
        '713':dict(decision='reject',reason='captures hair in mask')},
        review_html_sha256=digest(folder/'shortlist_review.html'),summary_sha256=digest(folder/'summary.json'),
        source_screen_sha256=digest(folder/'codex_source_screen.json'),
        scope='Exact displayed source/reference, identity and MST-conditioned input; no MST/color truth or other held-source approval.'))
    rows=[dict(r) for r in prior['rows']];excluded=list(prior['excluded'])
    sources={s['source_id']:s for s in data['records']}
    for name in ['51803','53109']:
        s=sources[name];assert s['status']=='pending_review'
        # Start from the established schema, replacing every source-specific field.
        for is_identity in [True,False]:
            template=next(r for r in prior['rows'] if (r['variant']=='identity')==is_identity)
            r=dict(template)
            for k in ['target_fit','target_fit_report_sha256','target_fit_report_path',
                      'distortion_gamma','distortion_red_gain','distortion_blue_gain']:
                r.pop(k,None)
            variant='identity' if is_identity else 'table2_'+s['assigned_severity']
            image=folder/'images'/(name+('_reference.png' if is_identity else '_input.png'))
            mask=folder/'images'/(name+('_reference_mask.png' if is_identity else '_input_mask.png'))
            rm=folder/'images'/(name+'_reference_mask.png');reference=folder/'images'/(name+'_reference.png')
            measurement=s['reference_measurement'] if is_identity else s['input_measurement']
            features=measurement['features'];pixels=s['reference_measurement']['skin_pixels']
            count=0 if is_identity else s['clipping']['clipped_pixels']
            r.update(pair_id=name+'__'+variant,source_image_id=s['image_id'],duplicate_group_id=s['duplicate_group_id'],
                variant=variant,input_processing_status=measurement['status'],measurement_contract_sha256=identity,
                input_mst_index=lookup.label(features['input_ita_degrees'])-1,
                reference_mst_estimate=s['reference_mst_estimate'],severity_probe=s['assigned_severity'],
                mask_review_report_sha256=digest(review),review_concern='a minor hole in the mask' if name=='51803' else '',
                clipped_pixel_count=count,clipped_channel_samples=0 if is_identity else s['clipping']['clipped_channel_samples'],
                generation_skin_pixels=pixels,clipped_pixel_fraction=count/pixels,
                input_path=str(image.relative_to(ROOT)),input_sha256=digest(image),
                input_mask_path=str(mask.relative_to(ROOT)),input_mask_sha256=digest(mask),
                reference_mask_path=str(rm.relative_to(ROOT)),reference_mask_sha256=digest(rm),reference_path=str(reference.relative_to(ROOT)))
            r.update(features)
            if is_identity:
                parameters=[1.,1.,1.]
                r.update(transform_version='encoded_rgb_gamma_then_gain_v1',target_method='exact_gamma_gain_inverse',
                    distortion_gamma=1.,distortion_red_gain=1.,distortion_blue_gain=1.)
            else:
                fit=s['target_fit'];fitpath=OUT/(name+'_target_fit.json');write(fitpath,fit);parameters=fit['parameters']
                r.update(transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',
                    target_fit=fit,target_fit_report_path=str(fitpath.relative_to(ROOT)),target_fit_report_sha256=digest(fitpath))
            r.update(zip(TARGETS,parameters));rows.append(r)
    excluded.extend(dict(pair_id='713__'+variant,reason='captures hair in mask') for variant in ['identity','table2_'+sources['713']['assigned_severity']])
    held=[dict(source_id=s['source_id'],status=s['status'],reason='Prior qualitative/numerical hold; not approved by this review') for s in data['records'] if s['source_id'] not in ['51803','53109','713']]
    rows=validate_stress_rows(rows,measurement_contract_sha256=identity,lookup_sha256=data['lookup_sha256'],eligible_pair_ids=[r['pair_id'] for r in rows])
    folds=source_group_folds(rows);assert len(rows)==20 and len(folds)==10
    rejected={'51739','40048','42532','63870','713'}
    assert not {r['pair_id'].split('__')[0] for r in rows}&rejected
    reviews=[old/'user_review.json',ROOT/'outputs/table2_stress_evaluation_v2/user_review.json',review]
    def verify_rows():
        for r in rows:
            for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[path])==r[key]
            assert r['mask_review_report_sha256'] in {digest(p) for p in reviews}
            if 'target_fit_report_path' in r:
                assert digest(ROOT/r['target_fit_report_path'])==r['target_fit_report_sha256']
                assert read(ROOT/r['target_fit_report_path'])==r['target_fit']
    verify_rows()
    tracked={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),old/'fit_plan.json',old/'summary.json',
        folder/'summary.json',folder/'verification.json',folder/'shortlist_review.html',folder/'screen_verification.json',
        artifact,ROOT/'src/data_preparation/table2_stress_contract.py',*reviews]}
    write(OUT/'fit_plan.json',dict(status='frozen_before_fit',rows=rows,excluded=excluded,retained_holds=held,folds=folds,
        settings=SETTINGS,features=MST_FEATURES,targets=TARGETS,sample_weight=None,identity_tolerance=0.,input_sha256=tracked,
        caveat='Exposed development; source/known-duplicate separation is not person separation. Severity counts are recorded separately.',
        severity_counts={severity:sum(r['variant']=='table2_'+severity for r in rows) for severity in ['light','medium','dark']}))
    def matrix(selected,columns):return np.asarray([[r[k] for k in columns] for r in selected],float)
    def rgb(path):return cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
    records=[]
    for fold in folds:
        training=[r for r in rows if r['pair_id'] in fold['train_pair_ids']];validation=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert len(training)==18 and len(validation)==2
        model=DecisionTreeRegressor(**SETTINGS).fit(matrix(training,MST_FEATURES),matrix(training,TARGETS))
        fdir=OUT/f"fold_{fold['fold_id']}";fdir.mkdir();joblib.dump(model,fdir/'decision_tree.joblib')
        payload=export_tree(model,MST_FEATURES,TARGETS,dict(fold_id=fold['fold_id'],experimental=True));write(fdir/'decision_tree.json',payload)
        portable=PortableTree(payload)
        for r in validation:
            parameters=model.predict([[r[k] for k in MST_FEATURES]])[0]
            np.testing.assert_allclose(portable.predict_one([r[k] for k in MST_FEATURES]),parameters,rtol=0,atol=1e-12)
            image=rgb(ROOT/r['input_path']);reference=rgb(ROOT/r['reference_path'])
            mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
            result=apply_correction(image,mask,parameters);assert np.array_equal(result[~mask],image[~mask])
            output=OUT/(r['pair_id']+'_corrected.png');assert cv2.imwrite(str(output),cv2.cvtColor(result,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],variant=r['variant'],fold_id=fold['fold_id'],parameters=parameters.tolist(),
                no_correction=image_errors(reference,image,scoring),learned=image_errors(reference,result,scoring),
                oracle=image_errors(reference,apply_correction(image,mask,[r[k] for k in TARGETS]),scoring),output_sha256=digest(output)))
    identities=[r for r in records if r['variant']=='identity'];distorted=[r for r in records if r['variant']!='identity']
    aggregate={key:{method+'_ciede2000':float(np.mean([r[method]['ciede2000_source_mask'] for r in subset])) for method in ['no_correction','learned','oracle']}
        for key,subset in [('all',records),('identity',identities),('distorted',distorted)]}
    harmed=[r['pair_id'] for r in identities if r['learned']['ciede2000_source_mask']>0]
    gate=dict(overall_improves=aggregate['all']['learned_ciede2000']<aggregate['all']['no_correction_ciede2000'],identity_pass=not harmed,harmed_identity_ids=harmed)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    verify_rows()
    assert tracked=={p:digest(ROOT/p) for p in tracked}
    write(OUT/'summary.json',dict(status='complete',admitted_pairs=20,sources=10,records=records,aggregate=aggregate,gate=gate,
        excluded=excluded,settings=SETTINGS,final_validated=False,runtime_replaced=False,review_sha256=digest(review)))
    print(json.dumps(dict(aggregate=aggregate,gate=gate),indent=2))


if __name__=='__main__':main()

