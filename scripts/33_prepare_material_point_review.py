"""Build a blind, unlabeled 24-point review and cache input-only observations."""
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
from src.distortion_generation.generate_distortions import transform_rgb
from src.skin_masking.guarded_correction_support import guarded_correction_support
from src.skin_masking.material_checked_support import material_checked_support

# Developer-selected diagnostic points, not human material labels. Coordinates
# are normalized in the unchanged decoded original, not in detector crops.
POINTS = {
 'fairface__train/19.jpg':[(.50,.12),(.28,.50),(.47,.68),(.04,.48)],
 'fairface__train/29962.jpg':[(.70,.12),(.84,.38),(.31,.50),(.49,.82)],
 'fairface__train/16798.jpg':[(.435,.10),(.735,.52),(.88,.62),(.55,.45)],
 'fairface__val/10480.jpg':[(.23,.53),(.45,.10),(.04,.20),(.48,.66)],
 'fairface__train/62331.jpg':[(.50,.13),(.28,.50),(.50,.85),(.94,.91)],
 'fairface__train/22211.jpg':[(.28,.49),(.50,.25),(.50,.08),(.93,.34)],
}


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path,value): path.write_text(json.dumps(value,indent=2),encoding='utf-8')


def point_card(image,x,y):
    full=cv2.resize(image,(448,448),interpolation=cv2.INTER_NEAREST)
    cx=round(x*448/image.shape[1]);cy=round(y*448/image.shape[0])
    # Gap leaves the exact center pixel visible; local zoom highlights its square.
    for color,thick in [((0,0,0),4),((255,255,255),2)]:
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            cv2.line(full,(cx+dx*5,cy+dy*5),(cx+dx*17,cy+dy*17),color,thick)
    padded=cv2.copyMakeBorder(image,10,10,10,10,cv2.BORDER_REPLICATE)
    zoom=cv2.resize(padded[y:y+21,x:x+21],(420,420),interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(zoom,(200,200),(219,219),(0,0,0),4)
    cv2.rectangle(zoom,(200,200),(219,219),(255,255,255),1)
    zoom=cv2.copyMakeBorder(zoom,14,14,14,14,cv2.BORDER_CONSTANT)
    return np.hstack([full,zoom])


def main():
    config=get_config();output=ROOT/config.OUTPUTS_ROOT/'material_point_review_v1'
    tables=ROOT/'data/manifests/material_review_v1'
    if output.exists() or tables.exists(): raise FileExistsError('Existing review; refusing overwrite')
    helper=importlib.import_module('29_compare_correction_boundaries')
    prepare=importlib.import_module('11_prepare_training_manifests')
    source_table=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources={r['image_id']:r for r in helper.read(source_table)}
    selected=[sources[key] for key in POINTS]
    if any(r['partition']=='reserved_test' for r in selected): raise ValueError('Final test source forbidden')
    template=ROOT/'scripts/templates/material_point_review.html'
    paths=[Path(__file__),template,source_table,ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
           ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'src/skin_masking/guarded_correction_support.py',
           ROOT/'src/skin_masking/material_checked_support.py',ROOT/'src/distortion_generation/generate_distortions.py']
    paths += [Path(r['image_path']) for r in selected]
    hashes={str(p):digest(p) for p in paths}
    output.mkdir();(output/'cards').mkdir();tables.mkdir()
    points=[];source_records=[];observations=[];failures=[]

    def baseline(bgr):
        boxes=prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1: raise ValueError('Expected one face')
        x,y,w,h=boxes[0];crop=bgr[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available: raise ValueError('Landmarks unavailable')
        return (x,y,w,h),crop,result

    for row in selected:
        image_id=row['image_id'];image=cv2.imread(row['image_path'])
        if image is None: raise ValueError('Missing original image')
        height,width=image.shape[:2];source_points=[]
        for nx,ny in POINTS[image_id]:
            x=round(nx*(width-1));y=round(ny*(height-1));point_id=f'P{len(points)+1:02d}'
            card_path='cards/'+point_id+'.png'
            if not cv2.imwrite(str(output/card_path),point_card(image,x,y)): raise OSError('Card write failed')
            record=dict(point_id=point_id,image_id=image_id,x=x,y=y,width=width,height=height,card_path=card_path)
            points.append(record);source_points.append(record)
        source_records.append(dict(image_id=image_id,image_path=row['image_path'],sha256=digest(Path(row['image_path'])),
                                   partition=row['partition'],prior_review=row['original_visual_decision']))
        try:
            box,_,clean_result=baseline(image);bx,by,bw,bh=box
            generation=np.zeros(image.shape[:2],bool);generation[by:by+bh,bx:bx+bw]=clean_result.mask>0
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);shift=rgb.copy()
            transformed=transform_rgb(rgb.astype(float)/255,1.,.85,1.15)
            shift[generation]=np.rint(transformed[generation]*255).astype(np.uint8)
            variants={'clean':image,'color_shift':cv2.cvtColor(shift,cv2.COLOR_RGB2BGR)}
            preparation_error=None
        except Exception as error:
            variants={'clean':image,'color_shift':None};preparation_error=str(error)
        for variant,bgr in variants.items():
            try:
                if bgr is None: raise ValueError('Shift source preparation failed: '+preparation_error)
                box,crop,result=baseline(bgr);bx,by,bw,bh=box
                original=result.mask>0;excluded=result.exclusion_mask>0
                callables={'original':lambda:original,'guarded':lambda:guarded_correction_support(original,excluded),
                           'material_checked':lambda:material_checked_support(crop,original,excluded)}
                common_error=None
            except Exception as error: callables={method:None for method in ('original','guarded','material_checked')};common_error=str(error)
            for method,compute in callables.items():
                error_message=common_error
                try:
                    if compute is None: raise ValueError(common_error)
                    local=compute();frame=np.zeros(image.shape[:2],bool);frame[by:by+bh,bx:bx+bw]=local
                    error_message=None
                except Exception as error: error_message=str(error)
                if error_message: failures.append(dict(image_id=image_id,variant=variant,method=method,error=error_message))
                for point in source_points:
                    observations.append(dict(point_id=point['point_id'],variant=variant,method=method,
                        selected=None if error_message else bool(frame[point['y'],point['x']]),error=error_message))
    manifest=dict(schema_version='material_point_review_v1',points=points,sources=source_records,
        label_definition='Center pixel only: skin=visible unpainted facial skin; hair includes brows/facial hair; paint=visible coating; other=eyes/lips/teeth/background/clothes; unsure=ambiguous.',
        purpose='Developer-selected regression points; human labels initially absent. Not independent held-out sampling, pixel-area segmentation truth, training data or final thesis evaluation.',
        variant_policy='Human material labels on clean coordinates reused for color-only red=.85 blue=1.15 gamma=1 synthetic variant; no warping.',input_sha256=hashes)
    manifest_path=tables/'review_manifest.json';write_json(manifest_path,manifest)
    sha=digest(manifest_path)
    write_json(tables/'prediction_observations.json',dict(manifest_sha256=sha,observations=observations,failures=failures,
        warning='Predictions kept out of the human review page; unavailable observations are not negative predictions.'))
    data=dict(manifest_sha256=sha,points=[{key:p[key] for key in ('point_id','card_path')} for p in points])
    (output/'review.html').write_text(template.read_text(encoding='utf-8').replace('__REVIEW_DATA__',json.dumps(data)),encoding='utf-8')
    assert all(digest(Path(p))==value for p,value in hashes.items())
    summary=dict(points=len(points),sources=len(selected),unlabeled_points=len(points),observations=len(observations),
                 unavailable_method_inputs=len(failures),manifest_sha256=sha,failures=failures,
                 reviewer_status='pending_human_labels',assets_sha256={p.name:digest(p) for p in sorted((output/'cards').glob('*.png'))})
    write_json(output/'build_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='assets_sha256'},indent=2))


if __name__=='__main__': main()
