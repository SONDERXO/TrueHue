"""Replay dense/veto masks and independent Lab/feature/reference calculations."""
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


def main():
    output=ROOT/'outputs/dense_face_parser_v1';summary_path=output/'summary.json'
    summary=json.loads(summary_path.read_text());baseline=json.loads((ROOT/'outputs/anatomical_contour_v1/summary.json').read_text())
    cases={r['key']:r for r in baseline['records']};loader=importlib.import_module('96_test_dense_face_parser')
    replayed=0;measurements=0;reference_scores=0
    for record in summary['records']:
        if record['status']!='available':continue
        key,ident=record['key'],record['image_id'];image,original,_=loader.load_case(cases[key])
        cats=cv2.imread(str(output/'categories'/(key+'.png')),0)
        assert cats.shape==image.shape[:2] and cats.max()<=18
        dense=np.logical_or(cats==1,cats==10)
        np.testing.assert_array_equal(cv2.imread(str(output/'masks'/(key+'_D.png')),0)>0,dense);replayed+=1
        if 'dense_reference' in record:
            labels=cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png')),0)
            for selected,full,interior in [(dense,record['dense_reference'],record['dense_interior_reference'])]+[
                (cv2.imread(str(output/'masks'/(key+'_'+stage+'_V.png')),0)>0,value['reference'],value['interior_reference']) for stage,value in record['stages'].items()]:
                for erode,metrics in [(False,full),(True,interior)]:
                    positive=(labels==1).astype(np.uint8);negative=(labels==3).astype(np.uint8)
                    if erode:
                        positive=cv2.erode(positive,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                        negative=cv2.erode(negative,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
                    assert metrics['selected_skin_pixels']==int(selected[positive>0].sum())
                    assert metrics['selected_exclusion_pixels']==int(selected[negative>0].sum())
                    reference_scores+=1
        for stage,mask in original.items():
            value=record['stages'][stage];saved=cv2.imread(str(output/'masks'/(key+'_'+stage+'_V.png')),0)>0
            np.testing.assert_array_equal(saved,mask & dense)
            assert value['removed_pixels']==int((mask & ~saved).sum())
            replayed+=1
        if 'measurement_statistics' in record:
            saved=cv2.imread(str(output/'masks'/(key+'_measurement_V.png')),0)>0
            lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);lab[:,:,0]*=100/255;lab[:,:,1:]-=128
            sample=lab[saved];means=[round(float(sample[:,i].mean()),4) for i in range(3)];ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
            stats=record['measurement_statistics']['statistics']
            np.testing.assert_allclose([stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']],means+[ita],atol=1e-4,rtol=0)
            yy,xx=np.nonzero(saved);xm,ym=(xx.min()+xx.max())/2,(yy.min()+yy.max())/2;L=lab[:,:,0][saved]
            p10,p25,p50,p75,p90=np.percentile(L,[10,25,50,75,90],method='linear')
            values=dict(input_l_p10=p10,input_l_median=p50,input_l_p90=p90,input_l_iqr=p75-p25,
                input_l_left_minus_right=float(L[xx<=xm].mean())-float(L[xx>xm].mean()),input_l_top_minus_bottom=float(L[yy<=ym].mean())-float(L[yy>ym].mean()))
            for name,value in values.items():np.testing.assert_allclose(record['measurement_statistics']['brightness']['features'][name],value,atol=1e-4,rtol=0)
            measurements+=1
    for variant in ['clean','global_color_shift']:
        key='83184_sentinel_'+variant;cats=cv2.imread(str(output/'categories'/(key+'.png')),0)
        np.testing.assert_array_equal(cv2.imread(str(output/'masks'/(key+'_D.png')),0)>0,np.isin(cats,[1,10]));replayed+=1
    assert replayed==158 and measurements==44
    assert all(digest(ROOT/p)==h for p,h in summary['input_sha256'].items())
    result=dict(status='pass',mask_replays=replayed,measurement_statistics_and_brightness_sets=measurements,
        reference_score_checks=reference_scores,input_hashes_unchanged=True,summary_sha256=digest(summary_path),verifier_sha256=digest(Path(__file__)),
        output_sha256={str(p.relative_to(ROOT)):digest(p) for folder in ['categories','masks'] for p in (output/folder).glob('*.png')},
        limitation='Postprocessing and scoring replay only; no independent ONNXRuntime/PyTorch backend parity or Android validation.')
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='output_sha256'},indent=2))


if __name__=='__main__':main()
