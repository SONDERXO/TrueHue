"""Verify training-only accounting and saved pixels/features without tree fitting."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.data_preparation.redesign_access import training_candidate
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.distortion_generation.table2_composite import composite_rgb
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup


def main():
    out=ROOT/'outputs/correction_training_preparation_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    summary=read(out/'summary.json');plan=read(out/'plan.json')
    assert summary['status']==read(out/'run_status.json')['status']=='complete_pending_review'
    frozen=ROOT/'outputs/correction_data_redesign_v1'
    selection,policy=read(frozen/'selection.json'),read(frozen/'access_policy.json')
    audit=ROOT/'outputs/correction_duplicate_audit_v1'
    dispositions={r['image_id']:r for r in read(audit/'candidate_dispositions.json')}
    queue=read(audit/'verified_training_queue.json')
    expected=[i for b in queue['batches'] for i in b['image_ids']]
    rows=[json.loads(line) for line in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    access=[json.loads(line) for line in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in rows]==[r['image_id'] for r in access]==expected
    assert len(expected)==len(set(expected))==418
    assert all(r['role']=='train' for r in access)
    assert summary['statuses']==dict(Counter(r['status'] for r in rows))
    assert summary['correction_models_fitted']==summary['training_admitted']==0
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    assert contract(ROOT)[1]==plan['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),plan['measurement_contract_sha256'])
    features_checked=0;composites_checked=0
    for r in rows:
        allowed=training_candidate(r['image_id'],selection,policy)
        assert dispositions[r['image_id']]['status']=='screen_clear_unreviewed'
        assert r['training_batch']==allowed['training_batch']
        assert r['training_eligible'] is False and r['user_decision']=='pending'
        assert digest(ROOT/r['source_path'])==r['source_sha256']
        name=r['source_id']
        assert (out/'boards'/f'{name}.png').is_file()
        for kind,key in [('reference','reference_measurement'),('input','input_measurement')]:
            measurement=r.get(key)
            if not measurement or measurement['status']!='success':continue
            image=cv2.imread(str(out/'images'/f'{name}_{kind}.png'))
            mask=cv2.imread(str(out/'images'/f'{name}_{kind}_mask.png'),0)
            assert image.shape==(256,256,3) and mask.shape==(256,256)
            assert set(np.unique(mask))<={0,255}
            stats=compute_masked_lab_statistics(image,mask,1000)
            assert stats['valid']
            for feature,key2 in zip(FEATURES,FEATURE_KEYS):
                assert float(stats[key2])==measurement['features'][feature]
            features_checked+=1
        if 'assigned_severity' in r:
            rgb=cv2.cvtColor(cv2.imread(str(out/'images'/f'{name}_reference.png')),cv2.COLOR_BGR2RGB)
            support=cv2.imread(str(out/'images'/f'{name}_reference_mask.png'),0)>0
            transformed,_=composite_rgb(rgb,r['assigned_severity']);expected_rgb=rgb.copy()
            expected_rgb[support]=transformed[support]
            actual=cv2.cvtColor(cv2.imread(str(out/'images'/f'{name}_input.png')),cv2.COLOR_BGR2RGB)
            np.testing.assert_array_equal(expected_rgb,actual)
            assert r['identity_target']==[1,1,1]
            assert r['official_mst_label'] is None
            assert r['reference_mst_estimate']==lookup.label(r['reference_measurement']['features']['input_ita_degrees'])
            if 'input_features' in r:
                assert r['input_features']['input_mst_index']==lookup.label(r['input_measurement']['features']['input_ita_degrees'])-1
            composites_checked+=1
    evidence={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}
    target.write_text(json.dumps(dict(status='pass',training_attempts_verified=len(rows),
        saved_measurements_recomputed=features_checked,table2_composites_reconstructed=composites_checked,
        validation_test_preparation_attempts=0,training_admitted=0,correction_models_fitted=0,
        evidence_sha256=evidence),indent=2),encoding='utf-8')
    print(f'PASS: {len(rows)} training attempts; {features_checked} saved measurements; {composites_checked} composites.')


if __name__=='__main__':main()
