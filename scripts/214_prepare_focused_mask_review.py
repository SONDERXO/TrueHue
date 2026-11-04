"""Create one reproducible 24-source reference-only diagnostic review."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate


def main():
    source=ROOT/'outputs/correction_training_preparation_v1'
    out=ROOT/'outputs/focused_mask_review24_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    rows=[json.loads(line) for line in (source/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    frozen=ROOT/'outputs/correction_data_redesign_v1'
    manifest,policy=read(frozen/'selection.json'),read(frozen/'access_policy.json')
    audit=ROOT/'outputs/correction_duplicate_audit_v1'
    disposition={r['image_id']:r for r in read(audit/'candidate_dispositions.json')}
    assert len(rows)==418
    for r in rows:
        training_candidate(r['image_id'],manifest,policy)
        assert disposition[r['image_id']]['status']=='screen_clear_unreviewed'
    def key(r,salt='focused_mask_review24_v1/'):
        return hashlib.sha256((salt+r['image_id']).encode()).hexdigest(),r['image_id']
    selected=[];used_groups=set()
    def take(pool,n,reason,rank=None):
        eligible=[r for r in pool if r['duplicate_group_id'] not in used_groups]
        ordered=sorted(eligible,key=lambda r:(rank(r),key(r)) if rank else key(r))
        chosen=[]
        for r in ordered:
            if r['duplicate_group_id'] in used_groups:continue
            chosen.append(dict(r,selection_reason=reason));used_groups.add(r['duplicate_group_id'])
            if len(chosen)==n:break
        assert len(chosen)==n,reason
        selected.extend(chosen)
    successful=[r for r in rows if r['reference_measurement']['status']=='success']
    def occupancy(r):
        ref=r['reference_measurement'];return ref['skin_pixels']/(ref['face_box'][2]*ref['face_box'][3])
    take(successful,4,'High mask occupancy (risk proxy)',lambda r:-occupancy(r))
    take([r for r in rows if 'reference_mask_retention' in r],4,'Large input/reference mask change (risk proxy)',lambda r:r['reference_mask_retention'])
    take([r for r in rows if r['reference_measurement'].get('reason')=='Required landmarks unavailable'],4,'Reference landmarks unavailable')
    take([r for r in rows if 'skin pixels' in r['reference_measurement'].get('reason','')],2,'Empty or insufficient reference skin support')
    take([r for r in rows if r['reference_measurement'].get('reason')=='Exactly one square-frame face required'],2,'Reference single-face failure')
    take([r for r in rows if r['status']=='pending_review'],8,'Successful candidate (fixed hash sample)')
    remaining=[r for r in rows if r['duplicate_group_id'] not in used_groups]
    check=[]
    for r in sorted(remaining,key=lambda r:key(r,'focused_mask_check12_v1/')):
        if r['duplicate_group_id'] in used_groups:continue
        check.append(r);used_groups.add(r['duplicate_group_id'])
        if len(check)==12:break
    assert len(selected)==24 and len(check)==12
    records=[]
    for r in selected:
        assert (source/'boards'/f'{r["source_id"]}.png').is_file()
        records.append(dict(image_id=r['image_id'],source_id=r['source_id'],status=r['status'],
            selection_reason=r['selection_reason'],reference_mst_estimate=r.get('reference_mst_estimate'),
            assigned_severity=r.get('assigned_severity'),clipping_fraction=r.get('clipping_fraction'),
            panel_count=4 if 'input_measurement' in r else 2,
            failure_reason=r['reference_measurement'].get('reason')))
    # Bind annotations to the source evidence AND the narrower review scope/list.
    binding=dict(source_attempts_sha256=digest(source/'attempts.jsonl'),review_scope='reference_photo_and_reference_mask_only',
        protocol_sha256=digest(ROOT/'docs/focused-mask-review-protocol.md'),selected_ids=[r['image_id'] for r in selected])
    identity=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()
    data=dict(batch='focused24',manifest_sha256=identity,review_scope=binding['review_scope'],reference_only=True,
        board_base='../correction_training_preparation_v1/boards',records=records)
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('selection.json',dict(status='reference_mask_review_only_not_training_admission',binding=binding,
        selected=[dict(image_id=r['image_id'],duplicate_group_id=r['duplicate_group_id'],selection_reason=r['selection_reason']) for r in selected],
        counts=dict(Counter(r['selection_reason'] for r in selected))))
    write('reserved_training_check.json',dict(status='reserved_not_displayed_for_mask_design',
        caveat='Previously processed training sources, not a final evaluation or verified person separation',
        sources=[dict(image_id=r['image_id'],duplicate_group_id=r['duplicate_group_id']) for r in check]))
    template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
    page=template.replace('__BATCH__','focused24').replace('__BATCH_LINKS__','One review · 24 photos').replace('__DATA__',json.dumps(data).replace('<','\\u003c'))
    page=page.replace('href="review.html"','href="../correction_training_preparation_v1/review.html"',1)
    page=page.replace('Training review · batch focused24','Focused reference and mask review · 24 photos')
    page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',
        'Review only the reference photo and reference mask. Accept = suitable reference and mask; reject = unsuitable; uncertain = needs discussion. Add hair, clothing, background, holes or lighting concerns. Automatic risk flags are not confirmed contamination. No distorted-image approval or training admission.')
    page=page.replace('Open complete board','Optional: inspect full board (includes distortion)')
    page=page.replace('<input type="checkbox" id="large">','<input type="checkbox" id="large" checked>')
    page=page.replace('<body>','<body class="large">') if '<body>' in page else page.replace('<header>','<body class="large"><header>',1)
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
    write('verification.json',dict(status='pass',selected_training_sources=24,reserved_training_check=12,
        duplicate_groups_disjoint=True,validation_test_selected=0,new_images_processed=0,models_fitted=0,
        review_scope=binding['review_scope'],manifest_sha256=identity,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(dict(selected=24,reserved=12,selection_counts=Counter(r['selection_reason'] for r in selected)),indent=2))


if __name__=='__main__':main()
