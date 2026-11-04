"""Evaluate frozen mask candidates on known TRAIN diagnostic frames, no fitting."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.face_parsing_experiment import DenseFaceParser,facial_skin
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.skin_masking.parser_material_experiment import combined_supports
from src.skin_masking.anatomical_contour_experiment import anatomy
from src.skin_masking.material_boundary_guard import guard_material_boundary
from src.distortion_generation.generate_distortions import transform_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,value):
    assert cv2.imwrite(str(path),value)
def main():
    out=ROOT/'outputs/paint_protection_validation_v1'
    if out.exists():raise FileExistsError(out)
    manifest_path=ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json'
    manifest=json.loads(manifest_path.read_text());assert manifest['status']=='frozen_before_candidate_inference'
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    scoring=importlib.import_module('90_score_face_boundary_references');bright=importlib.import_module('72_audit_brightness_features')
    witnesses=importlib.import_module('82_inspect_accepted_mask_notes').WITNESSES
    models=[ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx',ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH]
    tracked=[Path(__file__),manifest_path,ROOT/'docs/paint-protection-validation-protocol.md']+models
    tracked += [ROOT/p for p in ['src/skin_masking/face_parsing_experiment.py','src/skin_masking/selfie_material_segmenter.py',
        'src/skin_masking/parser_material_experiment.py','src/skin_masking/anatomical_contour_experiment.py','src/skin_masking/material_boundary_guard.py',
        'src/distortion_generation/generate_distortions.py','scripts/11_prepare_training_manifests.py','scripts/72_audit_brightness_features.py',
        'outputs/parser_material_boundary_v1/readiness.json']]
    hashes=dict(manifest['input_sha256']);hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    out.mkdir()
    for name in ['images','ingredients','masks','boards']:(out/name).mkdir()
    (out/'run_status.json').write_text('{"status":"running"}')
    export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text())
    paint_spec=next(f for f in export['images'] if Path(f['image_id']).stem=='16798')
    parser=DenseFaceParser(models[0]);semantic=SelfieMaterialSegmenter(models[1]);records=[]
    for frame in manifest['frames']:
        ident=frame['frame_id'];original=cv2.imread(str(ROOT/frame['source_path']));h,w=original.shape[:2]
        assert (w,h)==(frame['width'],frame['height'])
        labels=None;regions={}
        if frame['annotation']['kind']=='unchanged_user_reference':
            labels=cv2.imread(str(ROOT/frame['annotation']['labels_path']),0)
            if ident=='16798':
                paint=np.zeros((h,w),bool)
                for p in paint_spec['polygons'][:6]:paint|=scoring.polygon_pixels(p['points'],w,h)
                regions['user_paint']=paint&(labels==3)
                regions['user_features']=(labels==3)&~paint
            else:regions['user_features']=labels==3
        for r in frame['annotation'].get('regions',[]):regions[r['region_id']]=scoring.polygon_pixels(r['points'],w,h)
        source_arms=None;source_anchor=None
        for variant,recipe in manifest['variants'].items():
            key=ident+'_'+variant;clipped=0
            if recipe is None:image=original.copy()
            else:
                rgb=cv2.cvtColor(original,cv2.COLOR_BGR2RGB).astype(float)/255
                raw=transform_rgb(rgb,**recipe,clip=False);clipped=int(np.any((raw<0)|(raw>1),axis=2).sum())
                image=cv2.cvtColor(np.rint(np.clip(raw,0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            image_path=out/'images'/(key+'.png');save(image_path,image)
            record=dict(key=key,frame_id=ident,role=frame['role'],variant=variant,recipe=recipe,
                recipe_sha256=hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest(),clipped_pixels=clipped,
                image_sha256=digest(image_path),status='unavailable',training_eligible=False,stages={})
            try:
                dc=parser.categories_bgr(image);categories=semantic.categories_bgr(image)
                save(out/'ingredients'/(key+'_parser.png'),dc);save(out/'ingredients'/(key+'_semantic.png'),categories)
                boxes=prepare._detect_face_boxes(image,models[2],.85)
                if len(boxes)!=1:raise ValueError('Expected exactly one detected face; got '+str(len(boxes)))
                box=list(map(int,boxes[0]));x,y,bw,bh=box
                points,margin,status=prepare.detect_landmarks_with_margin(image,box,models[3])
                if points is None:raise ValueError('No anatomical landmarks')
                full=points+box[:2];np.save(out/'ingredients'/(key+'_landmarks.npy'),full)
                result=prepare.compute_versioned_skin_mask(image[y:y+bh,x:x+bw],image,box,models[3],'v2_complete_mouth_v1')
                if not result.landmarks_available:raise ValueError('No original measurement anchors')
                anchor=np.zeros((h,w),bool);anchor[y:y+bh,x:x+bw]=result.mask>0
                anchor&=np.isin(categories,[2,3])
                _,excluded,_,geometry=anatomy(image,full)
                arms,details,seeds,fd,cd=combined_supports(image,facial_skin(dc),categories,excluded,box,anchor)
                arms['C2'],outliers=guard_material_boundary(arms['A'],arms['C'])
            except (ValueError,cv2.error) as error:
                record['reason']=str(error);records.append(record)
                board=cv2.copyMakeBorder(image,32,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(board,key+' UNAVAILABLE',(2,12),cv2.FONT_HERSHEY_SIMPLEX,.28,(0,0,255),1)
                save(out/'boards'/(key+'.png'),board)
                print(key+': unavailable '+str(error),flush=True);continue
            record.update(status='available',face_box=box,material=details,landmark_status=status)
            for name,value in [('anchor',anchor),('excluded',excluded),('seeds',seeds)]:save(out/'ingredients'/(key+'_'+name+'.png'),value.astype(np.uint8)*255)
            if variant=='clean':source_arms={a:m.copy() for a,m in arms.items()};source_anchor=anchor.copy()
            stage_masks={'measurement':{a:anchor&m for a,m in arms.items()},'correction':arms}
            if variant=='clean':stage_masks={'generation':arms,**stage_masks}
            panels=[]
            raw_panel=cv2.copyMakeBorder(image,32,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(raw_panel,key,(2,12),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(raw_panel)
            for stage,values in stage_masks.items():
                record['stages'][stage]={}
                for arm,mask in values.items():
                    save(out/'masks'/(key+'_'+stage+'_'+arm+'.png'),mask.astype(np.uint8)*255)
                    item=dict(pixels=int(mask.sum()),protected_regions={})
                    for name,region in regions.items():
                        interior=cv2.erode(region.astype(np.uint8),np.ones((3,3),np.uint8))>0
                        item['protected_regions'][name]=dict(pixels=int(region.sum()),selected=int((region&mask).sum()),
                            interior_pixels=int(interior.sum()),interior_selected=int((interior&mask).sum()))
                    if labels is not None:item.update(user_reference=scoring.score(mask,labels),user_interior_reference=scoring.score(mask,labels,True))
                    if ident in witnesses:
                        x0,y0,x1,y1=witnesses[ident]['bounds'];item['diagnostic_witness_selected']=int(mask[y0:y1,x0:x1].sum())
                    if stage=='measurement':item.update(statistics=compute_masked_lab_statistics(image,mask.astype(np.uint8)*255,1000),brightness=bright.brightness_features(image,mask))
                    record['stages'][stage][arm]=item
                    if stage=='correction':
                        shown=image.copy();shown[mask]=np.rint(.55*shown[mask]+.45*np.array([0,220,0])).astype(np.uint8)
                        for region in regions.values():
                            contours,_=cv2.findContours(region.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(shown,contours,-1,(0,0,255),1)
                        shown=cv2.copyMakeBorder(shown,32,0,0,0,cv2.BORDER_CONSTANT)
                        cv2.putText(shown,arm+' correction',(2,12),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(shown)
            record['retention_recomputed_clean_anchor']={a:support_retention(source_anchor,stage_masks['measurement'][a],arms[a]) for a in arms} if source_anchor is not None and source_anchor.any() else None
            record['retention_prospective_generation']={a:support_retention(source_arms[a],stage_masks['measurement'][a],arms[a]) if source_arms[a].any() else None for a in arms} if source_arms else None
            save(out/'boards'/(key+'.png'),np.hstack(panels));records.append(record)
            print(key+': available',flush=True)
    semantic.close();assert len(records)==51
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_no_adoption_no_regeneration_no_fitting',records=records,input_sha256=hashes,
        frozen_manifest_sha256=digest(manifest_path),training_pairs_regenerated=0,models_fitted=0,
        limitations='Deliberately selected known development sources. New protected interiors are provisional Codex labels; no independent paint truth. Global stress probes are not training pairs. Clean anchor is recomputed, not historical saved generation.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps(dict(cases=51,available=sum(r['status']=='available' for r in records),masks=len(list((out/'masks').glob('*.png'))))))
if __name__=='__main__':main()
