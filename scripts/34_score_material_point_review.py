"""Score a completed human point review without fitting/tuning any model."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
from src.evaluation.material_point_review import validate_labels,score_points


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--labels',type=Path,default=ROOT/'data/manifests/material_review_v1/material_review_labels.json')
    args=parser.parse_args();folder=ROOT/'data/manifests/material_review_v1'
    manifest_path=folder/'review_manifest.json'
    sha=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    payload=json.loads(args.labels.read_text(encoding='utf-8-sig'))
    labels=validate_labels(manifest,payload,sha)
    prediction_path=folder/'prediction_observations.json'
    predictions=json.loads(prediction_path.read_text(encoding='utf-8'))
    if predictions['manifest_sha256']!=sha: raise ValueError('Predictions belong to a different manifest')
    expected={(p['point_id'],variant,method) for p in manifest['points'] for variant in ('clean','color_shift') for method in ('original','guarded','material_checked')}
    observed=[(r['point_id'],r['variant'],r['method']) for r in predictions['observations']]
    if len(observed)!=len(expected) or set(observed)!=expected: raise ValueError('Incomplete/duplicated prediction observations')
    result=dict(manifest_sha256=sha,labels_sha256=hashlib.sha256(args.labels.read_bytes()).hexdigest(),
        predictions_sha256=hashlib.sha256(prediction_path.read_bytes()).hexdigest(),
        reviewer=payload['reviewer'],results=score_points(predictions['observations'],labels),
        input_failures=predictions['failures'],
        warning='Conditional point-level development scores. Selected diagnostic points are not representative image-area accuracy, independent test evidence or proof of fairness.')
    destination=ROOT/get_config().OUTPUTS_ROOT/'material_point_review_v1/human_labeled_results.json'
    with destination.open('x',encoding='utf-8') as stream: json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
