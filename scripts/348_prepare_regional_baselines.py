"""Save no-correction regional baselines and clean controls; no tree training."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.evaluation.preferred_regions import evaluate_regions,REGIONS


def main():
    folder=ROOT/'outputs/preferred_support_pairs_v2';out=ROOT/'outputs/preferred_regional_baselines_v2'
    if out.exists():raise FileExistsError(out)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    records=read(folder/'records.json');controls=read(folder/'controls.json')
    tracked=[folder/'records.json',folder/'controls.json',Path(__file__),ROOT/'src/evaluation/preferred_regions.py']
    hashes={str(p):digest(p) for p in tracked}
    out.mkdir();results=[]
    rgb=lambda p:cv2.cvtColor(cv2.imread(str(ROOT/p)),cv2.COLOR_BGR2RGB)
    for row in records:
        reference=rgb(row['reference_path']);image=rgb(row['input_path'])
        assert digest(ROOT/row['input_path'])==row['input_sha256']
        regions={k:cv2.imread(str(ROOT/row['reference_region_masks'][k]),0)>0 for k in REGIONS}
        if row['measurement']['status']=='success':
            application=cv2.imread(str(ROOT/row['correction_mask_path']),0)>0
            result=evaluate_regions(reference,image,image,regions,application)
        else:result=dict(available=False,reason='input_processing_failed',stage=row['measurement']['stage'])
        results.append(dict(case_id=row['case_id'],source_image_id=row['source_image_id'],lane=row['lane'],
                            method='no_correction',result=result))
    clean=[]
    for row in controls:
        image=rgb(row['input_path']);regions={k:cv2.imread(str(ROOT/row['reference_region_masks'][k]),0)>0 for k in REGIONS}
        application=cv2.imread(str(ROOT/row['reference_region_masks']['combined']),0)>0
        result=evaluate_regions(image,image,image,regions,application,identity_control=True)
        assert result['clean_gate_pass']
        clean.append(dict(source_image_id=row['source_image_id'],result=result))
    assert all(digest(Path(p))==h for p,h in hashes.items())
    (out/'no_correction.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    (out/'identity_controls.json').write_text(json.dumps(clean,indent=2),encoding='utf-8')
    report=dict(status='regional_scoring_ready_no_model_trained',input_cases=len(results),clean_controls=len(clean),
        regions=list(REGIONS),all_clean_controls_unchanged=True,scoring_regions='fixed_reference_generation_masks',
        empty_regions='unavailable_not_zero',outside_application_checks=True,input_sha256=hashes,
        mask_approvals_added=0,correction_tree_fits=0,reserved_pixel_access=0,
        next_required='Actual reference decisions in preferred_reference_review_v2, followed by new-input admission')
    (out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
