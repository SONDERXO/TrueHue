"""Verify isolated service parity on all49saved attempts; no new inference."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.ita_estimation.faceocc_development import contract,evaluate_parent


def main():
    out=ROOT/'outputs/faceocc_development_service_v1'
    if out.exists():raise FileExistsError(out)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    spec,identity=contract(ROOT);records=[];hashes={};checks=0
    cases=[('faceocc_diagnostic_v1','additional_mst_eligibility_v1','mask.png'),
        ('faceocc_light_comparison_v1','faceocc_light_comparison_v1','baseline_mask.png')]
    for output_name,parent_name,mask_name in cases:
        folder=ROOT/'outputs'/output_name;parent_folder=ROOT/'outputs'/parent_name
        saved=read(folder/'summary.json');predictions=read(folder/'inference.json')
        ip=read(folder/('plan.json' if output_name=='faceocc_diagnostic_v1' else 'inference_plan.json'))
        assert all(digest(Path(p))==h for p,h in ip['input_sha256'].items())
        hashes.update(ip['input_sha256'])
        for p in [folder/'summary.json',folder/'inference.json']:hashes[str(p)]=digest(p)
        byid={r['image_id']:r for r in predictions['records']}
        for row in saved['records']:
            i=row['case_index'];old_features=row.get('candidate_report',row).get('features')
            if output_name=='faceocc_diagnostic_v1':
                original=read(parent_folder/'summary.json')['records'][i-1]
                success=original['status']=='success'
                case=parent_folder/('case_'+str(i));report=original
            else:
                original=row;report=row.get('parent_report',{'status':'failed','reason':row.get('reason')})
                success=report['status']=='success';case=parent_folder/('case_'+str(i))
            rec=dict(image_id=row['image_id'],cycle=output_name)
            if success:
                image=cv2.imread(str(case/'input.png'));mask=cv2.imread(str(case/mask_name),0)
                points=np.load(case/'landmarks.npy',allow_pickle=False)
                pred=byid[row['image_id']];lp=folder/pred['logits_path'];assert digest(lp)==pred['logits_sha256']
                logits=np.load(lp,allow_pickle=False)
                result=evaluate_parent(SimpleNamespace(report=report,image=image,mask=mask),points,template,
                    lambda _,saved_logits=logits:saved_logits)
                target=folder/('case_'+str(i))/'candidate_mask.png'
                assert np.array_equal(result.mask,cv2.imread(str(target),0))
                assert result.report['features']==old_features and result.report['status']=='success'
                hashes[str(lp)]=digest(lp);hashes[str(target)]=digest(target);checks+=1
                if output_name=='faceocc_diagnostic_v1':
                    baseline_aligned=ROOT/'outputs/faceocc_bridge_v1'/('case_'+str(i))/'aligned.png'
                else:baseline_aligned=case/'aligned.png'
                assert np.array_equal(result.aligned,cv2.imread(str(baseline_aligned)))
                rec.update(result.report)
            else:
                def forbidden(_):raise AssertionError('Failed parent must not predict')
                result=evaluate_parent(SimpleNamespace(report={'status':'failed','reason':report.get('reason')},image=None,mask=None),None,template,forbidden)
                assert result.report['features'] is None and result.report['mst'] is None
                rec.update(result.report)
            assert rec['actual_skin_validity']=='unverified' and not rec['training_admitted'] and not rec['calibration_admitted']
            records.append(rec)
    assert len(records)==49 and checks==35
    assert all(digest(Path(p))==h for p,h in hashes.items())
    assert contract(ROOT)[1]==identity
    out.mkdir()
    (out/'contract.json').write_text(json.dumps(dict(contract=spec,sha256=identity),indent=2))
    (out/'records.json').write_text(json.dumps(records,indent=2))
    (out/'input_sha256.json').write_text(json.dumps(hashes,indent=2))
    result=dict(status='development_service_saved_parity_passed',attempts=49,exact_mask_feature_aligned_replays=35,
        failed_parent_guards=14,all_actual_skin_validity_unverified=True,
        training_admitted=0,calibration_admitted=0,mst_available=0,
        candidate_contract_sha256=identity,new_model_forwards=0,new_source_images=0,active_runtime_changed=False)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
