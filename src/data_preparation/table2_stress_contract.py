"""Separate experimental admission policy; the default unclipped gate is intact."""
import math
from src.data_preparation.mst_training_contract import validate_mst_training_rows,_hash
from src.data_preparation.training_manifest import LABEL_TO_GROUP

POLICY='table2_clipping_stress_training_v1'


def validate_stress_rows(rows,*,measurement_contract_sha256,lookup_sha256,eligible_pair_ids):
    """Check declared approval/provenance; callers must verify actual evidence files.

    Reference MST selects distortion severity only. Distorted-input MST is the
    feature. Both remain experimental estimates, never official FairFace labels.
    """
    validated=[]
    for original in rows:
        row=dict(original)
        if row.get('admission_policy')!=POLICY:raise ValueError('Explicit stress policy required')
        count=row.get('clipped_pixel_count');channels=row.get('clipped_channel_samples');pixels=row.get('generation_skin_pixels')
        if any(type(v) is not int for v in (count,channels,pixels)) or pixels<100 or not 0<=count<=pixels or not count<=channels<=3*count:
            raise ValueError('Consistent generation-support clipping counts required')
        fraction=row.get('clipped_pixel_fraction')
        if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or abs(fraction-count/pixels)>1e-12:
            raise ValueError('Clipping fraction mismatch')
        if row.get('mask_review_status')!='approved' or not _hash(row.get('mask_review_report_sha256')):
            raise ValueError('Explicit same-contract mask review required')
        if row.get('scene_review_status')!='approved':raise ValueError('Explicit single-person scene review required')
        for key in ['input_sha256','input_mask_sha256','reference_mask_sha256']:
            if not _hash(row.get(key)):raise ValueError('Image/mask evidence hashes required')
        if row.get('variant')=='identity':
            if count or row.get('target_method')!='exact_gamma_gain_inverse' or any(row.get(k)!=1 for k in ['distortion_gamma','distortion_red_gain','distortion_blue_gain']):
                raise ValueError('Identity control must be unchanged with identity target')
        else:
            label=row.get('reference_mst_estimate')
            if type(label) is not int or label not in LABEL_TO_GROUP or row.get('severity_probe')!=LABEL_TO_GROUP[label]:
                raise ValueError('Severity must match declared reference MST estimate')
            if row.get('group_assignment_source')!='experimental_reference_ita_lookup' or row.get('reference_lookup_sha256')!=lookup_sha256:
                raise ValueError('Same-lookup estimated reference group required')
            if row.get('target_method')!='bounded_rgb_recovery_target_v1':raise ValueError('Approximate recovery targets required')
        # Delegate common invariants without changing the original record's counts.
        row['clipped_pixel_count']=0
        validated.append(row)
    validate_mst_training_rows(validated,measurement_contract_sha256=measurement_contract_sha256,
        lookup_sha256=lookup_sha256,eligible_pair_ids=eligible_pair_ids)
    return sorted((dict(r) for r in rows),key=lambda r:r['pair_id'])
