from types import SimpleNamespace
from pathlib import Path
import hashlib,json
import cv2,numpy as np,pytest
from src.demo.manual_brush import refine_masks
from src.demo.manual_refinement import apply_refinement,verify_export,digest
from src.demo.service import DemoRun,save_run,load_refined_run


def base_export(tmp_path):
    y,x=np.indices((64,64));image=np.stack([x+70,y+70,x+y+40],axis=2).astype(np.uint8)
    c=np.zeros((64,64),np.uint8);c[12:52,12:52]=255
    m=np.zeros_like(c);m[10:54,10:54]=255
    p=np.zeros_like(c);p[:,:8]=255
    report=dict(status='development_experimental_mst',masking_mode='current',
        measurement=dict(status='success',face_count=1),measurement_contract_sha256='old-current-contract',
        renderer_parameters_direct_gamma=[.8,1.1,.9],features={'input_ita_degrees':999},mst={'label':4,'measurement_source':'historical_mask'},
        masking=dict(requires_glasses_choice=False),limitations=[],quality_gate_passed=False)
    run=DemoRun('original.png','original-sha',SimpleNamespace(image=image,mask=c,measurement_mask=m,
        protected_mask=p,alpha=(c>0).astype(float),corrected=image.copy(),report=report),{})
    return save_run(run,tmp_path/'base')


def payload(folder,**stroke):
    return dict(schema_version='truehue_manual_mask_edits_v1',base_manifest_sha256=digest(folder/'manifest.json'),
        strokes=[dict(target='both',mode='remove',radius=4,points=[[25,25],[31,25]],**stroke)])


def test_export_refinement_preserves_originals_and_historical_controls(tmp_path):
    folder=base_export(tmp_path);before={p.name:digest(p) for p in folder.iterdir()}
    out=apply_refinement(folder,payload(folder),tmp_path/'edited')
    verify_export(out)
    assert {p.name:digest(p) for p in folder.iterdir()}==before
    report=json.loads((out/'report.json').read_text());old=json.loads((folder/'report.json').read_text())
    assert report['features']==old['features'] and report['mst']==old['mst']
    assert report['renderer_parameters_direct_gamma']==old['renderer_parameters_direct_gamma']
    assert report['measurement_contract_sha256']!=old['measurement_contract_sha256']
    assert report['automatic_measurement_contract_sha256']==old['measurement_contract_sha256']
    assert not report['manual_refinement']['model_reinferred'] and not report['manual_refinement']['mst_recomputed']
    assert report['manual_refinement']['removed_correction_pixels']>0
    assert (out/'automatic_report.json').read_bytes()==(folder/'report.json').read_bytes()
    c=cv2.imread(str(out/'correction_mask.png'),0);p=cv2.imread(str(out/'protected_mask.png'),0)
    image=cv2.imread(str(out/'photo_used.png'));result=cv2.imread(str(out/'experimental_correction.png'))
    np.testing.assert_array_equal(result[c==0],image[c==0]);np.testing.assert_array_equal(result[p>0],image[p>0])
    run=load_refined_run(out);assert run.success and 'refined by you' in run.message


def test_additions_require_explicit_unlock_of_protected_pixels(tmp_path):
    folder=base_export(tmp_path);q=payload(folder)
    q['strokes']=[dict(target='correction',mode='add',radius=3,points=[[4,32]],unlock=False)]
    assert apply_refinement(folder,q,tmp_path/'edited')==folder
    q['strokes'][0]['unlock']=True
    out=apply_refinement(folder,q,tmp_path/'edited')
    report=json.loads((out/'report.json').read_text())
    assert report['manual_refinement']['explicitly_unprotected_pixels']>0
    p=cv2.imread(str(out/'protected_mask.png'),0);assert p[32,4]==0 and p[0,0]==255


def test_second_edit_retains_first_automatic_evidence_and_previous_report(tmp_path):
    base=base_export(tmp_path);first=apply_refinement(base,payload(base),tmp_path/'edited')
    second=apply_refinement(first,payload(first,unlock=False),tmp_path/'edited')
    # Repeating the identical stroke has no net effect and returns current export.
    assert second==first
    q=payload(first);q['strokes'][0]['points']=[[40,40]]
    second=apply_refinement(first,q,tmp_path/'edited')
    assert (second/'automatic_measurement_mask.png').read_bytes()==(base/'measurement_mask.png').read_bytes()
    assert (second/'before_refinement_report.json').read_bytes()==(first/'report.json').read_bytes()
    assert (second/'automatic_report.json').read_bytes()==(base/'report.json').read_bytes()


def test_invalid_measurement_and_stale_payload_cannot_create_result(tmp_path):
    folder=base_export(tmp_path);q=payload(folder);q['base_manifest_sha256']='stale'
    with pytest.raises(ValueError,match='another result'):apply_refinement(folder,q,tmp_path/'edited')
    q=payload(folder);q['strokes']=[dict(target='measurement',mode='remove',radius=32,points=[[32,32]])]
    with pytest.raises(ValueError,match='unavailable'):apply_refinement(folder,q,tmp_path/'edited')
    assert not (tmp_path/'edited').exists()


def test_tampered_export_is_rejected(tmp_path):
    folder=base_export(tmp_path);q=payload(folder)
    (folder/'protected_mask.png').write_bytes(b'changed')
    with pytest.raises(ValueError,match='evidence changed'):apply_refinement(folder,q,tmp_path/'edited')


def test_unbound_automatic_evidence_cannot_be_injected(tmp_path):
    folder=base_export(tmp_path);q=payload(folder)
    (folder/'automatic_report.json').write_text('unbound')
    with pytest.raises(ValueError,match='membership changed'):apply_refinement(folder,q,tmp_path/'edited')


def test_generic_service_save_keeps_refined_history_and_automatic_evidence(tmp_path):
    base=base_export(tmp_path);out=apply_refinement(base,payload(base),tmp_path/'edited')
    saved=save_run(load_refined_run(out),tmp_path/'saved')
    verify_export(saved)
    assert {p.name:digest(p) for p in saved.iterdir()}=={p.name:digest(p) for p in out.iterdir()}
    assert (saved/'automatic_report.json').read_bytes()==(base/'report.json').read_bytes()


def test_brush_restore_undo_reset_and_continuous_line_have_same_contract():
    base=bytes([255]*40*40);blank=bytes(40*40)
    stroke=dict(target='both',mode='remove',radius=1,points=[[10,10],[30,10]])
    c,m,p=refine_masks(base,base,blank,40,40,[stroke])
    assert all(c[10*40+x]==0 and m[10*40+x]==0 for x in range(10,31))
    restore=dict(stroke,mode='restore')
    assert refine_masks(base,base,blank,40,40,[stroke,restore])==(base,base,blank)
    assert refine_masks(base,base,blank,40,40,[])==(base,base,blank)


@pytest.mark.parametrize('change',[{'points':[[float('nan'),1]]},{'points':[[-1,1]]},
    {'mode':'invent'},{'radius':True},{'radius':100},{'unlock':'yes'}])
def test_bad_strokes_fail(change):
    stroke=dict(target='both',mode='remove',radius=2,points=[[10,10]]);stroke.update(change)
    with pytest.raises(ValueError):refine_masks(bytes([255]*32*32),bytes([255]*32*32),bytes(32*32),32,32,[stroke])
