"""Persist generated-only engineering evidence; no datasets or model files read."""
from pathlib import Path
import sys
import json
import math
import hashlib
import struct

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_oblique_tree import payload, PortableObliqueTree  # noqa: E402
from src.model_training.oblique_regression_tao import train_oblique, refresh_leaves  # noqa: E402

OUT = ROOT/'outputs/oblique_tree_engineering_v1'


def main():
    dest = OUT/'generated_verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve engineering verification')
    preserved = json.loads((OUT/'preserved_inputs_PRIVATE.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in preserved.items())
    axes = [-3., -2., -1., 1., 2., 3.]
    x2 = np.array([(a,b) for a in axes for b in axes])
    y = np.array([[1.4,1.02,1.03] if a+b > .25 else [1.,1.,1.] for a,b in x2])
    results = [];models = []
    for width in [2,16]:
        x = x2 if width == 2 else np.column_stack([x2,np.full((36,14),7.)])
        initial = payload([f'generated_f{i}' for i in range(width)],[
            dict(kind='split',weights=[1.]+[0.]*(width-1),intercept=0.,left=1,right=2),
            dict(kind='leaf',values=[1.,1.,1.]),dict(kind='leaf',values=[1.4,1.02,1.03])],
            dict(generated_fixture=True, scientific_data=False))
        initial = refresh_leaves(initial,x,y)
        fitted, report = train_oblique(initial,x,y)
        serialized = json.loads(json.dumps(fitted,allow_nan=False))
        tree = PortableObliqueTree(serialized)
        independent_sse = 0.;routes = []
        for row,target in zip(x,y):
            values = [struct.unpack('!f',struct.pack('!f',float(v)))[0] for v in row]
            i = 0;nodes = serialized['nodes']
            while nodes[i]['kind'] == 'split':
                node = nodes[i]
                total = math.fsum([float(node['intercept'])]+[
                    float(w)*v for w,v in zip(node['weights'],values)])
                i = node['right'] if total > 0 else node['left']
            assert i == tree.leaf_id(row) and nodes[i]['values'] == tree.predict_one(row)
            assert np.allclose(nodes[i]['values'],target,rtol=0,atol=1e-12)
            independent_sse += sum((a-b)**2 for a,b in zip(nodes[i]['values'],target))
            routes.append(i)
        assert math.isclose(independent_sse,report['final_SSE'],rel_tol=1e-12,abs_tol=1e-20)
        assert report['final_SSE'] < report['initial_SSE'] and report['final_SSE'] < 1e-20
        assert all(b['SSE'] <= a['SSE'] for a,b in zip(report['SSE_history'],report['SSE_history'][1:]))
        for leaf in set(routes):
            members = [j for j,r in enumerate(routes) if r == leaf]
            expected = [math.fsum(float(y[j,k]) for j in members)/len(members) for k in range(3)]
            assert expected == nodes[leaf]['values']
        assert sum(abs(w) > 1e-9 for w in fitted['nodes'][0]['weights']) == 2
        results.append(dict(generated_fixture=True,scientific_rows=0,width=width,
            fitting_numeric_rows=36,independent_routes=36,independent_SSE=independent_sse,
            report=report))
        models.append(serialized)
    # A symmetric generated plateau explicitly records a failure to improve.
    xor_x = np.array([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
    xor_y = np.array([[1.,1.,1.],[1.4,1.02,1.03],[1.4,1.02,1.03],[1.,1.,1.]])
    initial = payload(['generated_f0','generated_f1'],[
        dict(kind='split',weights=[1.,0.],intercept=0.,left=1,right=2),
        dict(kind='leaf',values=[1.,1.,1.]),dict(kind='leaf',values=[1.4,1.02,1.03])])
    initial = refresh_leaves(initial,xor_x,xor_y)
    _, plateau = train_oblique(initial,xor_x,xor_y)
    assert plateau['final_SSE'] == plateau['initial_SSE'] > 0 and not plateau['global_optimality_claim']
    (OUT/'generated_models_ONLY_PRIVATE.json').write_text(json.dumps(models,indent=2,allow_nan=False),encoding='utf-8')
    result = dict(passed=True,generated_only=True,scientific_rows=0,
        generated_diagonal_checks=results,plateau=plateau,
        independent_routes=72,independent_three_output_leaf_mean_checks=4,
        global_optimality_claim=False, correction_improvement_claim=False,
        dataset_fits=0,dataset_predictions=0,photo_reads=0,holdout_reads=0,
        preserved_input_hashes_unchanged=True,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            Path(__file__), ROOT/'src/model_training/portable_oblique_tree.py',
            ROOT/'src/model_training/oblique_regression_tao.py',
            ROOT/'tests/test_oblique_regression_engineering.py',
            ROOT/'docs/oblique-tree-engineering-protocol-2026-11-12.md']})
    dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(dict(passed=True,independent_routes=72,
        diagonals=[dict(width=r['width'],initial_SSE=r['report']['initial_SSE'],
                       final_SSE=r['report']['final_SSE'],status=r['report']['status'],
                       solver_attempts=r['report']['solver_attempts']) for r in results],
        plateau_status=plateau['status'],plateau_SSE=plateau['final_SSE'],
        dataset_fits=0,photo_reads=0,holdout_reads=0),indent=2))


if __name__ == '__main__':
    main()
