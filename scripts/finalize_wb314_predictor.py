"""One fixed all-development WB314 fit; no tuning or runtime promotion."""
from pathlib import Path
import sys, math, copy, json, importlib.metadata
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from wb_feature_direct_workflow import ROOT, SETTINGS, ROLES, read, write, sha
from wb_feature_direct_verify import route, close
from src.model_training.luminance_chroma_operator import parameters, render_rgb8
from src.evaluation.luminance_chroma_scalar import replay

WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
QA = ROOT / 'outputs/wb314_final_training_engineering_v1'
OUT = ROOT / 'outputs/wb314_final_training_v1'
PROTOCOL = ROOT / 'docs/wb314-single-predictor-protocol-2026-11-18.md'


def validate(rows, generated):
    if len(rows) != 66 or len({r['case_id'] for r in rows}) != 66:
        raise ValueError('Exactly66unique development rows required')
    if len({r['source_id'] for r in rows}) != 11:
        raise ValueError('Eleven source groups required')
    for source in {r['source_id'] for r in rows}:
        if sorted(r['role'] for r in rows if r['source_id'] == source) != sorted(ROLES):
            raise ValueError('Complete six-role Cartesian roster required')
    for r in rows:
        x = r['x314']
        if (len(x) != 314 or not np.isfinite(x).all()
                or np.asarray(x, np.float32).astype(float).tolist() != x):
            raise ValueError('Finite exact float32 width314 required')
        parameters(r['y'])
        if r['y'][0] != 1 or r['y'][4] != 1 or r['generated_fixture'] is not generated:
            raise ValueError('Unchanged target/provenance contract required')


def export(native, generated):
    t = native.tree_
    nodes = []
    for i in range(t.node_count):
        if t.children_left[i] == -1:
            nodes.append(dict(kind='leaf', values=t.value[i, :, 0].tolist()))
        else:
            nodes.append(dict(kind='split', feature=int(t.feature[i]), threshold=float(t.threshold[i]),
                              left=int(t.children_left[i]), right=int(t.children_right[i])))
    return dict(schema='truehue_camera_control_cart_research_v1', dimensions=314,
                target_names=['gamma', 'exposure_gain', 'red_balance', 'blue_balance', 'chroma_scale'],
                settings=native.get_params(deep=False), comparison='<=', nodes=nodes,
                generated_fixture=generated, model_role='all_development_research_candidate_not_qualified_runtime')


def verify(model, rows):
    assert model['settings'] == SETTINGS and model['dimensions'] == 314 and model['comparison'] == '<='
    leaves = {}
    results = []
    for r in rows:
        leaf, p = route(model, r['x314'])
        parameters(p)
        leaves.setdefault(leaf, []).append(r)
        results.append(dict(case_id=r['case_id'], source_id=r['source_id'], role=r['role'], leaf=leaf, controls=p))
    assert set(leaves) == {i for i, n in enumerate(model['nodes']) if n['kind'] == 'leaf'}
    means = 0
    for leaf, own in leaves.items():
        for j in range(5):
            close(model['nodes'][leaf]['values'][j], math.fsum(r['y'][j] for r in own) / len(own), 1e-12)
            means += 1
    return results, means


def fit_checked(rows, generated):
    validate(rows, generated)  # All rows BEFORE constructing a tree.
    native = DecisionTreeRegressor(**SETTINGS)
    x = np.asarray([r['x314'] for r in rows], np.float32)
    native.fit(x, np.asarray([r['y'] for r in rows], np.float64))
    model = export(native, generated)
    results, means = verify(model, rows)
    assert [r['controls'] for r in results] == native.predict(x).tolist()
    assert [r['leaf'] for r in results] == native.apply(x).tolist()
    return model, results, means


