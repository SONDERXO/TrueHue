"""Explicit provenance contract for future square256 MST-aware training rows."""
import math
import re
from src.ita_estimation.square_measurement import MASK_VERSION
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.distortion_generation.generate_distortions import TRANSFORM_VERSION,inverse_parameters


def _hash(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def validate_mst_training_rows(rows,*,measurement_contract_sha256,lookup_sha256,eligible_pair_ids):
    """Validate explicitly admitted rows; never promote existing candidates here.

    The current exact inverse target contract covers gamma-then-gain only.
    Composite/optimized targets require their own declared contract.
    """
    if not _hash(measurement_contract_sha256) or not _hash(lookup_sha256):raise ValueError('Measurement and lookup hashes required')
    eligible=set(eligible_pair_ids)
    if len(eligible)!=len(eligible_pair_ids) or not rows:raise ValueError('Unique eligibility IDs and nonempty rows required')
    seen=set();source_groups={};result=[]
    for row in rows:
        pair=row['pair_id'];source=row['source_image_id'];group=row['duplicate_group_id']
        if not pair or pair in seen or pair not in eligible:raise ValueError('Unique explicitly eligible pairs required')
        seen.add(pair)
        if row['dataset_name'] not in ('FairFace','SCIN'):raise ValueError('MST-E is mapping/evaluation only, not correction training')
        if row['partition']!='train' or row['training_eligible'] is not True:raise ValueError('Explicit TRAIN admission required')
        if row['input_processing_status']!='success' or row['clipped_pixel_count']!=0:raise ValueError('Failed/clipped rows cannot fit')
        if row['measurement_shape']!=[256,256,3] or row['mask_version']!=MASK_VERSION:raise ValueError('Exact square256measurement policy required')
        if row['measurement_contract_sha256']!=measurement_contract_sha256 or row['lookup_sha256']!=lookup_sha256:raise ValueError('Mixed measurement/lookup contracts prohibited')
        if not source or not group or (source in source_groups and source_groups[source]!=group):raise ValueError('Consistent source/group identity required')
        source_groups[source]=group
        if row['mst_feature_source']!='distorted_input_ita_lookup':raise ValueError('Reference/official MST cannot substitute for input inference')
        for key in MST_FEATURES+TARGETS:
            v=row[key]
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('Finite numeric input features/targets required')
        mst=row['input_mst_index']
        if type(mst) is not int or not 0<=mst<=9:raise ValueError('Mapped MST config index0–9required')
        if row['target_method']=='exact_gamma_gain_inverse':
            if row['transform_version']!=TRANSFORM_VERSION:raise ValueError('Exact inverse requires gamma-gain transform')
            if row.get('brightness_offset',0)!=0 or row.get('contrast_multiplier',1)!=1:raise ValueError('Offsets/contrast invalidate exact gamma-gain inverse targets')
            inverse=inverse_parameters(row['distortion_gamma'],row['distortion_red_gain'],row['distortion_blue_gain'])
            if any(abs(float(row[k])-v)>1e-12 for k,v in zip(TARGETS,inverse.values())):raise ValueError('Inverse target mismatch')
        elif row['target_method']=='bounded_rgb_recovery_target_v1':
            if row['transform_version']!='table2_encoded_rgb_composite_v1':raise ValueError('Recovery target transform mismatch')
            fit=row.get('target_fit',{})
            if fit.get('status')!='available_approximate_target' or fit.get('target_method')!=row['target_method'] or fit.get('jacobian_rank')!=3 or fit.get('converged') is not True:
                raise ValueError('Converged identifiable recovery target report required')
            if not _hash(row.get('target_fit_report_sha256')):raise ValueError('Target report provenance required')
            if fit.get('parameters')!=[row[k] for k in TARGETS]:raise ValueError('Fitted target parameters differ from row')
            if not isinstance(fit.get('selected_pixels'),int) or fit['selected_pixels']<100:raise ValueError('Insufficient target fitting support')
            for name in ['float_rgb_rmse','identity_float_rgb_rmse','quantized_rgb_mae']:
                v=fit.get(name)
                if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError('Finite residual evidence required')
        else:raise ValueError('Unsupported transform/target contract')
        if any(row[k]<=0 for k in TARGETS):raise ValueError('Positive targets required')
        result.append(dict(row))
    if seen!=eligible:raise ValueError('Eligibility set must exactly match requested fitting rows')
    return sorted(result,key=lambda r:r['pair_id'])
