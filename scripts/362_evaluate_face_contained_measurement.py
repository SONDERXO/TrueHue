"""One frozen saved-evidence replay, no inference, calibration or fitting."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.face_contained_measurement import contract, measure_saved
from src.ita_estimation.nostril_measurement import nostril_guard
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features


def main():
    parent = ROOT / 'outputs/additional_mst_eligibility_v1'
    out = ROOT / 'outputs/face_contained_measurement_candidate_v1'
    if out.exists():
        raise FileExistsError(out)
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source = json.loads((parent / 'summary.json').read_text())
    spec, identity = contract(ROOT)
    hashes = {str(p): digest(p) for p in [parent/'summary.json', parent/'plan.json', parent/'visual_diagnostics.json',
        ROOT/'docs/measurement-error-proposal-2026-11-01.md', Path(__file__)]}
    # Freeze sparse diagnostic locations from original/baseline inspection before candidate comparison.
    marks = {4: dict(non_skin=[(125,225),(125,175)], skin=[(100,140)], uncertain=[]),
             10: dict(non_skin=[(125,140)], skin=[], uncertain=[(140,90)]),
             14: dict(non_skin=[(115,150)], skin=[(110,90)], uncertain=[])}
    annotations = []
    for index, r in enumerate(source['records'],1):
        assert digest(r['source_path']) == r['source_sha256']
        if r['status'] != 'success':
            continue
        folder = parent / Path(r['board_path']).parent
        for name, h in r['saved_sha256'].items():
            assert digest(folder/name) == h
            hashes[str(folder/name)] = h
        if index in marks:
            annotations.append(dict(image_id=r['image_id'], case_index=index,
                input_sha256=r['saved_sha256']['input.png'], marks=marks[index],
                annotator='assistant_visual_diagnostic', coordinates='integer_x_y_square256',
                scope='sparse_diagnostics_not_full_ground_truth_or_user_approval'))
    # Also bind correction evidence; it is not read into candidate features or modified.
    for directory in ['outputs/continuous_correction_r2', 'outputs/seamless_support_v5']:
        for p in (ROOT/directory).rglob('*'):
            if p.is_file(): hashes[str(p)] = digest(p)
    out.mkdir()
    (out/'plan.json').write_text(json.dumps(dict(attempt_ids=[r['image_id'] for r in source['records']],
        contract=spec, measurement_contract_sha256=identity, diagnostic_annotations=annotations,
        input_sha256=hashes, role='exposed_development_diagnostics_only', fits=0),indent=2))
    records=[]; cards=[]; boards=[]
    for index,r in enumerate(source['records'],1):
        rec=dict(image_id=r['image_id'], subject_id=r['subject_id'], baseline_status=r['status'], admitted=False)
        if r['status']!='success':
            rec.update(status='failed_parent', features=None, reason=r.get('reason'), removed_pixels=None)
            records.append(rec); continue
        folder=parent/Path(r['board_path']).parent
        image=cv2.imread(str(folder/'input.png')); baseline=cv2.imread(str(folder/'mask.png'),0)
        cats=cv2.imread(str(folder/'categories.png'),0); points=np.load(folder/'landmarks.npy')
        geometry=build_face_coverage(image,points); guard=nostril_guard(baseline.shape,points)
        replay=build_semantic_face_coverage(image,points,cats).mask; replay[guard]=0
        assert np.array_equal(replay,baseline)
        mask,report=measure_saved(image,baseline,points)
        assert mask is not None
        assert np.array_equal(mask,cv2.bitwise_and(replay,geometry.face_outline))
        forbidden=(~np.isin(cats,[1,10])) | (geometry.exclusion_mask>0) | guard
        assert not mask[forbidden].any() and not mask[geometry.face_outline==0].any()
        assert not mask[baseline==0].any()
        if report['status']=='success':
            stats=compute_masked_lab_statistics(image,mask,1000); assert stats==report['statistics']
            features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
            features.update(facial_endpoint_features(image,mask>0)['features']); assert features==report['features']
        rec.update(report, case_index=index)
        if index in marks:
            rec['sparse_mark_results']={k:[dict(x=x,y=y, baseline_selected=bool(baseline[y,x]),
                candidate_selected=bool(mask[y,x])) for x,y in coords] for k,coords in marks[index].items()}
        target=out/('case_'+str(index)); target.mkdir()
        assert cv2.imwrite(str(target/'mask.png'),mask)
        old=image.copy(); new=image.copy()
        for overlay,selected in [(old,baseline>0),(new,mask>0)]:
            overlay[selected]=np.rint(.5*overlay[selected]+.5*np.array([0,255,0])).astype(np.uint8)
        board=np.hstack((image,old,new,cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)))
        assert cv2.imwrite(str(target/'board.png'),board)
        label=np.full((25,board.shape[1],3),255,np.uint8)
        cv2.putText(label,str(index)+' '+r['subject_id']+' removed='+str(report['removed_pixels']),(8,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack((label,board)))
        rec['mask_sha256']=digest(target/'mask.png')
        records.append(rec); cards.append('<h2>'+str(index)+' '+r['image_id']+'</h2><p>'+str(report['removed_pixels'])+' pixels removed</p><img src="case_'+str(index)+'/board.png">')
    for i in range(0,len(boards),4):
        cv2.imwrite(str(out/('contact_'+str(i//4+1)+'.png')),np.vstack(boards[i:i+4]))
    assert all(digest(p)==h for p,h in hashes.items()) and contract(ROOT)[1]==identity
    available=[r for r in records if r['baseline_status']=='success']
    summary=dict(status='containment_passed_actual_skin_unresolved_stop',records=records,
        attempts=25,parent_failures=8,candidate_successes=sum(r['status']=='success' for r in available),
        newly_unavailable=sum(r['status']!='success' for r in available),
        changed_masks=sum(r['removed_pixels']>0 for r in available),
        total_removed_pixels=sum(r['removed_pixels'] for r in available),
        minimum_retained_fraction=min(r['retained_fraction'] for r in available),
        measurement_contract_sha256=identity,mask_and_feature_replays=17,
        correction_and_parent_artifact_hashes_unchanged=True, fits=0, runtime_adopted=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Face-contained measurement diagnostic</title><style>body{font:18px system-ui;max-width:1400px;margin:auto;padding:20px}img{width:100%}</style><h1>One measurement containment candidate</h1><p>Original; old measurement overlay; candidate overlay; candidate mask. Correction is unchanged. Containment does not exclude all beard/covering pixels. Eight parent failures retained, no new inference or fit.</p>'+''.join(cards),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))


if __name__=='__main__': main()
