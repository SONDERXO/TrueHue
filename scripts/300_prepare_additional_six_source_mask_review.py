"""Review only the new primary input masks; reuse completed reference judgments."""
import ast
import hashlib
import json
import os
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/additional_six_source_pairs_v1'
    out=ROOT/'outputs/additional_six_source_mask_review_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    verification=read(parent/'verification.json');assert verification['status']=='pass'
    for name,sha in verification['evidence_sha256'].items():assert digest(parent/name)==sha
    plan=read(parent/'plan.json');primary=read(parent/'primary_review_queue.json')
    registry=read(ROOT/'outputs/reviewed_source_evidence32_v1/registry.json')
    old_keys={(r['input_sha256'],r['input_mask_sha256']) for r in registry['rows']}
    assert len(primary)==15 and len({r['source_image_id'] for r in primary})==6
    assert not old_keys & {(r['input_sha256'],r['input_mask_sha256']) for r in primary}
    template_path=ROOT/'scripts/280_freeze_primary_data_and_review.py'
    assignments=[n for n in ast.walk(ast.parse(template_path.read_text(encoding='utf-8')))
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='page' for t in n.targets)
        and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)]
    assert len(assignments)==1;template=assignments[0].value.value
    out.mkdir();(out/'boards').mkdir();queue=[]
    for r in primary:
        image=cv2.imread(str(ROOT/r['input_path']));mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0
        overlay=image.copy();overlay[mask]=(.5*overlay[mask]+np.array([0,150,0])).astype(np.uint8)
        path=out/'boards'/f'{r["pair_id"]}.png';assert cv2.imwrite(str(path),np.hstack([image,overlay]))
        notes='; '.join(scope+': '+r['reference_judgments'][scope]['notes'] for scope in ['reference_suitability','reference_mask'] if r['reference_judgments'][scope]['notes'])
        queue.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],source_id=r['source_id'],
            variant=r['variant'],severity=r['severity'],duplicate_group_id=r['duplicate_group_id'],
            reference_concerns=notes,reference_path=r['reference_path'],input_path=r['input_path'],
            input_mask_path=r['input_mask_path'],input_sha256=r['input_sha256'],input_mask_sha256=r['input_mask_sha256'],
            board_path=path.relative_to(out).as_posix(),paper_target=r['paper_target'],training_eligible=False))
    manifest=dict(schema_version='truehue_primary_mask_review_v1',scope='exact_new_primary_candidate_input_masks_only',
        measurement_contract_sha256=plan['measurement_contract_sha256'],rows=queue,source_count=6,mask_count=15,
        source_groups_exposed_development=True,new_mask_approvals=0,
        source_origin='six additional reviewed sources; no old26 regenerated',model_fitting_authorized=False)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');identity=digest(out/'manifest.json')
    groups=[]
    for source in dict.fromkeys(r['source_image_id'] for r in queue):
        items=[r for r in queue if r['source_image_id']==source]
        groups.append(dict(source_id=items[0]['source_id'],reference_url=os.path.relpath(ROOT/items[0]['reference_path'],out).replace('\\','/'),rows=items))
    page=template.replace('__DATA__',json.dumps(groups).replace('<','\\u003c')).replace('__HASH__',identity)
    page=page.replace('26 existing photos, 61 mask decisions.','6 additional photos, 15 new mask decisions.')
    page=page.replace(' / 61 masks reviewed',' / 15 masks reviewed')
    page=page.replace('Normal-case training masks','New-source primary candidate masks').replace('Normal-case masks','New-source candidate masks')
    page=page.replace('These normal-case versions will supply the next planned training comparison; no model is trained from your choices automatically.',
        'These candidates expand the data on six additional sources. Only the new masks need review; no model fit follows automatically.')
    page=page.replace('truehue_primary_mask_decisions.json','truehue_additional_six_source_mask_decisions.json')
    assert '61 masks' not in page and '26 existing photos' not in page
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'review-script.js').write_text(page.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    for g in groups:
        assert (out/g['reference_url']).is_file()
        for r in g['rows']:assert (out/r['board_path']).is_file()
    result=dict(status='pass',source_groups=6,pending_input_masks=15,previous_original_reviews_repeated=0,
        reused_old_input_masks=0,clipped_stress_masks_requested=0,new_mask_approvals=0,new_fitting_admissions=0,
        manifest_sha256=identity,live_browser_tested=False,
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in [parent/'verification.json',parent/'primary_review_queue.json',template_path,Path(__file__)]},
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['input_sha256','evidence_sha256']},indent=2))


if __name__=='__main__':main()
