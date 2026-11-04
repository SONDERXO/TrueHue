"""Independent replay of both fixed parser/material cohorts and statistics."""
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    a=cv2.imread(str(path),0);assert a is not None
    return a>0


def main():
    verifier=Path(__file__);loader=importlib.import_module('96_test_dense_face_parser')
    originals={r['key']:r for r in json.loads((ROOT/'outputs/anatomical_contour_v1/summary.json').read_text())['records']}
    all_counts={}
    for folder in ['parser_material_core_v1','parser_material_historical_v1']:
        output=ROOT/'outputs'/folder;summary_path=output/'summary.json';summary=json.loads(summary_path.read_text())
        masks_verified=0;feature_sets=0;reference_checks=0
        for row in summary['records']:
            if row['status']!='available':continue
            key=row['key'];ident=row['image_id'];ingredients=output/'ingredients'
            dense=load(ingredients/(key+'_dense.png'));excluded=load(ingredients/(key+'_excluded.png'))
            cats=cv2.imread(str(ingredients/(key+'_categories.png')),0)
            parser_cats=cv2.imread(str(ingredients/(key+'_parser_categories.png')),0)
            np.testing.assert_array_equal(dense,np.isin(parser_cats,[1,10]))
            old_measurement=load(ingredients/(key+'_measurement.png'))
            if summary['historical']:
                parent=ROOT/'outputs/training_source60_variants_v1/images'
                image=cv2.imread(str(parent/(ident+'_reference.png' if key.endswith('_source') else key+'_input.png')))
                original={'generation':load(parent/(ident+'_generation.png'))} if key.endswith('_source') else dict(measurement=load(parent/(key+'_baseline_estimate.png')),correction=load(parent/(key+'_support.png')))
            else:image,original,_=loader.load_case(originals[key])
            x,y,w,h=row['material']['face_box'];pad=max(2,int(np.ceil(.10*max(w,h))))
            bounds=np.zeros(dense.shape,bool);bounds[max(0,y-pad):min(image.shape[0],y+h+pad),max(0,x-pad):min(image.shape[1],x+w+pad)]=True
            base=dense & (cats==3) & ~excluded & bounds;seeds=old_measurement & base
            np.testing.assert_array_equal(seeds,load(ingredients/(key+'_seeds.png')))
            lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB);sample=lab[seeds].astype(float)
            assert len(sample)>=1000
            center=np.median(sample,axis=0);scale=np.maximum(1.4826*np.median(np.abs(sample-center),axis=0),[12,6,6])
            normalized=np.square((lab-center)/scale)
            full=np.sqrt(normalized.sum(axis=2));chroma=np.sqrt(normalized[:,:,1:].sum(axis=2))
            np.testing.assert_allclose(np.load(ingredients/(key+'_distances.npy')),np.stack([full,chroma]),atol=1e-10,rtol=0)
            expected={'A':base,'F':base & (full<=3),'C':base & (chroma<=3)}
            for stage,item in row['stages'].items():
                for arm,value in item['arms'].items():
                    saved=load(output/'masks'/(key+'_'+stage+'_'+arm+'.png'));want=expected[arm] & original[stage] if stage=='measurement' else expected[arm]
                    np.testing.assert_array_equal(saved,want);masks_verified+=1
                    assert value['added_pixels']==int((saved&~original[stage]).sum())
                    assert value['removed_pixels']==int((original[stage]&~saved).sum())
                    if 'reference' in value:
                        labels=cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png')),0)
                        for erode,field in [(False,'reference'),(True,'interior_reference')]:
                            positive=(labels==1).astype(np.uint8);negative=(labels==3).astype(np.uint8)
                            if erode:
                                positive=cv2.erode(positive,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                                negative=cv2.erode(negative,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                            assert value[field]['selected_skin_pixels']==int(saved[positive>0].sum())
                            assert value[field]['selected_exclusion_pixels']==int(saved[negative>0].sum());reference_checks+=1
                    if stage=='measurement':
                        entry=row['measurement_statistics'][arm];st=entry['statistics'];bf=entry['brightness']
                        encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);encoded[:,:,0]*=100/255;encoded[:,:,1:]-=128
                        pixels=encoded[saved];assert len(pixels)>=1000
                        means=[round(float(pixels[:,i].mean()),4) for i in range(3)];ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
                        np.testing.assert_allclose([st[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']],means+[ita],atol=1e-4,rtol=0)
                        yy,xx=np.nonzero(saved);xm,ym=(xx.min()+xx.max())/2,(yy.min()+yy.max())/2;L=encoded[:,:,0][saved]
                        q10,q25,q50,q75,q90=np.percentile(L,[10,25,50,75,90],method='linear')
                        vals=dict(input_l_p10=q10,input_l_median=q50,input_l_p90=q90,input_l_iqr=q75-q25,
                            input_l_left_minus_right=float(L[xx<=xm].mean())-float(L[xx>xm].mean()),input_l_top_minus_bottom=float(L[yy<=ym].mean())-float(L[yy>ym].mean()))
                        assert st['valid'] and bf['valid']
                        for name,n in vals.items():np.testing.assert_allclose(bf['features'][name],n,atol=1e-4,rtol=0)
                        feature_sets+=1
        assert all(digest(ROOT/path)==h for path,h in summary['input_sha256'].items())
        result=dict(status='pass',masks_replayed=masks_verified,measurement_feature_sets=feature_sets,reference_count_checks=reference_checks,
            input_hashes_unchanged=True,summary_sha256=digest(summary_path),verifier_sha256=digest(verifier),
            output_sha256={str(p.relative_to(ROOT)):digest(p) for f in ['ingredients','masks'] for p in (output/f).iterdir() if p.is_file()})
        (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        all_counts[folder]={k:v for k,v in result.items() if k!='output_sha256'}
    assert sum(r['masks_replayed'] for r in all_counts.values())==804
    print(json.dumps(all_counts,indent=2))


if __name__=='__main__':main()
