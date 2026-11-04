"""Independent algebra, raster, transform and feature replay of saved diagnostics."""
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    a=cv2.imread(str(p),0);assert a is not None and set(np.unique(a))<={0,255}
    return a>0
def polygon(points,w,h):
    a=np.asarray(points,np.float32)
    return np.array([[cv2.pointPolygonTest(a,(float(x),float(y)),False)>=0 for x in range(w)] for y in range(h)])
def main():
    out=ROOT/'outputs/paint_protection_validation_v1';sp=out/'summary.json';data=json.loads(sp.read_text())
    manifest=json.loads((ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json').read_text())
    frames={f['frame_id']:f for f in manifest['frames']};regions={};user={}
    export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text())
    # Independently restore every original label using pixel-center point tests.
    for f in export['images']:
        ident=Path(f['image_id']).stem;spec=frames[ident];w,h=spec['width'],spec['height'];labels=np.zeros((h,w),np.uint8)
        for v,name in enumerate(['skin','uncertain','exclude'],1):
            for p in f['polygons']:
                if p['label']==name:labels[polygon(p['points'],w,h)]=v
        np.testing.assert_array_equal(labels,cv2.imread(str(ROOT/spec['annotation']['labels_path']),0));user[ident]=labels
        if ident=='16798':
            paint=np.zeros((h,w),bool)
            for p in f['polygons'][:6]:paint|=polygon(p['points'],w,h)
            regions[ident]={'user_paint':paint&(labels==3),'user_features':(labels==3)&~paint}
        else:regions[ident]={'user_features':labels==3}
    for f in frames.values():
        if f['annotation'].get('regions'):regions[f['frame_id']]={r['region_id']:polygon(r['points'],f['width'],f['height']) for r in f['annotation']['regions']}
    masks=features=references=region_checks=transforms=0
    for row in data['records']:
        key=row['key'];ident=row['frame_id'];spec=frames[ident];original=cv2.imread(str(ROOT/spec['source_path']))
        if row['recipe'] is None:want=original.copy();clipped=0
        else:
            recipe=row['recipe'];rgb=original[:,:,::-1].astype(np.float64)/255
            raw=(rgb**(1/recipe['gamma']))*np.array([recipe['red_gain'],1,recipe['blue_gain']])
            clipped=int(np.any((raw<0)|(raw>1),axis=2).sum());want=np.rint(np.clip(raw,0,1)*255).astype(np.uint8)[:,:,::-1]
        image=cv2.imread(str(out/'images'/(key+'.png')));np.testing.assert_array_equal(image,want)
        assert row['clipped_pixels']==clipped and row['image_sha256']==digest(out/'images'/(key+'.png'));transforms+=1
        assert row['recipe_sha256']==hashlib.sha256(json.dumps(row['recipe'],sort_keys=True).encode()).hexdigest()
        if row['status']!='available':
            assert row['stages']=={} and not list((out/'masks').glob(key+'_*.png'));continue
        ing=out/'ingredients';anchor=read(ing/(key+'_anchor.png'));excluded=read(ing/(key+'_excluded.png'))
        dense=cv2.imread(str(ing/(key+'_parser.png')),0);cats=cv2.imread(str(ing/(key+'_semantic.png')),0)
        assert dense.max()<=18 and cats.max()<=5
        x,y,w,h=row['face_box'];pad=max(2,math.ceil(.1*max(w,h)));bounds=np.zeros(anchor.shape,bool)
        bounds[max(0,y-pad):min(anchor.shape[0],y+h+pad),max(0,x-pad):min(anchor.shape[1],x+w+pad)]=True
        base=np.isin(dense,[1,10])&(cats==3)&~excluded&bounds;seeds=base&anchor
        np.testing.assert_array_equal(seeds,read(ing/(key+'_seeds.png')));assert seeds.sum()>=1000
        lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB);sample=lab[seeds].astype(float)
        center=np.median(sample,axis=0);scale=np.maximum(1.4826*np.median(abs(sample-center),axis=0),[12,6,6])
        np.testing.assert_allclose(row['material']['median'],center,rtol=0,atol=1e-10)
        np.testing.assert_allclose(row['material']['scale'],scale,rtol=0,atol=1e-10)
        z=((lab-center)/scale)**2;f=base&(np.sqrt(z.sum(axis=2))<=3);c=base&(np.sqrt(z[:,:,1:].sum(axis=2))<=3)
        # Exact integer disk of radius2 is independent of OpenCV distanceTransform.
        disk=np.array([[int(i*i+j*j<=4) for i in range(-2,3)] for j in range(-2,3)],np.uint8)
        near=cv2.dilate((base&~c).astype(np.uint8),disk,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
        arms={'A':base,'F':f,'C':c,'C2':c&~near}
        for stage,items in row['stages'].items():
            for arm,item in items.items():
                saved=read(out/'masks'/(key+'_'+stage+'_'+arm+'.png'));want=arms[arm]&anchor if stage=='measurement' else arms[arm]
                np.testing.assert_array_equal(saved,want);assert item['pixels']==int(saved.sum());masks+=1
                for name,r in regions.get(ident,{}).items():
                    interior=cv2.erode(r.astype(np.uint8),np.ones((3,3),np.uint8))>0
                    assert item['protected_regions'][name]==dict(pixels=int(r.sum()),selected=int(saved[r].sum()),interior_pixels=int(interior.sum()),interior_selected=int(saved[interior].sum()));region_checks+=1
                if ident in user:
                    labels=user[ident]
                    for field,erode in [('user_reference',False),('user_interior_reference',True)]:
                        positive=labels==1;negative=labels==3
                        if erode:
                            positive=cv2.erode(positive.astype(np.uint8),np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
                            negative=cv2.erode(negative.astype(np.uint8),np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
                        v=item[field];assert v['labeled_skin_pixels']==int(positive.sum()) and v['labeled_exclusion_pixels']==int(negative.sum())
                        assert v['selected_skin_pixels']==int(saved[positive].sum()) and v['selected_exclusion_pixels']==int(saved[negative].sum());references+=1
                if stage!='measurement':continue
                lab8=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);lab8[:,:,0]*=100/255;lab8[:,:,1:]-=128
                pixels=lab8[saved];st=item['statistics'];bf=item['brightness'];assert st['valid'] and bf['valid'] and len(pixels)>=1000
                means=[round(float(pixels[:,i].mean()),4) for i in range(3)];ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
                np.testing.assert_allclose([st[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']],means+[ita],rtol=0,atol=1e-4)
                yy,xx=np.nonzero(saved);L=pixels[:,0];xm,ym=(xx.min()+xx.max())/2,(yy.min()+yy.max())/2
                q10,q25,q50,q75,q90=np.percentile(L,[10,25,50,75,90],method='linear')
                values=dict(input_l_p10=q10,input_l_median=q50,input_l_p90=q90,input_l_iqr=q75-q25,
                    input_l_left_minus_right=float(L[xx<=xm].mean())-float(L[xx>xm].mean()),input_l_top_minus_bottom=float(L[yy<=ym].mean())-float(L[yy>ym].mean()))
                for name,v in values.items():np.testing.assert_allclose(bf['features'][name],v,rtol=0,atol=1e-4)
                features+=1
    assert all(digest(ROOT/p)==h for p,h in data['input_sha256'].items())
    result=dict(status='pass',diagnostic_transforms_replayed=transforms,masks_replayed=masks,measurement_feature_sets=features,
        user_reference_count_checks=references,protected_region_checks=region_checks,original_rasters_reconstructed=3,
        summary_sha256=digest(sp),verifier_sha256=digest(Path(__file__)),input_hashes_unchanged=True,
        limitation='Replay conditional on saved model outputs/geometry; no independent model accuracy or phone parity claim',
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for folder in ['images','ingredients','masks','boards'] for p in (out/folder).iterdir() if p.is_file()})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
