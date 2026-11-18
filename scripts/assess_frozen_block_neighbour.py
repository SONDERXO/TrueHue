"""Compare the one fixed neighbour candidate to both preserved tree runs."""
from pathlib import Path
import sys,json,collections
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
RUN=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
OUT=ROOT/'outputs/frozen_block_neighbour_assessment_v1'
BASES={'saved281':ROOT/'outputs/five_control_source_held_prediction_v1',
       'added4377tree':ROOT/'outputs/reiqa_added_feature_prediction_v1'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    if OUT.exists():raise FileExistsError(OUT)
    proof=read(RUN/'verification_PRIVATE.json');assert proof['passed']
    proofs={k:read(v/'verification_PRIVATE.json') for k,v in BASES.items()}
    for p in [proof,*proofs.values()]:
        assert p['passed'];p['artifact_sha256']={Path(k).as_posix():v for k,v in p['artifact_sha256'].items()}
    predictions=read(RUN/'models/held_controls_sealed.json');summary=read(RUN/'evaluation/summary.json')
    assert sha(RUN/'evaluation/summary.json')==proof['artifact_sha256']['evaluation/summary.json']
    cert=read(RUN/'models/all_indices_verified.json');indices={m['held_source_id']:read(m['index_path']) for m in cert['models']}
    matched=[];families={'identity':'no_exposure','colour_only':'no_exposure','exposure_under':'under','combined_under':'under','exposure_over':'over','combined_over':'over'}
    for p in predictions:
        relative='evaluation/'+p['case_id']+'.json'
        assert sha(RUN/relative)==proof['artifact_sha256'][relative]
        record=read(RUN/relative)
        older={}
        for label,root in BASES.items():
            assert sha(root/relative)==proofs[label]['artifact_sha256'][relative]
            old=read(root/relative)
            assert all(old[k]==record[k] for k in ['case_id','source_id','role','oracle_controls','generated_fixture'])
            assert old['regions']['primary']['input']==record['regions']['primary']['input']
            assert old['regions']['primary']['constant']==record['regions']['primary']['constant']
            older[label]=old['regions']['primary']['tree']
        neighbour=next(r for r in indices[p['source_id']]['rows'] if r['case_id']==p['neighbour_case_id'])
        assert neighbour['source_id']!=p['source_id'] and neighbour['y']==p['controls']
        matched.append(dict(case_id=p['case_id'],source_id=p['source_id'],role=p['role'],
            neighbour_case_id=p['neighbour_case_id'],neighbour_role=neighbour['role'],
            input=record['regions']['primary']['input'],candidate=record['regions']['primary']['tree'],
            **older,controls=p['controls'],oracle_controls=record['oracle_controls'],
            whole_identity_RGB_change=record['identity_mean_RGB_change']))
    result=dict(status=summary['status'],numeric_role_checks=summary['numeric_role_checks'],matched_cases=66,
        broad_family_matches=sum(families[r['role']]==families[r['neighbour_role']] for r in matched),
        role_matches=sum(r['role']==r['neighbour_role'] for r in matched),
        by_role={role:dict(**data,neighbour_roles=dict(collections.Counter(r['neighbour_role'] for r in matched if r['role']==role))) for role,data in summary['by_role'].items()},
        fit_block_energies={s:i['block_energy'] for s,i in indices.items()},
        index_constructions=11,tree_fits=0,new_target_fits=0,feature_recomputations=0,
        human_acceptability='not_assessed',model_ready=False,
        disposition='PREPARE_IDENTITY_REVIEW_NOT_ADOPTED' if summary['status']=='NUMERIC_PREDICTION_ELIGIBLE_ONLY' else 'FIXED_CANDIDATE_CLOSED_NOT_ADOPTED',
        evidence_hashes={str(p.relative_to(ROOT)):sha(p) for p in [RUN/'verification_PRIVATE.json',Path(__file__)]})
    OUT.mkdir()
    for name,data in [('matched_cases_PRIVATE.json',matched),('assessment_PRIVATE.json',result)]:
        (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['by_role','fit_block_energies','evidence_hashes']},indent=2))
if __name__=='__main__':main()
