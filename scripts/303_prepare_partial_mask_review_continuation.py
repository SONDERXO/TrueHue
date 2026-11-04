"""Carry forward exported judgments; display only still-blank mask entries."""
import ast
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'outputs/additional_six_source_mask_review_v1'
    imported=ROOT/'outputs/additional_six_source_mask_import_v1'
    out=ROOT/'outputs/additional_six_source_mask_review_continuation_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    verification=read(imported/'verification.json')
    for name,sha in verification['evidence_sha256'].items():assert digest(imported/name)==sha
    manifest=read(folder/'manifest.json');payload=read(imported/'original_user_export.json')
    identity=digest(folder/'manifest.json');assert payload['manifest_sha256']==identity
    assert set(payload['reviews'])=={r['pair_id'] for r in manifest['rows']}
    inherited={key:value for key,value in payload['reviews'].items() if value['decision']}
    pending=[r for r in manifest['rows'] if not payload['reviews'][r['pair_id']]['decision']]
    assert len(inherited)==2 and len(pending)==13
    assert all(v['decision']=='reject' for v in inherited.values())
    assert {r['source_id'] for r in pending}=={'25517','39083','63509','42965','77101'}
    groups=[]
    for source in dict.fromkeys(r['source_image_id'] for r in pending):
        items=[]
        for r in pending:
            if r['source_image_id']!=source:continue
            board=(folder/r['board_path']).resolve();assert board.is_file()
            items.append(dict(r,board_path=os.path.relpath(board,out).replace('\\','/')))
        groups.append(dict(source_id=items[0]['source_id'],
            reference_url=os.path.relpath(ROOT/items[0]['reference_path'],out).replace('\\','/'),rows=items))
    template_path=ROOT/'scripts/280_freeze_primary_data_and_review.py'
    assignments=[n for n in ast.walk(ast.parse(template_path.read_text(encoding='utf-8')))
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='page' for t in n.targets)
        and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)]
    assert len(assignments)==1;page=assignments[0].value.value
    page=page.replace('__DATA__',json.dumps(groups).replace('<','\\u003c')).replace('__HASH__',identity)
    page=page.replace('let index=0,decisions={};',
        'const inherited='+json.dumps(inherited).replace('<','\\u003c')+';let index=0,decisions=JSON.parse(JSON.stringify(inherited));')
    page=page.replace('const reviews={};for(const g of groups)',
        'const reviews=JSON.parse(JSON.stringify(inherited));for(const g of groups)')
    page=page.replace('26 existing photos, 61 mask decisions.',
        '5 remaining photos, 13 remaining mask decisions. The two rejections for 2434 are already saved and carried forward.')
    page=page.replace(' / 61 masks reviewed',' / 15 masks reviewed')
    page=page.replace('Normal-case training masks','Continue the new-source mask review')
    page=page.replace('Normal-case masks','Continue the new-source mask review')
    page=page.replace('These normal-case versions will supply the next planned training comparison; no model is trained from your choices automatically.',
        'Only unresolved new masks are shown. Original approvals and the two completed rejections remain preserved; no model fit follows automatically.')
    page=page.replace('truehue_primary_mask_decisions.json','truehue_additional_six_source_mask_decisions.json')
    assert 'const inherited=' in page and 'const reviews=JSON.parse(JSON.stringify(inherited))' in page
    assert '61 masks' not in page and '26 existing photos' not in page
    out.mkdir()
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'review-script.js').write_text(page.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    snapshot=dict(status='partial_user_export_preserved',original_manifest_sha256=identity,
        original_export_path='outputs/additional_six_source_mask_review_v1/a.json',
        inherited_judgments=inherited,pending_pair_ids=[r['pair_id'] for r in pending],
        displayed_source_count=5,displayed_mask_count=13,full_export_mask_count=15,
        inferred_acceptances=0,model_fits=0,
        next_import='Use a new versioned import directory; preserve the partial v1 export.')
    (out/'continuation.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',inherited_rejections=2,blank_decisions=13,
        completed_masks_shown_again=0,new_mask_approvals=0,manifest_changed=False,
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in [folder/'manifest.json',imported/'original_user_export.json',imported/'verification.json',template_path,Path(__file__)]},
        evidence_sha256={p.name:digest(p) for p in out.iterdir()}),indent=2),encoding='utf-8')
    print('Prepared continuation: 13 unresolved masks on five photos; both completed rejections retained in every export.')


if __name__=='__main__':main()
