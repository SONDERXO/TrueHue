"""Fixed blue derivatives and input-derived281features; no IO on import."""
from pathlib import Path
import hashlib,json,math
import cv2,numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.shared_core_mst import predict_score
from .whole_scene_features import scene_features
from .green_distribution_features import green_distribution_features
from .histogram_gap_features import histogram_gap_features,NAMES as GAP_NAMES
from .joint_log_colour import extract,NAMES as JOINT_NAMES
from .gap_training_feasibility import f32

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def blue_transform(rgb,operation):
    if not isinstance(rgb,np.ndarray) or rgb.dtype!=np.uint8 or rgb.shape!=(256,256,3):raise ValueError('Normalized256RGB8 required')
    if operation['gamma']!=1 or operation['red_gain']!=1 or operation['blue_gain'] not in [245/255,255/245]:raise ValueError('Only fixed pureblue operations allowed')
    raw=rgb.astype(float)/255;raw[:,:,2]*=operation['blue_gain']
    clips=(raw<0)|(raw>1)
    return np.rint(np.clip(raw,0,1)*255).astype(np.uint8),dict(clipped_channel_samples=int(clips.sum()),clipped_pixels=int(clips.any(axis=2).sum()))

def features281(rgb,measurement,mapping,names):
    if len(names)!=281 or names[16:22]!=list(GAP_NAMES) or names[22:]!=list(JOINT_NAMES):raise ValueError('Frozen281schema required')
    if rgb.dtype!=np.uint8 or rgb.shape!=(256,256,3):raise ValueError('NormalizedRGB8 required')
    if measurement.dtype!=np.uint8 or measurement.shape!=(256,256) or not set(np.unique(measurement))<={0,255}:raise ValueError('Binarymeasurement required')
    bgr=rgb[:,:,::-1].copy();stats=compute_masked_lab_statistics(bgr,measurement,1000)
    if not stats['valid']:raise ValueError('Inputmeasurement unavailable: '+stats['reason'])
    old={'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
    green=green_distribution_features(bgr,measurement)
    if not green['valid']:raise ValueError('Green features unavailable')
    old.update(green['features']);old.update(scene_features(rgb))
    mst=predict_score(mapping,stats['ita_degrees'],measurement_core_sha256=mapping['measurement_core_sha256'],feature_control_contract_sha256=mapping['feature_control_contract_sha256'])
    old['input_mst_score']=mst['score']
    gap=histogram_gap_features(rgb);joint=extract(rgb)
    if not gap['valid']:raise ValueError('Gap features unavailable')
    vector=[f32(old[n]) for n in names[:16]]+[f32(gap['features'][n]) for n in names[16:22]]+[f32(joint['features'][n]) for n in names[22:]]
    return vector,dict(statistics=stats,mst_prediction=mst,joint_available=joint['available'])

def existing_rows(root,plan):
    root=Path(root);base={r['case_id']:r for r in read(root/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(root/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    joint={r['case_id']:r for r in read(root/'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json')}
    result={}
    for item in plan['cases']:
        if item['kind']!='EXACT_OLD_RECORD_REUSE':continue
        c=item['case_id'];r=base[c];g=gaps[c];j=joint[c]
        if r['generated_fixture'] is not False or j['generated_fixture'] is not False or g['generated_fixture'] is not False:raise ValueError('Generated fixture cannot join scientific preparation')
        if r['status']!='available' or r['publisher_group']!=item['source'] or r['experimental_role']!=item['role']:raise ValueError('Existingcase provenance mismatch')
        x=r['input_vector_float32']+[f32(g['features'][n]) for n in plan['feature_names'][16:22]]+[f32(v) for v in j['features']]
        if len(x)!=281 or r['nominal_controls']!=item['nominal_controls']:raise ValueError('Exactold schema/target required')
        result[c]=dict(case_id=c,source=item['source'],role=item['role'],x=x,y=list(r['nominal_controls']),
            status='available',generated_fixture=False,synthetic_controlled_derivative=item['role']!='identity',
            old_record_reused=True,pixels_file=r['pixels_file'],pixels_sha256=r['pixels_sha256'])
    if len(result)!=plan['original_records_reused']:raise ValueError('Exactexisting44records required')
    return result

def prepare_once(root,out,plan,receipt):
    root=Path(root);out=Path(out);out.mkdir()
    write(out/'execution_plan_PRIVATE.json',receipt)
    try:
        old=existing_rows(root,plan);mapping=read(root/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')
        selected={s['source']:s for s in plan['support_sources']};identities={};masks={};parity=[]
        prep=root/'outputs/reviewed_ffhq_restoration_preparation_v1'
        # ALL11identityparities before creating any new scientific condition.
        for source in plan['source_references']:
            path=Path(source['identity_container'])
            if path.resolve()!=(prep/source['identity_case']/'paired_pixels.npz').resolve() or sha(path)!=source['identity_sha256']:raise ValueError('Bound identitycontainer required')
            with np.load(path,allow_pickle=False) as pack:rgb=pack['input_rgb8']
            s=selected[source['source']]['selected'];folder=root/s['directory']
            if sha(folder/s['receipt'])!=s['receipt_sha256']:raise ValueError('Selectedsupport receipt changed')
            if sha(folder/'measurement_mask.png')!=s['files']['measurement_mask.png']:raise ValueError('Measurement changed')
            mask=cv2.imread(str(folder/'measurement_mask.png'),0)
            values,_=features281(rgb,mask,mapping,plan['feature_names'])
            if values!=old[source['identity_case']]['x']:raise ValueError('Full281identityparity failed; no featurecontract rescue')
            identities[source['source']]=rgb;masks[source['source']]=mask
            parity.append(dict(source=source['source'],full281_exact=True))
        write(out/'all_identity_feature_parity_PRIVATE.json',dict(passed=True,identities=parity))
        rows=[]
        for item in plan['cases']:
            c=item['case_id']
            if item['kind']=='EXACT_OLD_RECORD_REUSE':row=old[c]
            else:
                clean=identities[item['source']];operation=plan['operations'][item['role']]
                rgb,forward=blue_transform(clean,operation)
                vector,details=features281(rgb,masks[item['source']],mapping,plan['feature_names'])
                folder=out/c;folder.mkdir();path=folder/'paired_pixels.npz'
                np.savez_compressed(path,input_rgb8=rgb,reference_rgb8=clean)
                row=dict(case_id=c,source=item['source'],role=item['role'],x=vector,y=list(item['nominal_controls']),
                    status='available',generated_fixture=False,synthetic_controlled_derivative=True,old_record_reused=False,
                    pixels_file=str(path),pixels_sha256=sha(path),forward_report=forward,feature_details=details)
            rows.append(row);write(out/'rows_PRIVATE.json',rows)
        if len(rows)!=66 or sum(not r['old_record_reused'] for r in rows)!=22:raise ValueError('Complete66rows required')
        write(out/'role_ledger_PRIVATE.json',[dict(case_id=r['case_id'],status=r['status']) for r in rows]+[dict(case_id=c,status='excluded_user_underexposed_reference') for c in plan['excluded_cases']])
        write(out/'status_PRIVATE.json',dict(status='PREPARED_PENDING_INDEPENDENT_VERIFICATION',old44_reused=44,new22_generated=22,rows=66,fits=0,predictions=0))
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
