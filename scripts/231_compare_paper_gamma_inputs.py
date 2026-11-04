"""New direct-gamma inputs on the exact20accepted development sources."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.paper_gamma import composite_rgb,transform_rgb,legacy_to_paper_parameters,COMPOSITE_VERSION,TRANSFORM_VERSION
from src.distortion_generation.generate_distortions import transform_rgb as legacy_transform
from src.model_training.recovery_targets import fit_recovery_target
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/paper_gamma_input_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    audit=ROOT/'outputs/accepted_training_pair_audit_v1'
    for name,sha in read(audit/'verification.json')['evidence_sha256'].items():assert digest(audit/name)==sha
    selected=[r for r in read(audit/'source_pair_dispositions.json') if r.get('input_technical_pass')]
    assert len(selected)==20
    parent=ROOT/'outputs/correction_training_preparation_v1'
    old_hashes=read(parent/'verification.json')['evidence_sha256']
    config=get_config();spec,identity=contract(ROOT)
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    paths=[Path(__file__),ROOT/'docs/paper-gamma-comparison-protocol.md',ROOT/'src/distortion_generation/paper_gamma.py',
        ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py',
        audit/'source_pair_dispositions.json',artifact,ROOT/'src/evaluation/mask_support_quality.py']
    paths.extend(ROOT/p for p in spec['dependency_sha256'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for folder in ['images','boards']:(out/folder).mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_generation',sources=[r['image_id'] for r in selected],
        input_sha256=hashes,measurement_contract_sha256=identity,lookup_sha256=digest(artifact),
        augmentation_version=COMPOSITE_VERSION,correction_parameter_version=TRANSFORM_VERSION,
        assumptions='Only gamma exponent changed; other composite operations are legacy engineering assumptions.',
        complete_three_variant_thesis_design=False,models_fitted=0))
    write('run_status.json',dict(status='running'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(im,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    def load(name,suffix,gray=False):
        relative=f'images/{name}_{suffix}.png';p=parent/relative
        assert digest(p)==old_hashes[relative]
        return cv2.imread(str(p),0 if gray else cv2.IMREAD_COLOR)
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def panel(im,label,mask=None):
        shown=im.copy()
        if mask is not None:
            chosen=mask>0;shown[chosen]=np.rint(.65*shown[chosen]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown
    records=[]
    try:
        for source in selected:
            name=source['source_id'];ref=load(name,'reference');ref_mask=load(name,'reference_mask',True)
            old_input=load(name,'input');old_mask=load(name,'input_mask',True)
            rgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB);support=ref_mask>0
            transformed,_=composite_rgb(rgb,source['assigned_severity'])
            _,clipping=composite_rgb(rgb[support][:,None,:],source['assigned_severity'])
            generated=rgb.copy();generated[support]=transformed[support]
            bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=source['image_id'],phase='matched_training_gamma_comparison'))+'\n')
            measured=measure(bgr,detector,masker)
            save(out/'images'/f'{name}_input.png',bgr)
            if measured.mask is not None:save(out/'images'/f'{name}_mask.png',measured.mask)
            r=dict(image_id=source['image_id'],source_id=name,assigned_severity=source['assigned_severity'],
                original_reference_notes=source['exact_notes'],status='input_failed',measurement=measured.report,
                old_clipping=source['clipping'],new_clipping=clipping,
                old_support_screen=source['exploratory_support_screen'],training_eligible=False,
                distorted_mask_review='pending',reference_path=f'outputs/correction_training_preparation_v1/images/{name}_reference.png',
                reference_mask_path=f'outputs/correction_training_preparation_v1/images/{name}_reference_mask.png')
            if measured.report['status']=='success':
                screen=support_retention(support,measured.mask>0,measured.mask>0)
                fit=fit_recovery_target(generated,rgb,measured.mask>0,support)
                r.update(status='target_unavailable',new_support_screen=screen,
                    input_features={**measured.report['features'],'input_mst_index':lookup.label(measured.report['features']['input_ita_degrees'])-1},
                    target_fit_legacy_coordinates=fit)
                if fit['parameters'] is not None:
                    params=legacy_to_paper_parameters(*fit['parameters'])
                    pixels=generated.astype(float)/255
                    np.testing.assert_allclose(transform_rgb(pixels,**params),legacy_transform(pixels,*fit['parameters']),rtol=0,atol=1e-14)
                    r.update(status='pending_input_review',paper_correction_target=params,
                        correction_transform_version=TRANSFORM_VERSION,
                        target_note='Approximate reference-informed fit; reciprocal gamma conversion preserves curve, not an exact composite inverse.')
            save(out/'boards'/f'{name}.png',np.vstack([
                np.hstack([panel(ref,name+' reviewed reference',ref_mask),panel(old_input,'Legacy input'),panel(old_input,'Legacy mask',old_mask)]),
                np.hstack([panel(ref,'Original reference'),panel(bgr,'Direct-gamma sensitivity'),panel(bgr,'New mask',measured.mask)])]))
            records.append(r)
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(r)+'\n')
            print(name,r['status'],source['clipping']['clipped_pixels'],'->',clipping['clipped_pixels'],flush=True)
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
        summary=dict(status='matched_sensitivity_complete_no_adoption',sources=20,
            old_clipped_inputs=sum(r['old_clipping']['clipped_pixels']>0 for r in records),
            new_clipped_inputs=sum(r['new_clipping']['clipped_pixels']>0 for r in records),
            old_clipped_pixels=sum(r['old_clipping']['clipped_pixels'] for r in records),
            new_clipped_pixels=sum(r['new_clipping']['clipped_pixels'] for r in records),
            old_support_screen_pass=sum(r['old_support_screen']['screen_pass'] for r in records),
            new_measurements_available=sum(r['measurement']['status']=='success' for r in records),
            new_support_screen_pass=sum(r.get('new_support_screen',{}).get('screen_pass',False) for r in records),
            new_unclipped_and_screen_passing=sum(r['new_clipping']['clipped_pixels']==0 and r.get('new_support_screen',{}).get('screen_pass',False) for r in records),
            approximate_targets_available=sum('paper_correction_target' in r for r in records),
            target_optimizer_calls=sum('target_fit_legacy_coordinates' in r for r in records),
            regression_tree_fits=0,training_admissions=0,active_assets_changed=False,reserved_validation_test_access=False,
            complete_three_distortion_recipe=False)
        write('summary.json',summary)
        sections=''.join(f'<section><h2>{r["source_id"]} — {r["status"]}</h2><p>Clipped support pixels: {r["old_clipping"]["clipped_pixels"]} → {r["new_clipping"]["clipped_pixels"]}. Original concern: {r["original_reference_notes"] or "none"}.</p><img loading="lazy" src="boards/{r["source_id"]}.png"></section>' for r in records)
        (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Direct-gamma matched comparison</title><style>body{font:17px system-ui;background:#171923;color:#eee;max-width:1100px;margin:28px auto;padding:16px}img{max-width:100%}section{border-top:1px solid #777;margin:24px 0}</style><h1>Same20 sources: gamma convention sensitivity</h1><p>No active model changed. Direct exponent follows the paper definition; other composite choices remain assumptions. New masks/targets are not automatically approved. These are not learned corrected outputs or the full three-variant thesis dataset.</p>'+sections,encoding='utf-8')
        write('run_status.json',dict(status='matched_sensitivity_complete_no_adoption'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)));raise


if __name__=='__main__':main()
