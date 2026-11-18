"""Independent cached service/render/projection replay; no inference or fitting."""
from pathlib import Path
from types import SimpleNamespace
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.skin_masking.correction_preview import render_preview
from src.model_training.aligned_correction_support import project_alpha
P=ROOT/'outputs/group_diversity_parent_screen_v1';OUT=ROOT/'outputs/group_diversity_final_masks_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'final_input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    prep=read(OUT/'preparation_PRIVATE.json');run=read(OUT/'inference.json');pred={r['image_id']:r for r in run['records']}
    assert run['plan_sha256']==sha(OUT/'inference_plan.json') and run['forwards']==83
    assert len(d['records'])==96 and len(pred)==83
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm'];checks=0;protected_pixels=0;available=0
    for r,old in zip(d['records'],prep['records'],strict=True):
        assert r['case_id']==old['case_id'] and r['role']=='development_candidate'
        assert not r['training_admitted'] and not r['calibration_admitted'] and not r['scientific_admission'] and r['MST'] is None
        if old['status']!='inference_ready':assert r['status']=='unavailable' and not r['final_masking_available'];continue
        folder=OUT/r['case_id'];parent=P/r['case_id'];image=cv2.imread(str(parent/'input.png'));facial=cv2.imread(str(parent/'parent_mask.png'),0)
        points=np.load(parent/'landmarks.npy',allow_pickle=False);cat=cv2.imread(str(parent/'categories.png'),0)
        prediction=pred[r['case_id']];path=OUT/prediction['logits_path'];assert sha(path)==prediction['logits_sha256'];logits=np.load(path,allow_pickle=False)
        result=evaluate_parent(SimpleNamespace(report=r['parent_report'],image=image,mask=facial),points,template,lambda _:logits)
        assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png'))) and result.report==r['measurement_report']
        assert np.array_equal(result.mask,cv2.imread(str(folder/'measurement_mask.png'),0)) and not ((result.mask>0)&(facial==0)).any()
        native,account=native_projection(result.mask,r['input_bridge'])
        assert np.array_equal(native,cv2.imread(r['measurement_native_path'],0)) and account==r['native_measurement_accounting']
        visible=map_visible_mask((logits>0).astype(np.uint8)*255,(256,256),result.matrix)
        preview=render_preview(image,facial,cat,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
        assert preview.report==r['correction_report'] and np.array_equal(preview.output,image)
        alpha,protected=project_alpha(preview.alpha,preview.protected,r['input_bridge'])
        np.testing.assert_array_equal(alpha,np.load(r['alpha_path'],allow_pickle=False))
        assert np.array_equal(protected,cv2.imread(r['protected_path'],0)>0) and not alpha[protected].any()
        # Independent native interpolation/protection reconstruction.
        x0,y0,x1,y1=r['input_bridge']['native_bounds'];expected=np.zeros((224,224),float)
        local=cv2.resize(preview.alpha,(x1-x0,y1-y0),interpolation=cv2.INTER_LINEAR)
        veto=cv2.resize(preview.protected.astype(np.float32),(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)>0;local[veto]=0
        expected[y0:y1,x0:x1]=local;np.testing.assert_array_equal(alpha,expected)
        ready=result.report['status']=='success' and bool(np.any(alpha))
        assert (r['status']=='available')==ready and r['final_masking_available']==ready
        if ready:
            assert r['raw_features']=={k:result.report['features'][k] for k in r['raw_features']};available+=1
        else:assert r['raw_features'] is None
        protected_pixels+=int(protected.sum());checks+=1
    assert checks==83 and available==d['summary']['available']
    result=dict(passed=True,attempts=96,cached_service_replays=checks,identity_support_replays=checks,
        native_measurement_replays=checks,independent_alpha_protection_replays=checks,
        protected_pixel_occurrences=protected_pixels,available=available,source_hashes=len(bound),new_fits=0,new_forwards=0,
        holdout_image_reads=0,verifier_sha256=sha(Path(__file__)),result_sha256=sha(OUT/'results_PRIVATE.json'))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
