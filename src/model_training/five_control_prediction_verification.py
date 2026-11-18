"""Independent scalar routing/leaf means; stdlib only, no trainer/runtime imports."""
import math
import struct

TARGETS=['gamma','red_gain','blue_gain','input_scale','input_offset']


def route(tree,x):
    values=[struct.unpack('!f',struct.pack('!f',v))[0] for v in x]
    i=0;seen=set()
    while tree['nodes'][i]['kind']=='split':
        assert i not in seen;seen.add(i)
        n=tree['nodes'][i];i=n['left'] if values[n['feature']]<=n['threshold'] else n['right']
    return i,list(tree['nodes'][i]['values'])


def verify_fit(tree,rows,replay,fold,names,settings):
    assert tree['schema_version']=='truehue_five_control_tree_research_v1'
    assert tree['feature_names']==names and tree['target_names']==TARGETS
    assert tree['comparison']=='<=' and tree['input_dtype']=='float32' and tree['threshold_dtype']=='float64'
    assert len(rows)==60 and [r['case_id'] for r in rows]==fold['fitting_cases']
    assert len({r['source_id'] for r in rows})==10 and fold['held_source_id'] not in {r['source_id'] for r in rows}
    assert replay['settings']==settings and replay['fit_calls']==1 and replay['held_predictions']==0
    expected=[];leaves=[];members={}
    for r in rows:
        assert len(r['x'])==281 and len(r['y'])==5
        assert all(math.isfinite(v) and struct.unpack('!f',struct.pack('!f',v))[0]==v for v in r['x'])
        leaf,p=route(tree,r['x']);expected.append(p);leaves.append(leaf);members.setdefault(leaf,[]).append(r)
    assert expected==replay['predictions'] and leaves==replay['leaves']
    assert set(members)=={i for i,n in enumerate(tree['nodes']) if n['kind']=='leaf'}
    for i,own in members.items():
        for j in range(5):
            mean=math.fsum(r['y'][j] for r in own)/len(own)
            assert math.isclose(tree['nodes'][i]['values'][j],mean,abs_tol=1e-12,rel_tol=1e-12)
    mean=[math.fsum(r['y'][j] for r in rows)/60 for j in range(5)]
    for a,b in zip(mean,replay['constant_controls']):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
    return dict(passed=True,scalar_fitting_routes=60,leaf_means_checked=len(members),held_predictions=0,
        fitting_sources=10,held_source_excluded=fold['held_source_id'],fit_calls=1,constant_controls=mean)
