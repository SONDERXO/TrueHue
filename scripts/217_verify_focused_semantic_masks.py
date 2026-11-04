"""Reconstruct candidate masks from saved categories and verify provenance."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.focused_semantic_mask import semantic_supports


def main():
    out=ROOT/'outputs/focused_semantic_mask_comparison_v1'
    target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    rows=[json.loads(line) for line in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    access=[json.loads(line) for line in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in rows]==[r['image_id'] for r in access]==plan['selected_ids']
    assert len(rows)==len({r['image_id'] for r in rows})==24
    parent=ROOT/'outputs/correction_training_preparation_v1'
    priors={r['image_id']:r for r in (json.loads(line) for line in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    reconstructed=0
    for r in rows:
        name=r['source_id'];ref=priors[r['image_id']]['reference_measurement']
        mask_path=parent/'images'/f'{name}_reference_mask.png'
        baseline=cv2.imread(str(mask_path),0) if mask_path.exists() else np.zeros((256,256),np.uint8)
        removal=cv2.imread(str(out/'masks'/f'{name}_removal.png'),0)
        candidate=cv2.imread(str(out/'masks'/f'{name}_candidate.png'),0)
        assert removal.shape==candidate.shape==(256,256)
        assert not np.any((removal>0)&(baseline==0))
        if r['parser_supports_available']:
            cats=cv2.imread(str(out/'categories'/f'{name}.png'),0)
            expected=semantic_supports(cats,baseline,[ref['face_box']])
            np.testing.assert_array_equal(removal,expected[0]);np.testing.assert_array_equal(candidate,expected[1])
            reconstructed+=1
        else:
            assert not candidate.any() and not removal.any()
        assert r['candidate_pixels']==int(np.count_nonzero(candidate))
        assert r['added_pixels']==int(np.count_nonzero((candidate>0)&(baseline==0)))
        assert r['removed_pixels']==int(np.count_nonzero((baseline>0)&(candidate==0)))
        assert r['training_eligible'] is False
        assert (out/'boards'/f'{name}.png').exists()
    summary=read(out/'summary.json')
    assert summary['reserved_training_check_attempts']==summary['correction_models_fitted']==summary['candidate_ita_mst_calls']==0
    assert summary['existing_mst_lookup_applicable'] is False
    target.write_text(json.dumps(dict(status='pass',reviewed_sources=24,reconstructed_parser_masks=reconstructed,
        input_hashes_unchanged=True,no_reserved_check_access=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(f'PASS: 24 accounted attempts; {reconstructed} candidate masks reconstructed; unchanged baseline and reserved manifests.')


if __name__=='__main__':main()
