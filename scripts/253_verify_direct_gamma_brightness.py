"""Independent feature/membership refits and60output replays for a failed candidate."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.facial_brightness_features import facial_brightness_features
from src.model_training.portable_tree import PortableTree,export_tree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/direct_gamma_brightness_comparison_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    parent=read(ROOT/'outputs/direct_gamma_regression_comparison_v1/plan.json')
    rows={r['pair_id']:r for r in parent['rows']};extra=read(out/'features.json');vectors={}
    for report in extra:
        row=rows[report['pair_id']];image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        result=facial_brightness_features(image,mask)
        assert result=={k:v for k,v in report.items() if k!='pair_id'} and result['valid']
        vectors[row['pair_id']]=[row[k] if k in row else result['features'][k] for k in plan['features']]
    assert len(vectors)==30
    controls=0
    for fold in plan['folds']:
        fid=fold['fold_id'];training=[rows[p] for p in fold['train_pair_ids']];held=[rows[p] for p in fold['inner_validation_pair_ids']]
        assert not {r['source_image_id'] for r in training}&{r['source_image_id'] for r in held}
        assert not {r['duplicate_group_id'] for r in training}&{r['duplicate_group_id'] for r in held}
        x=[vectors[r['pair_id']] for r in training];y=[parent['converted_targets'][r['pair_id']] for r in training]
        expected=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,y),plan['features'],parent['target_names'],{})
        raw=read(out/f'fold_{fid}/brightness_raw.json');protected=read(out/f'fold_{fid}/brightness_protected.json')
        assert expected['nodes']==raw['nodes'];tree=PortableTree(raw);candidate=PortableTree(protected)
        for index,(a,b) in enumerate(zip(raw['nodes'],protected['nodes'])):
            if a['kind']=='split':assert a==b;continue
            fitting_controls=[r for r in training if r['variant']=='identity' and tree.leaf_id(vectors[r['pair_id']])==index]
            assert b['values']==([1.,1.,1.] if fitting_controls else a['values'])
        for r in training:
            if r['variant']=='identity':assert candidate.predict_one(vectors[r['pair_id']])==[1.,1.,1.];controls+=1
    records=read(out/'predictions.json');summary=read(out/'summary.json')
    assert len(records)==60 and controls==210
    for record in records:
        row=rows[record['pair_id']];fid=record['fold_id']
        tree=PortableTree(read(out/f'fold_{fid}/{record["method"]}.json'))
        assert tree.predict_one(vectors[row['pair_id']])==record['parameters']
        image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        expected=image.copy();expected[mask]=np.rint(transform_rgb(image.astype(float)/255,*record['parameters'])[mask]*255).astype(np.uint8)
        path=out/f'fold_{fid}'/(row['pair_id']+'_'+record['method']+'.png')
        assert digest(path)==record['output_sha256']
        np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),expected)
        metrics=image_errors(reference,expected,score)
        for key,value in metrics.items():
            if value is None:assert record['metrics'][key] is None
            else:assert abs(value-record['metrics'][key])<1e-12
    for aggregate in summary['aggregates']:
        selected=[r for r in records if r['method']==aggregate['method'] and (aggregate['scope']=='all' or (r['variant']=='identity')==(aggregate['scope']=='identity'))]
        assert abs(np.mean([r['metrics']['ciede2000_source_mask'] for r in selected])-aggregate['candidate'])<1e-12
        assert sum(r['changed_input_pixels']>0 for r in selected)==aggregate['changed_pairs']
    assert not any(g['passed'] for g in summary['gates'].values())
    target.write_text(json.dumps(dict(status='pass',verified_input_feature_vectors=30,independent_refits=15,
        protected_tree_membership_verified=True,fitting_controls_checked=controls,reconstructed_outputs_and_metrics=60,
        failed_candidate_not_promoted=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:30input-only vectors,15refits,210fitting controls and60outputs;failed candidate retained without promotion.')


if __name__=='__main__':main()
