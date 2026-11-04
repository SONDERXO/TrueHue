"""Audit cached semantic classes against fixed references; no inference or masks."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.skin_masking.selfie_material_segmenter import LABELS
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def histogram(categories,region):
    counts=np.bincount(categories[region],minlength=6)
    total=int(region.sum())
    assert int(counts.sum())==total
    return dict(pixels=total,categories={name:int(counts[i]) for i,name in enumerate(LABELS)},
                face_skin_selected=int(counts[3]),face_or_body_skin_selected=int(counts[2]+counts[3]))


def main():
    output=ROOT/'outputs/semantic_reference_audit_v1';parent=ROOT/'outputs/landmark_framing_v1'
    if (output/'summary.json').exists():raise FileExistsError('Audit already exists')
    output.mkdir(exist_ok=True);(output/'boards').mkdir(exist_ok=True)
    framing=json.loads((parent/'summary.json').read_text())
    refs=ROOT/'data/manifests/face_boundary_reference_v1/original_export.json'
    export=json.loads(refs.read_text());manifest_path=ROOT/'data/manifests/face_boundary_review_v1/review_manifest.json'
    manifest=json.loads(manifest_path.read_text());assert digest(manifest_path)==export['manifest_sha256']
    assert digest(refs)=='3e4915b76bb1799fc23bbdedf20162f8757760d05520fe916a2bae4d5a8b9553'
    annotations={Path(a['image_id']).stem:a for a in export['images']}
    reference_records={Path(a['image_id']).stem:a for a in manifest['images']}
    raster=importlib.import_module('90_score_face_boundary_references')
    # Codex visual descriptions of EXISTING exclusions; not new reviewer labels.
    roles={'40048':{'features':[1,2,4,5,6],'paint':[]},
           '60162':{'features':[2,3,4,5,6,7,8],'paint':[]},
           '16798':{'features':[7,8,9,10,11,12,13],'paint':[1,2,3,4,5,6]}}
    tracked=[Path(__file__),refs,manifest_path,parent/'summary.json',parent/'verification.json',
             ROOT/'docs/semantic-reference-audit-protocol.md']
    tracked+=list((parent/'geometry').glob('*_categories.npy'))
    tracked+=[ROOT/'outputs/face_boundary_reference_v1/labels'/(i+'_labels.png') for i in roles]
    hashes=dict(framing['input_sha256']);hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    records,reference_results,point_results=[],[],[]
    groups={}
    for ident,annotation in annotations.items():
        ref=reference_records[ident];labels=cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png')),0)
        assert np.array_equal(labels,raster.rasterize(annotation['polygons'],ref['width'],ref['height']))
        feature=np.zeros(labels.shape,bool);paint=feature.copy();polygon_regions={}
        for role,indices in roles[ident].items():
            for index in indices:
                polygon=annotation['polygons'][index-1];assert polygon['label']=='exclude'
                selected=raster.polygon_pixels(polygon['points'],ref['width'],ref['height']) & (labels==3)
                polygon_regions[index]=selected
                if role=='paint':paint|=selected
                else:feature|=selected
        # Paint priority prevents double counting at touching/coarse polygon borders.
        feature &= ~paint
        assert np.array_equal(feature|paint,labels==3)
        groups[ident]=(labels,feature,paint,polygon_regions)
    spec=json.loads((ROOT/'data/manifests/material_review_v1/review_manifest.json').read_text())
    point_labels=json.loads((ROOT/'data/manifests/material_review_v1/material_review_labels.json').read_text())
    point_map={p['point_id']:p['label'] for p in point_labels['labels']}
    palette=np.array([[0,0,0],[100,100,100],[220,200,0],[0,180,0],[200,60,30],[0,140,255]],np.uint8)
    for path in sorted((parent/'geometry').glob('*_categories.npy')):
        key=path.stem.removesuffix('_categories');cats=np.load(path)
        assert cats.dtype==np.uint8 and cats.ndim==2 and cats.max()<=5
        record=dict(key=key,whole_frame=histogram(cats,np.ones(cats.shape,bool)))
        records.append(record)
        previous=next((r for r in framing['records'] if r['key']==key),None)
        if previous is None:continue  # sentinel histograms are not reference scores
        ident=previous['image_id']
        if ident in groups:
            labels,feature,paint,polygon_regions=groups[ident];assert cats.shape==labels.shape
            ref_result=dict(key=key,image_id=ident,regions={name:histogram(cats,region) for name,region in
                [('skin',labels==1),('feature_exclusions',feature),('paint_exclusions',paint),('uncertain',labels==2),('unlabeled',labels==0)]},
                polygons={str(index):histogram(cats,region) for index,region in polygon_regions.items()},
                face_skin=raster.score(cats==3,labels),face_or_body_skin=raster.score(np.isin(cats,[2,3]),labels),
                interior_face_skin=raster.score(cats==3,labels,True),interior_face_or_body_skin=raster.score(np.isin(cats,[2,3]),labels,True))
            reference_results.append(ref_result)
            if key.endswith('_source'):image=cv2.imread(str(ROOT/reference_records[ident]['image_path']))
            elif '_regression_' in key:
                image=cv2.imread(str(ROOT/reference_records[ident]['image_path']))
                if key.endswith('global_color_shift'):image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            else:
                paths=[p for folder in ('non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1') for p in (ROOT/'outputs'/folder/'images').glob(key+'_input.png')]
                assert len(paths)==1;image=cv2.imread(str(paths[0]))
            shown=image.copy();shown[(cats==3)&(labels==3)]=[0,0,255];shown[(cats!=3)&(labels==1)]=[255,100,0]
            panels=[]
            for title,img in [('Original',image),('Semantic classes',palette[cats]),('Face-only disagreements',shown)]:
                display=cv2.copyMakeBorder(img,24,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(display,title,(3,16),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(display)
            assert cv2.imwrite(str(output/'boards'/(key+'.png')),np.hstack(panels))
        if '_regression_' in key:
            variant=previous['key'].split('_regression_',1)[1]
            for point in spec['points']:
                if Path(point['image_id']).stem!=ident:continue
                assert cats.shape==(point['height'],point['width'])
                category=int(cats[point['y'],point['x']])
                point_results.append(dict(point_id=point['point_id'],image_id=ident,variant=variant,label=point_map[point['point_id']],category=category,category_name=LABELS[category]))
    assert len(records)==55 and len(reference_results)==9 and len(point_results)==48
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_read_only_semantic_reference_audit',records=records,references=reference_results,points=point_results,
        subgroup_description=dict(author='Codex visual inspection of numbered existing polygons',roles=roles,overlap_priority='paint before features',scope='Descriptive audit grouping only; original reviewer labels remain exclude'),
        input_sha256=hashes,models_fitted=0,new_inference_calls=0,
        limitations='55 cached maps are repeated known development sources, not55 independent sources. Class maps are argmax, not calibrated confidence. Semantic disagreement does not change reference labels or validate geometry. Unlabeled/uncertain regions not scored as negatives.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(dict(category_maps=55,reference_frames=9,point_observations=48,new_inference_calls=0)))


if __name__=='__main__':main()
