"""Independent rule reconstruction, user-point transitions and scope losses."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
PARENT=ROOT/'outputs/upper_face_measurement_candidate_v1'
SOURCE=ROOT/'outputs/stellenbosch_new_subjects_v1'
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
OUT=ROOT/'outputs/upper_face_measurement_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json');bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    old={r['case_id']:r for r in read(SOURCE/'results_PRIVATE.json')['records']};candidate=read(PARENT/'results_PRIVATE.json')
    domains={};checks=0;nativecounts=[]
    for r in candidate['records']:
        if r['case_id']=='case_29':assert r['status']=='failed';continue
        folder=SOURCE/r['case_id'];target=PARENT/r['case_id'];image=cv2.imread(str(folder/'input.png'))
        points=np.load(folder/'landmarks.npy',allow_pickle=False);cat=cv2.imread(str(folder/'categories.png'),0)
        geometry=build_face_coverage(image,points);excluded=(geometry.exclusion_mask>0)|nostril_guard((256,256),points)
        domain=(geometry.face_outline>0)&(np.arange(256)[:,None]<=points[2,1])&~excluded
        logits=np.load(SOURCE/old[r['case_id']]['logits_path'],allow_pickle=False);M=np.array(read(folder/'matrix.json'))
        visible=map_visible_mask(np.where(logits>0,255,0).astype(np.uint8),(256,256),M)>0
        expected=domain&visible&((cat==0)|(cat==1)|(cat==10))
        mask=cv2.imread(str(target/'mask.png'),0);assert np.array_equal(mask>0,expected)
        assert compute_masked_lab_statistics(image,mask,1000)==r['statistics'];checks+=1
        x0,y0,x1,y1=r['input_bridge']['native_bounds'];side=x1-x0;grid=np.zeros((224,224),np.uint8)
        grid[y0:y1,x0:x1]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
        assert np.array_equal(grid,cv2.imread(str(target/'native_grid.png'),0))
        nativecounts.append(int(np.count_nonzero(grid)));domains[r['case_id']]=cv2.resize(domain.astype(np.uint8),(side,side),interpolation=cv2.INTER_NEAREST)>0
    actual=read(IMPORTED/'actual_export_PRIVATE.json');bindings=read(REVIEW/'prediction_bindings_PRIVATE.json')
    transitions=Counter();percase=[];scope=Counter()
    for row in actual['rows']:
        binding=bindings[row['review_id']];case=binding['case_id'];counts=Counter()
        if binding['native_grid_path'] is None:
            percase.append(dict(review_id=row['review_id'],prediction='unavailable',points=len(row['points'])));continue
        x0,y0,x1,y1=binding['native_bounds']
        before=cv2.imread(binding['native_grid_path'],0)[y0:y1,x0:x1]>0
        after=cv2.imread(str(PARENT/case/'native_grid.png'),0)[y0:y1,x0:x1]>0
        for p in row['points']:
            if p['label']=='uncertain':continue
            x,y=p['x'],p['y'];a=bool(before[y,x]);b=bool(after[y,x]);kind='skin' if p['label']=='skin' else 'unwanted'
            change='retained' if a and b else 'gained' if b else 'lost' if a else 'still_excluded'
            transitions[kind+'_'+change]+=1;counts[kind+'_old']+=a;counts[kind+'_new']+=b
            if b and kind=='unwanted':transitions[p['label']+'_selected']+=1
            if kind=='skin':
                eligible=bool(domains[case][y,x]);scope['skin_inside_candidate_domain' if eligible else 'skin_outside_candidate_domain']+=1
                if b:scope['selected_skin_inside_domain' if eligible else 'selected_skin_outside_domain']+=1
        percase.append(dict(review_id=row['review_id'],counts=dict(counts)))
    point_summary=candidate['summary']['candidate_actual_points']
    assert transitions['skin_retained']+transitions['skin_gained']==point_summary['skin_selected']
    assert transitions['unwanted_retained']+transitions['unwanted_gained']==point_summary['unwanted_selected']
    assert scope['skin_inside_candidate_domain']+scope['skin_outside_candidate_domain']==113
    assert all(sha(p)==h for p,h in bound.items())
    report=dict(mask_statistics_native_reconstructions=checks,point_transitions=dict(transitions),upper_face_scope=dict(scope),per_review_PRIVATE=percase,
        successful_native_grid_range=[min(nativecounts),max(nativecounts)],all30boards_assistant_inspected=True,
        visual_findings='Upper-face skin recovered in dark/glasses examples, but some frame/reflection/background-class material can be re-admitted; fringe/hairline concerns remain. Genuine cheek/chin and upper forehead contour skin is lost. This changes anatomical estimand; no complete beard/skin protection.',
        decision='partial_development_tradeoff_not_adopted_as_fullface_repair_or_calibration_method',
        no_independent_validation=True,new_forwards=0,new_fits=0,admissions=0,parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if 'PRIVATE' not in k},indent=2))

if __name__=='__main__':main()
