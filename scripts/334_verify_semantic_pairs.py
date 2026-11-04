"""Replay pair statistics/targets and build an explicitly unapproved gallery."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.paper_gamma import transform_rgb


def main():
    folder=ROOT/'outputs/semantic_paired_preparation_v1'
    target=folder/'independent_verification.json'
    if target.exists():raise FileExistsError(target)
    records=json.loads((folder/'records.json').read_text());plan=json.loads((folder/'plan.json').read_text())
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert all(digest(ROOT/p)==h for p,h in plan['input_sha256'].items())
    replayed=0;target_replays=0;sections=[]
    for row in records:
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['mask_path']),0)
        assert digest(ROOT/row['input_path'])==row['input_sha256'] and digest(ROOT/row['mask_path'])==row['mask_sha256']
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats==row['measurement']['statistics']
        features={f'input_{k}':stats[k] for k in ('mean_l_star','mean_a_star','mean_b_star','ita_degrees')}
        features.update(facial_endpoint_features(image,mask>0)['features'])
        assert features==row['measurement']['features'] and row['mst'] is None and not row['training_admitted']
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);generation=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        assert np.array_equal(rgb[~generation],reference[~generation])
        params=row['target_direct_gamma_red_blue'];output=transform_rgb(rgb.astype(float)/255,*params)
        if row.get('target_fit'):
            selected=generation&(mask>0)
            error=float(np.abs(np.rint(output[selected]*255)-reference[selected]).mean()/255)
            assert abs(error-row['target_fit']['quantized_rgb_mae'])<1e-12
        else:
            error=float(np.abs(np.rint(output*255)-reference)[generation].mean()/255)
            assert abs(error-row['inverse_rgb_mae'])<1e-12
        replayed+=1;target_replays+=1
    for source in plan['sources']:
        group=[r for r in records if r['source_image_id']==source['source_image_id']]
        boards=[cv2.imread(str(folder/r['board_path'])) for r in group]
        assert len(boards)==5
        path=folder/'boards'/(source['case_id']+'_contact.png')
        assert cv2.imwrite(str(path),np.vstack(boards))
        sections.append('<section><h2>'+html.escape(source['case_id'])+'</h2><p>Left: reference; middle: generated input; right: new input mask overlay.</p>'+''.join(
            '<h3>'+html.escape(r['variant'])+' — '+html.escape(r['lane'])+'</h3><img src="'+r['board_path']+'">' for r in group)+'</section>')
    page='<!doctype html><meta charset="utf-8"><title>Rebuilt semantic paired examples</title><style>body{font:18px system-ui;max-width:1000px;margin:30px auto;padding:20px}img{max-width:100%}section{border-top:1px solid #aaa;padding-top:20px}</style><h1>Rebuilt paired examples</h1><p>Six reference masks were accepted by the user. These 30 new input masks are unreviewed. This read-only gallery requests no new annotations and is not a trained-model result. No matching MST lookup has been adopted. Existing clipped cases are retained as stress evidence.</p>'+''.join(sections)
    (folder/'gallery.html').write_text(page,encoding='utf-8')
    result=dict(status='passed',statistics_and_endpoint_replays=replayed,direct_gamma_target_replays=target_replays,
        outside_generation_support_unchanged=True,source_and_code_hashes_unchanged=True,
        fitting_admissions=0,new_distorted_mask_approvals=0,correction_tree_fits=0,
        mst_legacy_reuse=False,live_browser_tested=False)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
