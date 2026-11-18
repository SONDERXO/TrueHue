"""Single fixed eleven-fold real prediction test on already verified features."""
from pathlib import Path
import json
import hashlib
import importlib.metadata
import platform
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training import frozen_block_neighbour as work

OUT=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
PREP=ROOT/'outputs/five_control_real_feature_preparation_v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    if sys.argv[1:]!=['--execute-fixed-prediction-test']:
        raise SystemExit('Explicit --execute-fixed-prediction-test required')
    if OUT.exists():raise FileExistsError('Preserve prior or partial real attempt')
    completion=read(PREP/'completion_PRIVATE.json');verification=read(PREP/'verification_PRIVATE.json')
    assert completion['status']=='VERIFIED_FEATURE_PREPARATION_ONLY_NOT_TRAINING_OR_QUALIFICATION'
    assert completion['verification_sha256']==sha(PREP/'verification_PRIVATE.json')
    assert verification['passed'] and verification['scalar_feature_values']==18546
    assert completion['identity_vectors_exact']==11 and completion['nonidentity_vectors_prepared']==55
    for p,h in verification['artifact_sha256'].items():assert sha(PREP/p)==h
    prep_execution=read(PREP/'execution_plan_PRIVATE.json')
    for p,h in prep_execution['input_sha256'].items():assert sha(ROOT/p)==h
    qa_path=ROOT/'outputs/frozen_block_neighbour_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['actual_generated_indices']==11
    for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h
    for p,h in qa['artifact_sha256'].items():assert sha(qa_path.parent/p)==h
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p)
        for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']})
    assert versions==qa['versions']
    plan=read(ROOT/'outputs/frozen_block_neighbour_design_v1/plan_PRIVATE.json')
    check=read(ROOT/'outputs/frozen_block_neighbour_design_v1/verification_PRIVATE.json')
    assert check['passed'] and check['plan_sha256']==sha(ROOT/'outputs/frozen_block_neighbour_design_v1/plan_PRIVATE.json')
    for p,h in plan['added_feature_bindings'].items():assert sha(ROOT/p)==h
    for p,h in plan['neighbour_bindings'].items():assert sha(ROOT/p)==h
    rep=ROOT/'outputs/reiqa_development_representation_v1'
    assert read(rep/'independent_verification_PRIVATE.json')['passed']
    rows=read(PREP/'rows_PRIVATE.json');declared={r['case_id']:r for r in plan['rows']}
    with np.load(rep/'features.npz',allow_pickle=False) as pack:
        assert pack.files==[r['case_id'] for r in rows]
        for r in rows:
            vector=pack[r['case_id']]
            assert vector.shape==(4096,) and vector.dtype==np.float32 and np.isfinite(vector).all()
            r['x']=r['x']+vector.tolist()
    assert len(rows)==len(declared)==66 and len({r['case_id'] for r in rows})==66
    for r in rows:
        d=declared[r['case_id']]
        assert r['generated_fixture'] is False and r['source_id']==d['source_id'] and r['role']==d['role'] and r['y']==d['y']
        assert not r['parent_training_admitted'] and len(r['x'])==4377
    # Explicit declared development role; no parent admission flags changed.
    experiment=dict(plan,generated_fixture=False,
        execution_role='authorized_exposed_development_neighbour_predictor_not_final_admission',
        inherited_parent_tree_fit_plan=plan['planned_tree_fits'],planned_tree_fits=0,
        planned_index_constructions=11,tree_fits=0)
    input_hashes={}
    assert len(plan['feature_names'])==4377 and plan['predictor']=='fixed_equal_block_energy_1nn'
    for r in plan['rows']:
        for path_key,hash_key in [('input_pack','input_pack_sha256'),('cached_support_pack','cached_support_sha256')]:
            p=(ROOT/r[path_key]).resolve()
            assert p.is_relative_to(ROOT/'outputs/ffhq_directional_recoverability_v1/cases')
            assert sha(p)==r[hash_key];input_hashes[str(p)]=r[hash_key]
    bindings={p:sha(ROOT/p) for p in ['scripts/run_frozen_block_neighbour.py',
        'scripts/verify_frozen_block_neighbour.py']}
    for p in [PREP/'rows_PRIVATE.json',PREP/'completion_PRIVATE.json',PREP/'verification_PRIVATE.json',qa_path]:
        bindings[str(p.relative_to(ROOT))]=sha(p)
    bindings.update(plan['added_feature_bindings'])
    bindings.update(plan['neighbour_bindings'])
    bindings[str(rep.relative_to(ROOT)/'features.npz')]=sha(rep/'features.npz')
    OUT.mkdir()
    work.write(OUT/'adapter_bindings_PRIVATE.json',dict(input_sha256=bindings,versions=versions,
        cached_input_hashes=input_hashes,feature_recomputations=0,target_refits=0,
        expected_real_index_constructions=11,tree_fits=0,reference_access='cached reference RGB decoded only after all indices verified and66held controls sealed'))
    work.write(OUT/'execution_plan.json',experiment);work.write(OUT/'prepared_rows.json',rows)
    try:
        models=work.fit_all(experiment,rows,OUT/'models')
        assert len(models)==11
        inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
        work.write(OUT/'inference_inputs.json',inference)
        predictions=work.predict_held(experiment,inference,models,OUT/'models')
        assert len(predictions)==66
        # Only now may reference pixels be decoded for scoring.
        supports={};cases=[];access=[]
        for r in rows:
            d=declared[r['case_id']];source=r['source_id']
            if source not in supports:
                p=ROOT/d['cached_support_pack']
                with np.load(p,allow_pickle=False) as pack:
                    supports[source]={k:pack[k].copy() for k in ['reference','alpha','protected']}
                access.append(dict(source_id=source,path=str(p),keys=['reference','alpha','protected'],stage='after_all_indices_verified_and_held_controls_sealed'))
            with np.load(ROOT/d['input_pack'],allow_pickle=False) as pack:image=pack['input']
            access.append(dict(case_id=r['case_id'],path=d['input_pack'],keys=['input'],stage='scoring_only'))
            cases.append(dict(case_id=r['case_id'],source_id=source,role=r['role'],generated_fixture=False,
                              y=r['y'],image=image,**supports[source]))
        work.write(OUT/'scoring_access_PRIVATE.json',access)
        work.score(experiment,cases,predictions,OUT/'evaluation')
        for p,h in input_hashes.items():assert sha(p)==h
        for p,h in bindings.items():assert sha(ROOT/p)==h
        work.write(OUT/'complete.json',dict(real_index_constructions=11,tree_fits=0,fitting_routes=660,
            held_predictions=66,constant_renders=66,feature_recomputations=0,target_refits=0,
            model_ready=False,review_launched=False))
        print('Fixed real prediction test complete; independent verification pending.',flush=True)
    except Exception as error:
        work.write(OUT/'failure_PRIVATE.json',dict(status='failed_preserved',error_type=type(error).__name__,
            error=str(error),index_constructions_started=read(OUT/'models/index_accounting.json')['started'] if (OUT/'models/index_accounting.json').exists() else 0));raise


if __name__=='__main__':main()
