"""Verify new development parent masks from cached intermediates, no model calls."""
from pathlib import Path
import json,hashlib,sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
OUT=ROOT/'outputs/group_diversity_parent_screen_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json');plan=read(OUT/'plan_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    assert len(d['records'])==96 and [r['source_sha256'] for r in d['records']]==[r['source_sha256'] for r in plan['selection']]
    assert all(r['role']=='development_candidate' and not r['training_admitted'] and not r['calibration_admitted'] for r in d['records'])
    maskchecks=0;cropchecks=0;boards=[];selected=[];perband={};samples=[]
    for r in d['records']:
        folder=OUT/r['case_id'];scene=cv2.imread(str(folder/'scene_input.png'));assert scene is not None
        # Pixel replay of stored native crop/256 image and all stored parent masks.
        if (folder/'native_input.png').exists():
            b=r['input_bridge'];x0,y0,x1,y1=b['native_bounds'];native=cv2.imread(str(folder/'native_input.png'))
            assert np.array_equal(native,scene[y0:y1,x0:x1]);image=cv2.imread(str(folder/'input.png'))
            assert np.array_equal(image,cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR));cropchecks+=1
        if (folder/'parent_mask.png').exists():
            points=np.load(folder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
            mask=build_semantic_face_coverage(image,points,categories).mask
            if r['parent_report']['stage']=='nostril_measurement':mask[nostril_guard((256,256),points)]=0
            assert np.array_equal(mask,cv2.imread(str(folder/'parent_mask.png'),0))
            assert compute_masked_lab_statistics(image,mask,1000)==r['parent_report']['statistics']
            projected,account=native_projection(mask,b)
            assert np.array_equal(projected,cv2.imread(str(folder/'parent_native.png'),0)) and account==r['native_accounting'];maskchecks+=1
        if r['status']=='parent_available':samples.append(r['native_accounting']['selected_native_grid_locations'])
        band=r['score_interval'];perband.setdefault(band,dict(attempts=0,parent_available=0))
        perband[band]['attempts']+=1;perband[band]['parent_available']+=r['status']=='parent_available'
        # Fixed first recorded condition per publisher group, selected independently of outcome.
        if r['condition']!='F_cool_600':continue
        panel=scene.copy();nativepath=folder/'parent_native.png'
        if nativepath.exists():
            support=cv2.imread(str(nativepath),0)>0;panel[support]=np.rint(.5*panel[support]+.5*np.array([0,255,0])).astype(np.uint8)
        crop=cv2.imread(str(folder/'input.png')) if (folder/'input.png').exists() else np.zeros((256,256,3),np.uint8)
        crop=cv2.resize(crop,(224,224));overlay=crop.copy()
        if (folder/'parent_mask.png').exists():
            mask=cv2.resize(cv2.imread(str(folder/'parent_mask.png'),0),(224,224),interpolation=cv2.INTER_NEAREST)>0
            overlay[mask]=np.rint(.5*overlay[mask]+.5*np.array([0,255,0])).astype(np.uint8)
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,r['case_id']+' '+r['status']+' parentONLY original|nativegrid|crop|mask',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
        boards.append(np.vstack([title,np.hstack([scene,panel,crop,overlay])]))
        selected.append(r['case_id'])
    assert len(boards)==32
    sheets=OUT/'fixed_contact_sheets';sheets.mkdir(exist_ok=True)
    for i in range(0,len(boards),4):assert cv2.imwrite(str(sheets/f'{i//4:02d}.png'),np.vstack(boards[i:i+4]))
    result=dict(passed=True,records=96,native_crop_replays=cropchecks,parent_mask_stat_projection_replays=maskchecks,
        parent_available_native_pixels_min=min(samples),parent_available_native_pixels_max=max(samples),by_descriptive_interval=perband,
        fixed_visual_cases=selected,visual_selection='First fixed condition F_cool_600 for each of32development groups; not outcome selected',
        source_hashes=len(bound),result_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),new_model_forwards=0,new_fits=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
