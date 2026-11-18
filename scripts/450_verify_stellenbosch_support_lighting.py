"""Independent common-mask/original-statistic checks and private decision notes."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
CANDIDATE=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
PARENT=ROOT/'outputs/stellenbosch_support_lighting_v1'
OUT=ROOT/'outputs/stellenbosch_support_lighting_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NOTES={
 1:'Broad apparent facial skin support; hair lock/hairline and fine feature borders uncertain. Common support remains broadly facial, not annotation truth.',
 2:'Condition-dependent central-face parser holes remain; shared region excludes those areas but still cannot prove actual skin.',
 3:'Shared region largely forehead/upper cheek because cool mask misses lower face; broader warm masks alone would change anatomical sampling.',
 4:'Broad apparent facial support, small feature/contour shifts; common region more comparable but not exact correspondence.',
 5:'Broad facial coverage with chin/feature-border uncertainty; shared region removes some lower-face/contour variation.',
 6:'Incomplete subject; glasses/reflections and patchy warm masks remain. Shared probe unavailable, no admission.',
 7:'Incomplete subject; dim input and fragmented forehead/cheek support. Shared probe unavailable, no admission.',
 8:'Fragmented central-face/cheek differences; common region becomes disconnected forehead/cheek/chin pieces. Spatial restriction does not validate them.',
 9:'Common region is a small forehead strip in all three; very dim original pixels and tiny native detail. Broad facial comparability cannot be inferred.',
 10:'All three earlier failures retained. No measurements, shared region or fabricated skin support.'}

def manual_stats(image,mask):
    lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:,:,0]*=100/255;lab[:,:,1:]-=128
    values=lab[mask>0];means=[np.mean(values[:,k]) for k in range(3)]
    L,a,b=[round(float(x),4) for x in means]
    angle=None if abs(b)<1e-6 else round(math.degrees(math.atan((L-50)/b)),4)
    return dict(mean_l_star=L,mean_a_star=a,mean_b_star=b,ita_degrees=angle)

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json')
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    data=read(PARENT/'results_PRIVATE.json');rows=data['records'];groups=defaultdict(list)
    original={r['case_id']:r for r in read(CANDIDATE/'results_PRIVATE.json')['records']}
    for r in rows:
        assert r['source_mst_exact_decimal']==original[r['case_id']]['source_mst_exact_decimal']
        groups[r['subject_key']].append(r)
    assert len(rows)==30 and len(groups)==10
    checks=0;full_checks=0;common_checks=0;signs=defaultdict(list)
    for group in groups.values():
        for r in group:
            if r['full_statistics'] is not None:
                im=cv2.imread(str(BASE/r['case_id']/'input.png'));mask=cv2.imread(str(CANDIDATE/r['case_id']/'measurement_mask.png'),0)
                assert all(r['full_statistics'][k]==v for k,v in manual_stats(im,mask).items());full_checks+=1
        if not all(r['complete_subject'] for r in group):
            assert all(r['shared_statistics'] is None for r in group);continue
        masks=[cv2.imread(str(CANDIDATE/r['case_id']/'measurement_mask.png'),0) for r in group]
        matrices=[np.array(read(CANDIDATE/r['case_id']/'matrix.json')) for r in group]
        warped=[cv2.warpAffine(m,M,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0) for m,M in zip(masks,matrices)]
        common=np.bitwise_and.reduce(warped)
        assert np.array_equal(common,cv2.imread(str(PARENT/(str(group[0]['subject_index'])+'_aligned_shared.png')),0));common_checks+=1
        for r,mask,M in zip(group,masks,matrices):
            valid=cv2.warpAffine(np.full(mask.shape,255,np.uint8),M,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            projected=cv2.warpAffine(common&valid,cv2.invertAffineTransform(M),(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)&mask
            saved=cv2.imread(str(PARENT/(r['case_id']+'_shared.png')),0)
            assert np.array_equal(projected,saved) and not saved[mask==0].any()
            stats=manual_stats(cv2.imread(str(BASE/r['case_id']/'input.png')),saved)
            assert all(r['shared_statistics'][k]==v for k,v in stats.items())
            assert r['shared_statistics']['skin_pixels']==int(np.count_nonzero(saved))>=1000
            signs[r['condition']].append(stats['mean_b_star']);checks+=1
    assert checks==21 and common_checks==7 and full_checks==25
    assert all(b<0 for b in signs['F_cool_600']) and all(b>0 for c,v in signs.items() if c!='F_cool_600' for b in v)
    report=dict(all30boards_assistant_inspected=True,scores_hidden=True,notes_by_subject_index_PRIVATE=NOTES,
        original_label_memberships=30,manual_full_statistics_checks=full_checks,manual_common_masks=common_checks,
        manual_shared_original_statistics_and_projection_checks=checks,
        common_b_sign_pattern='7cool negative /14warm positive',
        decision='hold_current_method_for_calibration_across_these_conditions',
        reasons=['Actual-skin validity unverified; hair/glasses/fragmentary/native-detail concerns remain.',
            'Restricting to shared locations leaves large ITA variation; mask selection alone does not explain it.',
            'Recorded b sign changes across lighting conditions interact with existing atan ratio.',
            'Decimal-compatible calibration and subject-held evaluation still require justification.'],
        no_dataset_rejection=True,no_intrinsic_colour_requirement=True,no_formula_change=True,
        admissions=0,new_forwards=0,new_fits=0,parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if 'PRIVATE' not in k},indent=2))

if __name__=='__main__':main()
