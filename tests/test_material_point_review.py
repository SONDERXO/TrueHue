import pytest
from src.evaluation.material_point_review import validate_labels,score_points


def test_labels_require_manifest_identity_reviewer_and_complete_unique_points():
    manifest = {'points':[{'point_id':'P01'},{'point_id':'P02'}]}
    payload = dict(schema_version='material_point_labels_v1',manifest_sha256='abc',reviewer='AB',
                   labels=[dict(point_id='P01',label='skin'),dict(point_id='P02',label='unsure')])
    assert validate_labels(manifest,payload,'abc')=={'P01':'skin','P02':'unsure'}
    for changed in (dict(draft=True),dict(manifest_sha256='wrong'),dict(reviewer=''),dict(labels=[payload['labels'][0]]),
                    dict(labels=[payload['labels'][0]]*2),dict(labels=[dict(point_id='P01',label='yes'),payload['labels'][1]])):
        with pytest.raises(ValueError): validate_labels(manifest,{**payload,**changed},'abc')


def test_scoring_distinguishes_unavailable_and_unsure_from_rejected_skin():
    labels = dict(a='skin',b='skin',c='hair',d='paint',e='unsure',f='skin')
    rows = [dict(point_id=p,variant='clean',method='test',selected=value) for p,value in
            [('a',True),('b',False),('c',True),('d',False),('e',True),('f',None)]]
    result = score_points(rows,labels)[0]
    assert [result[k] for k in ('tp','fn','fp','tn')]==[1,1,1,1]
    assert result['skin_recall']==.5 and result['selected_point_precision']==.5
    assert result['unavailable_points']==1 and result['unsure_points']==1
    assert result['by_material']['hair']['selected']==1


def test_no_positive_or_available_labels_does_not_invent_scores():
    result = score_points([dict(point_id='x',variant='shift',method='test',selected=None)],dict(x='skin'))[0]
    assert result['skin_recall'] is None and result['selected_point_precision'] is None
    assert result['non_skin_selection_rate'] is None
