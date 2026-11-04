import pytest
from src.ita_estimation.threshold_calibration import fit_thresholds


def rows():
    return [dict(subject_id=f's{label}_{i}',source_mst_label=label,ita_degrees=80-label*12+i)
            for label in range(1,11) for i in range(2)]


def test_separated_centers_produce_nine_ordered_midpoints():
    result=fit_thresholds(rows())
    assert result['status']=='diagnostic_thresholds_fitted'
    assert len(result['thresholds'])==9 and result['thresholds']==sorted(result['thresholds'])
    assert all(v==2 for v in result['subject_support'].values())


def test_missing_category_blocks_instead_of_inventing_boundary():
    result=fit_thresholds([r for r in rows() if r['source_mst_label']!=10])
    assert result['status']=='blocked_missing_categories' and result['thresholds'] is None


def test_equal_or_reversed_centers_block_without_epsilon_gaps():
    data=rows()
    for r in data:r['ita_degrees']=10
    assert fit_thresholds(data)['status']=='blocked_pooled_category_centers'


def test_repeated_photos_do_not_count_as_independent_subjects():
    data=rows();data.extend([dict(data[0]) for _ in range(20)])
    assert fit_thresholds(data)['subject_support'][1]==2


def test_inconsistent_subject_labels_fail():
    data=rows();data[1]['subject_id']=data[0]['subject_id'];data[1]['source_mst_label']=2
    with pytest.raises(ValueError):fit_thresholds(data)