def generated():
    if QA.exists(): raise FileExistsError(QA)
    rows = []
    rng = np.random.default_rng(42)
    for source in range(11):
        for i, role in enumerate(ROLES):
            x = rng.normal(size=314).astype(np.float32)
            x[:6] = 0; x[i] = 1
            gain = 2 ** .5 if role.endswith('under') else 2 ** -.5 if role.endswith('over') else 1.
            cast = role == 'colour_only' or role.startswith('combined')
            rows.append(dict(case_id=f'generated_{source}_{role}', source_id=str(source), role=role,
                             generated_fixture=True, x314=x.astype(float).tolist(),
                             y=[1., gain, 1/.85 if cast else 1., 1/1.15 if cast else 1., 1.]))
    invalid = []
    for kind in ['width', 'nan', 'target', 'missing', 'provenance']:
        bad = copy.deepcopy(rows)
        if kind == 'width': bad[0]['x314'].pop()
        elif kind == 'nan': bad[0]['x314'][0] = float('nan')
        elif kind == 'target': bad[0]['y'][1] = 100
        elif kind == 'missing': bad.pop()
        else: bad[0]['generated_fixture'] = False
        try: validate(bad, True)
        except (ValueError, AssertionError): invalid.append(kind)
        else: raise AssertionError('Invalid final-fit payload accepted')
    model, predictions, means = fit_checked(rows, True)
    QA.mkdir(); write(QA/'generated_model.json', model)
    write(QA/'verification.json', dict(passed=True, generated_fits=1, real_fits=0,
          native_scalar_routes=66, leaf_means=means, invalid_rejections=invalid,
          source_sha256=sha(Path(__file__)), protocol_sha256=sha(PROTOCOL)))
    print('PASS one generated adaptation fit/66portable routes/leafmeans/5invalid guards;0real fits.', flush=True)


