"""Artificial images and temporary workspaces only; never scientific dataset IO."""
from copy import deepcopy
import importlib.util,json,subprocess,sys
from pathlib import Path
import cv2,numpy as np,pytest
from src.model_training.blue_axis_preparation import features281,blue_transform,prepare_once,read,write,sha
from src.model_training.blue_axis_training import join60,fit_once
from src.model_training.blue_axis_verification import verify
from src.model_training.histogram_gap_features import NAMES as GAP
from src.model_training.joint_log_colour import NAMES as JOINT
from src.model_training.gap_training_feasibility import SETTINGS

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('blue_independent',ROOT/'scripts/verify_blue_axis_feasibility.py')
independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
NAMES=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees','input_mst_score',
 'scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90','scene_any_zero_fraction','scene_any_full_fraction',
 'input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast']+list(GAP)+list(JOINT)
ROLES=['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']
TARGETS=[[1.,1.,1.],[.7,1.,1.],[1/.7,1.,1.],[1.,255/245,1.],[1.,1.,255/245],[1.,1.,245/255]]
OPS={r:dict(gamma=1,red_gain=1,blue_gain=b) for r,b in [('blue_decrease',245/255),('blue_increase',255/245)]}
MAP=dict(schema_version='truehue_shared_core_development_mst_v1',measurement_core_sha256='GENERATED',feature_control_contract_sha256='GENERATED',
 status='development_unvalidated_transfer',calibration_admitted=False,runtime_adopted=False,ita_knots=[-90.,90.],mst_score_knots=[10.,1.])

def image():
    y,x=np.indices((256,256));return np.stack([100+x%120,60+y%100,30+(x+y)%180],axis=2).astype(np.uint8)

@pytest.mark.parametrize('role',list(OPS))
def test_forward_all_codes_immutability_and_clipping(role):
    rgb=np.stack(np.meshgrid(np.arange(256,dtype=np.uint8),np.arange(256,dtype=np.uint8)),axis=2)
    rgb=np.concatenate([rgb,rgb[:,:,:1]],axis=2);before=rgb.copy();actual,report=blue_transform(rgb,OPS[role])
    b=OPS[role]['blue_gain'];expected=np.array([round(min(1.,(c/255)*b)*255) for c in range(256)],np.uint8)
    assert np.array_equal(actual[:,:,2],expected[rgb[:,:,2]]) and np.array_equal(actual[:,:,:2],rgb[:,:,:2])
    assert np.array_equal(rgb,before) and report['clipped_channel_samples']==int(((rgb[:,:,2]/255)*b>1).sum())

def test_full_features_independent_composition_and_blue_recomputation():
    rgb=image();mask=np.full((256,256),255,np.uint8);before=rgb.copy()
    original,_=features281(rgb,mask,MAP,NAMES);edited,_=blue_transform(rgb,OPS['blue_decrease']);new,_=features281(edited,mask,MAP,NAMES)
    scalar=independent.independent_features(edited,mask,MAP,NAMES)
    assert new[:22]==scalar[:22] and np.allclose(new[22:],scalar[22:],atol=1e-7,rtol=1e-7)
    assert original[:5]!=new[:5] and np.array_equal(rgb,before) and np.all(mask==255)
    with pytest.raises(ValueError):features281(rgb,np.zeros_like(mask),MAP,NAMES)

def workspace(root):
    base=[];gaps=[];joint=[];cases=[];refs=[];supports=[]
    for s in range(11):
        source=f'GENERATED_source{s}';rgb=np.roll(image(),s,axis=0);mask=np.full((256,256),255,np.uint8)
        folder=root/'outputs'/f'GENERATED_support{s}';folder.mkdir(parents=True);cv2.imwrite(str(folder/'measurement_mask.png'),mask);write(folder/'receipt.json',{'generated_fixture_only':True})
        supports.append(dict(source=source,selected=dict(directory=str(folder.relative_to(root)),receipt='receipt.json',receipt_sha256=sha(folder/'receipt.json'),files={'measurement_mask.png':sha(folder/'measurement_mask.png')})))
        for k,role in enumerate(ROLES):
            c=f'GENERATED_{s}_{role}';cases.append(dict(case_id=c,source=source,role=role,kind='EXACT_OLD_RECORD_REUSE' if k<4 else 'NEW_BLUE',nominal_controls=TARGETS[k]))
            if k>=4:continue
            edited=rgb.copy()
            if k in [1,2]:edited=np.rint((rgb.astype(float)/255)**(1/.7 if k==1 else .7)*255).astype(np.uint8)
            if k==3:edited[:,:,0]=np.rint(rgb[:,:,0].astype(float)*245/255).astype(np.uint8)
            path=root/'outputs/reviewed_ffhq_restoration_preparation_v1'/c/'paired_pixels.npz';path.parent.mkdir(parents=True);np.savez_compressed(path,input_rgb8=edited)
            x,_=features281(edited,mask,MAP,NAMES)
            base.append(dict(case_id=c,publisher_group=source,experimental_role=role,generated_fixture=False,status='available',input_vector_float32=x[:16],nominal_controls=TARGETS[k],pixels_file=str(path),pixels_sha256=sha(path)))
            gaps.append(dict(case_id=c,generated_fixture=False,features=dict(zip(GAP,x[16:22]))));joint.append(dict(case_id=c,generated_fixture=False,features=x[22:]))
            if k==0:refs.append(dict(source=source,identity_case=c,identity_container=str(path),identity_sha256=sha(path)))
    for rel,data in [('reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',base),('histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',gaps),('joint_log_colour_exposed_audit_v1/features_PRIVATE.json',joint),('shared_core_mst_features_v1/mapping_PRIVATE.json',MAP)]:
        p=root/'outputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);write(p,data)
    return dict(cases=cases,source_references=refs,support_sources=supports,feature_names=NAMES,operations=OPS,original_records_reused=44,excluded_cases=[f'GENERATED_excluded{i}' for i in range(6)],first_excluded_source='GENERATED_source0',first_fitting_cases=[c['case_id'] for c in cases if c['source']!='GENERATED_source0'])

