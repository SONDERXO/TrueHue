"""Fixed two-case reference-aware LOCAL diagnostic, never predictor training."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.luminance_chroma_operator import fit_target,render_rgb8
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/luminance_chroma_two_case_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def load_bound(root,rows,access):
    root=Path(root)
    for r in rows:assert sha(root/r['pack'])==r['sha256']
    result=[]
    for r in rows:
        with np.load(root/r['pack'],allow_pickle=False) as pack:arrays={k:pack[k].copy() for k in ['input','reference','alpha','protected']}
        access.append(dict(case_id=r['case_id'],path=r['pack'],keys=['input','reference','alpha','protected']))
        if arrays['input'].shape!=arrays['reference'].shape or arrays['input'].dtype!=np.uint8 or arrays['reference'].dtype!=np.uint8:raise ValueError('MatchedRGB8 required')
        result.append(dict(r,**arrays))
    return result
def main():
    if sys.argv[1:]!=['--execute-two-local-diagnostics']:raise SystemExit('Explicit two-local-diagnostics switch required')
    if OUT.exists():raise FileExistsError(OUT)
    qa_path=ROOT/'outputs/luminance_chroma_generated_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['generated_solver_calls']==2 and qa['loader_hash_barrier_poison_pass']
    for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h
    for p,h in qa['artifact_sha256'].items():assert sha(qa_path.parent/p)==h
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-image']})
    assert versions==qa['versions']
    run=ROOT/'outputs/frozen_block_neighbour_prediction_v1';verified=read(run/'verification_PRIVATE.json')
    assert verified['passed'];hashes={Path(k).as_posix():v for k,v in verified['artifact_sha256'].items()};rows=[]
    for source,role in [('29617','exposure_under'),('32685','exposure_over')]:
        case_id=f'five_prediction_ffhq_{source}__{role}';relative='evaluation/'+case_id+'.npz'
        rows.append(dict(case_id=case_id,source_id=source,role=role,pack=str((run/relative).relative_to(ROOT)),sha256=hashes[relative],generated_fixture=False))
    bindings=dict(qa['input_sha256']);bindings[str(qa_path.relative_to(ROOT))]=sha(qa_path)
    bindings[str((run/'verification_PRIVATE.json').relative_to(ROOT))]=sha(run/'verification_PRIVATE.json')
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(rows=rows,input_sha256=bindings,versions=versions,
        maximum_local_solver_calls=2,predictor_fits=0,scope='reference_aware_operator_feasibility_only',whole_cached_containers_hashed=True))
    access=[];count=0
    try:
        cases=load_bound(ROOT,rows,access)
        write(OUT/'all_inputs_hashed_loaded_PRIVATE.json',dict(passed=True,cases=2,solver_calls=0))
        for c in cases:
            if count>=2:raise RuntimeError('Two-local-fit budget exhausted')
            count+=1;write(OUT/'solver_accounting_PRIVATE.json',dict(calls_started=count,maximum=2,predictor_fits=0))
            fitted=fit_target(c['input'],c['reference'],c['alpha'],c['protected'])
            write(OUT/(c['case_id']+'.json'),{k:c[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(target=fitted))
            if fitted['status']!='available_local_diagnostic':raise RuntimeError('Unqualified local target; no fallback')
            output=render_rgb8(c['input'],c['alpha'],c['protected'],fitted['parameters'])
            np.savez(OUT/(c['case_id']+'.npz'),**{k:c[k] for k in ['input','reference','alpha','protected']},output=output)
            print(c['case_id']+' local diagnostic saved',flush=True)
        for r in rows:assert sha(ROOT/r['pack'])==r['sha256']
        for p,h in bindings.items():assert sha(ROOT/p)==h
        write(OUT/'completion_PRIVATE.json',dict(status='TWO_LOCAL_TARGETS_PENDING_SCALAR_VERIFICATION_NOT_MODEL',local_solver_calls=count,predictor_fits=0))
    except Exception as e:
        write(OUT/'failure_PRIVATE.json',dict(error_type=type(e).__name__,error=str(e),local_calls_started=count));raise
    finally:write(OUT/'array_access_PRIVATE.json',access)
if __name__=='__main__':main()
