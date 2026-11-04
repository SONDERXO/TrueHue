"""Fixed full-image versus saved crop-landmark E/EC ablation; no fitting."""
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
from src.skin_masking.landmark_exclusion import detect_face_landmarks
from src.skin_masking.anatomical_contour_experiment import anatomy,removal,extend
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.distortion_generation.generate_distortions import transform_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_mask(path):
    value=cv2.imread(str(path),0)
    assert value is not None and set(np.unique(value)).issubset({0,255})
    return value>0


def main():
    config=get_config();prior=ROOT/'outputs/anatomical_contour_v1';output=ROOT/'outputs/landmark_framing_v1'
    if output.exists():raise FileExistsError(output)
    baseline=json.loads((prior/'summary.json').read_text())
    scoring=importlib.import_module('90_score_face_boundary_references')
    brightness=importlib.import_module('72_audit_brightness_features')
    ycb=importlib.import_module('56_compare_ycrcb_estimation')
    tracked=[Path(__file__),ROOT/'docs/landmark-framing-protocol.md',prior/'summary.json',prior/'verification.json']
    tracked+=list((prior/'masks').glob('*.png'))
    hashes=dict(baseline['input_sha256'])
    hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    sources,pairs={},{}
    for folder in ('non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1'):
        parent=ROOT/'outputs'/folder/'images'
        for path in parent.glob('*_reference.png'):sources[path.stem.removesuffix('_reference')]=parent
        for path in parent.glob('*_input.png'):pairs[path.stem.removesuffix('_input')]=parent
    point_spec=json.loads((ROOT/'data/manifests/material_review_v1/review_manifest.json').read_text())
    points=point_spec['points']
    label_map={r['point_id']:r['label'] for r in json.loads((ROOT/'data/manifests/material_review_v1/material_review_labels.json').read_text())['labels']}
    refs={i:cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(i+'_labels.png')),0) for i in ('40048','60162','16798')}
    output.mkdir()
    for name in ('geometry','masks','boards'):(output/name).mkdir()
    (output/'protocol.md').write_bytes((ROOT/'docs/landmark-framing-protocol.md').read_bytes())
    (output/'run_status.json').write_text('{"status":"running"}')
    segmenter=SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    records,observations,boards,sentinels=[],[],{},[]
    replayed=0

    def geometry(image,box,key,cats):
        detection=detect_face_landmarks(image,str(ROOT/config.FACE_LANDMARKER_MODEL_PATH))
        if not detection.landmarks_available:raise ValueError(detection.status)
        points=detection.landmarks
        original,excluded,oval,details=anatomy(image,points)
        x,y,w,h=box;pad=max(2,int(np.ceil(.10*max(w,h))))
        x0,y0,x1,y1=max(0,x-pad),max(0,y-pad),min(image.shape[1],x+w+pad),min(image.shape[0],y+h+pad)
        proposal=ycb.ycrcb_mask(image[y0:y1,x0:x1],original[y0:y1,x0:x1]) & np.isin(cats[y0:y1,x0:x1],[2,3])
        ratio=float((proposal & oval[y0:y1,x0:x1]).sum()/proposal.sum()) if proposal.any() else 0.
        np.save(output/'geometry'/(key+'_landmarks.npy'),points)
        np.save(output/'geometry'/(key+'_categories.npy'),cats)
        for name,value in [('original_excluded',original),('expanded_excluded',excluded),('oval',oval)]:
            assert cv2.imwrite(str(output/'geometry'/(key+'_'+name+'.png')),value.astype(np.uint8)*255)
        return excluded,oval,dict(face_box=box,status=detection.status,oval_retention=ratio,extension_geometry_allowed=ratio>=.75,**details)

    try:
        for old_record in baseline['records']:
            key,ident=old_record['key'],old_record['image_id']
            generation=None
            if key.endswith('_source'):
                parent=sources[ident];image=cv2.imread(str(parent/(ident+'_reference.png')))
                original={'generation':read_mask(parent/(ident+'_generation.png'))};measurement=original['generation']
            elif '_regression_' in key:
                variant=old_record['variant'];image_id=next(p['image_id'] for p in points if Path(p['image_id']).stem==ident)
                image=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1]))
                if variant!='clean':image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                cats=segmenter.categories_bgr(image);stem=image_id.replace('/','_')+'_'+variant
                measurement=read_mask(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')) & np.isin(cats,[2,3])
                original={'measurement':measurement,'correction':read_mask(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')) & np.isin(cats,[2,3])}
                if variant=='clean':original['generation']=measurement.copy()
            else:
                parent=pairs[key];image=cv2.imread(str(parent/(key+'_input.png')))
                measurement=read_mask(parent/(key+'_baseline_estimate.png'))
                original={'measurement':measurement,'correction':read_mask(parent/(key+'_support.png'))}
                generation=read_mask(parent/(ident+'_generation.png'))
            cats=segmenter.categories_bgr(image);box=old_record['geometry']['face_box']
            record=dict(key=key,image_id=ident,status='full_frame_unavailable',stages={})
            try:
                excluded,oval,geo=geometry(image,box,key,cats)
                record.update(status='available',geometry=geo)
            except ValueError as error:record['reason']=str(error)
            for stage,old in original.items():
                arms={};availability=dict(status='unavailable',reason=record.get('reason'))
                if record['status']=='available':
                    arms['E']=removal(old,excluded)
                    if stage=='measurement':arms['EC']=arms['E'].copy();availability=dict(status='measurement_equals_E')
                    else:
                        try:
                            arms['EC'],detail=extend(image,old,excluded,oval,cats,measurement,box,geo['extension_geometry_allowed'])
                            availability=dict(status='available',**detail)
                        except ValueError as error:availability=dict(status='unavailable',reason=str(error))
                stage_result=dict(EC_availability=availability,arms={})
                for arm,value in arms.items():
                    assert cv2.imwrite(str(output/'masks'/(key+'_'+stage+'_'+arm+'.png')),value.astype(np.uint8)*255)
                    # Independent disk-morphology replay of bounded growth.
                    expected=old & ~excluded
                    if arm=='EC' and stage!='measurement':
                        x,y,w,h=box;r=max(1,int(np.ceil(.02*max(w,h))))
                        yy,xx=np.mgrid[-r:r+1,-r:r+1];disk=(xx*xx+yy*yy<=r*r).astype(np.uint8)
                        nearold=cv2.dilate(old.astype(np.uint8),disk)>0;nearoval=cv2.dilate(oval.astype(np.uint8),disk)>0
                        bounds=np.zeros_like(old);bounds[max(0,y-r):min(image.shape[0],y+h+r),max(0,x-r):min(image.shape[1],x+w+r)]=True
                        lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB);sample=lab[measurement & ~excluded].astype(float)
                        center=np.median(sample,axis=0);scale=np.maximum(1.4826*np.median(abs(sample-center),axis=0),[12,6,6])
                        consistent=np.sqrt(np.square((lab-center)/scale).sum(axis=2))<=3
                        expected=(old | (nearold & nearoval & bounds & (cats==3) & consistent)) & ~excluded
                    np.testing.assert_array_equal(read_mask(output/'masks'/(key+'_'+stage+'_'+arm+'.png')),expected);replayed+=1
                    item=dict(pixels=int(value.sum()),added_pixels=int((value & ~old).sum()),removed_pixels=int((old & ~value).sum()))
                    if ident in refs:
                        item.update(reference=scoring.score(value,refs[ident]),interior_reference=scoring.score(value,refs[ident],True))
                    if ident=='40048':item['cheek_202_124_selected']=bool(value[124,202])
                    stage_result['arms'][arm]=item
                record['stages'][stage]=stage_result
                if stage=='measurement' and arms:
                    stats=compute_masked_lab_statistics(image,arms['E'].astype(np.uint8)*255,1000)
                    feature=brightness.brightness_features(image,arms['E'])
                    record['measurement_statistics']=dict(statistics=stats,brightness=feature)
                if stage=='correction' and generation is not None:
                    record['retention_old_generation_denominator']={a:support_retention(generation,removal(measurement,excluded),v) for a,v in arms.items()}
                tiles=[]
                for arm in ('E','EC'):
                    for framing,value in [('Crop',read_mask(prior/'masks'/(key+'_'+stage+'_'+arm+'.png')) if arm in old_record['stages'][stage]['arms'] else None),('Full',arms.get(arm))]:
                        shown=image.copy()
                        if value is not None:shown[value]=np.rint(.55*shown[value]+[0,99,0]).astype(np.uint8)
                        shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
                        cv2.putText(shown,key+' '+stage,(3,11),cv2.FONT_HERSHEY_SIMPLEX,.25,(255,255,255),1)
                        cv2.putText(shown,framing+' '+arm+(' UNAVAILABLE' if value is None else ''),(3,23),cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1)
                        tiles.append(shown)
                boards.setdefault(ident,[]).append(np.hstack(tiles))
                if old_record.get('regression'):
                    for p in (p for p in points if Path(p['image_id']).stem==ident):
                        x,y=p['x'],p['y'];observations.append(dict(point_id=p['point_id'],variant=old_record['variant'],stage=stage,label=label_map[p['point_id']],
                            crop={a:bool(read_mask(prior/'masks'/(key+'_'+stage+'_'+a+'.png'))[y,x]) for a in old_record['stages'][stage]['arms']},
                            full={a:bool(v[y,x]) for a,v in arms.items()}))
            records.append(record)
        for old_geo in (r for r in baseline['geometry'] if 'sentinel' in r['key']):
            key=old_geo['key'];image=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace/train/83184.jpg'))
            if key.endswith('global_color_shift'):image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            try:
                _,_,geo=geometry(image,old_geo['face_box'],key,segmenter.categories_bgr(image));sentinels.append(dict(key=key,**geo))
            except ValueError as error:sentinels.append(dict(key=key,status='unavailable',reason=str(error)))
        for ident,rows in boards.items():
            for page,offset in enumerate(range(0,len(rows),4),1):assert cv2.imwrite(str(output/'boards'/f'{ident}_page{page}.png'),np.vstack(rows[offset:offset+4]))
        assert len(records)==53 and all(digest(ROOT/p)==h for p,h in hashes.items())
        summary=dict(status='complete_no_adoption_no_regeneration_no_fitting',records=records,point_observations=observations,sentinels=sentinels,
            independently_replayed_masks=replayed,input_sha256=hashes,models_fitted=0,
            limitations='Same legacy masks retain prior holes; full-frame E/EC is not a fresh segmentation rebuild. Compare unavailable denominators explicitly. Native regression inputs remain224.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'run_status.json').write_text('{"status":"complete"}')
        print(json.dumps(dict(records=len(records),full_available=sum(r['status']=='available' for r in records),replayed_masks=replayed,sentinels=sentinels)))
    finally:segmenter.close()


if __name__=='__main__':main()
