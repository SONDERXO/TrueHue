"""Narrow v2 guard: exact mapping-equivalent ties only. Original adapter preserved."""
import itertools
import numpy as np
import numpy.matlib
from wb_cue_adapter import ROOT, ASSETS, SOURCE, sha, load_model


def check_boundary(distance, mappings, k):
    values=np.sort(distance.reshape(-1))
    if values[k-1]==values[k]:
        tied=np.flatnonzero(distance.reshape(-1)==values[k-1])
        if not np.all(mappings[tied]==mappings[tied[0]]):
            raise ValueError('UNAVAILABLE_NONIDENTICAL_BOUNDARY_MAPPINGS')


def generated_guard_tests():
    d=np.array([0.,1.,1.,1.,2.])
    maps=np.zeros((5,33));maps[1:4]=.75;maps[0]=.2
    check_boundary(d,maps,3)
    answers=[]
    for pair in itertools.combinations([1,2,3],2):
        ids=[0,*pair];w=np.exp(-d[ids]/(2*.25**2))
        answers.append(sum(maps[ids]*w[:,None],0)/sum(w))
    assert all(np.array_equal(answers[0],a) for a in answers)
    maps[3,0]=.8
    try:check_boundary(d,maps,3)
    except ValueError:pass
    else:raise AssertionError('Nonidentical boundary accepted')
    check_boundary(np.array([0.,.5,1.,2.,3.]),maps,3)


def extract(model, normalize, rgb):
    if rgb.dtype!=np.uint8 or rgb.ndim!=3 or rgb.shape[2]!=3:raise ValueError('INVALID_RGB8')
    with np.errstate(divide='ignore',invalid='ignore'):
        hist=model.rgb_uv_hist(normalize(rgb))
    if not np.isfinite(hist).all():raise ValueError('UNAVAILABLE_NONFINITE_HISTOGRAM')
    query=model.encode(hist)
    if not np.isfinite(query).all():raise ValueError('UNAVAILABLE_QUERY')
    d=np.einsum('ij,ij->i',model.features,model.features)[:,None]+np.einsum('ij,ij->i',query,query)-2*model.features.dot(query.T)
    if not np.isfinite(d).all() or (d<0).any():raise ValueError('UNAVAILABLE_DISTANCE')
    check_boundary(d,model.mappingFuncs,model.K)
    indices=d.argpartition(model.K,axis=0)[:model.K]
    selected=np.sqrt(np.take_along_axis(d,indices,axis=0))
    weights=np.exp(-np.power(selected,2)/(2*model.sigma**2))
    if not np.isfinite(weights).all() or float(sum(weights)[0])<=0:raise ValueError('UNAVAILABLE_WEIGHTS')
    weights=weights/sum(weights)
    coefficients=sum(np.matlib.repmat(weights,1,33)*np.squeeze(model.mappingFuncs[indices,:]),0)
    if not np.isfinite(coefficients).all():raise ValueError('UNAVAILABLE_COEFFICIENTS')
    official=model.correctImage(rgb[...,::-1]).reshape(-1,order='F')
    assert np.array_equal(coefficients,official),'source prefix parity'
    return coefficients,query,d,indices
