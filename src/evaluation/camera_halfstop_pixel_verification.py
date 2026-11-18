"""Independent saved-run numerical replay; no trainer, optimizer or portable runtime imports."""
from pathlib import Path
import json
import math
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
from src.model_training.camera_halfstop_neighbour_scalar import search,verify_index
from .luminance_chroma_scalar import replay

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)


def verify_run(root):
    root=Path(root);plan=read(root/'execution_plan.json');rows=read(root/'prepared_rows.json')
    by_case={r['case_id']:r for r in rows};inference=read(root/'inference_inputs.json')
    assert len(inference)==66 and all(set(r)=={'case_id','source_id','role','generated_fixture','x'} for r in inference)
    assert all(r['x']==by_case[r['case_id']]['x'] for r in inference)
    cert=read(root/'models/all_indices_verified.json');assert cert['passed'] and cert['index_constructions']==11
    model_by_source={m['held_source_id']:m for m in cert['models']};fitting_checks=0
    for fold in plan['folds']:
        m=model_by_source[fold['held_source_id']]
        fitted=read(m['fitting_rows_path']);index=read(m['index_path']);native=read(m['replay_path'])
        for row in fitted:
            original=by_case[row['case_id']]
            assert row=={k:original[k] for k in ['case_id','source_id','role','generated_fixture','x','y']}
        proof=verify_index(index,fitted,native,fold)
        assert proof==read(m['verification_path']);fitting_checks+=60
    sealed=read(root/'models/held_controls_sealed.json');assert len(sealed)==66
    held_checks=0;render_checks=0;records=[]
    for p in sealed:
        row=by_case[p['case_id']];m=model_by_source[row['source_id']];index=read(m['index_path'])
        answer=search(index,row['x']);values=answer['controls']
        assert answer['neighbour_case_id']==p['neighbour_case_id'] and values==p['controls']
        close(answer['squared_distance'],p['squared_distance'])
        fitted=read(m['fitting_rows_path'])
        means=[math.fsum(r['y'][j] for r in fitted)/60 for j in range(5)]
        for a,b in zip(means,p['constant_controls']):close(a,b)
        record=read(root/'evaluation'/(p['case_id']+'.json'))
        for k,v in p.items():assert record[k]==v
        assert record['oracle_controls']==row['y']
        close(record['control_squared_error'],math.fsum((a-b)**2 for a,b in zip(values,row['y'])))
        with np.load(root/'evaluation'/(p['case_id']+'.npz'),allow_pickle=False) as pack:
            image,ref,alpha,protected,actual,constant=[pack[k] for k in ['input','reference','alpha','protected','tree','constant']]
        for controls,output in [(values,actual),(means,constant)]:
            rounded,_=replay(image,ref,alpha,protected,controls)
            np.testing.assert_array_equal(output,rounded)
            assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
            render_checks+=1
        masks={'primary':alpha>0,'core':alpha==1,'feather':(alpha>0)&(alpha<1),'whole':np.ones(alpha.shape,bool)}
        ref_lab=rgb2lab(ref/255.)
        for label,output in [('input',image),('tree',actual),('constant',constant)]:
            de=deltaE_ciede2000(rgb2lab(output/255.),ref_lab)
            rgb=np.abs(output.astype(float)-ref)
            for name,mask in masks.items():
                n=int(mask.sum());saved=record['regions'][name]
                assert saved['pixels']==n
                if n:
                    close(saved[label]['RGB'],math.fsum(float(v) for v in rgb[mask].flat)/(3*n))
                    close(saved[label]['DE'],math.fsum(float(v) for v in de[mask])/n)
                else:assert saved[label] is None
        if row['role']=='identity':
            assert record['identity_changed_pixels']==int(np.any(actual!=image,axis=2).sum())
            close(record['identity_mean_RGB_change'],float(np.abs(actual.astype(float)-image).mean()))
        held_checks+=1;records.append(record)
        if held_checks%6==0:print(f'Independent generated/research held replay {held_checks}/66',flush=True)
    assert fitting_checks==660 and held_checks==66 and render_checks==132
    summary=read(root/'evaluation/summary.json');role_checks={}
    for role in ROLES:
        own=[r for r in records if r['role']==role];saved=summary['by_role'][role];assert len(own)==saved['cases']==11
        for label in ['input','tree','constant']:
            for metric in ['RGB','DE']:close(saved['means'][label][metric],math.fsum(r['regions']['primary'][label][metric] for r in own)/11)
        for metric in ['RGB','DE']:
            assert saved['case_harms'][metric]==[r['case_id'] for r in own if r['regions']['primary']['tree'][metric]>r['regions']['primary']['input'][metric]+1e-10]
        if role!='identity':role_checks[role]=all(saved['means']['tree'][k]<saved['means'][b][k]-1e-10 for k in ['RGB','DE'] for b in ['input','constant'])
    assert summary['complete'] and summary['numeric_role_checks']==role_checks
    assert summary['status']==('NUMERIC_PREDICTION_ELIGIBLE_ONLY' if all(role_checks.values()) else 'NOT_ADVANCED')
    assert summary['human_identity_acceptability']=='not_assessed' and not summary['model_ready'] and not summary['review_launched']
    return dict(passed=True,fitting_route_replays=660,held_route_replays=66,render_metric_replays=132,
        source_equal_summaries=6,held_supervision_absent_from_inference_inputs=True,
        numeric_status=summary['status'],verifier_fits=0,model_ready=False)
