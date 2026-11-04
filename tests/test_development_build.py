import copy
import pytest
from src.model_training.development_build import activation_gate, validate_build_rows
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.distortion_generation.generate_distortions import inverse_parameters


def rows():
    result = []
    for source in ['a', 'b', 'c']:
        for variant, gamma in [('dark', .7), ('identity_control', 1)]:
            row = dict(pair_id=source+'_'+variant, source_image_id=source,
                       duplicate_group_id=source, variant=variant, partition='train',
                       table_use='train', input_processing_status='success', clipped_pixel_count=0,
                       distortion_gamma=gamma, distortion_red_gain=.85, distortion_blue_gain=.95)
            row.update(zip(FEATURES, [50, 10, 20, 0]))
            row.update(zip(TARGETS, inverse_parameters(gamma, .85, .95).values()))
            result.append(row)
    return result


def test_fit_order_is_stable_holds_excluded_and_input_unmodified():
    data = list(reversed(rows())); before=copy.deepcopy(data)
    held=['a_dark']; eligible=[r['pair_id'] for r in data if r['pair_id'] not in held]
    result=validate_build_rows(data,eligible,held)
    assert [r['pair_id'] for r in result]==sorted(eligible) and data==before
    result[0]['pair_id']='changed'; assert data==before


@pytest.mark.parametrize('change', [
    lambda r:r.update(input_mean_l_star=float('nan')),
    lambda r:r.update(target_gamma=-1),
    lambda r:r.update(target_red_gain=1.7),
    lambda r:r.update(distortion_gamma=0),
    lambda r:r.update(clipped_pixel_count=1),
    lambda r:r.update(partition='development_validation'),
    lambda r:r.update(input_processing_status='excluded'),
])
def test_invalid_input_routing_or_targets_rejected(change):
    data=rows(); ids=[r['pair_id'] for r in data]; change(data[0])
    with pytest.raises(ValueError): validate_build_rows(data,ids,[])


def evidence():
    return [dict(scope='primary',variant=variant,method=method,evaluation_kind='source_held_out',
                 pairs=6,sources=3,mean_ciede2000=error,equal_source_mean_ciede2000=error,worsened_pairs=harm)
            for method,variant,error,harm in [('no_correction','all',5,0),
                ('with_controls','all',4,0),('with_controls','identity_control',0,0),
                ('with_controls','mild_bright_exposure',1,0)]]


def test_numerical_gate_does_not_claim_production_readiness():
    result=activation_gate(evidence())
    assert result['status']=='passes_development_quality_gate' and result['production_ready'] is False


@pytest.mark.parametrize('index,key,value',[(1,'mean_ciede2000',5),(1,'equal_source_mean_ciede2000',6),
                                         (2,'worsened_pairs',1),(3,'worsened_pairs',1)])
def test_each_failed_quality_condition_blocks_activation(index,key,value):
    data=evidence();data[index][key]=value
    assert activation_gate(data)['status']=='held_quality_failure'


@pytest.mark.parametrize('change',[
    lambda r:r.pop(),lambda r:r.append(copy.deepcopy(r[0])),
    lambda r:r[1].update(evaluation_kind='seen_source_diagnostic'),
    lambda r:r[1].update(mean_ciede2000=float('nan')),
    lambda r:r[1].update(pairs=5),lambda r:r[2].update(worsened_pairs=7)])
def test_invalid_or_incomparable_evaluation_evidence_fails(change):
    data=evidence();change(data)
    with pytest.raises(ValueError):activation_gate(data)
