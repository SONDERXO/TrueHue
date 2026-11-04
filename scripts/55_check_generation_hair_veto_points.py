"""Removal-only generation-mask regression at the original24 labeled pixels.

Uses original224 images and original coordinates, not resized annotations.
This tests generation support, not corrected outputs or model performance.
"""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support
from src.skin_masking.material_checked_support import material_checked_support


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json'
    label_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(label_path.read_text())
    assert not labels['draft'] and labels['manifest_sha256']==digest(manifest)
    label_map={r['point_id']:r['label'] for r in labels['labels']}
    output=ROOT/'outputs/hair_clean_generation_v1/labeled_generation_regression.json'
    if output.exists():raise FileExistsError(output)
    tracked=[manifest,label_path,Path(__file__),ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,
             ROOT/'scripts/11_prepare_training_manifests.py']
    image_paths={image_id:ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1]
                 for image_id in {p['image_id'] for p in points}}
    tracked+=list(image_paths.values())
    hashes={str(p):digest(p) for p in tracked}
    segmenter=SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    observations=[]
    try:
        for image_id,path in sorted(image_paths.items()):
            image=cv2.imread(str(path));boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
            if len(boxes)!=1:raise ValueError('Expected single face '+image_id)
            x,y,w,h=boxes[0]
            result=prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,boxes[0],
                      ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
            if not result.landmarks_available:raise ValueError('Unavailable landmarks '+image_id)
            original=np.zeros(image.shape[:2],bool);original[y:y+h,x:x+w]=result.mask>0
            categories=segmenter.categories_bgr(image)
            cleaned=hair_veto_support(categories,original)
            assert not np.any(cleaned&~original)
            # Existing correction option still provides its material check;
            # do not substitute the generation mask for correction support.
            material=np.zeros_like(original)
            material[y:y+h,x:x+w]=material_checked_support(image[y:y+h,x:x+w],result.mask>0,result.exclusion_mask>0)
            correction=hair_veto_support(categories,material)
            for point in [p for p in points if p['image_id']==image_id]:
                assert image.shape[:2]==(point['height'],point['width'])
                px,py=point['x'],point['y']
                observations.append(dict(point_id=point['point_id'],image_id=image_id,label=label_map[point['point_id']],
                    original_generation=bool(original[py,px]),hair_clean_generation=bool(cleaned[py,px]),
                    existing_clean_correction_support=bool(correction[py,px])))
        assert len(observations)==24
        assert hashes=={p:digest(p) for p in hashes}
        counts={label:dict(total=sum(p['label']==label for p in observations),
                    original_generation=sum(p['label']==label and p['original_generation'] for p in observations),
                    hair_clean_generation=sum(p['label']==label and p['hair_clean_generation'] for p in observations),
                    existing_clean_correction_support=sum(p['label']==label and p['existing_clean_correction_support'] for p in observations))
                    for label in sorted({p['label'] for p in observations})}
        report=dict(status='complete',observations=observations,counts=counts,input_sha256=hashes,
                    limitation='24 development-selected clean-image pixels, not area accuracy or new shifted-image regression. Generation mask is not correction support. No paint classifier added.')
        output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(counts,indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
