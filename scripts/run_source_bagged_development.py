"""Explicit fixed stage1 and stage2 entrypoints. No effects on import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
import shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gap_training_feasibility import join_inputs, f32
from src.model_training.source_bagged_training import run_once
from src.model_training.source_bagged_verification import verify
from src.model_training.portable_bagged_tree import PortableBaggedTree
from src.model_training.gap_source_held_workflow import score_context, aggregate
from scripts.prepare_source_bagged_design import versions
import cv2
import numpy as np

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def load_plan():
    folder=ROOT/'outputs/source_bagged_design_v1';qa=read(folder/'engineering_PRIVATE.json');plan=read(folder/'plan_PRIVATE.json')
    assert qa['passed'] and qa['plan_sha256']==sha(folder/'plan_PRIVATE.json')
    assert qa['runtime_versions']==plan['runtime_versions']==versions()
    assert plan['user_authorized'] and plan['members']==64 and not plan['final_access']
    for name,digest in plan['input_sha256'].items():assert sha(ROOT/name)==digest,name
    return plan

def inputs(plan):
    rows={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps=read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')
    return rows,gaps

def snapshot(plan,fold,records,gaps):
    fit={c:records[c] for c in fold['fitting_cases']}
    local=dict(fitting_records=[dict(case_id=c,source=fit[c]['publisher_group'],role=fit[c]['experimental_role']) for c in fold['fitting_cases']],
               feature_names=plan['feature_names'],new_feature_names=plan['feature_names'][16:],excluded_group=fold['held_publisher_group'])
    rows=join_inputs(local,fit,gaps)
    assert len(rows)==40 and len({r['source'] for r in rows})==10
    return rows

def fit_fold(out,plan,fold,records,gaps):
    rows=snapshot(plan,fold,records,gaps)
    candidate,replay=run_once(out,rows,plan['feature_names'],fold['held_publisher_group'],dict(protocol_id=plan['protocol_id'],fold=fold))
    checked=verify(candidate,rows,replay,plan['feature_names'],fold['held_publisher_group'])
    write(out/'verification_PRIVATE.json',checked)
    return candidate

def first(plan):
    records,gaps=inputs(plan);out=ROOT/plan['first_output']
    fit_fold(out,plan,plan['folds'][0],records,gaps)
    write(out/'sealed_PRIVATE.json',dict(candidate_sha256=sha(out/'candidate_PRIVATE.json'),
        snapshot_sha256=sha(out/'fitting_inputs_PRIVATE.json'),plan_sha256=sha(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json'),
        held_predictions=0,member_fits=64))
    print('Stage1 complete:64member fits independently verified; 0held predictions/photos')

def all_fits(out,plan,records,gaps):
    reused=ROOT/plan['first_output'];seal=read(reused/'sealed_PRIVATE.json')
    assert seal['plan_sha256']==sha(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json')
    assert sha(reused/'candidate_PRIVATE.json')==seal['candidate_sha256']
    assert sha(reused/'fitting_inputs_PRIVATE.json')==seal['snapshot_sha256']
    write(out/'reuse_seal_PRIVATE.json',seal)
    models=[]
    for i,fold in enumerate(plan['folds']):
        folder=out/fold['held_publisher_group']
        if i==0:
            assert read(reused/'fitting_inputs_PRIVATE.json')==snapshot(plan,fold,records,gaps)
            folder.mkdir()
            for name in ['candidate_PRIVATE.json','fitting_inputs_PRIVATE.json','training_replay_PRIVATE.json']:
                shutil.copyfile(reused/name,folder/name)
            candidate=read(folder/'candidate_PRIVATE.json')
            assert sha(folder/'candidate_PRIVATE.json')==seal['candidate_sha256']
            checked=verify(candidate,read(folder/'fitting_inputs_PRIVATE.json'),read(folder/'training_replay_PRIVATE.json'),plan['feature_names'],fold['held_publisher_group'])
            write(folder/'verification_PRIVATE.json',checked)
        else:
            candidate=fit_fold(folder,plan,fold,records,gaps)
        models.append(dict(fold=fold,directory=folder.name,candidate_sha256=sha(folder/'candidate_PRIVATE.json'),reused=i==0))
        write(out/'models_PRIVATE.json',models)
    assert len(models)==11
    write(out/'all_fits_verified_PRIVATE.json',dict(passed=True,ensembles=11,total_member_fits=704,new_member_fits=640,reused_member_fits=64))
    return models

def load_supports(plan):
    supports={}
    for s in plan['supports']:
        folder=ROOT/s['directory']
        assert folder.resolve().parent==(ROOT/'outputs/histogram_gap_source_held_comparison_v1/supports').resolve()
        assert sha(folder/'manifest_PRIVATE.json')==s['manifest_sha256']
        for name,h in s['files'].items():assert sha(folder/name)==h
        alpha=np.load(folder/'alpha.npy',allow_pickle=False)
        protected=cv2.imread(str(folder/'protected_mask.png'),0)>0
        assert alpha.shape==protected.shape==(256,256) and np.isfinite(alpha).all() and ((alpha>=0)&(alpha<=1)).all()
        assert not alpha[protected].any()
        supports[s['source']]=dict(alpha=alpha,mask=alpha>0,protected=protected)
    assert len(supports)==11
    return supports

def comparison(plan):
    out=ROOT/plan['comparison_output'];out.mkdir()
    write(out/'execution_plan_PRIVATE.json',dict(plan=plan,plan_sha256=sha(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json')))
    try:
        records,gaps=inputs(plan)
        models=all_fits(out,plan,records,gaps)
        assert read(out/'all_fits_verified_PRIVATE.json')['passed']
        # First photographic/support array read occurs ONLY beyond this barrier.
        supports=load_supports(plan)
        write(out/'all_supports_sealed_PRIVATE.json',dict(passed=True,supports=plan['supports']))
        assets=out/'review_assets';assets.mkdir()
        gaps={r['case_id']:r for r in gaps};predictions=[];public=[]
        declared={r['case_id']:r for r in plan['pixel_containers']}
        prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
        for model in models:
            candidate=read(out/model['directory']/'candidate_PRIVATE.json');predictor=PortableBaggedTree(candidate)
            for case in model['fold']['evaluation_cases']:
                r=records[case];g=gaps[case];assert g['source']==r['publisher_group'] and g['role']==r['experimental_role']
                x=r['input_vector_float32']+[f32(g['features'][n]) for n in plan['feature_names'][16:]]
                controls=predictor.predict_one(x)
                path=Path(r['pixels_file']);assert path.resolve()==(prep/case/'paired_pixels.npz').resolve()
                assert path.resolve()==Path(declared[case]['path']).resolve() and sha(path)==r['pixels_sha256']==declared[case]['sha256']
                with np.load(path,allow_pickle=False) as pack:
                    image=pack['input_rgb8'];reference=pack['reference_rgb8'];protected=pack['protected']
                    support=supports[r['publisher_group']];assert np.array_equal(protected,support['protected'])
                    output,metric=score_context(image,reference,support['alpha'],support['mask'],protected,controls)
                    anonymous=f'case-{len(public)+1:02}'
                    bit=hashlib.sha256((plan['protocol_id']+case).encode()).digest()[-1]&1
                    for name,data in [('A',output if bit else image),('B',image if bit else output),('R',reference)]:
                        assert cv2.imwrite(str(assets/f'{anonymous}_{name}.png'),data[:,:,::-1])
                    predictions.append(dict(case_id=case,review_id=anonymous,source=r['publisher_group'],role=r['experimental_role'],
                        controls=controls,primary=metric,output_panel='A' if bit else 'B',
                        parameter_absolute_error=[abs(a-b) for a,b in zip(controls,r['nominal_controls'])]))
                    public.append(dict(id=anonymous,kind='identity' if r['experimental_role']=='identity' else 'distorted',
                        A=f'review_assets/{anonymous}_A.png',B=f'review_assets/{anonymous}_B.png',
                        R=None if r['experimental_role']=='identity' else f'review_assets/{anonymous}_R.png'))
                write(out/'predictions_PRIVATE.json',predictions)
        assert len(predictions)==44
        write(out/'review_public.json',dict(protocol_id=plan['protocol_id'],cases=public))
        write(out/'role_ledger_PRIVATE.json',read(prep/'role_ledger_PRIVATE.json'))
        byrole=aggregate(predictions,'primary')
        numeric=all(byrole[role]['source_equal_DE_improvement']>0 for role in plan['families'])
        write(out/'summary_PRIVATE.json',dict(attempted=48,available=44,excluded=4,primary=dict(by_role=byrole),
            numeric_families_pass=numeric,visual_status='PENDING' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE',model_ready=False))
        write(out/'status_PRIVATE.json',dict(status='COMPLETED_PENDING_INDEPENDENT_VERIFICATION',new_member_fits=640,
            reused_member_fits=64,held_controls=44,renders=44))
        for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
        print('Stage2 complete: all fits preceded44held predictions; independent verification required')
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise

def main():
    if sys.argv[1:] not in [['--execute-first-fitting-only'],['--execute-fixed-development']]:
        raise SystemExit('Explicit stage flag required')
    plan=load_plan()
    if sys.argv[1]=='--execute-first-fitting-only':first(plan)
    else:comparison(plan)

if __name__=='__main__':main()
