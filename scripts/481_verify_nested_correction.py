"""No-refit nested membership, portable predictions and renderer verification."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.ita_estimation.contextual_mst_experiment import predict
from src.correction.continuous_mst_candidate import continuous_model_features,CONTINUOUS_FEATURES
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1'
OUT=ROOT/'outputs/nested_correction_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    plan=read(PARENT/'plan_PRIVATE.json');v=read(PARENT/'results_PRIVATE.json');rows=read(PARENT/'prepared_rows_PRIVATE.json')
    assert all(sha(Path(p))==h for p,h in plan['input_sha256'].items())
    assert all(sha(PARENT/p)==h for p,h in read(PARENT/'sha256.json').items())
    indexed={r['case_id']:r for r in rows};preds={r['case_id']:r for r in v['records']};models=v['mapping_models']
    assert len(indexed)==len(preds)==420
    tracechecks=0;renderchecks=0
    for f in v['folds']:
        held=f['held_key'];tree=PortableTree(f['tree']);outer=models[f['outer_mapping_id']]
        assert outer['excluded_keys']==[held] and held not in outer['training_keys']
        targets=np.array([indexed[k]['target'] for k in f['training_cases']])
        np.testing.assert_allclose(targets.mean(axis=0),f['normalization']['fitting_target_mean'],atol=1e-12,rtol=0)
        np.testing.assert_allclose(targets.std(axis=0),f['normalization']['fitting_population_std'],atol=1e-12,rtol=0)
        for trace in f['training_feature_trace']:
            row=indexed[trace['case_id']];key=row['subject_id'];inner=models[trace['mapping_id']]
            assert set(inner['excluded_keys'])=={held,key}
            assert not ({held,key}&set(inner['training_keys']))
            mst=predict(inner['model'],row['features']);assert mst==trace['mst_prediction']
            features=continuous_model_features(row['features'],mst,measurement_contract_sha256=plan['contract_sha256'],estimator_measurement_contract_sha256=plan['contract_sha256'])
            assert [features[k] for k in CONTINUOUS_FEATURES]==trace['features'];tracechecks+=1
        for key in f['held_cases']:
            r=indexed[key];p=preds[key];assert r['subject_id']==held
            if p['status']=='unavailable_original':continue
            folder=PARENT/r['source_case'];pair=folder/r['case']['id']
            image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
            ref=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB)
            mask=cv2.imread(str(folder/'mask.png'),0)>0
            if p['parameters'] is not None:
                mst=predict(outer['model'],r['features']);assert mst==p['mst_prediction']
                assert tree.predict_one(p['features'])==p['parameters']
                output=render_rgb8(image,mask.astype(float),p['parameters'])
            else:output=image
            saved=cv2.cvtColor(cv2.imread(str(pair/'prediction.png')),cv2.COLOR_BGR2RGB)
            assert np.array_equal(output,saved) and np.array_equal(output[~mask],image[~mask])
            assert metrics(output,ref,mask)==p['predicted_metrics'];renderchecks+=1
    # Retain the two predeclared inspection cases of the failed source as explicit boards.
    failures=[]
    for r in rows:
        if r['status']=='unavailable_original' and r['case']['id'] in ['combined_cool_under','stress_combined_under']:
            image=cv2.imread(str(ROOT/'outputs/stellenbosch_new_subjects_v1'/r['source_case']/'input.png'))
            panel=np.full((188,640,3),255,np.uint8);panel[28:188,:160]=cv2.resize(image,(160,160))
            cv2.putText(panel,r['case_id']+' UNAVAILABLE: original landmarks',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
            failures.append((r['case_id'],panel))
    OUT.mkdir(parents=True)
    for key,panel in failures:cv2.imwrite(str(OUT/(key+'_failure.png')),panel)
    report=dict(attempts=420,nested_training_trace_checks=tracechecks,held_renderer_and_metric_replays=renderchecks,
        outer_folds=len(v['folds']),mapping_fits=v['mapping_ridge_fits'],tree_fits=v['correction_tree_fits'],
        failed_inspection_boards=len(failures),all_sources_unchanged=True,refits=0)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
