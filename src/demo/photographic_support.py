"""Save explicit research support reviews; no calibration or learned rendering."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid
import cv2
import numpy as np
from src.demo.manual_refinement import verify_export, digest
from src.demo.manual_brush import refine_masks
from src.demo.labelled_measurement import write, seal
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.seamless_blend import apply_blended


def save_support(folder,payload,output_parent):
    folder=Path(folder);verify_export(folder)
    identity=digest(folder/'manifest.json')
    report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
    if report.get('schema_version') not in ('truehue_photographic_support_task_v1','truehue_photographic_support_annotation_v1'):
        raise ValueError('Explicit photographic research task required')
    if payload.get('schema_version')!='truehue_photographic_support_edits_v1' or payload.get('base_manifest_sha256')!=identity:
        raise ValueError('Support edits must bind this exact task or preceding revision')
    review=payload.get('review')
    if review not in ('reviewed_selection','unjudgeable'):
        raise ValueError('Explicit support review required')
    if review=='reviewed_selection' and (payload.get('measurement_reviewed') is not True or payload.get('correction_reviewed') is not True):
        raise ValueError('Review measurement and correction separately before saving both')
    if not isinstance(payload.get('note',''),str):raise ValueError('Text note required')
    load=lambda name:cv2.imread(str(folder/name),0)
    image=cv2.imread(str(folder/'photo_used.png'))
    base=[load(n) for n in ['correction_mask.png','measurement_mask.png','protected_mask.png']]
    if image is None or image.shape!=(256,256,3) or any(a is None or a.shape!=(256,256) for a in base):
        raise ValueError('Matching normalized256 research inputs required')
    edited=refine_masks(*(a.tobytes() for a in base),256,256,payload.get('strokes'))
    c,m,p=[np.frombuffer(a,np.uint8).reshape(256,256) for a in edited]
    if np.any((c>0)&(p>0)):raise ValueError('Correction overlaps retained protection')
    stats=compute_masked_lab_statistics(image,m,1000)
    output,alpha,_=apply_blended(image,c,(1.,1.,1.),face_width=report['face_width'],protected=p>0)
    assert np.array_equal(output,image)
    valid=stats['valid'] and bool(c.any())
    status='reviewed_support_pending_admission' if review=='reviewed_selection' and valid else 'unavailable'
    current=deepcopy(report)
    current.update(schema_version='truehue_photographic_support_annotation_v1',
        task_manifest_sha256=report.get('task_manifest_sha256',identity),base_manifest_sha256=identity,
        saved_utc=datetime.now(timezone.utc).isoformat(),review=review,
        measurement_review='user_reviewed' if payload.get('measurement_reviewed') is True else 'not_approved',
        correction_review='user_reviewed' if payload.get('correction_reviewed') is True else 'not_approved',
        note=payload.get('note',''),status=status,measurement_statistics=stats,
        reason='user_unjudgeable' if review=='unjudgeable' else (stats['reason'] if not stats['valid'] else ('reviewed_pending_admission' if c.any() else 'empty_correction_support')),
        strokes=payload['strokes'],changed_pixels={k:int(np.count_nonzero(a!=b)) for k,a,b in zip(['correction','measurement','protection'],[c,m,p],base)},
        calibration_admitted=False,training_admitted=False,model_calls=0,mst_recomputed=False,
        identity_render_only=True,registration_verified=False)
    verify_export(folder)
    if digest(folder/'manifest.json')!=identity:raise ValueError('Base support changed during saving')
    dest=Path(output_parent)/('support_'+uuid.uuid4().hex);dest.mkdir(parents=True,exist_ok=False)
    for name in ['photo_used.png','measurement_mask.png','correction_mask.png','protected_mask.png','correction_alpha.npy','report.json']:
        original=folder/('automatic_'+name)
        if not original.exists():original=folder/name
        (dest/('automatic_'+name)).write_bytes(original.read_bytes())
    (dest/'before_support_report.json').write_bytes((folder/'report.json').read_bytes())
    for name,a in [('photo_used.png',image),('measurement_mask.png',m),('correction_mask.png',c),('protected_mask.png',p)]:
        if not cv2.imwrite(str(dest/name),a):raise OSError('Cannot save support mask')
    np.save(dest/'correction_alpha.npy',alpha,allow_pickle=False)
    write(dest/'report.json',current);write(dest/'edits.json',payload);seal(dest);verify_export(dest)
    return dest
