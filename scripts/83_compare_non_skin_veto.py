"""Fixed removal-only material veto on saved75 inputs and labeled regressions.

Diagnostic masks only: no regenerated variants, fitting or runtime adoption.
"""
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
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def veto(mask,categories):
    if mask.dtype!=bool or categories.dtype!=np.uint8 or mask.shape!=categories.shape:
        raise ValueError('Matching boolean mask/uint8 categories required')
    if (categories>5).any():raise ValueError('Unknown category')
    result=mask&np.isin(categories,[2,3])
    assert not (result&~mask).any()
    return result


def panel(image,mask,title):
    shown=image.copy();shown[mask]=np.rint(.55*shown[mask]+.45*np.asarray([0,220,0])).astype(np.uint8)
    shown=cv2.copyMakeBorder(shown,32,0,0,0,cv2.BORDER_CONSTANT)
    cv2.putText(shown,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1)
    return shown


def main():
    config=get_config();output=ROOT/'outputs/non_skin_veto_v1'
    if output.exists():raise FileExistsError(output)
    parent=ROOT/'outputs/training_source60_variants_v1'
    summary_path=parent/'summary.json';summary=json.loads(summary_path.read_text())
    review_path=ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json'
    review={r['pair_id']:r for r in json.loads(review_path.read_text())['pairs']}
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json'
    label_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(label_path.read_text())
    assert not labels['draft'] and labels['manifest_sha256']==digest(manifest)
    label_map={r['point_id']:r['label'] for r in labels['labels']}
    tracked=[Path(__file__),summary_path,review_path,manifest,label_path,
        ROOT/'data/manifests/training_source60_variants_v1/pair_dispositions.json',
        ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json',ROOT/'scripts/72_audit_brightness_features.py',
        ROOT/'data/manifests/development_exposure_additions.jsonl',ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
        ROOT/config.SELFIE_SEGMENTER_MODEL_PATH]
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    tracked += list((parent/'images').glob('*.png'))
    regression_paths={ident:ROOT/config.DATA_RAW/'FairFace'/ident.split('__',1)[1] for ident in {p['image_id'] for p in points}}
    old=ROOT/'outputs/ycrcb_estimation_ablation_v1';correction=ROOT/'outputs/additions_only_boundary_v1'
    for ident in regression_paths:
        tracked.append(regression_paths[ident])
        for variant in ['clean','global_color_shift']:
            stem=ident.replace('/','_')+'_'+variant
            tracked += [old/(stem+'_baseline_estimate.png'),correction/(stem+'_support.png')]
    hashes={str(p):digest(p) for p in tracked}
    output.mkdir();(output/'masks').mkdir();(output/'review_boards').mkdir()
    policy=dict(status='Fixed before execution; development masks only',rule='existing mask AND category in{body-skin2,face-skin3}; remove0background,1hair,4clothes,5others',
        generation='Categories from clean source only; intersect existing hair-clean source generation mask.',
        measurement_and_correction='Categories from each actual distorted input; same veto intersects existing baseline estimation and existing guarded correction support.',
        safeguards='Removal only; no expansion, no morphology/threshold tuning, no reference or manual witness region enters the veto.',
        scope='Compare all75 saved attempts including rejected/clipped/uncertain; do not promote failures. Existing inputs were generated with OLD masks, so this is not an end-to-end regenerated dataset.',
        limitations='Semantic predictions are not ground truth or paint classifier; retaining body-skin is not same-person neck localization. Existing material/paint protection retained by removal-only intersection.')
    (output/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    brightness=importlib.import_module('72_audit_brightness_features')
    segmenter=SelfieMaterialSegmenter(model);sources={};records=[];boards={};observations=[]
    try:
        for source in summary['sources']:
            ident=Path(source['image_id']).stem
            image=cv2.imread(str(parent/'images'/(ident+'_reference.png')))
            original=cv2.imread(str(parent/'images'/(ident+'_generation.png')),0)>0
            categories=segmenter.categories_bgr(image);candidate=veto(original,categories)
            sources[ident]=(original,candidate)
            cv2.imwrite(str(output/'masks'/(ident+'_generation.png')),candidate.astype(np.uint8)*255)
            cv2.imwrite(str(output/'masks'/(ident+'_source_categories.png')),categories)
            boards[ident]=[np.hstack([panel(image,original,'Source generation: original'),panel(image,candidate,'Source generation: candidate')])]
        for attempt in summary['attempts']:
            ident=Path(attempt['image_id']).stem;stem=ident+'_'+attempt['variant']
            image=cv2.imread(str(parent/'images'/(stem+'_input.png')))
            categories=segmenter.categories_bgr(image)
            masks={name:cv2.imread(str(parent/'images'/(stem+suffix)),0)>0 for name,suffix in [('measurement','_baseline_estimate.png'),('correction','_support.png')]}
            candidate={name:veto(mask,categories) for name,mask in masks.items()}
            for name,mask in candidate.items():cv2.imwrite(str(output/'masks'/(stem+'_'+name+'.png')),mask.astype(np.uint8)*255)
            cv2.imwrite(str(output/'masks'/(stem+'_categories.png')),categories)
            generation,new_generation=sources[ident]
            stats=compute_masked_lab_statistics(image,candidate['measurement'].astype(np.uint8)*255,1000)
            features=brightness.brightness_features(image,candidate['measurement'])
            record=dict(pair_id=stem,image_id=attempt['image_id'],variant=attempt['variant'],human_decision=review[stem]['human_decision'],
                prior_status=review[stem]['status'],clipped_pixels=attempt['clipped_pixels'],
                masks={name:dict(before=int(mask.sum()),after=int(candidate[name].sum()),retained_fraction=float(candidate[name].sum()/mask.sum())) for name,mask in masks.items()},
                generation=dict(before=int(generation.sum()),after=int(new_generation.sum())),
                baseline_statistics=attempt['estimators']['baseline'],candidate_statistics=stats,candidate_brightness=features,
                retention_original_denominator=support_retention(generation,candidate['measurement'],candidate['correction']),
                retention_candidate_denominator=support_retention(new_generation,candidate['measurement'],candidate['correction']) if new_generation.any() else None,
                training_eligible=False)
            records.append(record)
            boards[ident].append(np.hstack([panel(image,masks['measurement'],attempt['variant']+' original measure'),panel(image,candidate['measurement'],'Candidate measure')]))
            boards[ident].append(np.hstack([panel(image,masks['correction'],'Original correction'),panel(image,candidate['correction'],'Candidate correction')]))
        for ident,strips in boards.items():
            # Two pages preserve legibility for all five variants and source mask.
            for n,chunk in enumerate([strips[:5],strips[5:]],1):cv2.imwrite(str(output/'review_boards'/f'{ident}_page{n}.png'),np.vstack(chunk))
        # Reuse original224 points on clean/global-shift images, never resized labels.
        for ident,path in sorted(regression_paths.items()):
            clean=cv2.imread(str(path));clean_categories=segmenter.categories_bgr(clean)
            clean_stem=ident.replace('/','_')+'_clean'
            clean_mask=cv2.imread(str(old/(clean_stem+'_baseline_estimate.png')),0)>0
            generation=clean_mask&(clean_categories!=1);new_generation=veto(generation,clean_categories)
            for variant in ['clean','global_color_shift']:
                image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                cats=clean_categories if variant=='clean' else segmenter.categories_bgr(image)
                stem=ident.replace('/','_')+'_'+variant
                measure=cv2.imread(str(old/(stem+'_baseline_estimate.png')),0)>0
                support=cv2.imread(str(correction/(stem+'_support.png')),0)>0
                stages={'generation':(generation,new_generation),'measurement':(measure,veto(measure,cats)),'correction':(support,veto(support,cats))}
                for point in [p for p in points if p['image_id']==ident]:
                    assert image.shape[:2]==(point['height'],point['width'])
                    px,py=point['x'],point['y']
                    observations.append(dict(point_id=point['point_id'],variant=variant,label=label_map[point['point_id']],
                        stages={k:dict(before=bool(a[py,px]),after=bool(b[py,px])) for k,(a,b) in stages.items()}))
        assert len(records)==75 and len(observations)==48
        assert hashes=={p:digest(p) for p in hashes}
        regression={v:{stage:{label:dict(total=sum(p['variant']==v and p['label']==label for p in observations),
            before=sum(p['variant']==v and p['label']==label and p['stages'][stage]['before'] for p in observations),
            after=sum(p['variant']==v and p['label']==label and p['stages'][stage]['after'] for p in observations))
            for label in sorted(set(label_map.values()))} for stage in ['generation','measurement','correction']} for v in ['clean','global_color_shift']}
        report=dict(status='complete_no_regeneration_or_fitting',policy=policy,pairs=records,regression=regression,point_observations=observations,input_sha256=hashes,
            candidate_feature_available=sum(r['candidate_statistics']['valid'] and r['candidate_brightness']['valid'] for r in records),
            original_denominator_pass=sum(r['retention_original_denominator']['screen_pass'] for r in records),
            candidate_denominator_pass=sum(r['retention_candidate_denominator'] is not None and r['retention_candidate_denominator']['screen_pass'] for r in records))
        (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        (output/'review-index.md').write_text('# Non-skin veto experiment\n\nSame saved inputs; mask comparisons only, no new training examples. Left original, right candidate.\n\n'+'\n'.join(f'- [{ident}, page{n}](review_boards/{ident}_page{n}.png)' for ident in boards for n in [1,2]),encoding='utf-8')
        print(json.dumps(dict(feature_available=report['candidate_feature_available'],original_denominator_pass=report['original_denominator_pass'],candidate_denominator_pass=report['candidate_denominator_pass'],regression=regression),indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
