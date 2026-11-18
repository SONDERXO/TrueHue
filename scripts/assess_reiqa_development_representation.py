"""Prospective input-only66case representation assessment; no correction fitting."""
from pathlib import Path
import json
import sys
import time
import platform
import statistics
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha,FrozenQualityEncoder,generated_inputs

DESIGN=ROOT/'outputs/reiqa_development_representation_design_v1'
OUT=ROOT/'outputs/reiqa_development_representation_v1'
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
FAMILY={r:('no_exposure' if r in ['identity','colour_only'] else 'under' if r.endswith('under') else 'over') for r in ROLES}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def describe(rows,vectors):
    matrix=np.asarray(vectors,dtype=np.float64)
    distances=np.sqrt(np.maximum(0,((matrix[:,None,:]-matrix[None,:,:])**2).sum(axis=2)))
    retrieval=[]
    for i,r in enumerate(rows):
        candidates=[j for j,s in enumerate(rows) if s['source_id']!=r['source_id']]
        nearest=min(candidates,key=lambda j:(float(distances[i,j]),rows[j]['case_id']))
        own=[j for j,s in enumerate(rows) if j!=i and s['source_id']==r['source_id']]
        anywhere=min([j for j in range(len(rows)) if j!=i],key=lambda j:(float(distances[i,j]),rows[j]['case_id']))
        retrieval.append(dict(case_id=r['case_id'],role=r['role'],family=FAMILY[r['role']],
            nearest_other_source_case=rows[nearest]['case_id'],nearest_other_source_role=rows[nearest]['role'],
            nearest_other_source_family=FAMILY[rows[nearest]['role']],distance=float(distances[i,nearest]),
            nearest_any_case=rows[anywhere]['case_id'],nearest_any_same_source=rows[anywhere]['source_id']==r['source_id']))
    identities={r['source_id']:i for i,r in enumerate(rows) if r['role']=='identity'}
    changes={role:[float(distances[i,identities[r['source_id']]]) for i,r in enumerate(rows) if r['role']==role] for role in ROLES}
    identity_distances=[float(distances[i,j]) for i in identities.values() for j in identities.values() if i<j]
    summary=dict(rows=66,coordinates=4096,
        nearest_other_source_role_matches=sum(r['role']==r['nearest_other_source_role'] for r in retrieval),
        nearest_other_source_family_matches=sum(r['family']==r['nearest_other_source_family'] for r in retrieval),
        nearest_any_same_source=sum(r['nearest_any_same_source'] for r in retrieval),
        by_role={role:dict(cases=11,role_matches=sum(r['role']==r['nearest_other_source_role'] for r in retrieval if r['role']==role),
            family_matches=sum(r['family']==r['nearest_other_source_family'] for r in retrieval if r['role']==role),
            change_from_own_identity=changes[role],median_change=statistics.median(changes[role])) for role in ROLES},
        identity_cross_source_distances=identity_distances,median_identity_cross_source_distance=statistics.median(identity_distances),
        interpretation='descriptive retrieval only; no correction controls, targets, feature selection or classification training',
        ready_for_correction_fit=False)
    return retrieval,summary

def design():
    DESIGN.mkdir(exist_ok=False)
    parent=ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    full=read(parent);checked=read(parent.parent/'verification_PRIVATE.json')
    assert checked['passed'] and checked['plan_sha256']==sha(parent)
    rows=[{k:r[k] for k in ['case_id','source_id','role','input_pack','input_pack_sha256']} for r in full['rows']]
    assert len(rows)==66 and len({r['source_id'] for r in rows})==11
    assert {(r['source_id'],r['role']) for r in rows}=={(s,r) for s in {r['source_id'] for r in rows} for r in ROLES}
    for r in rows:
        p=(ROOT/r['input_pack']).resolve()
        assert p.is_relative_to(ROOT/'outputs/ffhq_directional_recoverability_v1/cases')
    paths=['scripts/assess_reiqa_development_representation.py','scripts/verify_reiqa_development_representation.py',
           'src/model_training/reiqa_frozen_features.py','docs/reiqa-development-representation-protocol-2026-11-15.md',
           'outputs/reiqa_frozen_generated_v1/verification_PRIVATE.json',
           'outputs/reiqa_frozen_generated_v1/independent_verification_PRIVATE.json',
           'outputs/reiqa_frozen_generated_v1/generated_features.npz']
    plan=dict(rows=rows,dimensions=4096,planned_extractions=77,identity_repeat=11,nonidentity=55,
              family=FAMILY,nearest='raw Euclidean4096; exclude same source before all60candidate distance comparisons; lexical case_id tie',
              input_sha256={p:sha(ROOT/p) for p in paths},parent_plan_sha256=sha(parent),
              whole_input_containers_hashed=True,decoded_keys=['input'],targets_references_read=False,
              feature_selection=False,correction_fits=0,model_ready=False)
    write(DESIGN/'plan_PRIVATE.json',plan)
    write(DESIGN/'verification_PRIVATE.json',dict(passed=True,rows=66,sources=11,plan_sha256=sha(DESIGN/'plan_PRIVATE.json')))
    print('Fixed66input-only design; no pixel decode.',flush=True)

