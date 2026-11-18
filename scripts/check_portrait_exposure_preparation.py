"""Generated arithmetic and public metadata only; no portrait or model reads."""
import csv
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from model_training.portrait_exposure_quality import exposure_probe, fit_scaler, rank_objective, ranking_pairs

OUT = ROOT / 'outputs/portrait_exposure_stage_preparation_v1'


def main():
    public = ROOT / 'outputs/portrait_exposure_prior_review_v1'
    tree = json.loads((public / 'tree.json').read_text())
    source_paths = {'Scene_Split.csv': 'Test split/Scene Split.csv',
                    'Image_Metadata.csv': 'Metadata/Image Metadata.csv'}
    receipts = []
    for local, remote in source_paths.items():
        path = OUT / local
        blob = next(t for t in tree['tree'] if t['path'] == remote)
        text = path.read_text(encoding='utf-8')
        variants = [text.encode(), text.replace('\n', '\r\n').encode()]
        matches = [b for b in variants if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == blob['sha']]
        assert len(matches) == 1
        path.write_bytes(matches[0])
        receipts.append({'file': local, 'bytes': len(matches[0]), 'git_blob_sha1': blob['sha'],
                         'sha256': hashlib.sha256(matches[0]).hexdigest()})
    def read(path):
        with path.open(encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    splits, metadata = read(OUT / 'Scene_Split.csv'), read(OUT / 'Image_Metadata.csv')
    scores = read(public / 'Scores_Exposure.csv')
    partition = {r['SCENE']: r['SPLIT'] for r in splits}
    devices = {r['Image']: r['Device'] for r in metadata}
    assert len(partition) == len(splits) == 50
    assert len(devices) == len(metadata)
    assert set(partition.values()) == {'Train', 'Test'}
    joined = []
    for r in scores:
        assert r['IMAGE'] in devices and r['SCENE'] in partition
        joined.append({'id': r['IMAGE'], 'scene': r['SCENE'], 'partition': partition[r['SCENE']],
                       'score': float(r['JOD']), 'low': float(r['CI LOW']), 'high': float(r['CI HIGH'])})
    pairs = ranking_pairs(joined)
    counts = Counter(joined[i]['partition'] for i, j in pairs)
    assert len(pairs) == 99159
    for scene in splits:
        assert sum(r['SCENE'] == scene['SCENE'] for r in scores) == int(scene['NB IMAGES'])
    # Generated guards: overlapping/touching CIs, another scene, another partition.
    rows = [{'id': str(i), 'scene': s, 'partition': p, 'low': lo, 'score': mid, 'high': hi}
            for i, (s,p,lo,mid,hi) in enumerate([
                ('a','Train',0,0.5,1), ('a','Train',2,2.5,3),
                ('a','Train',1,1.5,2), ('b','Train',5,6,7), ('a','Test',8,9,10)])]
    assert ranking_pairs(rows) == [(1,0)]
    x = np.array([[1.,2.,4.], [3.,2.,8.], [1e9,1e9,1e9]])
    original = x.copy()
    mean, scale = fit_scaler(x,[0,1])
    assert np.array_equal(mean,[2,2,6]) and np.array_equal(scale,[1,1,2])
    assert np.array_equal(x, original)
    d=np.array([[1.,-2.,3.],[-4.,2.,1.],[0.5,0.7,-0.9]])
    w=np.array([0.2,-0.3,0.4]); a=np.array([0.1,0.3,0.6])
    loss, grad = rank_objective(w,d,a)
    margins=[math.fsum(float(u)*float(v) for u,v in zip(row,w)) for row in d]
    scalar=math.fsum(float(ai)*(max(0,-m)+math.log1p(math.exp(-abs(m)))) for ai,m in zip(a,margins))+.0005*math.fsum(float(v)**2 for v in w)
    assert abs(loss-scalar)<1e-12
    finite=[]
    for k in range(len(w)):
        delta=np.zeros_like(w);delta[k]=1e-6
        finite.append((rank_objective(w+delta,d,a)[0]-rank_objective(w-delta,d,a)[0])/2e-6)
    assert np.max(np.abs(grad-finite))<1e-8
    extreme=rank_objective(np.array([1000.]),np.array([[1.],[-1.]]),[1,1])
    assert math.isfinite(extreme[0]) and np.isfinite(extreme[1]).all()
    for bad in [lambda: ranking_pairs(rows+[rows[0]]), lambda: fit_scaler(x,[]),
                lambda: rank_objective(w,np.empty((0,3)),[]),
                lambda: rank_objective([float('nan')],[[1]],[1])]:
        try: bad()
        except ValueError: pass
        else: raise AssertionError('Bad input was not rejected')
    rgb=np.arange(256,dtype=np.uint8).reshape(16,16,1).repeat(3,axis=2)
    before=rgb.copy()
    max_pixel_error=0
    for ev in [-.5,.5]:
        actual=exposure_probe(rgb,ev)
        expected=[]
        for value in range(256):
            c=value/255
            linear=c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
            v=min(1,max(0,linear*2**ev))
            encoded=12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
            expected.append(round(min(1,max(0,encoded))*255))
        error=int(np.abs(actual[:,:,0].astype(int).ravel()-expected).max())
        max_pixel_error=max(error,max_pixel_error)
        assert error == 0 and np.array_equal(actual,exposure_probe(rgb,ev))
    assert np.array_equal(rgb,before)
    report={'status':'GENERATED_MATH_AND_PUBLIC_METADATA_PASS', 'cache_sources':receipts,
            'joined_exposure_rows':len(joined),'scene_partitions':dict(Counter(partition.values())),
            'image_partitions':dict(Counter(r['partition'] for r in joined)),
            'derived_pair_partitions':dict(counts),'metadata_fields':list(metadata[0]),
            'person_disjointness':'NOT_ESTABLISHED_PUBLIC_METADATA_HAS_NO_PERSON_IDS',
            'loss_scalar_error':abs(loss-scalar),'gradient_finite_difference_max_error':float(np.max(np.abs(grad-finite))),
            'scalar_probe_rgb8_max_error':max_pixel_error,
            'portrait_pixels_read':0,'encoder_runs':0,'head_fits':0,'correction_fits':0,
            'limitations':'Not full encoder/optimizer/admission QA; access and permitted use unresolved; no real fit selected.'}
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
