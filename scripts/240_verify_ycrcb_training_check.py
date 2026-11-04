"""Verify prospective check selection, candidate identity and40frame replays."""
import hashlib
import importlib
import json
import re
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.ita_estimation.ycrcb_measurement import measure,contract
from src.distortion_generation.three_variant_recipe import render_rgb
from src.utilities.config import get_config


def main():
    out=ROOT/'outputs/ycrcb_training_check20_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');definition=read(out/'candidate_measurement_contract.json')
    assert contract(ROOT)[1]==plan['candidate_contract_sha256']==definition['sha256']
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    selected=plan['selected'];ids=[r['image_id'] for r in selected]
    original=read(ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json')['sources']
    reviewed={r['image_id'] for r in read(ROOT/'outputs/training_review36_import_v1/combined_original_mask_reviews60.json')}
    dispositions=read(ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json')
    groups={r['image_id']:r['duplicate_group'] for r in dispositions}
    blocked=reviewed|{r['image_id'] for r in original};blocked_groups={groups[i] for i in blocked}
    pool=[r for r in dispositions if r['role']=='train' and r['status']=='screen_clear_unreviewed' and r['image_id'] not in blocked and r['duplicate_group'] not in blocked_groups]
    expected=[];seen=set(blocked_groups)
    for r in sorted(pool,key=lambda r:(hashlib.sha256(('ycrcb_check20_extra8_v1/'+r['image_id']).encode()).hexdigest(),r['image_id'])):
        if r['duplicate_group'] in seen:continue
        expected.append(r['image_id']);seen.add(r['duplicate_group'])
        if len(expected)==8:break
    assert ids==[r['image_id'] for r in original]+expected
    assert len(ids)==len(set(ids))==len({groups[i] for i in ids})==20 and not set(ids)&reviewed
    rows=[json.loads(x) for x in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    access=[json.loads(x) for x in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in rows]==[r['image_id'] for r in access]==ids
    assert read(out/'development_replay.json')['exact_reviewed_mask_parity']==40
    prepare=importlib.import_module('11_prepare_training_manifests');config=get_config()
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    landmarks=lambda im,box:prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)[0]
    count=0
    for row in rows:
        name=row['source_id'];reference=cv2.imread(str(out/'images'/f'{name}_reference.png'))
        assert digest(out/'images'/f'{name}_reference.png')==row['reference_sha256']
        shifted,clipping=render_rgb(cv2.cvtColor(reference,cv2.COLOR_BGR2RGB),'medium','color')
        color=cv2.imread(str(out/'images'/f'{name}_color.png'))
        np.testing.assert_array_equal(cv2.cvtColor(color,cv2.COLOR_BGR2RGB),shifted)
        assert clipping==row['color_probe_clipping']
        for frame,image in [('reference',reference),('color',color)]:
            replay=measure(image,detector,landmarks)
            assert replay.report==row['frames'][frame]['candidate']
            path=out/'images'/f'{name}_{frame}_candidate_mask.png'
            if replay.mask is None:assert not path.exists()
            else:np.testing.assert_array_equal(cv2.imread(str(path),0),replay.mask)
            count+=1
        assert row['human_decision']=='pending' and not row['training_eligible']
    page=(out/'review.html').read_text(encoding='utf-8')
    spec=json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>',page,re.S)[1])
    assert [r['image_id'] for r in spec['records']]==ids and len(spec['panel_labels'])==6
    assert spec['manifest_sha256']==digest(out/'plan.json')
    target.write_text(json.dumps(dict(status='pass',prospectively_selected_sources=20,candidate_frame_replays=count,
        original_reserved12_preserved=True,prior_development_sources_excluded=60,review_scope_verified=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:20prospective IDs,original reserved12,40candidate frame replays and review data verified.')


if __name__=='__main__':main()
