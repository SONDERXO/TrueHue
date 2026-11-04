"""Complete the agreed 60-source development-review budget with 36 new IDs."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate


def main():
    out=ROOT/'outputs/training_review36_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/correction_training_preparation_v1'
    frozen=ROOT/'outputs/correction_data_redesign_v1'
    audit=ROOT/'outputs/correction_duplicate_audit_v1'
    reviewed_path=ROOT/'outputs/focused_mask_review24_import_v1/reconciled_reviews.json'
    reserved_path=ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json'
    color_path=ROOT/'outputs/training_reference_color_audit_v1/source_dispositions.json'
    rows=[json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    by_id={r['image_id']:r for r in rows}
    reviewed={r['image_id'] for r in read(reviewed_path)}
    reserved={r['image_id'] for r in read(reserved_path)['sources']}
    blocked=reviewed|reserved
    blocked_groups={by_id[i]['duplicate_group_id'] for i in blocked}
    colors={r['image_id']:r for r in read(color_path)}
    dispositions={r['image_id']:r for r in read(audit/'candidate_dispositions.json')}
    pool=[r for r in rows if r['status']=='pending_review' and r['image_id'] not in blocked
          and r['duplicate_group_id'] not in blocked_groups and colors.get(r['image_id'],{}).get('status')=='requires_reference_review']
    selection=[];used_groups=set()
    def key(r):return hashlib.sha256(('training_review36_v1/'+r['image_id']).encode()).hexdigest(),r['image_id']
    for severity,count in [('light',12),('medium',24)]:
        chosen=[]
        for r in sorted([r for r in pool if r['assigned_severity']==severity],key=key):
            if r['duplicate_group_id'] in used_groups:continue
            chosen.append(r);used_groups.add(r['duplicate_group_id'])
            if len(chosen)==count:break
        assert len(chosen)==count,severity
        selection.extend(chosen)
    manifest,policy=read(frozen/'selection.json'),read(frozen/'access_policy.json')
    evidence=read(parent/'verification.json')['evidence_sha256']
    for r in selection:
        training_candidate(r['image_id'],manifest,policy)
        assert dispositions[r['image_id']]['status']=='screen_clear_unreviewed'
        for suffix in ['reference','reference_mask']:
            p=f'images/{r["source_id"]}_{suffix}.png';assert digest(parent/p)==evidence[p]
        p=f'boards/{r["source_id"]}.png';assert digest(parent/p)==evidence[p]
    selected_ids=[r['image_id'] for r in selection]
    assert len(selected_ids)==len(set(selected_ids))==36 and not set(selected_ids)&blocked
    paths=[Path(__file__),ROOT/'docs/training-review36-protocol.md',parent/'attempts.jsonl',reviewed_path,reserved_path,color_path,
        frozen/'selection.json',frozen/'access_policy.json',audit/'candidate_dispositions.json']
    binding=dict(input_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},selected_ids=selected_ids,
        review_scope='original_rule_based_reference_and_mask_only')
    identity=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('selection.json',dict(status='unreviewed_training_development_not_admitted',binding=binding,
        selected=[dict(image_id=r['image_id'],source_id=r['source_id'],duplicate_group_id=r['duplicate_group_id'],
            assigned_severity=r['assigned_severity'],clipping_fraction=r['clipping_fraction']) for r in selection],
        excluded_previous_reviewed=len(reviewed),excluded_reserved=len(reserved),pool_count=len(pool)))
    spec=dict(batch='training36',manifest_sha256=identity,review_scope=binding['review_scope'],reference_only=True,
        board_base='../correction_training_preparation_v1/boards',records=[dict(image_id=r['image_id'],source_id=r['source_id'],
            status='pending_review',selection_reason='New development source, fixed hash within estimated severity',
            panel_count=4,failure_reason=None) for r in selection])
    template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
    page=template.replace('__BATCH__','training36').replace('__BATCH_LINKS__','36 new photos · original rule-based masks').replace('__DATA__',json.dumps(spec).replace('<','\\u003c'))
    page=page.replace('href="review.html"','href="../focused_mask_review24_v1/review.html"',1).replace('All batches','Previous 24')
    page=page.replace('Training review · batch training36','Training development review · 36 new photos')
    page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',
        'Review only the photo and its ORIGINAL rule-based face mask. Accept if both are usable; reject if either is unsuitable; use uncertain when unclear. Note reference problems (lighting/casts/occlusion) separately from mask problems (hair, clothing, background, holes). No need to redo your first24. No experimental parser masks shown; no automatic training admission.')
    page=page.replace('Open complete board','Optional full board (includes unreviewed distortion)')
    page=page.replace('<header>','<body class="large"><header>',1).replace('<input type="checkbox" id="large">','<input type="checkbox" id="large" checked>')
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
    summary=dict(status='ready_for_reference_mask_review',sources=36,previous_unique_sources_reviewed=24,
        total_development_review_budget=60,estimated_severity_counts=dict(Counter(r['assigned_severity'] for r in selection)),
        missing_successful_dark_severity=True,prior_review_ids_reused=0,reserved_check_ids_selected=0,
        validation_test_ids_selected=0,new_raw_images_opened=0,new_preprocessing=0,models_fitted=0,training_admissions=0,
        selected_clipped_distortions=sum(r['clipping']['clipped_pixels']>0 for r in selection))
    write('summary.json',summary)
    write('verification.json',dict(status='pass',ids_roles_groups_and_source_hashes_checked=True,manifest_sha256=identity,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