def fit():
    if OUT.exists(): raise FileExistsError('Existing real final-fit attempt; no retry')
    qa = read(QA/'verification.json')
    assert qa['passed'] and sha(Path(__file__)) == qa['source_sha256'] and sha(PROTOCOL) == qa['protocol_sha256']
    proof = read(WB/'verification.json'); assert proof['passed'] and proof['candidate_numeric_eligible']
    for p, digest in proof['artifacts'].items(): assert sha(WB/p) == digest
    schema = read(WB/'feature_schema.json'); assert len(schema['314']) == 314
    rows = read(WB/'rows.json'); validate(rows, False)
    assert read(WB/'plan.json')['settings'] == SETTINGS
    reviews = [ROOT/'outputs/wb_feature_identity_ratings_v1/assessment_PRIVATE.json',
               ROOT/'outputs/wb_feature_colour_user_correction_v1/assessment_PRIVATE.json',
               ROOT/'outputs/wb_feature_remaining_exposure_ratings_v1/combined_exposure_assessment.json',
               ROOT/'outputs/wb_feature_exposure_preference_clarification_v1/interpretation.json',
               ROOT/'outputs/wb_feature_exposure_preference_clarification_v1/user_reply.txt']
    assert read(reviews[0])['counts']['acceptable'] == 11
    assert read(reviews[1])['preference_counts']['candidate'] == 11
    exposure = read(reviews[2]); assert exposure['complete'] and exposure['cases'] == 44 and exposure['appearance_counts']['acceptable'] == 44
    for p, digest in exposure['bindings'].items(): assert sha(ROOT/p) == digest
    paths = reviews + [Path(__file__), PROTOCOL, QA/'verification.json', WB/'rows.json', WB/'feature_schema.json', WB/'verification.json', WB/'held_controls_sealed.json',
                      ROOT/'src/model_training/luminance_chroma_operator.py', ROOT/'src/evaluation/luminance_chroma_scalar.py']
    bindings = {p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    OUT.mkdir(); write(OUT/'bindings.json', bindings)
    write(OUT/'plan.json', dict(settings=SETTINGS, training_cases=[r['case_id'] for r in rows],
          feature_names=schema['314'], real_fit_budget=1, qualification_complete=False,
          interpretation='66exposed fitting rows; no independent final test or old-rating transfer',
          authorization='Okay lets do that. Keep working until you nneed my input',
          versions={k:importlib.metadata.version(k) for k in ['numpy','scikit-learn','scipy','scikit-image']}))
    write(OUT/'fit_accounting.json', dict(started=1, maximum=1))
    try:
        model, predictions, means = fit_checked(rows, False)
        write(OUT/'model.json', model)
        write(OUT/'model_seal.json', dict(model_sha256=sha(OUT/'model.json'), verified_routes=66,
                                        leaf_mean_checks=means, actual_fits=1, before_portrait_pixels=True))
        write(OUT/'training_predictions.json', predictions)
        old = {r['case_id']:r['controls314'] for r in read(WB/'held_controls_sealed.json')}
        changed = [r for r in predictions if any(abs(a-b)>1e-12 for a,b in zip(r['controls'],old[r['case_id']]))]
        write(OUT/'prediction_comparison.json', dict(comparison='New all-data FITTING predictions vs old source-held predictions; not held evaluation',
              changed_controls=changed, unchanged_within_1e12=66-len(changed)))
        for p, digest in bindings.items(): assert sha(ROOT/p) == digest
        write(OUT/'training_verification.json', dict(passed=True, real_fits=1, native_portable_routes=66,
              leaf_mean_checks=means, changed_controls=len(changed), model_sha256=sha(OUT/'model.json'),
              qualification_complete=False, new_pixel_reads=0, historical_reviews_transferred=False))
        print('SEALED one real final research tree; changed controls='+str(len(changed))+'/66.', flush=True)
    except Exception as error:
        write(OUT/'training_failure.json', dict(error=repr(error), retry_allowed=False)); raise


def render():
    if (OUT/'evaluation').exists(): raise FileExistsError('Existing final-candidate render attempt')
    v = read(OUT/'training_verification.json'); assert v['passed']
    assert sha(OUT/'model.json') == read(OUT/'model_seal.json')['model_sha256']
    for p, digest in read(OUT/'bindings.json').items(): assert sha(ROOT/p) == digest
    proof = read(WB/'verification.json'); known = {p.replace('\\','/'):h for p,h in proof['artifacts'].items()}
    predictions = read(OUT/'training_predictions.json')
    for r in predictions:
        p=WB/'evaluation'/(r['case_id']+'.npz'); assert sha(p)==known['evaluation/'+p.name]
    (OUT/'evaluation').mkdir(); records=[]
    try:
        for r in predictions:
            p=WB/'evaluation'/(r['case_id']+'.npz')
            with np.load(p,allow_pickle=False) as z: image,alpha,protected,old=[z[k] for k in ['input','alpha','protected','314']]
            output=render_rgb8(image,alpha,protected,r['controls'])
            independent,_=replay(image,image,alpha,protected,r['controls'])
            assert np.array_equal(output,independent)
            assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
            dest=OUT/'evaluation'/(r['case_id']+'.npz');np.savez(dest,candidate=output)
            records.append({k:r[k] for k in ['case_id','source_id','role','controls']}|dict(
                saved_sha256=sha(dest),pixel_equal_old=bool(np.array_equal(output,old)),
                pixels_changed_vs_old=int(np.any(output!=old,axis=2).sum()),
                pixel_equal_input=bool(np.array_equal(output,image))))
            if len(records)%11==0: print('Final-candidate scalar replay '+str(len(records))+'/66',flush=True)
        write(OUT/'render_comparison.json',dict(records=records,changed_cases=[r['case_id'] for r in records if not r['pixel_equal_old']],
              all66_scalar_replays_pass=True,old_reviews_automatically_transferred=False,qualification_complete=False))
        for r in predictions:
            p=WB/'evaluation'/(r['case_id']+'.npz');assert sha(p)==known['evaluation/'+p.name]
        write(OUT/'verification.json',dict(passed=True,real_fits=1,scalar_render_checks=66,
              changed_outputs=sum(not r['pixel_equal_old'] for r in records),qualification_complete=False,
              artifacts={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()}))
        print('COMPLETE final research tree/export/66scalar checks; changed outputs='+str(sum(not r['pixel_equal_old'] for r in records)),flush=True)
    except Exception as error:
        write(OUT/'render_failure.json',dict(error=repr(error),completed=len(records),retry_allowed=False));raise


if __name__=='__main__':
    {'generated':generated,'fit':fit,'render':render}[sys.argv[1]]()
