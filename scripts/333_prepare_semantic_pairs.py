"""Rebuild pairs on six accepted semantic masks; no MST/tree fit or adoption."""
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.semantic_measurement import contract, measure
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.three_variant_recipe import render_rgb, VARIANTS
from src.distortion_generation.table2_composite import SETTINGS
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters
from src.model_training.recovery_targets import fit_recovery_target
from src.evaluation.mask_support_quality import support_retention


def generate(reference_rgb, mask, group, variant):
    generated = reference_rgb.copy(); inverse = None
    if variant in VARIANTS:
        transformed, _ = render_rgb(reference_rgb, group, variant)
        _, clipping = render_rgb(reference_rgb[mask][:, None, :], group, variant)
        generated[mask] = transformed[mask]
    else:
        g = SETTINGS[group]['gamma']; exponent = g if variant == 'gamma_lighten' else 1/g
        transformed = np.power(reference_rgb.astype(float)/255, exponent)
        generated[mask] = np.rint(transformed[mask]*255).astype(np.uint8)
        inverse = [1/exponent, 1., 1.]
        clipping = dict(clipped_channel_samples=0, clipped_pixels=0,
                        total_channel_samples=int(mask.sum())*3, exponent=exponent)
    assert np.array_equal(generated[~mask], reference_rgb[~mask])
    return generated, clipping, inverse


