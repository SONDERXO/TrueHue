"""One explicitly approved106-case facial-scope assessment, using cached data only.

Private expected-output bindings keep individual feedback out of public source.
Expected images are compared only after effective controls are sealed.
"""
from pathlib import Path
import sys
import json
import numpy as np
import cv2

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assess_wb314_exposure_headroom import data,read,sha,write
from src.model_training.facial_exposure_headroom import cap_facial_exposure_headroom
from src.model_training.luminance_chroma_operator import render_rgb8
from src.evaluation.luminance_chroma_scalar import replay

AUTH=ROOT/'outputs/wb314_facial_headroom_authorization_v1'
PARENT=ROOT/'outputs/wb314_exposure_headroom_assessment_v1'
OUT=ROOT/'outputs/wb314_facial_headroom_assessment_v1'
MODEL_SHA='7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'


def measurement(row,cache):
    if row['measurement_kind']=='png':
        path=row['measurement_path']
        if path not in cache:
            image=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
            if image is None:raise ValueError('Bound measurement mask failed decoding')
            cache[path]=image
        return cache[path].copy()
    with np.load(row['input_path'],allow_pickle=False) as z:return z['measurement'].copy()


def main():
    if OUT.exists():raise FileExistsError('No repeated scoped assessment')
    approval=read(AUTH/'approval.json')
    assert approval['exact_reply']=='Approve one scoped check and conditional integration'
    assert sha(AUTH/'approved_proposal.md')==approval['approved_proposal_sha256']
    qa=read(AUTH/'generated_QA.json');assert qa['passed']
    guard=ROOT/'src/model_training/facial_exposure_headroom.py'
    assert sha(guard)==qa['guard_module_sha256']
    assert sha(ROOT/'tests/test_facial_exposure_headroom.py')==qa['test_sha256']
    oldqa=read(ROOT/'outputs/wb314_exposure_headroom_generated_QA_v1/verification.json')
    assert sha(ROOT/'src/model_training/exposure_headroom.py')==oldqa['module_sha256']
    assert read(PARENT/'summary.json')['passed'] is False
    assert sha(ROOT/'outputs/wb314_final_training_v1/model.json')==MODEL_SHA
    for path,digest in read(PARENT/'bindings.json').items():assert sha(Path(path))==digest
    masks=read(ROOT/'outputs/wb314_exposure_headroom_user_feedback_v1/measurement_mask_availability_PRIVATE.json')
    assert masks['passed'];source_masks={r['source_id']:r for r in masks['records']}
    case_sources={r['case_id']:r['source_id'] for r in read(ROOT/'outputs/wb_feature_direct_prediction_v1/rows.json')}
    expected=read(AUTH/'expected_normal_outputs_PRIVATE.json')['records'];assert len(expected)==20
    expected_by_key={r['key']:r for r in expected}
    for r in expected:assert sha(Path(r['expected_path']))==r['expected_sha256']
    rows=read(PARENT/'controls_sealed.json')['records'];assert len(rows)==106
    bindings={str(p):sha(p) for p in [Path(__file__),AUTH/'approval.json',AUTH/'approved_proposal.md',
        AUTH/'generated_QA.json',AUTH/'expected_normal_outputs_PRIVATE.json',guard,
        ROOT/'tests/test_facial_exposure_headroom.py',PARENT/'controls_sealed.json',PARENT/'summary.json']}
    for row in rows:
        if row['group']=='final66':
            source=source_masks[case_sources[row['key']]];path=ROOT/source['measurement_path']
            assert sha(path)==source['measurement_sha256'];bindings[str(path)]=sha(path)
            row['measurement_kind']='png';row['measurement_path']=str(path)
        else:row['measurement_kind']='npz'
        for k in ['input_path','old_output_path']:bindings[row[k]]=sha(Path(row[k]))
    OUT.mkdir();(OUT/'evaluation').mkdir();write(OUT/'bindings.json',bindings)
    write(OUT/'plan.json',dict(cases=106,source_masks=11,decision_scope='measurement_intersect_application_unprotected',
        exact_prior_output_checks=86,private_normal_expected_output_checks=20,
        new_model_inference=0,new_fits=0,source_JPEG_decodes=0,mask_inference=0,
        retries_allowed=False,old_failed_assessment_preserved=True))
    masks_cache={};decisions=[]
    for row in rows:
        image,alpha,protected,old=data(row);m=measurement(row,masks_cache)
        decisions.append(dict(row,facial_guard=cap_facial_exposure_headroom(image,m,alpha,protected,row['controls'])))
    write(OUT/'controls_sealed.json',dict(records=decisions,sealed_before_expected_image_comparison=True))
    results=[];scalar_count=0
    for i,r in enumerate(decisions):
        image,alpha,protected,old=data(r);m=measurement(r,masks_cache)
        immutable=[a.tobytes() for a in [image,alpha,protected,m]]
        effective=r['facial_guard']['effective_controls'];candidate=render_rgb8(image,alpha,protected,effective)
        if r['facial_guard']['applied']:
            scalar,_=replay(image,image,alpha,protected,effective)
            assert np.array_equal(scalar,candidate);scalar_count+=1
        assert immutable==[a.tobytes() for a in [image,alpha,protected,m]]
        assert np.array_equal(candidate[protected],image[protected]) and np.array_equal(candidate[alpha==0],image[alpha==0])
        target=old
        if r['group']=='normal20':
            e=expected_by_key[r['key']]
            with np.load(e['expected_path'],allow_pickle=False) as z:target=z[e['expected_key']].copy()
        path=OUT/'evaluation'/f'{i:03d}.npz';np.savez(path,candidate=candidate)
        results.append(dict(group=r['group'],key=r['key'],facial_guard=r['facial_guard'],
            output_path=str(path),output_sha256=sha(path),exact_previous_output=bool(np.array_equal(candidate,old)),
            exact_expected_output=bool(np.array_equal(candidate,target)),old_exact_input=bool(np.array_equal(old,image)),
            new_exact_input=bool(np.array_equal(candidate,image))))
    prior=[r for r in results if r['group']!='normal20'];normals=[r for r in results if r['group']=='normal20']
    gates=dict(all86_prior_outputs_exact=all(r['exact_previous_output'] for r in prior),
        all20_expected_normal_outputs_exact=all(r['exact_expected_output'] for r in normals),
        all10_normal_identities_preserved=all(r['new_exact_input'] for r in normals if r['old_exact_input']),
        protected_outside_and_inputs_preserved=True,old_global_screen_remains_failed=read(PARENT/'summary.json')['passed'] is False)
    for path,digest in bindings.items():assert sha(Path(path))==digest
    summary=dict(passed=all(gates.values()),gates=gates,cases=106,model_sha256=MODEL_SHA,
        policy='facial_measurement_luminance_headroom_v1',guard_module_sha256=sha(guard),
        prior_outputs_exact=sum(r['exact_previous_output'] for r in prior),prior_outputs=86,
        expected_normal_outputs_exact=sum(r['exact_expected_output'] for r in normals),normal_outputs=20,
        changed_controls=sum(r['facial_guard']['applied'] for r in results),
        changed_control_scalar_checks=scalar_count,protected_outside_checks=106,input_immutability_checks=106,
        new_model_inference=0,new_fits=0,source_JPEG_decodes=0,mask_inference=0,
        automatic_integration_permitted=all(gates.values()),general_correction_necessity_proven=False,
        final_qualification_complete=False,expert_Form_changed=False,new_human_ratings=0)
    write(OUT/'results_PRIVATE.json',results);write(OUT/'summary.json',summary)
    write(OUT/'verification.json',dict(completed=True,technical_checks_pass=True,screen_pass=summary['passed'],
        artifacts={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
