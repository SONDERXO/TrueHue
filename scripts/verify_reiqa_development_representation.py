"""Independent scalar saved-feature retrieval replay. No torch or image loading."""
from pathlib import Path
import hashlib
import json
import math
import statistics
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reiqa_development_representation_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    target=OUT/'independent_verification_PRIVATE.json'
    if target.exists():raise FileExistsError(target)
    plan=read(OUT/'execution_plan_PRIVATE.json');done=read(OUT/'completion_PRIVATE.json')
    assert done['vectors']==66 and done['finite_values']==270336
    assert sha(OUT/'features.npz')==done['feature_sha256']
    assert sha(OUT/'summary_PRIVATE.json')==done['summary_sha256']
    assert read(OUT/'before_real_decode_PRIVATE.json')['all66input_hashes_verified']
    assert read(OUT/'before_real_decode_PRIVATE.json')['generated_parities_exact']==6
    assert read(OUT/'all_identities_repeated_PRIVATE.json')==dict(exact=11,nonidentity_decodes=0)
    rows=plan['rows'];logged=read(OUT/'array_access_PRIVATE.json')
    assert len(logged)==66 and len({r['case_id'] for r in logged})==66
    assert all(r['keys']==['input'] for r in logged)
    lookup={r['case_id']:r for r in rows}
    assert all(r['path']==lookup[r['case_id']]['input_pack'] for r in logged)
    assert all(lookup[r['case_id']]['role']=='identity' for r in logged[:11])
    with np.load(OUT/'features.npz',allow_pickle=False) as pack:
        assert pack.files==[r['case_id'] for r in rows]
        vectors=[]
        for r in rows:
            value=pack[r['case_id']]
            assert value.shape==(4096,) and value.dtype==np.float32
            vector=value.tolist();assert all(math.isfinite(v) for v in vector)
            vectors.append(vector)
    distances=[[0.]*66 for _ in rows]
    for i in range(66):
        for j in range(i+1,66):
            value=math.sqrt(math.fsum((a-b)**2 for a,b in zip(vectors[i],vectors[j])))
            distances[i][j]=distances[j][i]=value
    saved=read(OUT/'retrieval_PRIVATE.json');family=plan['family'];nearest_any_count=0
    for i,(row,result) in enumerate(zip(rows,saved)):
        assert result['case_id']==row['case_id']
        available=[j for j in range(66) if rows[j]['source_id']!=row['source_id']]
        assert len(available)==60
        nearest=min(available,key=lambda j:(distances[i][j],rows[j]['case_id']))
        assert result['nearest_other_source_case']==rows[nearest]['case_id']
        assert result['nearest_other_source_role']==rows[nearest]['role']
        assert result['nearest_other_source_family']==family[rows[nearest]['role']]
        assert math.isclose(result['distance'],distances[i][nearest],rel_tol=1e-12,abs_tol=1e-12)
        anywhere=min([j for j in range(66) if i!=j],key=lambda j:(distances[i][j],rows[j]['case_id']))
        assert result['nearest_any_case']==rows[anywhere]['case_id']
        nearest_any_count+=rows[anywhere]['source_id']==row['source_id']
    summary=read(OUT/'summary_PRIVATE.json')
    assert summary['nearest_any_same_source']==nearest_any_count
    assert summary['nearest_other_source_role_matches']==sum(r['role']==r['nearest_other_source_role'] for r in saved)
    assert summary['nearest_other_source_family_matches']==sum(r['family']==r['nearest_other_source_family'] for r in saved)
    identities={r['source_id']:i for i,r in enumerate(rows) if r['role']=='identity'}
    for role,data in summary['by_role'].items():
        changes=[distances[i][identities[r['source_id']]] for i,r in enumerate(rows) if r['role']==role]
        assert len(changes)==11
        assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(changes,data['change_from_own_identity']))
        assert math.isclose(statistics.median(changes),data['median_change'],rel_tol=1e-12,abs_tol=1e-12)
        assert data['role_matches']==sum(r['role']==r['nearest_other_source_role'] for r in saved if r['role']==role)
        assert data['family_matches']==sum(r['family']==r['nearest_other_source_family'] for r in saved if r['role']==role)
    across=[distances[i][j] for i in identities.values() for j in identities.values() if i<j]
    assert len(across)==55
    assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(across,summary['identity_cross_source_distances']))
    assert math.isclose(statistics.median(across),summary['median_identity_cross_source_distance'],rel_tol=1e-12,abs_tol=1e-12)
    for p,h in plan['input_sha256'].items():assert sha(ROOT/p)==h
    result=dict(passed=True,finite_values=270336,scalar_pair_distances=2145,source_excluded_retrievals=66,
                correction_fits=0,real_pixel_redecodes=0,verifier_sha256=sha(Path(__file__)))
    target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
