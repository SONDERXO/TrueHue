"""Independent scalar projector-span/prototype proof, no trainer or SVD import."""
import math
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)
def scaled(index,x):
    return [v/math.sqrt(index['block_energy'][0 if j<281 else 1]) for j,v in enumerate(x)]
def project(index,x):
    a=[v-m for v,m in zip(scaled(index,x),index['clean_mean'])]
    dot=[math.fsum(v*b for v,b in zip(a,basis)) for basis in index['nuisance_basis']]
    return [v-math.fsum(d*b[j] for d,b in zip(dot,index['nuisance_basis'])) for j,v in enumerate(a)]
def search(index,x):
    z=project(index,x)
    choices=[(math.fsum((a-b)**2 for a,b in zip(z,c['projected_mean'])),c['role'],c['controls']) for c in index['centres']]
    distance,role,controls=min(choices,key=lambda c:(c[0],c[1]))
    return dict(prototype_role=role,squared_distance=distance,controls=controls)
def verify_index(index,rows,replay,fold):
    assert index['schema']=='truehue_paired_reference_prototype_research_v1'
    assert len(rows)==60 and [r['case_id'] for r in rows]==fold['fitting_cases']
    assert len({r['source_id'] for r in rows})==10 and fold['held_source_id'] not in {r['source_id'] for r in rows}
    assert index['rows']==sorted(rows,key=lambda r:r['case_id'])
    for b,(lo,hi) in enumerate([(0,281),(281,4377)]):
        means=[math.fsum(r['x'][j] for r in rows)/60 for j in range(lo,hi)]
        expected=math.fsum((r['x'][j]-means[j-lo])**2 for r in rows for j in range(lo,hi))/60
        close(expected,index['block_energy'][b]);assert expected>0
    clean=[r for r in index['rows'] if r['role']=='identity'];assert len(clean)==10
    assert index['clean_case_ids']==[r['case_id'] for r in clean]
    normal=[scaled(index,r['x']) for r in clean]
    for j in range(4377):close(index['clean_mean'][j],math.fsum(x[j] for x in normal)/10)
    centred=[[v-m for v,m in zip(x,index['clean_mean'])] for x in normal]
    basis=index['nuisance_basis'];assert len(basis)==index['nuisance_rank']<=9
    assert len(index['basis_combinations'])==len(basis)
    for vector,coefficient in zip(basis,index['basis_combinations']):
        assert len(vector)==4377 and len(coefficient)==10
        for j,value in enumerate(vector):close(value,math.fsum(c*x[j] for c,x in zip(coefficient,centred)))
    for i,a in enumerate(basis):
        for j,b in enumerate(basis):close(math.fsum(x*y for x,y in zip(a,b)),1. if i==j else 0.)
    for r in clean:assert max(abs(v) for v in project(index,r['x']))<1e-10
    projected={r['case_id']:project(index,r['x']) for r in rows}
    assert [c['role'] for c in index['centres']]==sorted({r['role'] for r in rows})
    for c in index['centres']:
        own=sorted([r for r in rows if r['role']==c['role']],key=lambda r:r['case_id']);assert len(own)==10
        assert c['fitting_cases']==[r['case_id'] for r in own]
        for j,value in enumerate(c['projected_mean']):close(value,math.fsum(projected[r['case_id']][j] for r in own)/10)
        for j,value in enumerate(c['controls']):close(value,math.fsum(r['y'][j] for r in own)/10)
    assert len(replay)==60
    for r,saved in zip(rows,replay):
        actual=search(index,r['x']);assert saved['case_id']==r['case_id']
        assert actual['prototype_role']==saved['prototype_role'] and actual['controls']==saved['controls']
        close(actual['squared_distance'],saved['squared_distance'])
    return dict(passed=True,fit_routes=60,block_moments=2,clean_references=10,nuisance_rank=index['nuisance_rank'],
        prototype_means=6,reference_span_verified=True,held_predictions=0,held_source_excluded=fold['held_source_id'])
