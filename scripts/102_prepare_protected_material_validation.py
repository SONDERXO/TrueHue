"""Inventory already exposed sources; prepare separately attributed region drafts."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# Conservative diagnostic interiors, drawn from original images without new-mask
# overlays. These are NOT reviewer labels and do not describe whole makeup areas.
REGIONS={
 '3183':[
  ('warm_eye_cosmetic',[[44,45],[51,41],[62,40],[75,43],[80,48],[73,51],[59,50],[47,52]]),
  ('lower_lip_cosmetic_feature',[[97,179],[110,181],[124,180],[134,176],[131,184],[119,190],[109,190],[98,185]])],
 '58397':[
  ('image_left_eye_cosmetic_feature',[[44,61],[54,55],[68,54],[82,58],[88,63],[86,67],[71,65],[56,65],[46,68]]),
  ('image_right_eye_cosmetic_feature',[[132,59],[142,54],[157,54],[170,58],[176,63],[173,68],[159,66],[145,65],[135,68]])],
 '67436':[
  ('image_left_purple_eye_cosmetic',[[45,58],[55,53],[66,54],[75,58],[77,63],[68,63],[55,61],[47,63]]),
  ('image_right_purple_eye_cosmetic',[[133,60],[146,56],[159,58],[168,63],[166,68],[152,67],[139,67]]),
  ('upper_lip_cosmetic_feature',[[75,145],[88,138],[102,137],[114,140],[124,144],[133,151],[125,154],[113,149],[97,148],[84,153]]),
  ('lower_lip_cosmetic_feature',[[79,173],[90,181],[106,183],[122,181],[130,176],[128,185],[112,191],[94,190],[83,183]])],
 '84888':[
  ('image_left_blue_eye_cosmetic',[[52,60],[61,56],[73,56],[82,59],[89,64],[88,68],[77,67],[66,66],[56,68]]),
  ('image_right_blue_eye_cosmetic',[[137,59],[145,55],[158,55],[167,58],[171,64],[169,68],[159,65],[148,65],[140,66]])],
 '81250':[
  ('light_forehead_mark',[[110,17],[117,16],[125,18],[126,22],[117,23],[109,21]]),
  ('vertical_red_forehead_mark',[[116,28],[120,29],[121,36],[120,40],[116,40],[115,35]]),
  ('lower_red_forehead_mark',[[111,44],[117,43],[123,44],[124,48],[119,51],[112,49]])]
}
ROLES={
 '16798':'existing_user_paint_reference','40048':'existing_user_skin_reference','60162':'existing_user_skin_reference',
 '3183':'cosmetic_challenge','58397':'cosmetic_challenge','67436':'cosmetic_challenge','84888':'cosmetic_challenge',
 '81250':'visible_forehead_mark_challenge','13529':'uncertain_colored_appearance','72347':'uncertain_colored_appearance',
 '81965':'patterned_light_challenge','76160':'strong_color_lighting_challenge',
 '31154':'hair_background_witness','63870':'fabric_witness','51446':'scarf_control','55007':'hair_control','56444':'foliage_control'}


def main():
    tables=ROOT/'data/manifests/paint_protection_validation_v1';out=ROOT/'outputs/paint_protection_inventory_v1'
    if tables.exists():raise FileExistsError(tables)
    ledger_path=ROOT/'data/manifests/development_exposure_additions.jsonl'
    ledger=[json.loads(line) for line in ledger_path.read_text().splitlines() if line]
    exposed={r['image_id'] for r in ledger};assert len(exposed)==114
    source_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    with source_path.open(encoding='utf-8',newline='') as f:sources={r['image_id']:r for r in csv.DictReader(f)}
    review_paths=[ROOT/'data/manifests'/p for p in ['training_coverage_audit_v1/candidate_disposition.json',
      'source_screening_followup_v1/candidate_disposition.json','brightness_color_source_screen_v1/candidate_disposition.json',
      'training_source60_screen_v1/source_dispositions.json']]
    evidence={}
    for path in review_paths:
        data=json.loads(path.read_text());rows=data.get('observations',data.get('new_sources',[]))
        for row in rows:evidence.setdefault(row['image_id'],[]).append(dict(path=path.relative_to(ROOT).as_posix(),record=row))
    inventory=[]
    for key in sorted(exposed):
        row=sources[key];assert row['partition']=='train';path=Path(row['image_path']);assert path.is_file()
        inventory.append(dict(image_id=key,source_path=path.relative_to(ROOT).as_posix(),source_sha256=digest(path),partition='train',
            prior_development_exposure=True,repeat_visual_inventory='Reviewed on10 contact sheets, no new candidate overlays',
            selected=Path(key).stem in ROLES,role=ROLES.get(Path(key).stem,'not_selected_in_fixed_set'),prior_reviews=evidence.get(key,[])))
    user_manifest=ROOT/'data/manifests/face_boundary_review_v1/review_manifest.json'
    user={Path(r['image_id']).stem:r for r in json.loads(user_manifest.read_text())['images']}
    tables.mkdir();out.mkdir(exist_ok=True);(out/'regions').mkdir(exist_ok=True)
    frames=[];tracked=[Path(__file__),ledger_path,source_path,user_manifest,ROOT/'docs/paint-protection-validation-protocol.md',
        ROOT/'data/manifests/face_boundary_reference_v1/original_export.json',ROOT/'data/manifests/face_boundary_reference_v1/completion_confirmation.json',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json']+review_paths
    raster=importlib.import_module('90_score_face_boundary_references')
    for ident,role in ROLES.items():
        key='fairface__train/'+ident+'.jpg';row=sources[key]
        assert row['partition']=='train' and (key in exposed or ident=='16798')
        if ident in user:path=ROOT/user[ident]['image_path']
        elif ident in ['31154','63870','51446','55007','56444']:path=ROOT/'outputs/training_source60_variants_v1/images'/(ident+'_reference.png')
        else:path=Path(row['image_path'])
        image=cv2.imread(str(path));assert image is not None;h,w=image.shape[:2];tracked.append(path)
        regions=[];protected=np.zeros((h,w),bool)
        for index,(name,points) in enumerate(REGIONS.get(ident,[]),1):
            array=np.asarray(points,float);assert len(points)>=3 and np.isfinite(array).all()
            assert (array>=0).all() and (array[:,0]<=w-1).all() and (array[:,1]<=h-1).all()
            assert abs(cv2.contourArea(array.astype(np.float32)))>=1
            region=raster.polygon_pixels(points,w,h);protected|=region
            regions.append(dict(region_id=ident+'_R'+str(index),name=name,label='protected_cosmetic_or_mark_interior',points=points,
                author='Codex visual development annotation',user_verified=False,exhaustive=False,purpose='Protected diagnostic interior; not a new user label or training target'))
        if ident in user:
            label_path=ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png');tracked.append(label_path)
            annotation=dict(kind='unchanged_user_reference',labels_path=label_path.relative_to(ROOT).as_posix(),labels_sha256=digest(label_path))
        elif regions:annotation=dict(kind='provisional_codex_protected_interiors',regions=regions)
        else:annotation=dict(kind='no_new_material_truth',note='Qualitative/witness challenge only; unmarked pixels are not negative or positive labels')
        frames.append(dict(image_id=key,frame_id=ident,role=role,source_path=path.relative_to(ROOT).as_posix(),source_sha256=digest(path),
            width=w,height=h,partition='train',prior_development_exposure=True,prior_reviews=evidence.get(key,[]),annotation=annotation,
            training_eligible=False,previous_human_decision_unchanged=True))
        if regions:
            shown=cv2.resize(image,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
            for r in regions:
                polygon=np.rint(np.asarray(r['points'])*3).astype(np.int32);cv2.polylines(shown,[polygon],True,(0,0,255),2)
                x,y=polygon.mean(axis=0).astype(int);cv2.putText(shown,r['region_id'].split('_')[-1],(x,y),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
            assert cv2.imwrite(str(out/'regions'/(ident+'_proposed.png')),shown)
            assert cv2.imwrite(str(out/'regions'/(ident+'_protected.png')),protected.astype(np.uint8)*255)
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    manifest=dict(version='paint_protection_validation_v1',date='2026-10-26',status='draft_region_QA_before_candidate_evaluation',
        inventory_sources=114,selected_frames=17,frames=frames,inventory=inventory,
        annotation_status='Original user references preserved; new Codex protected interiors provisional, no independent material truth on ambiguous cases',
        candidate_policy='Frozen A/F/C/C2, no retuning',variants=dict(clean=None,dark=dict(gamma=.7,red_gain=.85,blue_gain=.95),color_shift=dict(gamma=1.,red_gain=.85,blue_gain=1.15)),
        scope='Known exposed development sources only; diagnostic global stress probes, not training-pair regeneration or final evaluation',input_sha256=hashes)
    (tables/'draft_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(inventory=114,frames=17,provisional_regions=sum(len(f['annotation'].get('regions',[])) for f in frames),status=manifest['status'])))


if __name__=='__main__':main()