def run():
    OUT.mkdir(exist_ok=False)
    accesses=[];records=[]
    try:
        plan=read(DESIGN/'plan_PRIVATE.json')
        assert read(DESIGN/'verification_PRIVATE.json')['plan_sha256']==sha(DESIGN/'plan_PRIVATE.json')
        for p,h in plan['input_sha256'].items():assert sha(ROOT/p)==h,p
        for r in plan['rows']:assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
        write(OUT/'execution_plan_PRIVATE.json',plan)
        qa=read(ROOT/'outputs/reiqa_frozen_generated_v1/verification_PRIVATE.json')
        assert qa['status']=='GENERATED_MECHANICS_PASS_ONLY'
        import torch,torchvision,PIL
        versions=dict(torch=torch.__version__,torchvision=torchvision.__version__,numpy=np.__version__,pillow=PIL.__version__)
        assert versions==qa['versions'] and platform.python_version()==qa['python']
        model=FrozenQualityEncoder(ROOT)
        with np.load(ROOT/'outputs/reiqa_frozen_generated_v1/generated_features.npz',allow_pickle=False) as saved:
            for name,image in generated_inputs():assert np.array_equal(model.encode(image),saved[name].reshape(-1)),name
        write(OUT/'before_real_decode_PRIVATE.json',dict(all66input_hashes_verified=True,generated_parities_exact=6,versions=versions))
        rows=plan['rows'];vectors={};times={}
        for identity_stage in [True,False]:
            for r in rows:
                if (r['role']=='identity')!=identity_stage:continue
                # ONLY this key; no other cached array/reference/support is accessed.
                with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:image=pack['input'].copy()
                accesses.append(dict(case_id=r['case_id'],path=r['input_pack'],keys=['input']))
                start=time.perf_counter();vector=model.encode(image);times[r['case_id']]=time.perf_counter()-start
                if identity_stage:assert np.array_equal(vector,model.encode(image)),r['case_id']
                vectors[r['case_id']]=vector
                write(OUT/'progress_PRIVATE.json',dict(completed=len(vectors),identity_repeats=min(11,len(vectors)),correction_fits=0))
                if len(vectors)%11==0:print(f'Frozen input vectors {len(vectors)}/66',flush=True)
            if identity_stage:write(OUT/'all_identities_repeated_PRIVATE.json',dict(exact=11,nonidentity_decodes=0))
        model.verify_unchanged()
        arrays=[vectors[r['case_id']] for r in rows]
        np.savez(OUT/'features.npz',**{r['case_id']:vectors[r['case_id']] for r in rows})
        metadata=[dict(r,extraction_seconds=times[r['case_id']]) for r in rows]
        retrieval,summary=describe(rows,arrays)
        write(OUT/'rows_PRIVATE.json',metadata);write(OUT/'retrieval_PRIVATE.json',retrieval);write(OUT/'summary_PRIVATE.json',summary)
        for r in rows:assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
        for p,h in plan['input_sha256'].items():assert sha(ROOT/p)==h
        write(OUT/'completion_PRIVATE.json',dict(status='INPUT_ONLY_REPRESENTATION_COMPLETE_NOT_CORRECTION_QUALIFICATION',
            vectors=66,finite_values=270336,identity_repeats_exact=11,generated_parities_exact=6,
            encoder_unchanged=True,correction_fits=0,targets_references_decoded=0,
            feature_sha256=sha(OUT/'features.npz'),summary_sha256=sha(OUT/'summary_PRIVATE.json')))
        print(json.dumps({k:v for k,v in summary.items() if k not in ['by_role','identity_cross_source_distances']},indent=2))
    except Exception as e:
        write(OUT/'failure_PRIVATE.json',dict(error_type=type(e).__name__,error=str(e),correction_fits=0));raise
    finally:write(OUT/'array_access_PRIVATE.json',accesses)

if __name__=='__main__':
    {'--design':design,'--run-input-only':run}[sys.argv[1]]()
