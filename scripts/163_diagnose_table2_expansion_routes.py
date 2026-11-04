"""Explain eight saved Table2 folds without fitting or changing predictions."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import joblib
import numpy as np
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.feature_target_diagnostic import neighbor_diagnostic
from src.model_training.portable_tree import float32, PortableTree

OUT = ROOT / 'outputs/table2_expansion_route_diagnosis_v1'
PARENT = ROOT / 'outputs/table2_reviewed_expansion_evaluation_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    def read(p): return json.loads(p.read_text(encoding='utf-8'))
    def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p, v): p.write_text(json.dumps(v, indent=2), encoding='utf-8')
    plan = read(PARENT/'fit_plan.json'); summary = read(PARENT/'summary.json')
    verification = read(PARENT/'verification.json')
    assert digest(PARENT/'fit_plan.json') == verification['fit_plan_sha256']
    assert digest(PARENT/'summary.json') == verification['summary_sha256']
    rows = {r['pair_id']: r for r in plan['rows']}
    assert len(rows) == 16 and len(plan['folds']) == 8
    assert not {'51739','40048','42532','63870'} & {p.split('__')[0] for p in rows}
    paths = [Path(__file__), PARENT/'fit_plan.json', PARENT/'summary.json', PARENT/'verification.json',
             ROOT/'outputs/table2_application_mask_comparison_v1/summary.json',
             ROOT/'src/evaluation/feature_target_diagnostic.py', ROOT/'src/model_training/portable_tree.py']
    paths += list(PARENT.glob('fold_*/*'))
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    OUT.mkdir()
    write(OUT/'protocol.json', dict(scope='Saved-fold explanation only; no fit, search, admission or prediction changes',
        queries='All16accepted pairs; rejected sources excluded',
        routes='float32 inputs, original sklearn thresholds and training members',
        neighbors='Fixed top3 using fitting-only population standardization: Lab3 primary; all5 sensitivity',
        target_comparison='Identity vs nonidentity only; fitted distortion targets differ continuously and are not severity classes',
        leakage='No held source or known duplicate group in fitting neighborhoods',
        caution='Distances are descriptive, not confidence or perceptual similarity; MST retained as required',
        user_statement_verbatim="No, that wasn't the one. It's better though. Anyways, let's continue on the next step.",
        user_review_interpretation='Earlier method not identified; favorable comparison is not blanket mask approval.'))
    records = []; folds = []
    for fold in plan['folds']:
        fid = fold['fold_id']; training = [rows[p] for p in fold['train_pair_ids']]
        model = joblib.load(PARENT/f'fold_{fid}/decision_tree.joblib')
        portable = PortableTree(read(PARENT/f'fold_{fid}/decision_tree.json'))
        matrix = np.array([[r[k] for k in MST_FEATURES] for r in training])
        targets = np.array([[r[k] for k in TARGETS] for r in training])
        leaves = model.apply(matrix)
        usage = {k: int(np.sum(model.tree_.feature == i)) for i,k in enumerate(MST_FEATURES)}
        folds.append(dict(fold_id=fid, split_counts=usage, training_pairs=len(training)))
        for prediction in [r for r in summary['records'] if r['fold_id']==fid]:
            row = rows[prediction['pair_id']]
            assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id'] != row['source_image_id'] and r['duplicate_group_id'] != row['duplicate_group_id'] for r in training)
            x = [row[k] for k in MST_FEATURES]
            leaf = int(model.apply([x])[0]); node = 0; path = []
            while model.tree_.children_left[node] != -1:
                f = int(model.tree_.feature[node]); threshold = float(model.tree_.threshold[node])
                value = float32(x[f]); left = value <= threshold
                path.append(dict(node=node, feature=MST_FEATURES[f], input_float32=value, threshold=threshold, branch='left' if left else 'right'))
                node = int(model.tree_.children_left[node] if left else model.tree_.children_right[node])
            assert node == leaf
            members = [r for r,l in zip(training,leaves) if l==leaf]
            mean = np.mean([[r[k] for k in TARGETS] for r in members],axis=0)
            np.testing.assert_allclose(mean, prediction['parameters'], rtol=0, atol=1e-12)
            np.testing.assert_allclose(portable.predict_one(x), prediction['parameters'], rtol=0, atol=1e-12)
            neighbors = {label: neighbor_diagnostic([r['pair_id'] for r in training], matrix, targets, x,
                [row[k] for k in TARGETS], axes) for label,axes in [('Lab3',[0,1,2]),('all5',[0,1,2,3,4])]}
            # Independently verify every distance and ordering, without using the helper.
            for label, axes in [('Lab3',[0,1,2]),('all5',[0,1,2,3,4])]:
                scales = [float(np.std(matrix[:,a],ddof=0)) for a in axes]
                distances = [(r['pair_id'], sum(((float(matrix[i,a])-float(x[a]))/s)**2 for a,s in zip(axes,scales) if s>0)**.5)
                             for i,r in enumerate(training)]
                ordered = sorted(distances,key=lambda t:(t[1],t[0]))
                assert [p for p,d in ordered] == [r['pair_id'] for r in neighbors[label]['ranking']]
                np.testing.assert_allclose([d for p,d in ordered],[r['distance'] for r in neighbors[label]['ranking']],rtol=0,atol=1e-12)
            records.append(dict(pair_id=row['pair_id'], variant=row['variant'], fold_id=fid, leaf=leaf,
                parameters=prediction['parameters'], input_features=dict(zip(MST_FEATURES,x)), path=path,
                leaf_members=[dict(pair_id=r['pair_id'],variant=r['variant'],targets=[r[k] for k in TARGETS]) for r in members],
                leaf_identity_members=sum(r['variant']=='identity' for r in members), leaf_total_members=len(members),
                neighbors=neighbors, ciede2000=prediction['learned']['ciede2000_source_mask'],
                no_correction_ciede2000=prediction['no_correction']['ciede2000_source_mask'],
                prediction_is_identity=bool(np.all(np.abs(np.array(prediction['parameters'])-1)<=1e-12))))
    identities = [r for r in records if r['variant']=='identity']
    harmed = [r for r in identities if r['ciede2000']>0]
    result = dict(records=records, folds=folds, harmed_identity_ids=[r['pair_id'] for r in harmed],
        uncorrected_distorted_ids=[r['pair_id'] for r in records if r['variant']!='identity' and r['prediction_is_identity']],
        harmful_identity_neighbors={m:dict(different_target_nearer=sum(r['neighbors'][m]['different_target_strictly_closer'] is True for r in harmed),total=len(harmed)) for m in ['Lab3','all5']},
        split_counts={k:sum(f['split_counts'][k] for f in folds) for k in MST_FEATURES}, input_sha256=hashes,
        caveat='MST is deterministic from input ITA; split usage is not proof of validated category-aware correction or feature importance. No impossibility claim.')
    assert hashes == {p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',result)
    write(OUT/'verification.json',dict(status='pass',verified_routes=16,verified_leaf_means=16,
        independently_checked_neighbor_rankings=32,portable_prediction_parity=True,source_and_duplicate_separation=True,
        inputs_unchanged=True,summary_sha256=digest(OUT/'summary.json')))
    lines = ['# Saved eight-source routing diagnosis','','No refit. Leaf members come only from the other seven source groups.','',
             '| Input | Error before / after | Fitting leaf members |','| --- | ---: | --- |']
    for r in records:
        lines.append(f"| {r['pair_id']} | {r['no_correction_ciede2000']:.3f} / {r['ciede2000']:.3f} | " + ', '.join(m['pair_id'] for m in r['leaf_members'])+' |')
    (OUT/'review-index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','folds','input_sha256']},indent=2))
    for r in records:
        if r in harmed or (r['variant']!='identity' and r['prediction_is_identity']):
            print(r['pair_id'], 'leaf:',[m['pair_id'] for m in r['leaf_members']], 'Lab neighbors:',r['neighbors']['Lab3']['top3'])


if __name__ == '__main__':
    main()
