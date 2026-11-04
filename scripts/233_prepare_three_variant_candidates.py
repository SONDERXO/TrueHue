"""Build20controls and60declared distortions, preserving all holds and failures."""
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
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.three_variant_recipe import render_rgb,VARIANTS,VERSION
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters,TRANSFORM_VERSION
from src.model_training.recovery_targets import fit_recovery_target
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/three_variant_training_candidates_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    audit=ROOT/'outputs/accepted_training_pair_audit_v1'
    selected=[r for r in read(audit/'source_pair_dispositions.json') if r.get('input_technical_pass')]
    assert len(selected)==20
    previous=ROOT/'outputs/paper_gamma_input_comparison_v1'
    for name,sha in read(previous/'verification.json')['evidence_sha256'].items():assert digest(previous/name)==sha
    parent=ROOT/'outputs/correction_training_preparation_v1'
    prior={r['image_id']:r for r in (json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    old=read(parent/'verification.json')['evidence_sha256']
    config=get_config();spec,identity=contract(ROOT)
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    paths=[Path(__file__),ROOT/'docs/three-variant-augmentation-protocol.md',
        ROOT/'src/distortion_generation/three_variant_recipe.py',ROOT/'src/distortion_generation/paper_gamma.py',
        ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py',
        audit/'source_pair_dispositions.json',previous/'verification.json',artifact]
    paths.extend(ROOT/p for p in spec['dependency_sha256'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for name in ['images','boards']:(out/name).mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_generation',recipe_version=VERSION,
        declared_engineering_variants=list(VARIANTS),distortions_per_source=3,extra_identity_controls=1,
        planned_attempts=80,source_ids=[r['image_id'] for r in selected],
        measurement_contract_sha256=identity,input_sha256=hashes,
        exact_author_generation_recipe=False,training_admitted=0,regression_tree_fits=0))
    write('run_status.json',dict(status='running'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(im,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def panel(image,label,mask=None):
        shown=image.copy()
        if mask is not None:
            selected=mask>0;shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown
    rows=[]
    def append(row):
        rows.append(row)
        with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(row)+'\n')
    try:
        for selected_row in selected:
            image_id=selected_row['image_id'];name=selected_row['source_id'];source=prior[image_id]
            ref_relative=f'images/{name}_reference.png';mask_relative=f'images/{name}_reference_mask.png'
            assert digest(parent/ref_relative)==old[ref_relative] and digest(parent/mask_relative)==old[mask_relative]
            ref=cv2.imread(str(parent/ref_relative));ref_mask=cv2.imread(str(parent/mask_relative),0)
            rgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB);support=ref_mask>0
            common=dict(source_image_id=image_id,source_id=name,duplicate_group_id=selected_row['duplicate_group_id'],
                partition='train',table_use='held_development_candidate_not_fitting',training_eligible=False,
                reference_notes=selected_row['exact_notes'],reference_review='accepted_original_mask',
                assigned_severity=selected_row['assigned_severity'],
                reference_path=str((parent/ref_relative).relative_to(ROOT)),reference_mask_path=str((parent/mask_relative).relative_to(ROOT)),
                measurement_contract_sha256=identity,correction_transform_version=TRANSFORM_VERSION)
            append(dict(common,pair_id=image_id+'__identity',variant='identity',status='reference_control_only',
                input_path=common['reference_path'],input_mask_path=common['reference_mask_path'],
                input_features=source['identity_features'],paper_correction_target=dict(gamma=1.,red_gain=1.,blue_gain=1.),
                exact_identity_target=True,clipped_pixels=0))
            panels=[panel(ref,name+' reference'),panel(ref,'Reviewed original mask',ref_mask)]
            for variant in VARIANTS:
                transformed,_=render_rgb(rgb,selected_row['assigned_severity'],variant)
                _,clipping=render_rgb(rgb[support][:,None,:],selected_row['assigned_severity'],variant)
                generated=rgb.copy();generated[support]=transformed[support]
                bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
                if variant=='combined':np.testing.assert_array_equal(bgr,cv2.imread(str(previous/'images'/f'{name}_input.png')))
                with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=image_id,variant=variant,phase='training_three_variant_candidate'))+'\n')
                measured=measure(bgr,detector,masker)
                input_path=out/'images'/f'{name}_{variant}.png';mask_path=out/'images'/f'{name}_{variant}_mask.png'
                save(input_path,bgr)
                if measured.mask is not None:save(mask_path,measured.mask)
                row=dict(common,pair_id=image_id+'__'+variant,variant=variant,status='input_failed',clipping=clipping,
                    clipped_pixels=clipping['clipped_pixels'],measurement=measured.report,
                    input_path=str(input_path.relative_to(ROOT)),input_mask_path=str(mask_path.relative_to(ROOT)) if measured.mask is not None else None,
                    distorted_mask_review='pending',primary_route='stress_only_pending_review' if clipping['clipped_pixels'] else 'unclipped_pending_review')
                if measured.report['status']=='success':
                    fit=fit_recovery_target(generated,rgb,measured.mask>0,support)
                    row.update(status='target_unavailable',target_fit_legacy_coordinates=fit,
                        input_features={**measured.report['features'],'input_mst_index':lookup.label(measured.report['features']['input_ita_degrees'])-1},
                        support_screen=support_retention(support,measured.mask>0,measured.mask>0))
                    if fit['parameters'] is not None:row.update(status='pending_input_review',paper_correction_target=legacy_to_paper_parameters(*fit['parameters']),exact_identity_target=False)
                append(row);panels.extend([panel(bgr,variant),panel(bgr,variant+' mask',measured.mask)])
                print(name,variant,row['status'],clipping['clipped_pixels'],flush=True)
            save(out/'boards'/f'{name}.png',np.vstack([np.hstack(panels[:4]),np.hstack(panels[4:])]))
        assert len(rows)==80 and len({r['pair_id'] for r in rows})==80
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
        summary=dict(status='complete_candidate_manifest_not_admitted',sources=20,controls=20,distorted_attempts=60,variants={})
        for variant in VARIANTS:
            values=[r for r in rows if r['variant']==variant]
            summary['variants'][variant]=dict(attempts=len(values),statuses=dict(Counter(r['status'] for r in values)),
                clipped_inputs=sum(r['clipped_pixels']>0 for r in values),clipped_pixels=sum(r['clipped_pixels'] for r in values),
                support_screen_pass=sum(r.get('support_screen',{}).get('screen_pass',False) for r in values),
                unclipped_screen_passing_target_candidates=sum(r['clipped_pixels']==0 and r.get('support_screen',{}).get('screen_pass',False) and 'paper_correction_target' in r for r in values))
        summary.update(training_admissions=0,regression_tree_fits=0,reserved_validation_test_access=False,
            exact_paper_generation_recipe=False,combined_previous_version_pixel_parity=20)
        write('summary.json',summary)
        sections=''.join(f'<section><h2>{r["source_id"]}</h2><img loading="lazy" src="boards/{r["source_id"]}.png"></section>' for r in selected)
        (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Three-variant development candidates</title><style>body{font:17px system-ui;background:#171923;color:#eee;margin:28px}img{max-width:100%}section{border-top:1px solid #666;margin:24px 0}</style><h1>Three declared distortions + unchanged control</h1><p>Engineering decomposition of Table2; no claim that the paper defines these exact recipes. Same20reviewed references. All new variant masks pending review; no model fitted. Original concerns remain in the manifest.</p>'+sections,encoding='utf-8')
        write('run_status.json',dict(status='complete_candidate_manifest_not_admitted'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(rows),error=str(error)));raise


if __name__=='__main__':main()
