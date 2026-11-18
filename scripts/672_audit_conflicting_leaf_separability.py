"""Descriptive fitting-only ranges/collisions; no threshold search or model change."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_tree import float32, PortableTree

OUT = ROOT / 'outputs/conflicting_leaf_separability_v1'
OLD = ROOT / 'outputs/facial_veto_exception_models_v1/models_PRIVATE.json'
NEW = ROOT / 'outputs/fixed_structure_nonharm_models_v1/models_PRIVATE.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():
        raise FileExistsError('Preserve audit artifacts')
    paths = [OLD, NEW, NEW.parent/'verification_PRIVATE.json', Path(__file__),
             ROOT/'docs/conflicting-leaf-separability-protocol-2026-11-09.md']
    bound = {str(p):sha(p) for p in paths}
    old, new = [json.loads(p.read_text()) for p in (OLD, NEW)]
    assert json.loads(paths[2].read_text())['passed']
    assert sha(NEW) == json.loads(paths[2].read_text())['model_sha256']
    records = []
    for f, g in zip(old['folds']+[old['full']], new['folds']+[new['full']], strict=True):
        assert f['held_key'] == g['held_key']
        assert f['training_features'] == g['training_features'] and f['training_cases'] == g['training_cases']
        a, b = f['pre_veto_model'], g['pre_veto_model']
        assert a['costs'] == b['costs'] and a['actions'] == b['actions']
        vectors = [[float32(v) for v in x] for x in f['training_features']]
        tree = PortableTree(a['tree'])
        for n, (p, q) in enumerate(zip(a['tree']['nodes'], b['tree']['nodes'], strict=True)):
            if p['kind'] != 'leaf' or p['values'] == q['values']:
                continue
            ix = a['trace'][n]['rows']
            assert ix == b['trace'][n]['rows']
            assert set(ix) == {i for i,x in enumerate(vectors) if tree.leaf_id(x)==n}
            action = a['actions'].index(p['values'])
            cost = a['costs']
            blockers = [i for i in ix if b['nonharm'][i] and cost[i][action] > cost[i][0]]
            clean_blockers = [i for i in ix if a['clean'][i] and cost[i][action] > 0]
            exposure = [i for i in ix if f['training_cases'][i].split('__',1)[1].endswith(('_under','_over')) and cost[i][action] < cost[i][0]]
            assert blockers and exposure
            ranges = []
            for k, name in enumerate(new['feature_names']):
                br = [min(vectors[i][k] for i in blockers), max(vectors[i][k] for i in blockers)]
                er = [min(vectors[i][k] for i in exposure), max(vectors[i][k] for i in exposure)]
                ranges.append(dict(feature=name, colour_blocker_range=br, exposure_beneficiary_range=er,
                    strictly_disjoint=br[1]<er[0] or er[1]<br[0]))
            collisions = [[i,j] for i in blockers for j in exposure if vectors[i]==vectors[j]]
            outside = [i for i in blockers if any(vectors[i][k]<r['exposure_beneficiary_range'][0] or vectors[i][k]>r['exposure_beneficiary_range'][1] for k,r in enumerate(ranges))]
            records.append(dict(configuration=f['held_key'], leaf=n, old_action=action,
                reassigned_action=b['actions'].index(q['values']), leaf_rows=ix,
                colour_blockers=blockers, clean_blockers=clean_blockers,
                exposure_beneficiaries=exposure, ranges=ranges,
                identical_float32_vector_conflicts=collisions,
                blockers_outside_exposure_bounding_box=outside,
                rows=[dict(index=i,case_id=f['training_cases'][i],features=vectors[i],
                    old_action_cost=cost[i][action],identity_cost=cost[i][0],
                    new_action_cost=cost[i][b['actions'].index(q['values'])]) for i in ix]))
    assert len(records)==11
    summary=dict(changed_leaves=len(records), configurations=len({r['configuration'] for r in records}),
        repeated_colour_blockers=sum(len(r['colour_blockers']) for r in records),
        repeated_exposure_beneficiaries=sum(len(r['exposure_beneficiaries']) for r in records),
        clean_blockers=sum(len(r['clean_blockers']) for r in records),
        leaves_with_disjoint_axis=sum(any(x['strictly_disjoint'] for x in r['ranges']) for r in records),
        exact_vector_conflicts=sum(len(r['identical_float32_vector_conflicts']) for r in records))
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir()
    result=dict(summary=summary,records=records,input_sha256=bound,
        scope='All changed pre-veto leaves; saved fitting rows only. Float32 ranges, strict disjointness and exact-vector collisions. No threshold enumeration or selection.',
        new_fits=0,new_evaluation_predictions=0,image_reads=0,holdout_image_reads=0)
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
