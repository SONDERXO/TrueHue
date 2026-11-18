"""Independent real feature arithmetic and binding replay; never trains a model."""
from pathlib import Path
import sys
import json
import hashlib
import math
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation.five_control_feature_scalar import features

OUT=ROOT/'outputs/five_control_real_feature_preparation_v1'


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');plan=execution['plan'];status=read(OUT/'status_PRIVATE.json')
    for p,h in execution['input_sha256'].items():assert sha(ROOT/p)==h
    assert status['tree_fits']==status['target_fits']==status['predictions']==0
    access=read(OUT/'array_access_PRIVATE.json')
    assert all(r['key'] in ['input','alpha','protected','measurement_png'] for r in access)
    assert not any(r['key'] in ['reference','output'] for r in access)
    inputs=[a for a in access if a['key']=='input']
    identity_inputs=[a for a in inputs if a['role']=='identity']
    nonidentity_inputs=[a for a in inputs if a['role']!='identity']
    assert all(a['role']=='identity' for a in inputs[:len(identity_inputs)])
    if status['status']=='BLOCKED_IDENTITY_FEATURE_PARITY':
        assert not nonidentity_inputs and status['nonidentity_vectors']==0
        failed=read(OUT/'identity_failure_PRIVATE.json')
        assert failed['x']!=failed['expected'] and failed['differences']
        rows=read(OUT/'partial_rows_PRIVATE.json') if (OUT/'partial_rows_PRIVATE.json').exists() else []
        rows=rows+[failed]
    else:
        assert status['status']=='PREPARED_PENDING_INDEPENDENT_VERIFICATION'
        rows=read(OUT/'rows_PRIVATE.json');assert len(rows)==66
        assert len(identity_inputs)==11 and len(nonidentity_inputs)==55
    mapping=read(ROOT/plan['mapper_path']);source={s['source_id']:s for s in plan['feature_sources']}
    declarations={r['case_id']:r for r in plan['rows']};checks=0;maximum=0.
    for row in rows:
        bound=declarations[row['case_id']]
        assert row['y']==bound['y'] and row['generated_fixture'] is False and not row['parent_training_admitted']
        path=ROOT/bound['input_pack'];assert sha(path)==bound['input_pack_sha256']
        with np.load(path,allow_pickle=False) as pack:image=pack['input']
        mask_path=ROOT/source[row['source_id']]['measurement_path']
        assert sha(mask_path)==source[row['source_id']]['measurement_sha256']
        mask=cv2.imread(str(mask_path),0)
        independent=features(image,mask,mapping,plan['feature_names'])
        for a,b in zip(row['x'],independent):
            maximum=max(maximum,abs(a-b));assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7),(row['case_id'],a,b)
        if row['role']=='identity' and not (status['status']=='BLOCKED_IDENTITY_FEATURE_PARITY' and row['case_id']==failed['case_id']):
            assert row['x']==source[row['source_id']]['identity_saved_feature_vector']
        checks+=281
        print(f'Independent feature replay {checks//281}/{len(rows)}',flush=True)
    assert all(sha(ROOT/p)==h for p,h in execution['input_sha256'].items())
    result=dict(passed=True,scope='independent_feature_preparation_verification_not_training',
        preparation_status=status['status'],independent_vectors=len(rows),scalar_feature_values=checks,
        independent_max_absolute_float32_difference=maximum,identity_parity_tolerance='exact_no_relaxation',
        independent_scalar_arithmetic_tolerance='abs/rel1e-7_not_an_identity_parity_threshold',
        identity_inputs_decoded=len(identity_inputs),nonidentity_inputs_decoded=len(nonidentity_inputs),
        tree_fits=0,target_fits=0,predictions=0,locked_access=False,
        artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Verified feature preparation status='+status['status']+'; no fits.',flush=True)


if __name__=='__main__':main()
