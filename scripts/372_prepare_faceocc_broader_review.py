"""Freeze 24 existing-data attempts and prepare originals-only patch annotation."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
from src.data_preparation.redesign_access import training_candidate


def main():
    out=ROOT/'outputs/faceocc_broader_annotation_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(rel):
        raw=(ROOT/rel).read_bytes();hashes[rel]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    inventory=read('outputs/next_cycle_data_plan_v1/remaining_fairface_inventory.json')
    allocation=read('outputs/correction_data_redesign_v1/selection.json')
    policy=read('outputs/correction_data_redesign_v1/access_policy.json')
    prior=read('outputs/additional_mst_eligibility_v1/plan.json')
    cohort=read('outputs/preferred_support_cohort_v1/records.json')
    previous={r['image_id'] for r in prior['selected']}
    rank=lambda r:hashlib.sha256(('faceocc-broader-v1/'+r['image_id']).encode()).hexdigest()
    chosen=[];groups=set()
    for row in sorted(inventory,key=rank):
        assert row['role']=='train'
        if row['duplicate_group'] not in groups:
            entry=training_candidate(row['image_id'],allocation,policy)
            chosen.append(dict(image_id=row['image_id'],lane='additional_fairface',role='train',
                source_path=entry['relative_image_path'],duplicate_group=row['duplicate_group'],
                exposure_evidence=row['exposure_evidence'],historical_reviews=row['scoped_review_evidence'],
                official_mst=None,person_independence='not_verified'))
            groups.add(row['duplicate_group'])
        if len(chosen)==12:break
    table='data/raw/mst-e_data/mst-e_image_details.csv';raw=(ROOT/table).read_bytes();hashes[table]=hashlib.sha256(raw).hexdigest()
    official=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    for subject in ['subject_1','subject_9','subject_10','subject_11']:
        for lighting in ['well_lit','poorly_lit']:
            pool={}
            for r in official:
                key='mst_e__'+r['subject_name']+'/'+r['image_ID']
                if r['subject_name']==subject and r['lighting']==lighting and key not in previous:
                    pool[key]=dict(image_id=key,lane='additional_mst_same_subject',role='exposed_mapping_development',
                        source_path='data/raw/mst-e_data/'+subject+'/'+r['image_ID'],subject_id=subject,
                        official_mst=int(r['MST']),recorded_lighting=lighting,
                        person_independence='same_exposed_subject_not_new_person')
            chosen.append(sorted(pool.values(),key=rank)[0])
    challenges={'74882':'glasses','39083':'facial_hair','29321':'mouth_shadow','77101':'outer_face_hairline'}
    for r in cohort:
        sid=Path(r['image_id']).stem
        if sid in challenges:
            entry=training_candidate(r['image_id'],allocation,policy)
            chosen.append(dict(image_id=r['image_id'],lane='exposed_challenge',role='train',
                source_path=entry['relative_image_path'],challenge_reason=challenges[sid],
                prior_source_decision=r['original_source_decision'],official_mst=None,
                prior_reviews_preserved=True,person_independence='not_verified'))
    assert len(chosen)==len({r['image_id'] for r in chosen})==24
    for rel in ['docs/faceocc-broader-evaluation-protocol-2026-11-01.md',
                'scripts/review_tools/faceocc_patch_review.js']:
        hashes[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir();(out/'images').mkdir()
    (out/'selection.json').write_text(json.dumps(dict(status='frozen_before_pixel_reads',rows=chosen,
        input_sha256=hashes,replacement=False,model_inference=False),indent=2))
    rows=[];failures=[]
    for i,r in enumerate(chosen,1):
        row=dict(r,key=str(i))
        source=ROOT/r['source_path']
        with (out/'access_ledger.jsonl').open('a') as f:f.write(json.dumps(dict(image_id=r['image_id'],role=r['role'],phase='originals_only_annotation_preparation'))+'\n')
        if not source.is_file():
            row.update(status='unavailable',reason='source_file_missing');failures.append(row);continue
        row['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
        image=cv2.imread(str(source))
        if image is None:
            row.update(status='unavailable',reason='decode_failed');failures.append(row);continue
        image=cv2.resize(image,(256,256),interpolation=cv2.INTER_LINEAR)
        path=out/'images'/(str(i)+'.png');assert cv2.imwrite(str(path),image)
        row.update(status='annotation_pending',image_path='images/'+path.name,
            image_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(row)
    manifest=dict(schema_version='truehue_faceocc_broader_patches_v1',rows=rows,technical_failures=failures,
        total_attempts=24,annotation_scope='partial_clear_region_polygons_not_full_segmentation_truth',
        predictions_hidden=True,all_model_inference_pending=True,automatic_adoption=False)
    encoded=json.dumps(manifest,indent=2).encode();identity=hashlib.sha256(encoded).hexdigest()
    (out/'manifest.json').write_bytes(encoded)
    controls='''<h1>FaceOcc broader evaluation — originals only</h1>
<p>Annotate clear facial-skin interiors and unwanted regions without seeing either model’s masks. These patches are evaluation evidence, not full ground truth. Keep uncertain edges separate. No model comparison will run until your export is imported.</p>
<p><b>How:</b> choose a label, click around a patch, then click <b>Finish polygon</b>. Mark several visible skin areas (forehead, cheeks/chin where visible) and relevant unwanted regions near/on the face. Avoid eyes, brows, lips and nostrils as skin. Use Uncertain for ambiguous hair/stubble or borders. Do not mark only distant background. Draw more than one patch as needed.</p>
<label>Annotator name or code <input id="annotator" placeholder="Your name or code"></label>
<div id="bar"><span id="progress"></span> <button id="export">Download annotations</button><span id="message"></span></div>
<p id="case"></p><p><button id="prev">Previous</button> <button id="next">Next</button></p>
<canvas id="canvas" width="256" height="256"></canvas>
<p><select id="label"><option value="skin">Clear facial skin</option><option value="facial_hair">Facial/head hair</option><option value="object">Glasses / covering / object</option><option value="outside">Neck / clothing / background</option><option value="uncertain">Uncertain</option></select> <button id="finish">Finish polygon</button> <button id="undo">Undo point</button> <button id="delete">Delete last polygon</button></p>
<p id="polygons"></p><label>Gradability <select id="status"><option value="pending">Choose</option><option value="gradable">Gradable — skin and unwanted patches marked</option><option value="ungradable">Ungradable — explain below</option></select></label>
<p>Visible conditions (unknown is allowed):</p><div id="tags"></div><label>Notes / uncertainty / ungradable reason<textarea id="notes"></textarea></label>
<p>Appearance and lighting labels do not establish true skin colour or verified MST. All prior rejections and failures remain; this annotation does not approve training.</p>'''
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FaceOcc prediction-hidden patch review</title><style>body{font:18px/1.5 system-ui;max-width:1050px;margin:auto;padding:24px;background:#faf8f4}canvas{width:512px;max-width:100%;border:1px solid #777;touch-action:none;cursor:crosshair}button,select,input,textarea{font:inherit;padding:8px;margin:4px}label{display:block}textarea{width:95%;height:80px}#bar{position:sticky;top:0;background:#fff0bf;padding:10px;z-index:2}</style>'+controls+'<script id="data" type="application/json">'+json.dumps(dict(manifest_sha256=identity,rows=rows,technical_failures=failures)).replace('<','\\u003c')+'</script><script src="review.js"></script></html>'
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'review.js').write_bytes((ROOT/'scripts/review_tools/faceocc_patch_review.js').read_bytes())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    print(json.dumps(dict(attempts=24,annotation_images=len(rows),technical_failures=len(failures),manifest_sha256=identity,inferences=0),indent=2))


if __name__=='__main__':main()
