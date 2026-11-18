"""Independent block-moment and neighbour replay; stdlib only."""
import math

def moments(rows):
    n=len(rows)
    means=[math.fsum(r['x'][j] for r in rows)/n for j in range(4377)]
    return [math.fsum((r['x'][j]-means[j])**2 for r in rows for j in range(lo,hi))/n for lo,hi in [(0,281),(281,4377)]]

def search(index,x):
    choices=[]
    for r in index['rows']:
        distance=math.fsum((math.fsum((a-b)**2 for a,b in zip(x[lo:hi],r['x'][lo:hi]))/scale)
                           for (lo,hi),scale in zip([(0,281),(281,4377)],index['block_energy']))
        choices.append((distance,r['case_id'],r))
    distance,_,chosen=min(choices,key=lambda value:(value[0],value[1]))
    return dict(neighbour_case_id=chosen['case_id'],neighbour_source_id=chosen['source_id'],
                squared_distance=distance,controls=chosen['y'])

def verify_index(index,rows,replay,fold):
    assert index['schema']=='truehue_two_block_1nn_research_v1'
    assert len(rows)==60 and [r['case_id'] for r in rows]==fold['fitting_cases']
    assert fold['held_source_id'] not in {r['source_id'] for r in rows}
    assert index['rows']==sorted(rows,key=lambda r:r['case_id'])
    expected=moments(rows)
    assert all(math.isfinite(e) and e>0 for e in expected)
    assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(expected,index['block_energy']))
    assert len(replay)==60
    for r,saved in zip(rows,replay):
        answer=search(index,r['x'])
        assert saved['case_id']==r['case_id']
        assert answer['neighbour_case_id']==saved['neighbour_case_id'] and answer['controls']==saved['controls']
        assert math.isclose(answer['squared_distance'],saved['squared_distance'],rel_tol=1e-12,abs_tol=1e-12)
    return dict(passed=True,fit_routes=60,block_moments=2,held_predictions=0,held_source_excluded=fold['held_source_id'])
