"""Explain held clean failures from saved fitting membership, without refitting."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_tree import PortableTree, float32


def main():
    folder = ROOT / 'outputs/clean_control_tree_depth_v1'
    def read(p): return json.loads(p.read_text(encoding='utf-8'))
    plan = read(folder / 'plan.json')
    rows = {r['pair_id']:r for r in plan['rows']}
    report = []
    for r in read(folder / 'predictions.json'):
        if r['variant'] != 'identity' or not r['changed_input_pixels']: continue
        payload = read(folder / f'fold_{r["fold_id"]}' / (r['method'] + '.json'))
        row = rows[r['pair_id']]
        values = [float32(row[k]) for k in plan['features']]
        index, path = 0, []
        while payload['nodes'][index]['kind'] == 'split':
            node = payload['nodes'][index]; feature = node['feature']
            left = values[feature] <= node['threshold']
            path.append(dict(node_id=index, feature=plan['features'][feature],
                input_value_float32=values[feature], threshold=node['threshold'], branch='left' if left else 'right'))
            index = node['left'] if left else node['right']
        assert index == r['leaf_id'] == PortableTree(payload).leaf_id(values)
        members = [rows[p] for p in r['fitting_leaf_pair_ids']]
        assert members and all(m['variant'] != 'identity' for m in members)
        assert row['source_image_id'] not in {m['source_image_id'] for m in members}
        report.append(dict(pair_id=r['pair_id'], method=r['method'], path=path,
            predicted_parameters=r['parameters'], ciede2000=r['metrics']['ciede2000_source_mask'],
            fitting_leaf_members=[dict(pair_id=m['pair_id'], variant=m['variant'],
                features={k:m[k] for k in plan['features']}, training_target=m['paper_target']) for m in members]))
    assert len(report) == 10
    (folder / 'clean_failure_routes.json').write_text(json.dumps(dict(
        status='diagnostic_only_no_model_change', clean_failures=report,
        conclusion='All changed held clean photos reached leaves containing distorted fitting examples only. Fitting-control protection cannot guarantee held-clean safety.'), indent=2), encoding='utf-8')
    print('Verified 10 held clean failure routes across both methods; no source-specific rule added.')


if __name__ == '__main__': main()
