"""Refine a bound demo export without refitting or reusing edited MST features."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,uuid
import cv2,numpy as np
from src.demo.manual_brush import refine_masks
from src.correction.seamless_blend import apply_blended
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_export(folder):
    folder=Path(folder);manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    actual={p.name for p in folder.iterdir() if p.is_file() and p.name!='manifest.json'}
    if actual!=set(manifest['files']):raise ValueError('Export file membership changed')
    for name,entry in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Export filenames must be local')
        p=folder/name
        if p.is_symlink():raise ValueError('Export images must be regular local files')
        if digest(p)!=entry['sha256'] or p.stat().st_size!=entry['bytes']:raise ValueError('Export evidence changed: '+name)
    return manifest

def apply_refinement(folder,payload,output_parent):
    folder=Path(folder);verify_export(folder)
    if payload.get('schema_version')!='truehue_manual_mask_edits_v1':raise ValueError('Known manual edit schema required')
    if payload.get('base_manifest_sha256')!=digest(folder/'manifest.json'):raise ValueError('Edits refer to another result')
    old_manifest=digest(folder/'manifest.json')
    report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
    if report.get('masking_mode')!='current' or report.get('status')!='development_experimental_mst':
        raise ValueError('Run the current-mask demo successfully before refinement')
    def image(name,gray=False):
        a=cv2.imread(str(folder/name),0 if gray else cv2.IMREAD_COLOR)
        if a is None:raise ValueError('Required export image unavailable: '+name)
        return a
    original=image('photo_used.png');base_c=image('correction_mask.png',True)
    base_m=image('measurement_mask.png',True);base_p=image('protected_mask.png',True)
    h,w=original.shape[:2]
    if any(a.shape!=(h,w) for a in (base_c,base_m,base_p)):raise ValueError('Matching image/masks required')
    strokes=payload.get('strokes');c,m,p=refine_masks(base_c.tobytes(),base_m.tobytes(),base_p.tobytes(),w,h,strokes)
    masks=[np.frombuffer(a,np.uint8).reshape(h,w).copy() for a in (c,m,p)];c,m,p=masks
    if np.any((c>0)&(p>0)):raise ValueError('Correction cannot overlap retained protection')
    if np.array_equal(c,base_c) and np.array_equal(m,base_m) and np.array_equal(p,base_p):return folder
    stats=compute_masked_lab_statistics(original,m,1000)
    if not stats['valid']:raise ValueError('Refined facial measurement is unavailable: '+stats['reason']+'. Undo or restore visible facial skin.')
    parameters=report.get('renderer_parameters_direct_gamma')
    if not isinstance(parameters,list) or len(parameters)!=3:raise ValueError('Captured renderer parameters required')
    auto_m=folder/'automatic_measurement_mask.png'
    width_mask=cv2.imread(str(auto_m),0) if auto_m.exists() else base_m
    _,xs=np.nonzero(width_mask)
    if not len(xs):raise ValueError('Original facial measurement width unavailable')
    corrected,alpha,blend=apply_blended(original,c,tuple(parameters),face_width=int(xs.max()-xs.min()+1),protected=p>0)
    assert np.array_equal(corrected[alpha==0],original[alpha==0])
    assert np.array_equal(corrected[p>0],original[p>0])
    refined=deepcopy(report);previous_id=report['demo']['run_id'];new_id=uuid.uuid4().hex
    manual=dict(schema_version='truehue_manual_mask_refinement_v1',human_assisted=True,
        previous_run_id=previous_id,base_manifest_sha256=old_manifest,strokes=strokes,
        added_correction_pixels=int(((c>0)&(base_c==0)).sum()),removed_correction_pixels=int(((c==0)&(base_c>0)).sum()),
        added_measurement_pixels=int(((m>0)&(base_m==0)).sum()),removed_measurement_pixels=int(((m==0)&(base_m>0)).sum()),
        explicitly_unprotected_pixels=int(((base_p>0)&(p==0)).sum()),measurement_statistics=stats,
        model_reinferred=False,mst_recomputed=False,controls_source='unchanged_captured_historical_model',
        calibration_admitted=False,scientifically_validated=False)
    refined.update(manual_refinement=manual,workflow='human_assisted_mask_refinement',display_features={
        'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']},
        measurement=dict(status='success',face_count=report.get('measurement',{}).get('face_count',1),
            source='manual_mask_refinement',statistics=stats,features={
                'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}),
        application_pixels=int((alpha>0).sum()),combined_pipeline_validated=False,quality_gate_passed=False)
    refined['automatic_measurement_contract_sha256']=report.get('automatic_measurement_contract_sha256',report.get('measurement_contract_sha256'))
    refined['measurement_contract_sha256']=hashlib.sha256(json.dumps(dict(version='explicit_manual_measurement_v1',
        image_sha256=digest(folder/'photo_used.png'),mask_bytes_sha256=hashlib.sha256(m.tobytes()).hexdigest(),
        automatic_contract=refined['automatic_measurement_contract_sha256']),sort_keys=True).encode()).hexdigest()
    refined['measurement']['old_lookup_compatible']=False
    refined['demo'].update(run_id=new_id,manual_refinement=True,
        message='Mask refined by you. Correction controls and MST remain experimental.')
    refined.setdefault('limitations',[]).append('User-refined measurement is displayed only; historical MST/features/controls were not recomputed from this edited mask.')
    refined.setdefault('masking',{}).update(manual_refinement=True,blend_report=blend)
    verify_export(folder)
    if digest(folder/'manifest.json')!=old_manifest:raise ValueError('Base result changed during editing')
    output=Path(output_parent)/('truehue_refined_'+new_id[:12]);output.mkdir(parents=True,exist_ok=False)
    # Preserve automatic evidence through every edit revision, plus immediate predecessor.
    automatic=['photo_used.png','correction_mask.png','measurement_mask.png','protected_mask.png','experimental_correction.png','report.json','correction_alpha.npy']
    for name in automatic:
        first=folder/('automatic_'+name);source=first if first.exists() else folder/name
        if source.exists():(output/('automatic_'+name)).write_bytes(source.read_bytes())
    (output/'before_refinement_report.json').write_bytes((folder/'report.json').read_bytes())
    def save(name,a):
        ok,data=cv2.imencode('.png',a)
        if not ok:raise OSError('Cannot encode refined image')
        (output/name).write_bytes(data.tobytes())
    def overlay(mask):
        shown=original.copy();selected=mask>0
        shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8);return shown
    for name,a in [('photo_used.png',original),('correction_mask.png',c),('skin_mask.png',c),('measurement_mask.png',m),
        ('protected_mask.png',p),('experimental_correction.png',corrected),('selected_skin.png',overlay(c)),('facial_measurement.png',overlay(m))]:save(name,a)
    np.save(output/'correction_alpha.npy',alpha,allow_pickle=False)
    (output/'manual_edits.json').write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
    (output/'report.json').write_text(json.dumps(refined,indent=2,allow_nan=False),encoding='utf-8')
    manifest=dict(schema_version='truehue_demo_export_v1',run_id=new_id,saved_utc=datetime.now(timezone.utc).isoformat(),
        files={p.name:dict(sha256=digest(p),bytes=p.stat().st_size) for p in output.iterdir() if p.is_file()})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    verify_export(output);return output
