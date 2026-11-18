from pathlib import Path
import json
import hashlib
import cv2
import numpy as np
import pytest
from src.model_training import five_control_feature_preparation as prep


def fixture(root):
    rows=[];sources=[];names=[f'x{i}' for i in range(281)]
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for i in range(11):
        source=f'generated_{i:02}';folder=root/'outputs'/source;folder.mkdir(parents=True)
        alpha=np.ones((256,256),float);protected=np.zeros((256,256),bool);protected[0,0]=True;alpha[protected]=0
        np.savez(folder/'support.npz',alpha=alpha,protected=protected,reference=np.array([object()],dtype=object))
        assert cv2.imwrite(str(folder/'measurement.png'),np.full((256,256),255,np.uint8))
        (folder/'receipt.json').write_text('{}')
        sources.append(dict(source_id=source,measurement_path=str(folder/'measurement.png'),measurement_sha256=sha(folder/'measurement.png'),
            selected_receipt=str(folder/'receipt.json'),selected_receipt_sha256=sha(folder/'receipt.json'),identity_saved_feature_vector=[0.]*281))
        for role in prep.ROLES:
            image=np.full((256,256,3),0 if role=='identity' else 1,np.uint8)
            p=folder/(role+'.npz');np.savez(p,input=image,output=np.array([object()],dtype=object))
            rows.append(dict(case_id=source+'__'+role,source_id=source,role=role,generated_fixture=True,
                y=[1.,1.,1.,1.,0.],allowed_input_key='input',input_pack=str(p),input_pack_sha256=sha(p),
                cached_support_pack=str(folder/'support.npz'),cached_support_sha256=sha(folder/'support.npz'),parent_training_admitted=False))
    return dict(rows=rows,feature_sources=sources,feature_names=names)


def fake(image,*args):return [float(image[0,0,0])]*281,{'generated_test':True}


def test_staged_keys_and_poison_members_unread(tmp_path):
    plan=fixture(tmp_path);inputs=prep.BoundInputs(tmp_path,plan);events=[]
    rows=prep.prepare(plan,inputs,{},extractor=fake,record=lambda event,row:events.append(event))
    assert len(rows)==66 and events[:11]==['identity_pass']*11 and events[11]=='all_identities_passed'
    assert not any(r['key'] in ['reference','output'] for r in inputs.access)
    decoded=[r for r in inputs.access if r['key']=='input']
    assert len(decoded)==66 and all(r['role']=='identity' for r in decoded[:11])


def test_last_identity_failure_blocks_all_nonidentity_decodes(tmp_path):
    plan=fixture(tmp_path);plan['feature_sources'][-1]['identity_saved_feature_vector'][0]=1.
    inputs=prep.BoundInputs(tmp_path,plan);events=[]
    with pytest.raises(prep.IdentityParityError):prep.prepare(plan,inputs,{},extractor=fake,record=lambda e,r:events.append(e))
    assert events.count('identity_pass')==10 and events[-1]=='identity_failure'
    assert all(r['role']=='identity' for r in inputs.access if r['key']=='input')


def test_hash_barrier_before_any_decode(tmp_path,monkeypatch):
    plan=fixture(tmp_path);plan['rows'][-1]['input_pack_sha256']='0'*64
    monkeypatch.setattr(np,'load',lambda *a,**k:pytest.fail('No arrays before full hash barrier'))
    monkeypatch.setattr(cv2,'imread',lambda *a,**k:pytest.fail('No mask before full hash barrier'))
    with pytest.raises(ValueError):prep.BoundInputs(tmp_path,plan)


def test_forbidden_path_or_key_rejected(tmp_path):
    plan=fixture(tmp_path);plan['rows'][0]['allowed_input_key']='output'
    with pytest.raises(ValueError):prep.BoundInputs(tmp_path,plan)
    plan['rows'][0]['allowed_input_key']='input';plan['rows'][0]['input_pack']=str(tmp_path/'outputs/locked/final24.npz')
    with pytest.raises(ValueError):prep.BoundInputs(tmp_path,plan)


def test_nonidentity_feature_failure_preserved_without_substitution(tmp_path):
    plan=fixture(tmp_path);inputs=prep.BoundInputs(tmp_path,plan);events=[]
    def fail(image,*args):
        if image[0,0,0]:raise ValueError('feature unavailable')
        return fake(image,*args)
    with pytest.raises(ValueError):prep.prepare(plan,inputs,{},extractor=fail,record=lambda e,r:events.append(e))
    assert events.count('identity_pass')==11 and events[-1]=='all_identities_passed'
    assert len([r for r in inputs.access if r['key']=='input' and r['role']!='identity'])==1


def test_immutable_files_rechecked(tmp_path):
    plan=fixture(tmp_path);inputs=prep.BoundInputs(tmp_path,plan)
    Path(plan['feature_sources'][0]['selected_receipt']).write_text('{"changed":true}')
    with pytest.raises(ValueError):inputs.recheck()


@pytest.mark.parametrize('variant,direction',[('clean','none'),('color','none'),('exposure','under'),('exposure','over'),('combined','under'),('combined','over')])
def test_independent281arithmetic_on_generated_rgb(variant,direction):
    import math
    from src.evaluation.five_control_feature_scalar import features
    from src.model_training.blue_axis_preparation import features281
    from src.model_training.whole_scene_features import SCENE_FEATURES
    from src.model_training.green_distribution_features import ADDITIONS
    from src.model_training.histogram_gap_features import NAMES as GAP
    from src.model_training.joint_log_colour import NAMES as JOINT
    from src.distortion_generation.directional_exposure_recipe import render_rgb
    names=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees','input_mst_score']+list(SCENE_FEATURES)+list(ADDITIONS)+list(GAP)+list(JOINT)
    mapping=dict(schema_version='truehue_shared_core_development_mst_v1',status='development_unvalidated_transfer',
        measurement_core_sha256='generated_core',feature_control_contract_sha256='generated_contract',
        ita_knots=[-90.,90.],mst_score_knots=[9.,2.],calibration_admitted=False,runtime_adopted=False)
    original=np.random.default_rng(151).integers(0,256,(256,256,3),dtype=np.uint8)
    image,_=render_rgb(original,np.ones((256,256),float),'medium',variant,direction)
    mask=np.full((256,256),255,np.uint8)
    actual,_=features281(image,mask,mapping,names);expected=features(image,mask,mapping,names)
    assert len(actual)==len(expected)==281
    assert all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(actual,expected))
