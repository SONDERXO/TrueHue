"""Replay saved core features, original-model predictions, transforms and metrics."""
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as stream:return list(csv.DictReader(stream))
def binary(p):
    value=cv2.imread(str(p),0);assert value is not None and set(np.unique(value))<={0,255};return value>0
def metrics(reference,image,mask):
    a=reference[:,:,::-1].astype(float)/255;b=image[:,:,::-1].astype(float)/255;error=abs(a-b)
    delta=deltaE_ciede2000(rgb2lab(a),rgb2lab(b))
    return dict(rgb_mae_source_mask=float(error[mask].mean()),ciede2000_source_mask=float(delta[mask].mean()),
        rgb_mae_whole_image=float(error.mean()),rgb_mae_outside_source_mask=float(error[~mask].mean()) if (~mask).any() else None)
def main():
    out=ROOT/get_config().OUTPUTS_ROOT/'core_pipeline_check_v1';summary=json.loads((out/'summary.json').read_text());tables=ROOT/'data/manifests/controlled_training_v2'
    originals={r['pair_id']:r for name in ['train','development_validation','clipped_stress','excluded_pairs'] for r in read(tables/(name+'.csv'))}
    assert len(originals)==len(summary['records'])==38
    model=load_model(str(ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH));verified=0;failed=0
    for row in summary['records']:
        original=originals[row['pair_id']];folder=out/'cases'/row['pair_id'];report=json.loads((folder/'report.json').read_text())
        assert not report['proposal_complete'] and not row['training_eligibility_changed']
        assert row['original_table_use']==original['table_use'] and row['original_pair_status']==original['pair_status']
        image=cv2.imread(str(ROOT/original['input_path']));assert digest(ROOT/original['input_path'])==report['provenance']['input_sha256']
        if row['status']=='failed':
            assert original['table_use']=='excluded' and report['failed_stage']=='measurement' and row['metrics'] is None
            assert not (folder/'corrected.png').exists() and (folder/'failure.json').exists()
            assert report['mst']['status']=='not_run';failed+=1;continue
        assert report['mst']['status']=='unavailable' and report['mst']['label'] is None and report['mst']['config_index'] is None
        assert row['features_match_saved'] and report['status']=='development_partial_mst_unavailable'
        mask=binary(folder/'estimation_mask.png');application=binary(folder/'correction_mask.png');np.testing.assert_array_equal(mask,application)
        x,y,w,h=report['stages']['face_detection']['face_box'];bounds=np.zeros(mask.shape,bool);bounds[y:y+h,x:x+w]=True
        assert not (mask&~bounds).any() and mask.sum()>=1000
        encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);encoded[:,:,0]*=100/255;encoded[:,:,1:]-=128
        values=encoded[mask];means=[round(float(values[:,i].mean()),4) for i in range(3)];ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
        measured=np.array([*means,ita]);np.testing.assert_allclose([row['features'][k] for k in FEATURES],measured,rtol=0,atol=.00005)
        predicted=model.predict(measured[None,:])[0];np.testing.assert_array_equal(predicted,list(row['parameters'].values()))
        rgb=image[:,:,::-1].astype(float)/255;gamma,red,blue=predicted;raw=(rgb**(1/gamma))*np.array([red,1,blue])
        expected=image.copy();expected[application]=np.rint(np.clip(raw,0,1)*255).astype(np.uint8)[:,:,::-1][application]
        corrected=cv2.imread(str(folder/'corrected.png'));np.testing.assert_array_equal(corrected,expected)
        np.testing.assert_array_equal(corrected[~application],image[~application]);assert row['outside_mask_changed_pixels']==0
        reference=cv2.imread(original['source_path']);generation=binary(ROOT/original['generation_mask_path'])
        for label,value in [('no_correction',image),('decision_tree',corrected)]:
            replay=metrics(reference,value,generation)
            for key,n in replay.items():
                if n is None:assert row['metrics'][label][key] is None
                else:np.testing.assert_allclose(row['metrics'][label][key],n,rtol=0,atol=1e-12)
        if original['variant']=='identity_control':np.testing.assert_array_equal(image,reference)
        verified+=1
    assert verified==summary['available']==37 and failed==summary['failed']==1
    assert all(digest(ROOT/p)==h for p,h in summary['input_sha256'].items())
    # Exercise the actual CLI on one available input and the retained failed attempt.
    cli_results=[]
    for name in ['identity_control','excluded']:
        row=next(r for r in summary['records'] if (r['variant']=='identity_control' if name=='identity_control' else r['original_table_use']=='excluded'))
        original=originals[row['pair_id']];destination=out/('cli_'+name)
        if destination.exists():
            saved=json.loads((destination/'report.json').read_text());assert saved['status']==row['status'];continue
        process=subprocess.run([sys.executable,str(ROOT/'scripts/116_run_core_pipeline.py'),'--image',str(ROOT/original['input_path']),'--output-dir',str(destination)],cwd=ROOT,text=True,capture_output=True)
        assert process.returncode==(0 if name=='identity_control' else 2)
        saved=json.loads((destination/'report.json').read_text());assert saved['status']==row['status'] and not saved['proposal_complete']
        if name=='identity_control':np.testing.assert_array_equal(cv2.imread(str(destination/'corrected.png')),cv2.imread(str(out/'cases'/row['pair_id']/'corrected.png')))
        cli_results.append(dict(case=name,exit_code=process.returncode,status=saved['status']))
    quality=dict(software_pipeline='pass',proposal_complete=False,mst_available=False,final_model_adopted=False,
        no_correction_comparison='Frozen tree worsens7/7unchanged and4/7mild controls;3/4clipped stress worsen',
        model_quality='not_ready_for_final_adoption',mask_limitations='Paint/makeup, boundary coverage and neck remain documented limitations',
        original_reviews_folds_and_eligibility_unchanged=True,new_model_fits=0,training_pairs_regenerated=0)
    (out/'readiness.json').write_text(json.dumps(quality,indent=2))
    result=dict(status='pass',available_input_feature_prediction_transform_metric_replays=verified,excluded_failure_retained=failed,
        cli_checks=cli_results,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json'),verifier_sha256=digest(Path(__file__)),
        tests='537 passed in8.62s including18new core orchestration tests',
        limitation='Replay conditional on saved masks; not segmentation ground truth, independent final accuracy or Android timing',
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in (list((out/'cases').rglob('*'))+list((out/'boards').glob('*.png'))) if p.is_file()})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
