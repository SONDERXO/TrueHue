"""Prepare three unlabeled reference frames and a standalone offline polygon UI."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import cv2

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config=get_config()
    output=ROOT/'outputs/face_boundary_review_v1'
    tables=ROOT/'data/manifests/face_boundary_review_v1'
    if output.exists() or tables.exists():raise FileExistsError('Boundary review exists')
    tools=ROOT/'scripts/review_tools'
    sources=[
        ('40048',ROOT/'outputs/non_skin_regenerated_remaining28_v1/images/40048_reference.png',
         '40048: missed cheek boundary','Trace the visible facial skin, including the missed cheek on the right side of the image. Exclude hair, lips and eyes; do not copy the old detection box.'),
        ('16798',ROOT/config.DATA_RAW/'FairFace/train/16798.jpg',
         '16798: paint exclusion','Trace actual visible facial skin and exclude painted regions. Use Uncertain where skin versus paint is difficult to distinguish.'),
        ('60162',ROOT/'outputs/non_skin_regenerated_two_v1/images/60162_reference.png',
         '60162: face versus background','Trace cheek/jaw edges and exclude nearby background, hair, lips and eyes. Leave neck skin unmarked in this facial-only reference set.')]
    tracked=[p for _,p,_,_ in sources]+[tools/'face_boundary_annotation.js',tools/'face_boundary_review.html',
        ROOT/'data/manifests/material_review_v1/material_review_labels.json',
        ROOT/'data/manifests/development_exposure_additions.jsonl',ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    hashes={str(p):digest(p) for p in tracked}
    output.mkdir();tables.mkdir();(output/'images').mkdir()
    images=[];embedded=[]
    for ident,path,title,hint in sources:
        image=cv2.imread(str(path))
        if image is None:raise ValueError('Unreadable reference '+str(path))
        h,w=image.shape[:2]
        assert (w,h)==((224,224) if ident=='16798' else (256,256))
        target=output/'images'/(ident+'_reference.png')
        assert cv2.imwrite(str(target),image)
        record=dict(image_id='fairface__train/'+ident+'.jpg',title=title,hint=hint,width=w,height=h,
            source_path=path.relative_to(ROOT).as_posix(),source_sha256=digest(path),
            image_path=target.relative_to(ROOT).as_posix(),image_sha256=digest(target),
            annotation_status='unlabeled_pending_user',known_development_exposure=True)
        images.append(record);embedded.append({**record,'data_url':'data:image/png;base64,'+base64.b64encode(target.read_bytes()).decode()})
    manifest=dict(version='face_boundary_review_v1',prepared_date='2026-10-25',images=images,
        labels=dict(skin='Visible facial skin intended for correction',exclude='Intentional non-skin/feature exclusions',uncertain='Unclear boundary; not usable as positive/negative reference'),
        label_priority=['exclude','uncertain','skin'],outside_polygons='unlabeled, not automatic negative',
        scope='Three development-selected frames from three known sources; no prior masks/labels prefilled. Facial reference guide only, not final evaluation or calibrated skin-color truth. Neck left unmarked, not rejected.',
        coordinate_system='Exact saved-image pixels; no resizing of annotation coordinates.16798 retains native224frame; other two are existing256reference frames.')
    manifest_path=tables/'review_manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    payload=dict(version=manifest['version'],manifest_sha256=digest(manifest_path),images=embedded)
    html=(tools/'face_boundary_review.html').read_text(encoding='utf-8').replace('__REVIEW_PAYLOAD__',json.dumps(payload).replace('<','\\u003c')).replace('__REVIEW_APPLICATION__',(tools/'face_boundary_annotation.js').read_text(encoding='utf-8'))
    assert '__REVIEW_' not in html
    (output/'review.html').write_text(html,encoding='utf-8')
    assert hashes=={p:digest(Path(p)) for p in hashes}
    (output/'preparation.json').write_text(json.dumps(dict(status='prepared_unlabeled',images=3,manifest_sha256=digest(manifest_path),input_sha256=hashes,models_fitted=0,new_exposures=0,annotations_supplied=0),indent=2),encoding='utf-8')
    print('Prepared standalone annotation page:3 known references, no prefilled labels, no masks/models/ledger changed.')


if __name__=='__main__':main()
