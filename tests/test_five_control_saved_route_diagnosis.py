import pytest
from src.evaluation.five_control_saved_route_diagnosis import trace,detailed_path,composition,summarize_errors,errors


def fixture():
    tree=dict(feature_names=['existing_brightness','existing_colour'],nodes=[
        dict(kind='split',feature=0,threshold=.5,left=1,right=2),
        dict(kind='leaf',values=[1.,1.,1.,1.,0.]),dict(kind='leaf',values=[.7,1.,1.,.9,.2])])
    rows=[dict(case_id='n',source_id='source_a',role='identity',x=[.2,.4],y=[1,1,1,1,0]),
          dict(case_id='c',source_id='source_b',role='colour_only',x=[.4,.5],y=[1,1,1,1,0]),
          dict(case_id='e',source_id='source_c',role='exposure_under',x=[.7,.1],y=[.7,1,1,.9,.2])]
    return tree,rows


def test_existing_split_exclusion_and_ranges():
    t,rows=fixture();routes=[trace(t,r['x']) for r in rows]
    result=detailed_path(t,[.6,.4],rows,routes)
    first=result['first_neutral_exclusion']
    assert first['feature_name']=='existing_brightness' and first['threshold']==.5
    assert first['parent']['neutral']==2 and first['chosen']['neutral']==0 and first['chosen']['exposure']==1
    assert first['node_feature_range']['held_inside'] and not first['node_neutral_feature_range']['held_inside']
    assert not first['node_family_feature_ranges_overlap']


def test_float32_tie_uses_saved_threshold():
    t,_=fixture()
    assert trace(t,[.5000000001,0])['leaf']==1
    assert trace(t,[.50001,0])['leaf']==2


def test_mixed_leaf_does_not_become_pure_exposure():
    t,rows=fixture();rows[0]['x']=[.6,.4]
    result=detailed_path(t,[.6,.4],rows,[trace(t,r['x']) for r in rows])
    assert result['reached_leaf']['neutral']==1 and result['first_neutral_exclusion'] is None


def test_sse_counts_repeated_occurrences_explicitly():
    e=errors([1,1,1,1,-.1],[1,1,1,1,.1]);s=summarize_errors([e,e])
    assert s['occurrences']==2 and s['mean_total_control_SSE']==pytest.approx(.04)


def test_cycle_rejected():
    t,_=fixture();t['nodes'][0]['left']=0
    with pytest.raises(ValueError):trace(t,[.1,0])
