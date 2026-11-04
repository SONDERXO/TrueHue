"""One fixed new-source data preparation, never a correction-tree experiment."""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.three_variant_recipe import render_rgb,VARIANTS,VERSION
from src.distortion_generation.table2_composite import SETTINGS
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters
from src.model_training.recovery_targets import fit_recovery_target
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.evaluation.mask_support_quality import support_retention


def main():
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;out=base/'additional_six_source_pairs_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    registry=read(base/'reviewed_source_evidence32_v1/registry.json')
    verification=read(base/'reviewed_source_evidence32_v1/verification.json')
    assert digest(base/'reviewed_source_evidence32_v1/registry.json')==verification['evidence_sha256']['registry.json']
    candidates=[r for r in registry['rows'] if r['stratum']=='original_control' and r['evidence_origin'] in {'exact_three_source_review','exact_four_source_review'}]
    assert len(candidates)==6 and {Path(r['source_image_id']).stem for r in candidates}=={'2434','25517','39083','63509','42965','77101'}
    manifest=read(base/'correction_data_redesign_v1/selection.json');policy=read(base/'correction_data_redesign_v1/access_policy.json')
    attempts_path=base/'correction_training_preparation_v1/attempts.jsonl'
    hashes[attempts_path.relative_to(ROOT).as_posix()]=digest(attempts_path)
    old={r['image_id']:r for r in map(json.loads,attempts_path.read_text().splitlines())}
    specification,identity=contract(ROOT);assert identity==registry['measurement_contract_sha256']
    lookup_path=base/'mst_monotone_square256_v1/development_lookup.json'
    assert digest(lookup_path)==registry['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(lookup_path),identity)
    sources=[]
    for r in candidates:
        training_candidate(r['source_image_id'],manifest,policy)
        assert all(r['exact_user_judgments'][scope]['decision']=='accept' for scope in ['reference_suitability','reference_mask'])
        assert digest(ROOT/r['input_path'])==r['input_sha256'] and digest(ROOT/r['input_mask_path'])==r['input_mask_sha256']
        sources.append(dict(source_image_id=r['source_image_id'],source_id=Path(r['source_image_id']).stem,
            duplicate_group_id=r['duplicate_group_id'],reference_path=r['input_path'],reference_mask_path=r['input_mask_path'],
            reference_sha256=r['input_sha256'],reference_mask_sha256=r['input_mask_sha256'],
            reference_judgments=r['exact_user_judgments'],severity=old[r['source_image_id']]['assigned_severity'],
            settings=SETTINGS[old[r['source_image_id']]['assigned_severity']]))
        hashes[r['input_path']]=r['input_sha256'];hashes[r['input_mask_path']]=r['input_mask_sha256']
    dependencies=[Path(__file__),ROOT/'docs/additional-six-source-paired-data-protocol.md',
        ROOT/'src/distortion_generation/three_variant_recipe.py',ROOT/'src/distortion_generation/table2_composite.py',
        ROOT/'src/distortion_generation/paper_gamma.py',ROOT/'src/model_training/recovery_targets.py',
        ROOT/'src/model_training/facial_endpoint_features.py',ROOT/'src/evaluation/mask_support_quality.py']
    dependencies.extend(ROOT/p for p in specification['dependency_sha256'])
    for p in dependencies:hashes[p.relative_to(ROOT).as_posix()]=digest(p)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    out.mkdir();(out/'images').mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    variants=list(VARIANTS)+['gamma_lighten','gamma_darken']
    write('plan.json',dict(status='frozen_before_generation',sources=sources,variants=variants,attempts=30,
        recipe_version=VERSION,gamma_recipe='supplemental_gamma_only_two_directions_v1',
        measurement_contract_sha256=identity,lookup_sha256=digest(lookup_path),features=registry['features'],
        source_control_policy='reuse existing six approved controls; do not generate/count duplicate originals',
        input_sha256=hashes,training_authorized=False,model_fits=0,reserved_roles_locked=True))
    write('run_status.json',dict(status='running'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(square,box):
        x,y,w,height=box
        return prepare.compute_versioned_skin_mask(square[y:y+height,x:x+w],square,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    records=[]
    try:
        for source in sources:
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=source['source_image_id'],role='train',
                    phase='declared_new_source_paired_data_preparation',
                    files=[source['reference_path'],source['reference_mask_path']],raw_source_opened=False))+'\n')
            reference=cv2.imread(str(ROOT/source['reference_path']));ref_mask=cv2.imread(str(ROOT/source['reference_mask_path']),0)>0
            assert reference is not None and reference.shape==(*ref_mask.shape,3)
            rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB)
            for variant in variants:
                generated=rgb.copy();inverse=None
                if variant in VARIANTS:
                    transformed,_=render_rgb(rgb,source['severity'],variant)
                    _,clipping=render_rgb(rgb[ref_mask][:,None,:],source['severity'],variant)
                    generated[ref_mask]=transformed[ref_mask]
                else:
                    g=source['settings']['gamma'];exponent=g if variant=='gamma_lighten' else 1/g
                    floating=np.power(rgb.astype(float)/255,exponent)
                    assert np.isfinite(floating).all() and np.all((floating>=0)&(floating<=1))
                    generated[ref_mask]=np.rint(floating[ref_mask]*255).astype(np.uint8)
                    inverse=[1/exponent,1.,1.]
                    clipping=dict(clipped_pixels=0,clipped_channel_samples=0,total_channel_samples=int(ref_mask.sum())*3,
                        recipe='supplemental_gamma_only_two_directions_v1',exponent=exponent)
                assert np.array_equal(generated[~ref_mask],rgb[~ref_mask])
                bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR);measured=measure(bgr,detector,masker)
                mask=measured.mask if measured.mask is not None else np.zeros(ref_mask.shape,np.uint8)
                stem=source['source_id']+'_'+variant;ip=out/'images'/f'{stem}.png';mp=out/'images'/f'{stem}_mask.png'
                assert cv2.imwrite(str(ip),bgr) and cv2.imwrite(str(mp),mask)
                row=dict(source_image_id=source['source_image_id'],source_id=source['source_id'],
                    duplicate_group_id=source['duplicate_group_id'],reference_path=source['reference_path'],
                    reference_mask_path=source['reference_mask_path'],reference_judgments=source['reference_judgments'],
                    severity=source['severity'],pair_id=source['source_id']+'__additional_'+variant,variant=variant,
                    input_path=ip.relative_to(ROOT).as_posix(),input_mask_path=mp.relative_to(ROOT).as_posix(),
                    input_sha256=digest(ip),input_mask_sha256=digest(mp),measurement=measured.report,clipping=clipping,
                    newly_zero_channel_samples=int(((generated==0)&(rgb>0))[ref_mask].sum()),
                    lane='input_failure_hold',exact_input_mask_review='pending',training_eligible=False)
                if inverse is not None:
                    restored=np.rint(np.power(generated.astype(float)/255,inverse[0])*255).astype(np.uint8)
                    row.update(paper_target=inverse,target_semantics='algebraic_float_inverse_not_exact_after_quantization',
                        inverse_rgb_mae_on_generation_support=float(np.abs(restored.astype(float)-rgb)[ref_mask].mean()/255))
                if measured.report['status']=='success':
                    features=dict(measured.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
                    endpoints=facial_endpoint_features(measured.image,mask>0);assert endpoints['valid'];features.update(endpoints['features'])
                    screen=support_retention(ref_mask,mask>0,mask>0)
                    row.update(features=features,support_screen=screen,lane='target_unavailable_hold')
                    if inverse is None:
                        fitted=fit_recovery_target(generated,rgb,mask>0,ref_mask);row['target_fit']=fitted
                        if fitted['parameters'] is not None:
                            converted=legacy_to_paper_parameters(*fitted['parameters'])
                            row.update(paper_target=[converted['gamma'],converted['red_gain'],converted['blue_gain']],
                                target_semantics='bounded_approximate_RGB_fit_direct_gamma_converted')
                    if 'paper_target' in row:
                        row['lane']=('clipped_stress_pending_exact_mask_review' if clipping['clipped_pixels'] else
                            'unclipped_mask_screen_hold' if not screen['screen_pass'] else 'primary_pending_exact_mask_review')
                records.append(row)
            write('attempts.json',records);print(source['source_id']+': five fixed variants prepared',flush=True)
        assert len(records)==len({r['pair_id'] for r in records})==30
        assert contract(ROOT)[1]==identity and all(digest(ROOT/p)==sha for p,sha in hashes.items())
        primary=[r for r in records if r['lane']=='primary_pending_exact_mask_review']
        write('primary_review_queue.json',primary)
        summary=dict(status='data_prepared_no_model_fit',sources=6,generated_attempts=30,
            lanes=dict(Counter(r['lane'] for r in records)),primary_candidates=len(primary),
            primary_variants=dict(Counter(r['variant'] for r in primary)),
            primary_sources=len({r['source_image_id'] for r in primary}),
            target_optimizer_calls=sum('target_fit' in r for r in records),
            new_mask_approvals=0,new_fitting_admissions=0,correction_tree_fits=0,
            old26_sources_regenerated=0,raw_source_decodes=0,reserved_pixel_access=0)
        write('summary.json',summary);write('run_status.json',dict(status='complete'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)))
        raise


if __name__=='__main__':main()
