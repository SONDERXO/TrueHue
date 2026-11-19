"""One fixed context-balanced assessment; expert model never changes."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from wb_feature_direct_workflow import SETTINGS, ROLES
from wb_feature_direct_verify import route
from wb314_research_predictor import FrozenWB314, MODEL_SHA256
from src.model_training.blue_axis_preparation import features281
from wb_cue_equivalent_ties import extract
from src.model_training.luminance_chroma_operator import parameters, render_rgb8
from src.evaluation.luminance_chroma_scalar import replay
from src.evaluation.directional_recoverability import metrics

OUT = ROOT / 'outputs/wb314_background_balance_candidate_v1'
BASE = ROOT / 'outputs/wb_feature_direct_prediction_v1'
PROTOCOL = ROOT / 'docs/wb314-background-balance-protocol-2026-11-19.md'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    with Path(p).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def context_view(image, reference, alpha, measurement):
    if image.shape != (256, 256, 3) or image.dtype != np.uint8 or reference.shape != image.shape or reference.dtype != np.uint8:
        raise ValueError('Matching normalized RGB8 required')
    if alpha.shape != (256, 256) or measurement.shape != alpha.shape or not np.isfinite(alpha).all():
        raise ValueError('Matching finite masks required')
    retained = (alpha > 0) | (measurement > 0)
    result = reference.copy(); result[retained] = image[retained]
    return result, retained


def weighted_fit(rows, held_source=None):
    fitting = [r for r in rows if r['source_id'] != held_source]
    if not fitting or held_source is not None and any(r['source_id'] == held_source for r in fitting):
        raise ValueError('Nonempty source-disjoint fitting rows required')
    for row in fitting:
        if len(row['x']) != 314 or not np.isfinite(row['x']).all() or row['weight'] <= 0:
            raise ValueError('Finite314 vector and positive case weight required')
        parameters(row['y'])
    x = np.asarray([r['x'] for r in fitting], np.float32)
    native = DecisionTreeRegressor(**SETTINGS)
    native.fit(x, np.asarray([r['y'] for r in fitting], float), sample_weight=[r['weight'] for r in fitting])
    tree = native.tree_; nodes = []
    for i in range(tree.node_count):
        if tree.children_left[i] == -1:
            nodes.append(dict(kind='leaf', values=tree.value[i, :, 0].tolist()))
        else:
            nodes.append(dict(kind='split', feature=int(tree.feature[i]), threshold=float(tree.threshold[i]),
                              left=int(tree.children_left[i]), right=int(tree.children_right[i])))
    model = dict(schema='truehue_camera_control_cart_research_v1', dimensions=314, comparison='<=',
        settings=SETTINGS, nodes=nodes, generated_fixture=False,
        model_role='separate_background_balance_assessment_not_adopted')
    found = [route(model, r['x']) for r in fitting]
    assert [p for _, p in found] == native.predict(x).tolist()
    assert [leaf for leaf, _ in found] == native.apply(x).tolist()
    for leaf in set(i for i, _ in found):
        own = [r for r, (i, _) in zip(fitting, found) if i == leaf]
        total = math.fsum(r['weight'] for r in own)
        means = [math.fsum(r['weight'] * r['y'][j] for r in own) / total for j in range(5)]
        assert all(abs(a-b) < 1e-12 for a, b in zip(means, nodes[leaf]['values']))
    return model


def prepare():
    if OUT.exists(): raise FileExistsError('Preserve this attempt; no silent retry')
    assert sha(ROOT / 'outputs/wb314_final_training_v1/model.json') == MODEL_SHA256
    plan = read(BASE / 'plan.json'); old = read(BASE / 'rows.json')
    references = read(ROOT / 'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')
    references = {r['publisher_group'].removeprefix('ffhq_source_'): r for r in references if r['role'] == 'identity'}
    assert len(old) == 66 and len(plan['folds']) == 11
    original = {r['case_id']: r for r in plan['rows']}
    paths = {str(PROTOCOL): sha(PROTOCOL), str(Path(__file__)): sha(Path(__file__)),
             str(BASE / 'rows.json'): sha(BASE / 'rows.json'), str(BASE / 'plan.json'): sha(BASE / 'plan.json')}
    for row in old:
        source = references[row['source_id']]; paths[source['pixels_file']] = source['pixels_sha256']
        item = original[row['case_id']]; paths[str(ROOT / item['input_pack'])] = item['input_pack_sha256']
    assert all(sha(p) == h for p, h in paths.items())
    OUT.mkdir(); (OUT / 'packs').mkdir(); write(OUT / 'bindings_PRIVATE.json', paths)
    predictor = FrozenWB314(); rows = []; extractions = 0; prepared = []
    try:
        measurements = {}
        for sid in {r['source_id'] for r in old}:
            with np.load(references[sid]['pixels_file'], allow_pickle=False) as data:
                measurements[sid] = data['measurement_mask'].copy()
        for row in old:
            with np.load(ROOT / original[row['case_id']]['input_pack'], allow_pickle=False) as pack:
                image, reference, alpha, protected = [pack[k].copy() for k in ['input', 'reference', 'alpha', 'protected']]
            measurement = measurements[row['source_id']]
            changed, retained = context_view(image, reference, alpha, measurement)
            variants = [('original', image)]
            if not np.array_equal(changed, image): variants.append(('reference_background', changed))
            for kind, pixels in variants:
                if kind == 'original': vector = row['x314']
                else:
                    first, _ = features281(pixels, measurement, predictor.mapping, predictor.names[:281])
                    coefficients, _, _, _ = extract(predictor.wb, predictor.normalize, pixels)
                    extractions += 1; assert extractions <= 55
                    vector = np.asarray(first + coefficients.tolist(), np.float32).astype(float).tolist()
                    assert [vector[i] for i in [0,1,2,3,4,12,13,14,15]] == [row['x314'][i] for i in [0,1,2,3,4,12,13,14,15]]
                assert np.array_equal(pixels[retained], image[retained])
                case = row['case_id'] + '__' + kind
                target = OUT / 'packs' / (case + '.npz')
                np.savez(target, input=pixels, reference=reference, alpha=alpha, protected=protected)
                rows.append(dict(case_id=case, parent_case=row['case_id'], source_id=row['source_id'], role=row['role'],
                    view=kind, x=vector, y=row['y'], weight=1./len(variants), pack_sha256=sha(target)))
            prepared.append(row['case_id'])
            if len(prepared) % 11 == 0: print(f'Prepared {len(prepared)}/66 original cases; new WB forwards {extractions}', flush=True)
        assert all(sha(p) == h for p, h in paths.items())
        for case in original:
            assert math.fsum(r['weight'] for r in rows if r['parent_case'] == case) == 1.
        write(OUT / 'rows_PRIVATE.json', rows)
        write(OUT / 'preparation.json', dict(passed=True, original_cases=66, views=len(rows),
            context_feature_extractions=extractions, new_sources=0, new_masks=0, fits=0,
            all_facial_and_application_pixels_preserved=True, case_total_weights_one=True))
    except Exception as error:
        write(OUT / 'preparation_failure.json', dict(error=repr(error), completed=prepared, forwards=extractions, retry=False)); raise


def fit_and_score():
    assert read(OUT / 'preparation.json')['passed']
    if (OUT / 'fit_started.json').exists(): raise FileExistsError('Existing fit attempt; no retry')
    for path, digest in read(OUT / 'bindings_PRIVATE.json').items(): assert sha(path) == digest
    rows = read(OUT / 'rows_PRIVATE.json'); plan = read(BASE / 'plan.json')
    models = read(BASE / 'all_fits_verified.json')['models']
    write(OUT / 'fit_started.json', dict(maximum_held_fits=11, final_fit_only_after_pass=True))
    controls = []; fits = 0
    for fold in plan['folds']:
        sid = fold['held_source_id']; candidate = weighted_fit(rows, sid); fits += 1
        write(OUT / ('held_' + sid + '.json'), candidate)
        parent = next(r for r in models if r['arm'] == '314' and r['source_id'] == sid)
        assert sha(BASE / parent['path']) == parent['sha256']; baseline = read(BASE / parent['path'])
        for row in [r for r in rows if r['source_id'] == sid]:
            controls.append(dict(case_id=row['case_id'], candidate=route(candidate,row['x'])[1], baseline=route(baseline,row['x'])[1]))
        print(f'Verified source-held fit {fits}/11', flush=True)
    write(OUT / 'held_controls_sealed_PRIVATE.json', controls)
    predictions = {r['case_id']:r for r in controls}; scores = []; render_checks = 0
    for row in rows:
        path = OUT / 'packs' / (row['case_id'] + '.npz'); assert sha(path) == row['pack_sha256']
        with np.load(path,allow_pickle=False) as pack: image,reference,alpha,protected=[pack[k].copy() for k in ['input','reference','alpha','protected']]
        rec = {k:row[k] for k in ['case_id','parent_case','source_id','role','view','weight']}
        rec['input'] = metrics(image,reference,alpha>0)
        for kind in ['candidate','baseline']:
            p = predictions[row['case_id']][kind]; rendered = render_rgb8(image,alpha,protected,p)
            independent,_ = replay(image,image,alpha,protected,p)
            assert np.array_equal(rendered,independent)
            assert np.array_equal(rendered[protected | (alpha==0)],image[protected | (alpha==0)])
            rec[kind] = metrics(rendered,reference,alpha>0)
            rec[kind+'_changed'] = not np.array_equal(rendered,image); render_checks += 1
        scores.append(rec)
    write(OUT / 'scores_PRIVATE.json', scores)
    means = {}
    for view in ['original','reference_background']:
        means[view] = {}
        for role in ROLES:
            own=[r for r in scores if r['view']==view and r['role']==role]
            if own: means[view][role]={kind:{m:math.fsum(r[kind][m] for r in own)/len(own) for m in ['RGB','DE']} for kind in ['input','baseline','candidate']}
    gates = {}
    for role in ROLES:
        d=means['original'][role]
        gates['original_nonregression_'+role]=all(d['candidate'][m]<=d['baseline'][m]+1e-10 for m in ['RGB','DE'])
        own=[r for r in scores if r['view']=='original' and r['role']==role]
        gates['no_extra_harm_'+role]=all(sum(r['candidate'][m]>r['input'][m]+1e-10 for r in own)<=sum(r['baseline'][m]>r['input'][m]+1e-10 for r in own) for m in ['RGB','DE'])
    identity=[r for r in scores if r['view']=='original' and r['role']=='identity']
    gates['identity_changed_count_nonincrease']=sum(r['candidate_changed'] for r in identity)<=sum(r['baseline_changed'] for r in identity)
    for role in ['exposure_under','combined_under']:
        d=means['reference_background'].get(role)
        gates['context_improvement_'+role]=d is not None and all(d['candidate'][m]<d['baseline'][m]-1e-10 for m in ['RGB','DE'])
    passed=all(gates.values())
    summary=dict(assessment_executed=True,software_checks_passed=True,candidate_gate_passed=passed,
        original_cases=66,source_groups=11,training_views=len(rows),source_held_fits=fits,
        new_context_WB_forwards=read(OUT/'preparation.json')['context_feature_extractions'],
        scalar_and_protection_checks=render_checks,final_candidate_fits=0,expert_model_unchanged=True,
        user_photos_used_for_training=False,new_sources=0,new_mask_inference=0,model_adopted=False,
        correction_fix_complete=False,qualification_complete=False,gates=gates,by_view_role=means)
    write(OUT / 'summary.json',summary)
    print(json.dumps(summary),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','assess']);args=parser.parse_args()
    prepare() if args.stage=='prepare' else fit_and_score()
