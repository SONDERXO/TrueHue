"""Independent cached-array comparison replay. No optimizer or target fitter imports."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation import affine_capacity_verification as independent

OUT=ROOT/'outputs/affine_capacity_comparison_v1'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');done=read(OUT/'execution_complete_PRIVATE.json')
    assert not execution['generated_fixture'] and done['records']==66 and done['actual_local_solver_calls']<=55
    for p,h in execution['input_sha256'].items():assert sha(ROOT/p)==h
    base=Path(execution['baseline_root']);parent=read(base/'verification_PRIVATE.json')
    for p,h in parent['artifact_sha256'].items():assert sha(base/p)==h
    records=[]
    for source_id in execution['source_ids']:
        folder=base/execution['relative_run']/source_id
        with np.load(folder/'support.npz',allow_pickle=False) as pack:
            support={k:pack[k] for k in ['reference','alpha','protected']}
        for role in independent.ROLES:
            old=read(folder/(role+'.json'))
            with np.load(folder/(role+'.npz'),allow_pickle=False) as pack:
                image=pack['input'];old_output=pack['output']
            case=dict(source_id=source_id,role=role,image=image,baseline_output=old_output,
                baseline=old,generated_fixture=False,**support)
            current=OUT/'candidate'/source_id
            record=read(current/(role+'.json'))
            with np.load(current/(role+'.npz'),allow_pickle=False) as pack:
                output=pack['output'] if 'output' in pack.files else None
            assert independent.verify_case(case,record,output)
            records.append(record)
        print(f'Independent matched replay {len(records)}/66',flush=True)
    assert len(records)==len({(r['source_id'],r['role']) for r in records})==66
    summary=read(OUT/'candidate/summary.json');assert independent.verify_summary(records,summary)
    assert done['actual_local_solver_calls']==sum(r['target'].get('evaluations',0)>0 for r in records)
    assert read(OUT/'solver_accounting_PRIVATE.json')['local_solver_calls_started']==done['actual_local_solver_calls']
    report=dict(passed=True,records=66,independent_matched_case_replays=66,
        independent_source_equal_summaries=6,actual_local_solver_calls=done['actual_local_solver_calls'],
        new_baseline_fits=0,verifier_fits=0,tree_fits=0,capacity_status=summary['status'],model_ready=False,
        locked_access=False,artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:66independent matched replays; capacity status='+summary['status'],flush=True)


if __name__=='__main__':main()