def test_generated_66_preparation_and_independent_roundtrip(tmp_path):
    plan=workspace(tmp_path);out=tmp_path/'prepared';prepare_once(tmp_path,out,plan,dict(generated_fixture_only=True))
    assert independent.verify_preparation(tmp_path,out,plan)['passed']
    rows=read(out/'rows_PRIVATE.json');assert len(join60(plan,rows+[{'case_id':'GENERATED_HELD_MALFORMED'}]))==60
    assert sum(r['old_record_reused'] for r in rows)==44
    with pytest.raises(FileExistsError):prepare_once(tmp_path,out,plan,{})

def test_identity_parity_failure_before_new_derivatives(tmp_path):
    plan=workspace(tmp_path);p=tmp_path/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json';rows=read(p);rows[0]['input_vector_float32'][0]+=1;write(p,rows)
    out=tmp_path/'failed'
    with pytest.raises(ValueError,match='identityparity'):prepare_once(tmp_path,out,plan,{})
    assert not any(p.is_dir() for p in out.iterdir()) and read(out/'status_PRIVATE.json')['status']=='FAILED_PRESERVED_NO_RETRY'

def toy():
    rows=[];cases=[]
    for s in range(10):
        for k,role in enumerate(ROLES):
            c=f'GENERATED_{s}_{role}';source=f'GENERATED_source{s}'
            rows.append(dict(case_id=c,source=source,role=role,x=[float(k)]+[0.]*280,y=TARGETS[k].copy(),generated_fixture=False,status='available'))
            cases.append(dict(case_id=c,source=source,role=role,nominal_controls=TARGETS[k].copy()))
    return dict(cases=cases,first_fitting_cases=[r['case_id'] for r in rows],first_excluded_source='GENERATED_HELD'),rows

@pytest.mark.parametrize('fault',['missing','duplicate','source','role','generated','target','nonfinite','held'])
def test_bad_join_rejected(fault):
    p,r=toy()
    if fault=='missing':r.pop()
    elif fault=='duplicate':r.append(deepcopy(r[0]))
    elif fault=='source':r[0]['source']='wrong'
    elif fault=='role':r[0]['role']='wrong'
    elif fault=='generated':r[0]['generated_fixture']=True
    elif fault=='target':r[0]['y'][0]=0
    elif fault=='nonfinite':r[0]['x'][0]=float('nan')
    elif fault=='held':p['first_excluded_source']=r[0]['source']
    with pytest.raises(ValueError):join60(p,r)

@pytest.fixture(scope='module')
def fitted(tmp_path_factory):
    p,r=toy();rows=join60(p,r);out=tmp_path_factory.mktemp('GENERATED_blue')/'fit';fit_once(out,rows,NAMES,{'generated_fixture_only':True})
    return rows,read(out/'candidate_PRIVATE.json'),read(out/'training_replay_PRIVATE.json')

def test_fit_export_independent_blue_gates(fitted):
    rows,tree,replay=fitted;result=verify(tree,rows,replay,NAMES,'GENERATED_HELD')
    assert result['classification']=='BLUE_FITTING_FEASIBILITY_PASS' and result['held_predictions']==0

@pytest.mark.parametrize('fault',['leaf','prediction','settings','graph'])
def test_scalar_corruption_rejected(fitted,fault):
    rows,t,r=deepcopy(fitted)
    if fault=='leaf':next(n for n in t['nodes'] if n['kind']=='leaf')['values'][2]+=.1
    elif fault=='prediction':r['candidate_predictions'][0][2]+=.1
    elif fault=='settings':r['settings']['max_depth']=5
    elif fault=='graph':t['nodes'][0]=dict(kind='split',feature=0,threshold=0.,left=0,right=0)
    with pytest.raises(AssertionError):verify(t,rows,r,NAMES,'GENERATED_HELD')

def test_constant_blue_correctly_stops(fitted):
    rows,t,r=deepcopy(fitted);mean=np.mean([row['y'] for row in rows],axis=0).tolist()
    t['nodes']=[dict(kind='leaf',values=mean)];r['candidate_predictions']=[mean]*60;r['candidate_leaves']=[0]*60
    assert verify(t,rows,r,NAMES,'GENERATED_HELD')['classification']=='BLUE_FITTING_FEASIBILITY_STOP'

def test_failed_fit_preserved_no_retry(tmp_path):
    p,r=toy();calls=[]
    class Broken:
        def __init__(self,**kw):calls.append(kw)
        def fit(self,x,y):raise RuntimeError('GENERATED failure')
    out=tmp_path/'failed'
    with pytest.raises(RuntimeError):fit_once(out,join60(p,r),NAMES,{},factory=Broken)
    assert len(calls)==1 and read(out/'status_PRIVATE.json')['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):fit_once(out,join60(p,r),NAMES,{})

def test_scalar_verifier_import_has_no_optimizer():
    code="import sys;from src.model_training.blue_axis_verification import verify;assert 'sklearn' not in sys.modules;assert 'numpy' not in sys.modules"
    assert subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True).returncode==0
