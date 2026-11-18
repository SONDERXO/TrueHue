"""Matched old/new availability, scores, support and target-only review boards."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.segmentation_appearance_probe import parser_input
P=ROOT/'outputs/detector_appearance_merged_v1';E=ROOT/'outputs/detector_appearance_correction_v1';OLD=ROOT/'outputs/input_derived_correction_v1';BASE=ROOT/'outputs/input_derived_mask_check_v1';O=ROOT/'outputs/detector_appearance_comparison_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if O.exists():raise FileExistsError(O)
    data=read(E/'results_PRIVATE.json');prior=read(OLD/'results_PRIVATE.json');old={r['case_id']:r for r in prior['records']};masks=read(P/'results_PRIVATE.json')['records'];records={r['case_id']:r for r in data['records']};untargeted=0;targets=[];traces=0
    O.mkdir()
    for s in masks:
        cid=s['case_id'];r=records[cid];prev=old[cid]
        if not s['detector_fallback_target']:
            assert r==prev
            for name in r['paths']:assert sha(E/cid/(name+'.png'))==sha(OLD/cid/(name+'.png'))
            untargeted+=1;continue
        targets.append(cid);folder=Path(s['artifact_root']);image=cv2.imread(s['source_path']);ref=cv2.imread(str(ROOT/'outputs/frozen_split_subject_check_v1'/s['source_case']/'source.jpeg'))
        for index,t in enumerate(s['detector_trace']):
            if index==0:detectorinput=cv2.resize(image,(256,256),interpolation=cv2.INTER_LINEAR)
            else:
                native=cv2.imread(str(folder/'native_crop.png'));detectorinput=cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR)
            assert sha_bytes(detectorinput)==t['original_input_sha256']
            if t['fallback_attempted']:
                assert t['original_boxes']==[];assert sha_bytes(parser_input(detectorinput))==t['enhanced_input_sha256'];assert t['accepted']==(len(t['enhanced_boxes'])==1)
            else:assert len(t['original_boxes'])!=0
            traces+=1
        overlay=image.copy();mask=cv2.imread(str(folder/'native_grid.png'),0)>0 if s['status']=='success' else np.zeros(image.shape[:2],bool);overlay[mask]=np.rint(.6*image[mask]+.4*np.array([0,255,0])).astype(np.uint8)
        panels=[ref,image,overlay,cv2.imread(str(OLD/cid/'input_gated.png')),cv2.imread(str(E/cid/'input_gated.png'))]
        title=np.full((28,1120,3),255,np.uint8);cv2.putText(title,cid+' '+s['status']+' original|input|candidate mask|old gated|new gated',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.37,(0,0,0),1)
        assert cv2.imwrite(str(O/(cid+'.png')),np.vstack([title,np.hstack(panels)]))
    assert untargeted==288 and len(targets)==48
    bylayer={}
    for layer in ['clean','core','composite_stress_design']:
        rr=[records[cid] for cid in targets if records[cid]['layer']==layer]
        bylayer[layer]=dict(target_attempts=len(rr),recovered_measurements=sum(r['features'] is not None for r in rr),gated_actions=sum(r['gate'] is not None and r['gate']['apply_correction'] for r in rr),gated_full_scene_harms=sum(r['paths']['input_gated']['scene_metrics']['rgb8_mae_codes']>r['paths']['unchanged']['scene_metrics']['rgb8_mae_codes'] for r in rr))
    summary=dict(old_summary=prior['summary'],candidate_summary=data['summary'],target_layers=bylayer,unchanged_cases_exact=288,detector_trace_replays=traces,targets=targets,new_fits=0)
    (O/'comparison_PRIVATE.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (O/'review_PRIVATE.html').write_text('<!doctype html><h1>Private targeted zero-face fallback</h1><p>Original | input | candidate mask | old gated | new gated. All 48 targets, no new labels.</p>'+''.join('<img width="100%" src="'+cid+'.png">' for cid in targets),encoding='utf-8')
    for i in range(12):
        panels=[cv2.imread(str(O/(cid+'.png'))) for cid in targets[4*i:4*i+4]]
        assert cv2.imwrite(str(O/f'contact_{i+1:02d}.png'),np.vstack(panels))
    (O/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in O.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(dict(target_layers=bylayer,unchanged_cases_exact=288,detector_trace_replays=traces),indent=2))
def sha_bytes(a):return hashlib.sha256(a.tobytes()).hexdigest()
if __name__=='__main__':main()