def main():
    out = ROOT / 'outputs/semantic_paired_preparation_v1'
    if out.exists(): raise FileExistsError(out)
    hashes = {}
    def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(relative):
        p = ROOT / relative; hashes[relative] = digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    decisions = read('outputs/semantic_reference_mask_import_v1/decisions.json')
    manifest = read('outputs/semantic_reference_readiness_v1/manifest.json')
    old = read('outputs/additional_six_source_pairs_v1/plan.json')
    groups = {r['source_image_id']: r['severity'] for r in old['sources']}
    byid = {r['case_id']: r for r in manifest['rows']}
    spec, identity = contract(ROOT)
    assert all(r['measurement_contract_sha256'] == identity for r in decisions)
    sources = []
    for d in decisions:
        if d['mask_decision'] != 'accept': continue
        r = byid[d['case_id']]
        for key in ('source_sha256', 'mask_sha256'): assert r[key] == d[key]
        for key, hashkey in [('source_path','source_sha256'), ('mask_path','mask_sha256')]:
            assert digest(ROOT/r[key]) == r[hashkey]; hashes[r[key]] = r[hashkey]
        sources.append(dict(r, severity=groups[r['source_image_id']], mask_decision=d))
    assert len(sources) == 6
    tracked = [Path(__file__), ROOT/'docs/semantic-paired-data-preparation-protocol.md',
        ROOT/'src/distortion_generation/three_variant_recipe.py', ROOT/'src/distortion_generation/table2_composite.py',
        ROOT/'src/distortion_generation/paper_gamma.py', ROOT/'src/model_training/recovery_targets.py',
        ROOT/'src/evaluation/mask_support_quality.py', ROOT/'src/demo/service.py',
        ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json']
    tracked += [ROOT/p for p in spec['dependency_sha256']]
    for p in tracked: hashes[p.relative_to(ROOT).as_posix()] = digest(p)
    out.mkdir(); (out/'images').mkdir(); (out/'boards').mkdir()
    def write(name, value): (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    variants = list(VARIANTS)+['gamma_lighten','gamma_darken']
    write('plan.json',dict(status='frozen_before_generation', sources=sources, variants=variants,
        planned_inputs=30, planned_controls=6, measurement_contract_sha256=identity,
        input_sha256=hashes, mst_policy='unavailable_no_matching_lookup_adopted',
        group_policy='historical_engineering_recipe_assignment_not_new_MST_truth',
        source_role='already_exposed_training_method_migration_not_independent_expansion',
        correction_tree_fits=0, automatic_training=False))
    config = get_config(); prepare = importlib.import_module('11_prepare_training_manifests')
    detector = lambda im: prepare._detect_face_boxes(im, ROOT/config.FACE_MODEL_PATH, .85)
    def landmarks(im,box):
        points,_,_ = prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        return None if points is None else points+np.array(box[:2])
    parser = DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    records = []; controls = []
    for source in sources:
        reference = cv2.imread(str(ROOT/source['source_path'])); refmask = cv2.imread(str(ROOT/source['mask_path']),0)>0
        rgb = cv2.cvtColor(reference, cv2.COLOR_BGR2RGB)
        stats = compute_masked_lab_statistics(reference,refmask.astype(np.uint8)*255,1000)
        assert stats['valid']
        controls.append(dict(source_image_id=source['source_image_id'], reference_path=source['source_path'],
            mask_path=source['mask_path'], statistics=stats, endpoint_features=facial_endpoint_features(reference,refmask),
            target_direct_gamma_red_blue=[1.,1.,1.], mst=None, training_admitted=False,
            exact_mask_decision=source['mask_decision']))
        for variant in variants:
            generated, clipping, inverse = generate(rgb,refmask,source['severity'],variant)
            bgr = cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
            measured = measure(bgr,detector,landmarks,parser)
            stem = source['case_id'].replace('_reference','')+'_'+variant
            ip = out/'images'/(stem+'.png'); assert cv2.imwrite(str(ip),bgr)
            row = dict(case_id=stem, source_image_id=source['source_image_id'],variant=variant,
                reference_path=source['source_path'], generation_mask_path=source['mask_path'],
                reference_sha256=source['source_sha256'],generation_mask_sha256=source['mask_sha256'],
                severity=source['severity'],input_path=ip.relative_to(ROOT).as_posix(),input_sha256=digest(ip),
                measurement=measured.report,clipping=clipping,mask_decision='pending',training_admitted=False,
                lane='processing_hold',mst=None,
                newly_zero_channel_samples=int(((generated==0)&(rgb>0))[refmask].sum()))
            if measured.mask is not None:
                mp = out/'images'/(stem+'_mask.png'); assert cv2.imwrite(str(mp),measured.mask)
                row.update(mask_path=mp.relative_to(ROOT).as_posix(),mask_sha256=digest(mp))
            if inverse is not None:
                restored=np.rint(np.power(generated.astype(float)/255,inverse[0])*255)
                row.update(target_direct_gamma_red_blue=inverse,
                    target_semantics='known_float_inverse_not_exact_after_quantization',
                    inverse_rgb_mae=float(np.abs(restored-rgb)[refmask].mean()/255))
            if measured.report['status']=='success':
                row['support_screen']=support_retention(refmask,measured.mask>0,measured.mask>0)
                if inverse is None:
                    fitted=fit_recovery_target(generated,rgb,measured.mask>0,refmask);row['target_fit']=fitted
                    if fitted['parameters'] is not None:
                        converted=legacy_to_paper_parameters(*fitted['parameters'])
                        row.update(target_direct_gamma_red_blue=[converted[k] for k in ('gamma','red_gain','blue_gain')],
                                   target_semantics='bounded_approximate_RGB_target_fit_not_exact_inverse')
                row['lane']='target_hold'
                if row.get('target_direct_gamma_red_blue') is not None:
                    row['lane']=('support_hold' if not row['support_screen']['screen_pass'] else
                        'clipped_stress_unreviewed' if clipping['clipped_channel_samples'] else 'primary_unreviewed')
            mask = measured.mask if measured.mask is not None else np.zeros((256,256),np.uint8)
            alpha=.45*(mask>0)[:,:,None]
            overlay=np.rint(bgr*(1-alpha)+np.array([0,255,0])*alpha).astype(np.uint8)
            bp=out/'boards'/(stem+'.png');assert cv2.imwrite(str(bp),np.hstack((reference,bgr,overlay)))
            row['board_path']=bp.relative_to(out).as_posix();records.append(row)
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(
                source_image_id=source['source_image_id'],role='train',phase='semantic_generation_measurement',
                reference_path=source['source_path'],new_input_path=row['input_path']))+'\n')
            print(stem,row['lane'],flush=True)
    replayed=0
    for row in records:
        source=next(r for r in sources if r['source_image_id']==row['source_image_id'])
        ref=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        expected,_,_=generate(ref,mask,source['severity'],row['variant'])
        actual=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        assert np.array_equal(expected,actual);assert digest(ROOT/row['input_path'])==row['input_sha256']
        replayed+=1
    assert contract(ROOT)[1]==identity and all(digest(ROOT/p)==h for p,h in hashes.items())
    write('controls.json',controls);write('records.json',records)
    result=dict(status='data_preparation_complete_not_fitting_ready',sources=len(sources),controls=len(controls),
        variants=len(records),lanes=dict(Counter(r['lane'] for r in records)),generation_pixel_replays=replayed,
        new_mask_approvals=0,correction_tree_fits=0,matching_lookup_adopted=False,demo_changed=False,
        reserved_pixel_access=0,measurement_contract_sha256=identity)
    write('verification.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
