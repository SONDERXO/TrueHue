"""Explicit input-only feature schema and controlled-pair routing."""
import math
from src.data_preparation.source_partition import classify_pair

FEATURES = ('input_mean_l_star', 'input_mean_a_star', 'input_mean_b_star', 'input_ita_degrees')
FEATURE_KEYS = ('mean_l_star', 'mean_a_star', 'mean_b_star', 'ita_degrees')
TARGETS = ('target_gamma', 'target_red_gain', 'target_blue_gain')


def pair_table_row(metadata, input_result, correction):
    """Never substitute reference measurements if input processing fails."""
    if metadata['partition'] not in ('train', 'development_validation'):
        raise ValueError('Controlled subset allows only train/development validation')
    if set(FEATURES) & set(metadata) or set(TARGETS) & set(metadata):
        raise ValueError('Metadata must not supply features or targets')
    row=dict(metadata)
    row.update(input_processing_status=input_result['processing_status'],
               input_exclusion_reason=input_result.get('exclusion_reason',''))
    row.update(dict.fromkeys(FEATURES,''))
    for key,name in zip(('gamma','red_gain','blue_gain'),TARGETS):
        value=float(correction[key])
        if not math.isfinite(value) or value<=0:
            raise ValueError('Invalid correction target')
        row[name]=value
    status=classify_pair(input_result['processing_status'],int(metadata['clipped_pixel_count']))
    if input_result['processing_status']=='success':
        try:
            values=[float(input_result[k]) for k in FEATURE_KEYS]
            if not all(math.isfinite(v) for v in values):
                raise ValueError('Nonfinite input statistics')
        except (KeyError,ValueError,TypeError):
            row.update(input_processing_status='excluded',input_exclusion_reason='invalid_input_feature_vector')
            status='excluded_input_pipeline_failure'
        else:
            row.update(zip(FEATURES,values))
    row['pair_status']=status
    row['table_use']=('stress_only' if status=='stress_only_clipped' else
                      'excluded' if status=='excluded_input_pipeline_failure' else metadata['partition'])
    return row
