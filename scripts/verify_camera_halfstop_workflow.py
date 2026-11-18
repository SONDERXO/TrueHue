"""Independent forward/label/feature joins and full held scalar render replay."""
from pathlib import Path
import sys,json,math
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.evaluation.camera_halfstop_generation_scalar import forward,controls
from src.evaluation.five_control_feature_scalar import features as scalar_features
from src.evaluation.camera_halfstop_pixel_verification import verify_run
from src.model_training.reiqa_frozen_features import sha
DATA=ROOT/'outputs/camera_halfstop_data_v1';NEURAL=ROOT/'outputs/camera_halfstop_neural_v1';RUN=ROOT/'outputs/camera_halfstop_prediction_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    target=RUN/'verification_PRIVATE.json'
    if target.exists():raise FileExistsError(target)
    rows=read(DATA/'rows281_PRIVATE.json');joined=read(RUN/'prepared_rows.json');plan=read(DATA/'plan_PRIVATE.json')
    assert len(rows)==len(joined)==66
    for p,h in read(DATA/'bindings_PRIVATE.json')['input_sha256'].items():assert sha(ROOT/p)==h
    for p,h in read(RUN/'bindings_PRIVATE.json').items():assert sha(ROOT/p)==h
    parent=read(ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json')
    src={s['source_id']:s for s in parent['feature_sources']};mapping=read(ROOT/parent['mapper_path'])
    masks={s:cv2.imread(str(ROOT/v['measurement_path']),0) for s,v in src.items()}
    clean={};meta={r['case_id']:r for r in read(DATA/'case_metadata_PRIVATE.json')};maxdiff=0.
    original_identity={r['source_id']:r for r in parent['rows'] if r['role']=='identity'}
    for s,r in original_identity.items():
        assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
        with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:clean[s]=pack['input'].copy()
    with np.load(NEURAL/'features.npz',allow_pickle=False) as neural:
        for r,j in zip(rows,joined):
            assert r['case_id']==j['case_id'] and r['generated_fixture'] is j['generated_fixture'] is False
            assert r['parent_training_admitted'] is False and r['synthetic_condition'] is True
            assert r['y']==j['y']==controls(r['role'])
            assert j['x']==r['x']+neural[r['case_id']].tolist()
            assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
            with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:
                image=pack['input'];reference=pack['reference'];alpha=pack['alpha']
            np.testing.assert_array_equal(reference,clean[r['source_id']])
            expected,clipped=forward(reference,r['role']);np.testing.assert_array_equal(image,expected)
            recorded=meta[r['case_id']]['generation']
            assert recorded['preclip_overflow_channel_samples']==int(clipped.sum())
            assert math.isclose(recorded['primary_clipped_pixel_fraction'],float(clipped.any(axis=2)[alpha>0].mean()),abs_tol=1e-15)
            independent=scalar_features(image,masks[r['source_id']],mapping,parent['feature_names'])
            maxdiff=max(maxdiff,max(abs(a-b) for a,b in zip(r['x'],independent)))
            assert all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(r['x'],independent))
            if r['role']=='identity':assert r['x']==src[r['source_id']]['identity_saved_feature_vector']
    result=verify_run(RUN)
    assert read(RUN/'models/index_accounting.json')['started']==11
    result.update(scope='separate_camera_inspired_task_not_oldstress_validation',independent_forward_cases=66,scalar_feature_values=18546,
        max_scalar_feature_difference=maxdiff,analytic_target_cases=66,target_optimizer_calls=0,index_constructions=11,
        identity281_exact=11,identity4096_exact=read(NEURAL/'completion_PRIVATE.json')['identity4096_exact'],model_ready=False,
        artifact_sha256={str(p.relative_to(RUN)):sha(p) for p in RUN.rglob('*') if p.is_file()})
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('PASS independent camera-inspired forward/labels18546features660fit66held132render; status='+result['numeric_status'],flush=True)
if __name__=='__main__':main()
