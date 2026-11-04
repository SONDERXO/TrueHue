"""Saved-pixel/exclusion/refit verification; no new scientific candidate."""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.ita_estimation.nostril_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.evaluation.mst_validation import evaluate_mst


def main():
    parent=ROOT/'outputs/nostril_mst_measurement_v4';cal=ROOT/'outputs/nostril_mst_calibration_v4'
    out=ROOT/'outputs/nostril_mst_verification_v4'
    if out.exists():raise FileExistsError(out)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    measured=read(parent/'summary.json');report=read(cal/'summary.json');plan=read(parent/'plan.json')
    rows=measured['records'];byid={r['image_id']:r for r in rows}
    assert len(rows)==len(byid)==418 and contract(ROOT)[1]==measured['measurement_contract_sha256']==report['measurement_contract_sha256']
    checked=0;fitchecks=0;predictionchecks=0
    for row in rows:
        if row['status']!='success':continue
        for pathkey,hashkey in [('mask_path','mask_sha256'),('category_path','category_sha256'),
            ('landmarks_path','landmarks_sha256'),('nostril_guard_path','nostril_guard_sha256')]:
            assert digest(parent/row[pathkey])==row[hashkey]
        image=cv2.resize(cv2.imread(row['source_path']),(256,256),interpolation=cv2.INTER_LINEAR)
        categories=cv2.imread(str(parent/row['category_path']),0);points=np.load(parent/row['landmarks_path'])
        mask=cv2.imread(str(parent/row['mask_path']),0);geometry=build_face_coverage(image,points)
        base=build_semantic_face_coverage(image,points,categories).mask
        guard=nostril_guard(mask.shape,points);base[guard]=0
        assert np.array_equal(base,mask)
        assert not mask[~np.isin(categories,[1,10])].any()
        assert not mask[(geometry.exclusion_mask>0)|guard].any()
        assert np.array_equal(guard,cv2.imread(str(parent/row['nostril_guard_path']),0)>0)
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats==row['statistics']
        features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(image,mask>0)['features']);assert features==row['features']
        checked+=1
    predictions={r['image_id']:r for r in report['predictions']}
    for saved in report['fold_models']:
        expected={r['image_id'] for r in rows if r['status']=='success' and r['subject_id']!=saved['held_subject']}
        assert set(saved['fit_image_ids'])==expected
        training=[byid[i] for i in saved['fit_image_ids']];counts=Counter(r['subject_id'] for r in training)
        assert saved['held_subject'] not in counts
        weights=[1/counts[r['subject_id']] for r in training];assert weights==saved['fit_weights']
        model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
        model.fit([r['features']['input_ita_degrees'] for r in training],
            [r['source_mst_label'] for r in training],sample_weight=weights)
        assert model.X_thresholds_.tolist()==saved['x_knots'] and model.y_thresholds_.tolist()==saved['y_knots']
        fitchecks+=1
        expectedheld={r['image_id'] for r in rows if r['status']=='success' and r['subject_id']==saved['held_subject']}
        assert set(saved['held_image_ids'])==expectedheld
        for key in saved['held_image_ids']:
            prediction=predictions[key];x=byid[key]['features']['input_ita_degrees']
            value=float(np.interp(x,saved['x_knots'],saved['y_knots']))
            assert abs(value-prediction['continuous_prediction'])<1e-12
            assert int(np.floor(value+.5))==prediction['prediction'];predictionchecks+=1
    attempts=[dict(image_id=r['image_id'],subject_id=r['subject_id'],mst=r['source_mst_label'],lighting=r['lighting'],measured=r['status']=='success') for r in rows]
    assert evaluate_mst(attempts,report['predictions'],report['folds'])==report['metrics']
    assert all(digest(Path(p))==h for p,h in measured['input_sha256'].items())
    out.mkdir();cards=[]
    for key in plan['diagnostic_ids']:
        row=byid[key]
        cards.append('<section><h2>'+html.escape(key)+'</h2><p>'+html.escape(row['status']+': '+row.get('reason','measurement available'))+'</p>'+
            ('<img src="../nostril_mst_measurement_v4/'+row['board_path']+'">' if row.get('board_path') else '<p>No diagnostic board available.</p>')+'</section>')
    page='<!doctype html><meta charset="utf-8"><title>Nostril-excluded MST diagnostics</title><style>body{font:18px system-ui;max-width:1000px;margin:30px auto;padding:20px}img{width:100%}section{border-top:1px solid #aaa}</style><h1>ITA/MST measurement exclusions</h1><p>Original; selected measurement skin; binary measurement mask. Fixed one-per-subject diagnostics, not approved masks or ground truth. Whole-face correction support and blending do not supply these measurement pixels.</p>'+''.join(cards)
    (out/'diagnostics.html').write_text(page,encoding='utf-8')
    result=dict(status='passed',successful_measurement_replays=checked,exclusion_reconstructions=checked,
        subject_held_refit_replays=fitchecks,prediction_replays=predictionchecks,
        all_metric_denominators_replayed=True,source_separation=True,input_hashes_unchanged=True,
        diagnostic_attempts=len(plan['diagnostic_ids']),new_mask_approvals=0,
        production_lookup_exported=False,correction_tree_fits=0,reserved_pixel_access=0)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
