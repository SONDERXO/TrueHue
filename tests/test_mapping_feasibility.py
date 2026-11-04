import numpy as np
import pytest
from src.ita_estimation.mapping_feasibility import fit_predict,leave_subject_out,paired_cohorts


def test_monotone_lookup_direction_and_bounds():
    result,continuous=fit_predict([-60,-30,0,30,60],[10,8,5,3,1],list('abcde'),[-100,-50,0,50,100])
    assert np.all(np.diff(continuous)<=0)
    assert np.all((result['monotone_ita_lookup']>=1)&(result['monotone_ita_lookup']<=10))


def test_heldout_subject_never_enters_mapping_fit():
    rows=[dict(image_id=f'{s}{i}',subject_id=s,ita_degrees=x,source_mst_label=y)
          for s,x,y in [('a',50,1),('b',-50,10)] for i in range(2)]
    results=leave_subject_out(rows)
    assert len(results)==12
    assert all(r['predicted_mst']==(10 if r['subject_id']=='a' else 1) for r in results)
    assert all(not r['true_label_present_in_training'] for r in results)


def test_isotonic_fit_weights_subjects_not_number_of_photos():
    _,continuous=fit_predict([0]*101,[1]*100+[10],['a']*100+['b'],[0])
    np.testing.assert_allclose(continuous,[5.5])


def test_inconsistent_subject_labels_and_single_subject_fail():
    with pytest.raises(ValueError,match='inconsistent'):
        fit_predict([1,2],[1,2],['a','a'],[0])
    with pytest.raises(ValueError,match='two distinct'):
        leave_subject_out([dict(subject_id='a',ita_degrees=0,source_mst_label=1)])


def comparison(image_id, current_status='success'):
    return dict(image_id=image_id,subject_id='subject_0',source_mst_label='3',source_lighting='well_lit',
        historical_status='success',historical_ita=10,regenerated_v2_status='success',regenerated_v2_ita=11,
        complete_mouth_status=current_status,complete_mouth_ita=12)


def test_paired_cohorts_use_identical_ids_and_version_specific_measurements():
    cohorts=paired_cohorts([comparison('kept'),comparison('failed','insufficient_skin_pixels')])
    assert all([r['image_id'] for r in rows]==['kept'] for rows in cohorts.values())
    assert [cohorts[v][0]['ita_degrees'] for v in ('historical','regenerated_v2','complete_mouth')]==[10,11,12]


def test_paired_cohorts_do_not_impute_measurements_for_failures():
    assert all(not rows for rows in paired_cohorts([comparison('failed','failed')]).values())


def test_successful_nonfinite_comparison_rejected():
    row=comparison('invalid');row['complete_mouth_ita']=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):
        paired_cohorts([row])
