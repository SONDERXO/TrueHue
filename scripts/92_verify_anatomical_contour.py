"""Independent morphology replay of script91 outputs and feature checks."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mask(path):
    value = cv2.imread(str(path),0)
    assert value is not None and set(np.unique(value)).issubset({0,255})
    return value > 0


def main():
    config = get_config()
    output = ROOT/'outputs/anatomical_contour_v1'
    summary = json.loads((output/'summary.json').read_text())
    sources,pairs = {},{}
    for folder in ('non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1'):
        parent=ROOT/'outputs'/folder/'images'
        for path in parent.glob('*_reference.png'):
            sources[path.stem.removesuffix('_reference')]=parent
        for path in parent.glob('*_input.png'):
            pairs[path.stem.removesuffix('_input')]=parent
    replayed=0
    features=0
    cheek=[]
    segmenter=SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    output_hashes={str(p.relative_to(ROOT)):digest(p) for p in (output/'masks').glob('*.png')}
    try:
        for record in summary['records']:
            key,ident=record['key'],record['image_id']
            if key.endswith('_source'):
                parent=sources[ident]
                image=cv2.imread(str(parent/(ident+'_reference.png')))
                old={'generation':mask(parent/(ident+'_generation.png'))}
                seeds=old['generation']
            elif '_regression_' in key:
                variant=record['variant']
                image_id='fairface__'+('val/' if ident=='10480' else 'train/')+ident+'.jpg'
                image=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1]))
                if variant!='clean':
                    image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                cats=segmenter.categories_bgr(image)
                stem=image_id.replace('/','_')+'_'+variant
                seeds=mask(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')) & np.isin(cats,[2,3])
                old={'measurement':seeds,'correction':mask(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')) & np.isin(cats,[2,3])}
                if variant=='clean':old['generation']=seeds.copy()
            else:
                parent=pairs[key]
                image=cv2.imread(str(parent/(key+'_input.png')))
                seeds=mask(parent/(key+'_baseline_estimate.png'))
                old={'measurement':seeds,'correction':mask(parent/(key+'_support.png'))}
            cats=segmenter.categories_bgr(image)
            excluded=mask(output/'geometry'/(key+'_expanded_excluded.png'))
            oval=mask(output/'geometry'/(key+'_oval.png'))
            x,y,w,h=record['geometry']['face_box']
            radius=max(1,math.ceil(.02*max(w,h)))
            yy,xx=np.mgrid[-radius:radius+1,-radius:radius+1]
            disk=((xx*xx+yy*yy)<=radius*radius).astype(np.uint8)
            near_oval=cv2.dilate(oval.astype(np.uint8),disk)>0
            bounds=np.zeros_like(oval)
            bounds[max(0,y-radius):min(image.shape[0],y+h+radius),max(0,x-radius):min(image.shape[1],x+w+radius)]=True
            lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
            sample=lab[seeds & ~excluded].astype(float)
            center=np.median(sample,axis=0)
            scale=np.maximum(np.median(np.abs(sample-center),axis=0)*1.4826,[12,6,6])
            distance=np.sqrt(np.square((lab-center)/scale).sum(axis=2))
            for stage,stage_record in record['stages'].items():
                original=old[stage]
                e=original & ~excluded
                for arm,item in stage_record['arms'].items():
                    saved=mask(output/'masks'/(key+'_'+stage+'_'+arm+'.png'))
                    if arm=='E' or stage=='measurement':
                        expected=e
                    else:
                        assert record['geometry']['extension_geometry_allowed']
                        assert len(sample)>=1000
                        near_old=cv2.dilate(original.astype(np.uint8),disk)>0
                        expected=(original | (near_old & near_oval & bounds & (cats==3) & (distance<=3))) & ~excluded
                    np.testing.assert_array_equal(saved,expected)
                    assert item['added_pixels']==int((saved & ~original).sum())
                    assert item['removed_pixels']==int((original & ~saved).sum())
                    if 'reference' in item:
                        labels=cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png')),0)
                        for interior,field in ((False,'reference'),(True,'interior_reference')):
                            positive=(labels==1).astype(np.uint8)
                            negative=(labels==3).astype(np.uint8)
                            if interior:
                                positive=cv2.erode(positive,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                                negative=cv2.erode(negative,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                            assert item[field]['selected_skin_pixels']==int(saved[positive>0].sum())
                            assert item[field]['selected_exclusion_pixels']==int(saved[negative>0].sum())
                    replayed+=1
                if ident=='40048' and stage!='measurement':
                    near_old=cv2.dilate(original.astype(np.uint8),disk)>0
                    cheek.append(dict(key=key,stage=stage,probe=[202,124],radius=radius,
                        semantic_class=int(cats[124,202]),relative_lab_distance=float(distance[124,202]),
                        near_old=bool(near_old[124,202]),near_oval=bool(near_oval[124,202]),
                        within_processing_bounds=bool(bounds[124,202]),excluded=bool(excluded[124,202])))
            if 'measurement_statistics' in record:
                saved=mask(output/'masks'/(key+'_measurement_E.png'))
                # Conventional Lab computed directly; use float32 like production conversion.
                encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32)
                encoded[:,:,0]*=100/255
                encoded[:,:,1:]-=128
                values=encoded[saved]
                means=[round(float(values[:,channel].mean()),4) for channel in range(3)]
                ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
                yy,xx=np.nonzero(saved)
                light=encoded[:,:,0]
                xm,ym=(xx.min()+xx.max())/2,(yy.min()+yy.max())/2
                p10,p25,p50,p75,p90=np.percentile(light[saved],[10,25,50,75,90],method='linear')
                bf=dict(input_l_p10=p10,input_l_median=p50,input_l_p90=p90,input_l_iqr=p75-p25,
                    input_l_left_minus_right=float(light[saved][xx<=xm].mean())-float(light[saved][xx>xm].mean()),
                    input_l_top_minus_bottom=float(light[saved][yy<=ym].mean())-float(light[saved][yy>ym].mean()))
                for arm in ('E','EC'):
                    entry=record['measurement_statistics'][arm]
                    stats=entry['statistics']
                    np.testing.assert_allclose([stats[k] for k in ('mean_l_star','mean_a_star','mean_b_star','ita_degrees')],means+[ita],atol=1e-4,rtol=0)
                    for name,value in bf.items():
                        np.testing.assert_allclose(entry['brightness']['features'][name],value,atol=1e-4,rtol=0)
                features+=1
        assert replayed==196
        assert all(digest(ROOT/name)==value for name,value in summary['input_sha256'].items())
        assert all(digest(ROOT/name)==value for name,value in output_hashes.items())
        result=dict(status='pass',saved_masks_independently_replayed=replayed,
            measurement_feature_sets_verified=features,cheek_gate_diagnosis=cheek,
            verifier_sha256=digest(Path(__file__)),summary_sha256=digest(output/'summary.json'),
            output_mask_sha256=output_hashes,input_hashes_unchanged=True)
        (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k!='output_mask_sha256'},indent=2))
    finally:
        segmenter.close()


if __name__=='__main__':
    main()
