"""Independent membership, fixed-refit, transform and metric replay of the comparison."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from skimage.color import rgb2lab,deltaE_ciede2000
from src.model_training.train_model import load_model
from src.utilities.config import get_config

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as stream:return list(csv.DictReader(stream))
def main():
    out=ROOT/get_config().OUTPUTS_ROOT/'core_control_comparison_v1';summary=json.loads((out/'summary.json').read_text());parent=ROOT/'outputs/core_pipeline_check_v1'
    rows=read(ROOT/'data/manifests/controlled_training_v2/train.csv');by_id={r['pair_id']:r for r in rows};eligible=set(summary['eligible_ids']);held=set(summary['held_ids'])
    pass_rows=read(ROOT/'data/manifests/square_mask_quality_v1/screen_pass_train.csv');held_rows=read(ROOT/'data/manifests/square_mask_quality_v1/held_train.csv')
    assert eligible=={r['parent_pair_id'] for r in pass_rows} and held=={r['parent_pair_id'] for r in held_rows}
    assert eligible|held==set(by_id) and not eligible&held
    features=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees'];targets=['target_gamma','target_red_gain','target_blue_gain']
    core={r['pair_id']:r for r in json.loads((parent/'summary.json').read_text())['records']}
    groups={r['duplicate_group_id'] for r in rows};models={};checked_predictions=0
    assert len(groups)==7
    for audit in summary['fit_audits']:
        fold=next(f for f in summary['folds'] if f['fold_id']==audit['fold_id']);group=fold['held_out_duplicate_group']
        expected_eval=sorted(r['pair_id'] for r in rows if r['duplicate_group_id']==group)
        expected_fit=sorted(p for p in eligible if by_id[p]['duplicate_group_id']!=group and (audit['method']=='with_controls' or by_id[p]['variant'] not in ['identity_control','mild_bright_exposure']))
        assert audit['fit_pair_ids']==expected_fit and sorted(audit['evaluation_pair_ids'])==expected_eval
        assert audit['feature_columns']==features and audit['target_columns']==targets and audit['sample_weight'] is None
        assert not {by_id[p]['source_image_id'] for p in expected_fit}&{by_id[p]['source_image_id'] for p in expected_eval}
        assert not set(expected_fit)&held
        for p in expected_fit:
            row=by_id[p];assert row['partition']=='train' and row['table_use']=='train' and int(row['clipped_pixel_count'])==0
            gamma,red,blue=[float(row['distortion_'+k]) for k in ['gamma','red_gain','blue_gain']]
            np.testing.assert_allclose([float(row[t]) for t in targets],[1/gamma,red**(-gamma),blue**(-gamma)],rtol=0,atol=1e-12)
        x=np.array([[core[p]['features'][f] for f in features] for p in expected_fit]);y=np.array([[float(by_id[p][t]) for t in targets] for p in expected_fit])
        path=out/'fold_models'/f"fold{audit['fold_id']}_{audit['method']}.joblib";assert digest(path)==summary['fold_model_sha256'][path.name]
        model=load_model(str(path));assert model.get_params()==audit['settings']
        repeat=DecisionTreeRegressor(max_depth=3,random_state=42,min_samples_leaf=1).fit(x,y)
        for field in ['children_left','children_right','feature','threshold','value']:
            np.testing.assert_array_equal(getattr(model.tree_,field),getattr(repeat.tree_,field))
        models[(audit['fold_id'],audit['method'])]=model
    assert len(models)==14
    frozen=load_model(str(ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH));all_predictions={(p['pair_id'],p['method']):p for p in summary['predictions']}
    assert len(all_predictions)==120
    for p in summary['predictions']:
        pair=p['pair_id'];row=by_id[pair];x=np.array([core[pair]['features'][f] for f in features]);np.testing.assert_array_equal(x,p['features'])
        if p['method']=='no_correction':want=np.ones(3)
        elif p['method']=='frozen_runtime_seen_source':
            assert p['evaluation_kind']=='seen_source_diagnostic';want=frozen.predict(x[None,:])[0]
        else:
            assert p['evaluation_kind']=='source_held_out';want=models[(p['fold_id'],p['method'])].predict(x[None,:])[0]
        np.testing.assert_array_equal(want,p['predicted_parameters'])
        image=cv2.imread(str(ROOT/row['input_path']))[:,:,::-1].copy();ref=cv2.imread(row['source_path'])[:,:,::-1].astype(float)/255
        support=cv2.imread(str(parent/'cases'/pair/'correction_mask.png'),0)>0;scoring=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        raw=(image.astype(float)/255)**(1/want[0])*np.array([want[1],1,want[2]])
        corrected=image.copy();corrected[support]=np.rint(np.clip(raw,0,1)*255).astype(np.uint8)[support]
        np.testing.assert_array_equal(corrected[~support],image[~support]);output=corrected.astype(float)/255;diff=abs(ref-output)
        delta=deltaE_ciede2000(rgb2lab(ref),rgb2lab(output))
        replay=dict(ciede2000_source_mask=float(delta[scoring].mean()),rgb_mae_source_mask=float(diff[scoring].mean()),rgb_mae_whole_image=float(diff.mean()),rgb_mae_outside_source_mask=float(diff[~scoring].mean()))
        for k,v in replay.items():np.testing.assert_allclose(p[k],v,rtol=0,atol=1e-12)
        np.testing.assert_allclose(p['parameter_absolute_error'],abs(want-np.array(p['target_parameters'])),rtol=0,atol=1e-12)
        if p['method']=='frozen_runtime_seen_source':np.testing.assert_allclose(p['ciede2000_source_mask'],core[pair]['metrics']['decision_tree']['ciede2000_source_mask'],rtol=0,atol=1e-12)
        checked_predictions+=1
    for a in summary['aggregate']:
        ids=eligible if a['scope']=='primary' else held
        cohort=[p for p in summary['predictions'] if p['pair_id'] in ids and p['method']==a['method'] and (a['variant']=='all' or p['variant']==a['variant'])]
        sources={p['source_image_id'] for p in cohort};equal=np.mean([np.mean([p['ciede2000_source_mask'] for p in cohort if p['source_image_id']==s]) for s in sources])
        assert a['pairs']==len(cohort) and a['sources']==len(sources)
        np.testing.assert_allclose(a['mean_ciede2000'],np.mean([p['ciede2000_source_mask'] for p in cohort]),rtol=0,atol=1e-12)
        np.testing.assert_allclose(a['equal_source_mean_ciede2000'],equal,rtol=0,atol=1e-12)
        assert a['worsened_pairs']==sum(p['ciede2000_source_mask']>all_predictions[(p['pair_id'],'no_correction')]['ciede2000_source_mask']+1e-12 for p in cohort)
    # Descriptive complete-five sensitivity; no model/setting selection.
    expected_variants={'dark','color_shift','bright_warm','identity_control','mild_bright_exposure'}
    complete=[s for s in sorted({by_id[p]['source_image_id'] for p in eligible}) if {by_id[p]['variant'] for p in eligible if by_id[p]['source_image_id']==s}==expected_variants]
    sensitivity=[];source_scores=[]
    for method in ['no_correction','older_recipe','with_controls']:
        part=[p for p in summary['predictions'] if p['pair_id'] in eligible and p['method']==method and p['source_image_id'] in complete]
        sensitivity.append(dict(method=method,sources=complete,pairs=len(part),mean_ciede2000=float(np.mean([p['ciede2000_source_mask'] for p in part])) if part else None))
        for s in sorted({by_id[p]['source_image_id'] for p in eligible}):
            source_part=[p for p in summary['predictions'] if p['pair_id'] in eligible and p['method']==method and p['source_image_id']==s]
            source_scores.append(dict(source=s,method=method,pairs=len(source_part),mean_ciede2000=float(np.mean([p['ciede2000_source_mask'] for p in source_part]))))
    (out/'sensitivity_and_sources.json').write_text(json.dumps(dict(complete_five=sensitivity,source_scores=source_scores),indent=2))
    def aggregate(method,variant='all'):return next(a for a in summary['aggregate'] if a['scope']=='primary' and a['method']==method and a['variant']==variant)
    revised=aggregate('with_controls')
    readiness=dict(status='hold_no_runtime_replacement',primary_equal_source_better_than_old=bool(revised['equal_source_mean_ciede2000']<aggregate('older_recipe')['equal_source_mean_ciede2000']),
        primary_equal_source_better_than_no_correction=bool(revised['equal_source_mean_ciede2000']<aggregate('no_correction')['equal_source_mean_ciede2000']),
        unchanged_nonharm=aggregate('with_controls','identity_control')['worsened_pairs']==0,
        mild_nonharm=aggregate('with_controls','mild_bright_exposure')['worsened_pairs']==0,
        leakage_checks='pass',held_IDs_fitted=0,clipped_or_external_rows_fitted=0,original_runtime_replaced=False,
        interpretation='Controls help versus old recipe but do not establish acceptable correction. No threshold/feature/capacity search follows.',
        primary_pairs=22,held_diagnostic_pairs=8,eligible_source_groups=6,diagnostic_outer_groups=7)
    (out/'readiness.json').write_text(json.dumps(readiness,indent=2))
    assert all(digest(ROOT/path)==h for path,h in summary['input_sha256'].items())
    result=dict(status='pass',fold_models_refit_verified=14,parameter_transform_metric_predictions_replayed=checked_predictions,
        aggregate_rows_verified=len(summary['aggregate']),eligible_held_split_verified=True,original_hashes_unchanged=True,
        summary_sha256=digest(out/'summary.json'),verifier_sha256=digest(Path(__file__)),
        verification_refits=14,refits_are_replay_only_not_additional_candidates=True,
        output_sha256={str(p.relative_to(ROOT)):digest(p) for p in list((out/'fold_models').glob('*.joblib'))+list((out/'boards').glob('*.png'))})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='output_sha256'}))
if __name__=='__main__':main()
