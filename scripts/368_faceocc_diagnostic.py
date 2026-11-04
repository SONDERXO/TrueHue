"""Freeze/finalize a single FaceOcc comparison using saved logits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.faceocc_veto_candidate import combine_saved,VERSION
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features

OUT=ROOT/'outputs/faceocc_diagnostic_v1'
PARENT=ROOT/'outputs/additional_mst_eligibility_v1'
BRIDGE=ROOT/'outputs/faceocc_bridge_v1'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    baseline=read(PARENT/'summary.json');bridge=read(BRIDGE/'summary.json')
    bound=read(BRIDGE/'plan.json')
    assert all(digest(p)==h for p,h in bound['input_sha256'].items())
    assert [r['image_id'] for r in baseline['records']]==[r['image_id'] for r in bridge['records']]
    paths=[Path(__file__),ROOT/'scripts/369_run_faceocc_logits.py',PARENT/'summary.json',BRIDGE/'summary.json',
        ROOT/'docs/faceocc-single-diagnostic-protocol-2026-11-01.md',
        ROOT/'models/faceocc_candidate_v1/model.safetensors',ROOT/'models/faceocc_candidate_v1/config.json',
        ROOT/'src/ita_estimation/faceocc_veto_candidate.py',ROOT/'src/skin_masking/faceocc_coordinates.py',
        ROOT/'src/ita_estimation/compute_ita.py',ROOT/'src/model_training/facial_endpoint_features.py',
        ROOT/'outputs/faceocc_loading_v1/environment-freeze.txt']
    hashes={str(p):digest(p) for p in paths};hashes.update(bound['input_sha256'])
    attempts=[]
    for old,aligned in zip(baseline['records'],bridge['records']):
        row=dict(image_id=old['image_id'],subject_id=old['subject_id'],case_index=aligned['case_index'],
            parent_status=old['status'],alignment_status=aligned['status'],parent_reason=old.get('reason'))
        if old['status']=='success' and aligned['status']=='aligned_input_available':
            folder=PARENT/Path(old['board_path']).parent
            row.update(aligned_path=str(BRIDGE/aligned['aligned_path']),baseline_mask=str(folder/'mask.png'),
                input_path=str(folder/'input.png'),matrix=aligned['forward_matrix'])
            assert digest(row['aligned_path'])==aligned['aligned_sha256']
            for p in [row['aligned_path'],row['baseline_mask'],row['input_path']]:hashes[str(p)]=digest(p)
        attempts.append(row)
    for name in ['continuous_correction_r2','seamless_support_v5']:
        for p in (ROOT/'outputs'/name).rglob('*'):
            if p.is_file():hashes[str(p)]=digest(p)
    marks=read(ROOT/'outputs/face_contained_measurement_candidate_v1/plan.json')['diagnostic_annotations']
    spec=dict(version=VERSION,rule='preferred_parent_AND_inverse_mapped_FaceOcc_logit_gt_zero',
        weights_sha256=digest(ROOT/'models/faceocc_candidate_v1/model.safetensors'),
        input_sha256=hashes,minimum_pixels=1000,diagnostic_annotations=marks)
    identity=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    OUT.mkdir();(OUT/'logits').mkdir()
    (OUT/'plan.json').write_text(json.dumps(dict(status='frozen_before_inference',attempts=attempts,
        contract=spec,candidate_contract_sha256=identity,input_sha256=hashes,
        diagnostic_annotations=marks,model_adoption=False,fits=0),indent=2))
    print('Frozen25attempts/17available; contract '+identity)


def finalize():
    if (OUT/'summary.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'plan.json');run=read(OUT/'inference.json')
    assert all(digest(p)==h for p,h in plan['input_sha256'].items())
    assert run['plan_sha256']==digest(OUT/'plan.json')
    inference={r['image_id']:r for r in run['records']}
    marks={r['case_index']:r['marks'] for r in plan['diagnostic_annotations']}
    records=[];boards=[];cards=[]
    for row in plan['attempts']:
        i=row['case_index'];rec=dict(image_id=row['image_id'],case_index=i,subject_id=row['subject_id'],admitted=False)
        if 'aligned_path' not in row:
            rec.update(status='parent_failed',features=None,reason=row['parent_reason']);records.append(rec);continue
        pred=inference[row['image_id']]
        if pred['status']!='success':
            rec.update(status='model_failed',features=None,reason=pred['reason']);records.append(rec);continue
        lp=OUT/pred['logits_path'];assert digest(lp)==pred['logits_sha256']
        logits=np.load(lp,allow_pickle=False)
        image=cv2.imread(row['input_path']);baseline=cv2.imread(row['baseline_mask'],0)
        candidate,visible,report=combine_saved(image,baseline,logits,np.array(row['matrix']))
        assert not candidate[baseline==0].any()
        replay,_,check=combine_saved(image,baseline,logits,np.array(row['matrix']))
        assert np.array_equal(replay,candidate) and check==report
        if report['status']=='success':
            stats=compute_masked_lab_statistics(image,candidate,1000);assert stats==report['statistics']
            f={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
            f.update(facial_endpoint_features(image,candidate>0)['features']);assert f==report['features']
        rec.update(report)
        if i in marks:
            rec['sparse_mark_results']={k:[dict(x=x,y=y,parent_selected=bool(baseline[y,x]),
                candidate_selected=bool(candidate[y,x])) for x,y in values] for k,values in marks[i].items()}
        folder=OUT/('case_'+str(i));folder.mkdir()
        shown=[]
        for mask in [baseline,visible,candidate]:
            overlay=image.copy();sel=mask>0
            overlay[sel]=np.rint(.5*overlay[sel]+.5*np.array([0,255,0])).astype(np.uint8);shown.append(overlay)
        board=np.hstack([image]+shown)
        for name,array in [('candidate_mask.png',candidate),('mapped_visible.png',visible),('board.png',board)]:
            assert cv2.imwrite(str(folder/name),array)
        rec['candidate_sha256']=digest(folder/'candidate_mask.png')
        label=np.full((25,1024,3),255,np.uint8)
        cv2.putText(label,str(i)+' '+row['subject_id']+' retained='+str(round(report['retained_fraction']*100,1))+'%',(8,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack((label,board)));records.append(rec)
        cards.append('<h2>'+str(i)+' '+row['image_id']+'</h2><p>'+str(round(report['retained_fraction']*100,1))+'% retained; '+report['status']+'</p><img src="case_'+str(i)+'/board.png">')
    for i in range(0,len(boards),4):cv2.imwrite(str(OUT/('contact_'+str(i//4+1)+'.png')),np.vstack(boards[i:i+4]))
    assert all(digest(p)==h for p,h in plan['input_sha256'].items())
    measured=[r for r in records if 'removed_pixels' in r]
    summary=dict(status='single_diagnostic_complete_not_adopted',records=records,attempts=25,
        parent_failures=8,model_outputs=len(measured),candidate_successes=sum(r['status']=='success' for r in measured),
        newly_unavailable=sum(r['status']!='success' for r in measured),
        minimum_retention=min(r['retained_fraction'] for r in measured),
        total_removed_pixels=sum(r['removed_pixels'] for r in measured),
        candidate_contract_sha256=plan['candidate_contract_sha256'],
        parent_and_correction_hashes_unchanged=True,fits=0,adopted=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>One FaceOcc comparison</title><style>body{font:18px system-ui;max-width:1300px;margin:auto;padding:20px}img{width:100%}</style><h1>FaceOcc measurement veto: one fixed diagnostic</h1><p>Original; preferred measurement; mapped FaceOcc visible-face prediction; combined measurement candidate. These are MEASUREMENT overlays, not correction masks. Eight original failures remain. No mask adoption or MST fitting.</p>'+''.join(cards),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))


if __name__=='__main__':
    finalize() if '--finalize' in sys.argv else prepare()
