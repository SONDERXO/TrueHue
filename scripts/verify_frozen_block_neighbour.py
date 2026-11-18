"""Independent actual-record joins and scalar prediction replay; no fit imports."""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation.frozen_block_neighbour_pixel_verification import verify_run

OUT=ROOT/'outputs/frozen_block_neighbour_prediction_v1'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    bindings=read(OUT/'adapter_bindings_PRIVATE.json')
    for p,h in bindings['input_sha256'].items():assert sha(ROOT/p)==h
    for p,h in bindings['cached_input_hashes'].items():assert sha(p)==h
    plan=read(OUT/'execution_plan.json');rows=read(OUT/'prepared_rows.json')
    prepared=read(ROOT/'outputs/five_control_real_feature_preparation_v1/rows_PRIVATE.json')
    with np.load(ROOT/'outputs/reiqa_development_representation_v1/features.npz',allow_pickle=False) as features:
        for r in prepared:r['x']=r['x']+features[r['case_id']].tolist()
    assert rows==prepared and plan['generated_fixture'] is False and len(rows)==66
    assert len(plan['feature_names'])==4377 and all(len(r['x'])==4377 for r in rows)
    declared={r['case_id']:r for r in plan['rows']};support={}
    for row in rows:
        d=declared[row['case_id']];assert not row['generated_fixture'] and row['y']==d['y']
        source=row['source_id']
        if source not in support:
            with np.load(ROOT/d['cached_support_pack'],allow_pickle=False) as pack:
                support[source]={k:pack[k] for k in ['reference','alpha','protected']}
        with np.load(ROOT/d['input_pack'],allow_pickle=False) as pack:image=pack['input']
        with np.load(OUT/'evaluation'/(row['case_id']+'.npz'),allow_pickle=False) as pack:
            np.testing.assert_array_equal(pack['input'],image)
            for key,value in support[source].items():np.testing.assert_array_equal(pack[key],value)
    result=verify_run(OUT)
    assert read(OUT/'models/index_accounting.json')['started']==11
    assert read(OUT/'complete.json')['real_index_constructions']==11
    for p,h in bindings['cached_input_hashes'].items():assert sha(p)==h
    result.update(real_index_constructions=11,tree_fits=0,feature_recomputations=0,target_refits=0,
        oracle_or_reference_in_inference=False,locked_access=False,
        artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS: real660fitting/66held routes/132renders; frozen status='+result['numeric_status'],flush=True)


if __name__=='__main__':main()
