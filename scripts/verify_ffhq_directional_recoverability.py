"""Independent saved-array scalar replay; never calls a fitter or reads original sources."""
from pathlib import Path
import sys
import json
import hashlib
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation import directional_recoverability_scalar as scalar

OUT=ROOT/'outputs/ffhq_directional_recoverability_v1'
ROLES=('identity','colour_only','exposure_under','exposure_over','combined_under','combined_over')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)
def ahash(a):return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');plan=execution['plan']
    completed=read(OUT/'execution_complete_PRIVATE.json')
    assert completed['cases']==66 and completed['sources']==11 and completed['tree_fits']==0
    for name,digest in execution['input_sha256'].items():assert sha(ROOT/name)==digest
    qa=read(ROOT/'outputs/directional_recoverability_engineering_v1/verification_PRIVATE.json')
    for name,digest in qa['input_sha256'].items():assert sha(ROOT/name)==digest
    arrays={r['source_id']:r for r in read(OUT/'source_array_bindings_PRIVATE.json')}
    records=[];checks=0
    for ref in plan['source_references']:
        source_id=ref['source_id'];folder=OUT/'cases'/source_id
        with np.load(folder/'support.npz',allow_pickle=False) as pack:
            source={k:pack[k] for k in ['reference','alpha','protected']}
        source.update(source_id=source_id,generated_fixture=False)
        for key in ['reference','alpha','protected']:assert ahash(source[key])==arrays[source_id][key]
        assert source['reference'].shape==(256,256,3)
        assert not np.any(source['alpha'][source['protected']])
        for role in ROLES:
            r=read(folder/(role+'.json'))
            assert r['source_id']==source_id and r['role']==role and not r['generated_fixture']
            assert not r['training_admitted'] and not r['model_ready']
            with np.load(folder/(role+'.npz'),allow_pickle=False) as pack:
                image=pack['input'];output=pack['output'] if 'output' in pack.files else None
            assert scalar.verify(source,r,image,output)
            if role=='identity':
                assert r['target']['parameters']==[1.,1.,1.] and r['target']['evaluations']==0
                np.testing.assert_array_equal(image,source['reference'])
                np.testing.assert_array_equal(output,source['reference'])
            elif r['target']['parameters'] is not None:
                assert np.isfinite(r['target']['parameters']).all()
                assert all(.25<=p<=4 for p in r['target']['parameters'])
                assert r['target']['converged'] and r['target']['jacobian_rank']==3
                close(r['target']['rgb8_mae_codes'],r['regions']['primary']['output']['RGB'])
                close(r['target']['input_rgb8_mae_codes'],r['regions']['primary']['input']['RGB'])
            records.append(r);checks+=1
        print(f'Independent replay {checks}/66',flush=True)
    assert len({(r['source_id'],r['role']) for r in records})==66
    summary=read(OUT/'cases/summary.json')
    for role in ROLES:
        own=[r for r in records if r['role']==role]
        paired=[r for r in own if r['regions']['primary']['output'] is not None]
        assert len(own)==summary[role]['attempted']==11
        assert len(paired)==summary[role]['available']
        for prefix in ['input','output','benefit']:
            for key in ['RGB','DE']:
                expected=math.fsum(r['regions']['primary'][prefix][key] for r in paired)/len(paired) if paired else None
                if expected is None:assert summary[role]['primary'][prefix][key] is None
                else:close(expected,summary[role]['primary'][prefix][key])
    status=read(OUT/'cases/status.json');assert status['completed_cases']==66 and status['status']=='complete'
    assert status['nonidentity_target_calls']==55
    accounted=read(OUT/'solver_accounting_PRIVATE.json')['actual_local_solver_calls_started']
    assert accounted==completed['actual_local_solver_calls']<=55
    assert accounted==sum(r['target'].get('evaluations',0)>0 for r in records)
    result=dict(passed=True,sources=11,scalar_case_replays=66,source_equal_summaries=6,
        actual_local_solver_calls=accounted,verifier_solver_calls=0,tree_fits=0,
        available_targets=sum(r['target']['parameters'] is not None for r in records),
        unavailable_targets=sum(r['target']['parameters'] is None for r in records),
        reference_controls_are_oracle_supervision=True,model_ready=False,
        official_tone_labels_or_fairness_established=False,locked_access=False,
        artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS:66scalar case replays and6source-equal summaries; no verifier fits.',flush=True)


if __name__=='__main__':main()
