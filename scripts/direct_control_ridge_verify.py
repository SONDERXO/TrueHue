"""Independent fitting-statistic/normal-equation proof; no solver or trainer import."""
import math


def close(a, b, tol=1e-9):
    assert math.isclose(a,b,rel_tol=tol,abs_tol=tol),(a,b)


def scalar_predict(model, x):
    return [model['intercept'][k] + math.fsum(
        ((float(x[j])-model['mean'][j])/model['scale'][j])*model['slopes'][j][k]
        for j in range(314)) for k in range(5)]


def verify_fit(model, rows, fold):
    assert len(rows)==60 and len({r['source_id'] for r in rows})==10
    assert all(r['source_id']!=fold['held_source_id'] for r in rows)
    assert [r['case_id'] for r in rows]==fold['fitting_cases']==model['fitting_cases']
    assert model['schema']=='truehue_camera_control_global_ridge_research_v1'
    assert model['width']==314 and model['alpha']==1.0
    for j in range(314):
        mean=math.fsum(r['x314'][j] for r in rows)/60
        variance=math.fsum((r['x314'][j]-mean)**2 for r in rows)/60
        scale=math.sqrt(variance) if variance else 1.0
        close(model['mean'][j],mean,1e-12);close(model['scale'][j],scale,1e-12)
        if variance==0:assert model['scale'][j]==1.0
    for k in range(5):close(model['intercept'][k],math.fsum(r['y'][k] for r in rows)/60,1e-12)
    residuals=[[p-y for p,y in zip(scalar_predict(model,r['x314']),r['y'])] for r in rows]
    max_residual=0.0
    for j in range(314):
        for k in range(5):
            terms=[((r['x314'][j]-model['mean'][j])/model['scale'][j])*e[k] for r,e in zip(rows,residuals)]
            normal=math.fsum(terms)+model['slopes'][j][k]
            bound=1e-8*max(1.0,math.fsum(abs(v) for v in terms),abs(model['slopes'][j][k]))
            assert abs(normal)<=bound,(j,k,normal,bound)
            max_residual=max(max_residual,abs(normal))
    for k in range(5):close(math.fsum(r[k] for r in residuals),0,1e-8)
    return dict(fitting_predictions=60, normal_equations=1570, max_normal_residual=max_residual)
