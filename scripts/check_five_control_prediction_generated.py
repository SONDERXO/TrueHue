"""Generated-only full prediction-workflow rehearsal; no real arrays or real fits."""
from pathlib import Path
import json
import hashlib
import sys
import platform
import importlib.metadata
from sklearn.tree import DecisionTreeRegressor

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training import five_control_prediction_workflow as work
from src.model_training.five_control_prediction_fixtures import build
from src.evaluation.five_control_prediction_pixel_verification import verify_run

OUT=ROOT/'outputs/five_control_prediction_engineering_v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    if sys.argv[1:]!=['--generated-only']:raise SystemExit('Explicit --generated-only required')
    if OUT.exists():raise FileExistsError('Preserve completed or partial engineering run')
    design_path=ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    check=read(design_path.parent/'verification_PRIVATE.json')
    assert check['passed'] and sha(design_path)==check['plan_sha256']
    design=read(design_path)
    for p,h in design['input_sha256'].items():assert sha(ROOT/p)==h
    files=['src/model_training/portable_five_control_tree.py',
        'src/model_training/five_control_prediction_verification.py',
        'src/model_training/five_control_prediction_workflow.py',
        'src/model_training/five_control_prediction_fixtures.py',
        'src/evaluation/five_control_prediction_pixel_verification.py',
        'src/evaluation/affine_prepower_scalar.py','src/model_training/affine_prepower_targets.py',
        'src/evaluation/directional_recoverability.py',
        'src/distortion_generation/directional_exposure_recipe.py',
        'src/distortion_generation/table2_composite.py','src/distortion_generation/paper_gamma.py',
        'scripts/check_five_control_prediction_generated.py','tests/test_five_control_prediction_workflow.py']
    bindings={p:sha(ROOT/p) for p in files}
    bindings[str(design_path.relative_to(ROOT))]=sha(design_path)
    bindings.update(design['input_sha256'])
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p)
        for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']})
    OUT.mkdir()
    work.write(OUT/'execution_plan_PRIVATE.json',dict(scope='generated_only',input_sha256=bindings,
        versions=versions,planned_tree_fits=11,planned_target_fits=0,planned_fitting_replays=660,
        planned_held_predictions=66,planned_constant_renders=66))
    try:
        plan,cases,mapping=build(design['feature_names'],design['settings'])
        assert len(cases)==66 and all(c['generated_fixture'] for c in cases)
        assert sum(c['y'][-1]==.3 for c in cases)==6
        work.write(OUT/'generated_mapping.json',mapping)
        # Expected identity vectors generated once; preparation must reproduce all11.
        identities={c['source_id']:work.features281(c['image'],c['measurement'],mapping,plan['feature_names'])[0]
            for c in cases if c['role']=='identity'}
        work.write(OUT/'generated_expected_identities.json',identities)
        work.write(OUT/'generated_case_metadata.json',[{k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']} for c in cases])
        fits=[]
        def factory(**settings):
            model=DecisionTreeRegressor(**settings);original=model.fit
            def counted(*args,**kwargs):
                if len(fits)>=11:raise RuntimeError('Frozen11-tree budget exhausted')
                fits.append(True)
                return original(*args,**kwargs)
            model.fit=counted
            return model
        rows,models,records=work.execute(plan,cases,mapping,identities,OUT/'generated_run',factory=factory)
        assert len(fits)==11 and len(rows)==len(records)==66 and len(models)==11
        # Check saved fixture inputs remained exact; no substitution during scoring.
        import numpy as np
        for c in cases:
            with np.load(OUT/'generated_run/evaluation'/(c['case_id']+'.npz'),allow_pickle=False) as pack:
                for key,field in [('input','image'),('reference','reference'),('alpha','alpha'),('protected','protected')]:
                    np.testing.assert_array_equal(pack[key],c[field])
        verified=verify_run(OUT/'generated_run')
        assert all(sha(ROOT/p)==h for p,h in bindings.items())
        work.write(OUT/'verification_PRIVATE.json',dict(**verified,scope='generated_only_prediction_engineering',
            actual_generated_tree_fits=11,workflow_target_optimizer_calls=0,
            feature_vectors_prepared=66,identity_parity_replays=11,nonidentity_extractions=55,
            expected_identity_fixture_computations=11,generated_bound_targets_retained=6,
            real_source_arrays=0,real_tree_fits=0,real_held_predictions=0,locked_access=False,
            versions=versions,input_sha256=bindings,
            artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}))
        print('PASS: generated11trees/660fitting routes/66held routes/132renders, with full independent replay.',flush=True)
    except Exception as error:
        work.write(OUT/'failure_PRIVATE.json',dict(status='failed_preserved',error_type=type(error).__name__,error=str(error)));raise


if __name__=='__main__':main()
