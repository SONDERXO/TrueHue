"""Stage eight proposed pairs alongside frozen31; no fitting or final admission."""
import csv
import importlib
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS
from src.data_preparation.source_group_folds import source_group_folds
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.distortion_generation.generate_distortions import inverse_parameters,transform_rgb,TRANSFORM_VERSION


def read(path):
    with Path(path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,rows,fields):
    with path.open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)


def main():
    config=get_config();version='controlled_expansion39_v1'
    output=ROOT/config.OUTPUTS_ROOT/version;tables=ROOT/'data/manifests'/version
    if output.exists() or tables.exists():raise FileExistsError('Staging outputs exist')
    old_path=ROOT/'data/manifests/controlled_expansion31_v1/staged_train.csv'
    prior=read(old_path);fields=list(prior[0])
    if len(prior)!=31:raise ValueError('Expected frozen31')
    source_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources={r['image_id']:r for r in read(source_path)}
    parent=ROOT/'outputs/brightness_color_variants_v1';policy_path=ROOT/'data/manifests/brightness_color_variants_v1/policy.json'
    audit_path=parent/'summary.json';audit=json.loads(audit_path.read_text());policy=json.loads(policy_path.read_text())
    disposition_path=policy_path.with_name('screen_disposition.json')
    dispositions={(r['image_id'],r['variant']):r for r in json.loads(disposition_path.read_text())['pairs']}
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
    exposure={json.loads(line)['image_id'] for line in ledger.read_text().splitlines() if line}
    proposed=[r for r in audit['attempts'] if dispositions[(r['image_id'],r['variant'])]['status']=='proposed_for_separate_staging']
    assert len(proposed)==8 and len({r['image_id'] for r in proposed})==2
    tracked=[Path(__file__),old_path,source_path,audit_path,policy_path,disposition_path,ledger,
             ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/'src/data_preparation/source_group_folds.py',ROOT/'src/ita_estimation/compute_ita.py',
             ROOT/'src/data_preparation/controlled_training_table.py',ROOT/'src/distortion_generation/generate_distortions.py']
    tracked+=list((ROOT/'data/manifests/square_mask_quality_v1').glob('*.csv'))
    for row in prior:tracked += [ROOT/row[key] for key in ['input_path','generation_mask_path','reference_path','correction_mask_path']]
    for row in audit['attempts']:
        ident=Path(row['image_id']).stem;stem=ident+'_'+row['variant']
        tracked += [parent/'images'/(stem+suffix) for suffix in ['_input.png','_baseline_estimate.png','_support.png']]
        tracked += [parent/'images'/(ident+suffix) for suffix in ['_reference.png','_generation.png']]
    sys.path.insert(0,str(ROOT/'scripts'))
    brightness=importlib.import_module('72_audit_brightness_features')
    schema_path=ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json'
    feature_path=schema_path.with_name('input_features.csv')
    mask_audit_path=schema_path.with_name('summary.json')
    schema=json.loads(schema_path.read_text())
    old_features=read(feature_path)
    old_masks={r['pair_id']:r['estimation_mask_path'] for r in json.loads(mask_audit_path.read_text())['records']}
    assert len(old_features)==31 and {r['pair_id'] for r in old_features}=={r['pair_id'] for r in prior}
    tracked += [schema_path,feature_path,mask_audit_path,ROOT/'scripts/72_audit_brightness_features.py']+[ROOT/p for p in old_masks.values()]
    hashes={str(p):digest(p) for p in tracked}
    additions=[];checks=[]
    for record in proposed:
        image_id=record['image_id'];source=sources[image_id];ident=Path(image_id).stem;stem=ident+'_'+record['variant']
        if source['partition']!='train' or source['source_split']!='train' or image_id not in exposure:raise ValueError('Allocation/exposure mismatch')
        if not record['estimators']['baseline']['valid'] or not record['estimators']['baseline']['retention']['screen_pass']:
            raise ValueError('Staging invalid or quality-held baseline features')
        assert dispositions[(image_id,record['variant'])]['status']=='proposed_for_separate_staging'
        input_path=parent/'images'/(stem+'_input.png');estimate_path=parent/'images'/(stem+'_baseline_estimate.png')
        generation_path=parent/'images'/(ident+'_generation.png');reference_path=parent/'images'/(ident+'_reference.png')
        support_path=parent/'images'/(stem+'_support.png')
        bgr=cv2.imread(str(input_path));estimate=cv2.imread(str(estimate_path),0)
        stats=compute_masked_lab_statistics(bgr,estimate,1000)
        assert stats=={key:record['estimators']['baseline'][key] for key in stats}
        assert bgr.shape==(256,256,3) and stats['valid']
        reference=cv2.cvtColor(cv2.imread(str(reference_path)),cv2.COLOR_BGR2RGB)
        generation=cv2.imread(str(generation_path),0)>0
        parameters=policy['variants'][record['variant']];target=inverse_parameters(**parameters)
        raw=transform_rgb(reference.astype(float)/255,**parameters,clip=False)
        clipping=int((generation&((raw<0)|(raw>1)).any(axis=2)).sum());assert clipping==record['clipped_pixels']==0
        generated=reference.astype(float)/255;generated[generation]=np.clip(raw[generation],0,1)
        np.testing.assert_array_equal(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB),np.rint(generated*255).astype(np.uint8))
        row=dict.fromkeys(fields,'')
        row.update(pair_id='square256__'+image_id.replace('/','_')+'__'+record['variant'],
            source_image_id=image_id,source_path=source['image_path'],source_split=source['source_split'],partition=source['partition'],
            duplicate_group_id=source['duplicate_group_id'],variant=record['variant'],mask_version='v2_complete_mouth_v1',
            transform_version=TRANSFORM_VERSION,policy_version='hair_clean_generation_v1',
            **{'distortion_'+key:value for key,value in parameters.items()},clipped_pixel_count=0,generation_skin_pixels=int(generation.sum()),
            input_path=input_path.relative_to(ROOT).as_posix(),generation_mask_path=generation_path.relative_to(ROOT).as_posix(),
            reference_path=reference_path.relative_to(ROOT).as_posix(),parent_pair_id='brightness_color_variants_v1/'+stem,
            historical_table_use='screen_pass_pending_review',image_width=256,image_height=256,
            intended_use='controlled_development_not_final_thesis',feature_source='saved_distorted_input_only',
            input_processing_status='success',input_exclusion_reason=stats['reason'],
            pair_status='staged_development_candidate_not_final_approval',table_use='train',
            development_selection='eight_proposed_expansion_pairs_pending_final_source_eligibility',
            correction_mask_path=support_path.relative_to(ROOT).as_posix(),parent_table=policy_path.relative_to(ROOT).as_posix())
        row.update(zip(FEATURES,[stats[k] for k in FEATURE_KEYS]));row.update(zip(TARGETS,[target[k] for k in ['gamma','red_gain','blue_gain']]))
        additions.append(row);checks.append(dict(pair_id=row['pair_id'],source_image_id=image_id,original_human_decision=source['original_visual_decision'],
            final_training_ready=source['training_ready'],baseline_features_recomputed=True,clipped_pixels=0,
            caveat='6356temple/side-lighting or62676pose/jaw boundary caveats retained; development staging only'))
    combined=prior+additions
    assert len(combined)==len({r['pair_id'] for r in combined})==39
    assert len({r['source_image_id'] for r in combined})==10
    assert all(r['partition']=='train' and r['table_use']=='train' and int(r['clipped_pixel_count'])==0 for r in combined)
    # Source-level duplicate recheck; no identity inference or reallocation.
    fingerprints=[]
    for image_id in sorted({r['source_image_id'] for r in combined}):
        path=Path(next(r['source_path'] for r in combined if r['source_image_id']==image_id));image=cv2.imread(str(path))
        exact=hashlib.sha256(str(image.shape).encode()+image.tobytes()).hexdigest()
        thumb=cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),(9,8),interpolation=cv2.INTER_AREA)
        bits=(thumb[:,1:]>thumb[:,:-1]).ravel();dhash=sum(int(bit)<<i for i,bit in enumerate(bits))
        fingerprints.append(dict(image_id=image_id,decoded_sha256=exact,dhash64=dhash))
    links=[]
    for a,b in combinations(fingerprints,2):
        distance=(a['dhash64']^b['dhash64']).bit_count()
        if a['decoded_sha256']==b['decoded_sha256'] or distance<=4:links.append(dict(a=a['image_id'],b=b['image_id'],distance=distance))
    if links:raise ValueError('New duplicate candidates require explicit grouping review: '+str(links))
    feature_rows=[]
    old_features_by_id={r['pair_id']:r for r in old_features}
    for row in combined:
        pair=row['pair_id']
        mask_path=ROOT/old_masks[pair] if pair in old_masks else ROOT/row['input_path'].replace('_input.png','_baseline_estimate.png')
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(mask_path),0)>0
        stats=compute_masked_lab_statistics(image,mask.astype(np.uint8)*255,1000)
        np.testing.assert_array_equal([float(row[k]) for k in FEATURES],[stats[k] for k in FEATURE_KEYS])
        measured=brightness.brightness_features(image,mask);assert measured['valid']
        f=dict(pair_id=pair,available=True,**{k:row[k] for k in FEATURES},**measured['features'])
        if pair in old_features_by_id:
            np.testing.assert_array_equal([float(f[k]) for k in schema['proposed_features']],[float(old_features_by_id[pair][k]) for k in schema['proposed_features']])
        feature_rows.append(f)
    folds=source_group_folds(combined)
    assert len(folds)==10
    assert hashes=={p:digest(p) for p in hashes},'Prior artifacts changed'
    output.mkdir(parents=True);tables.mkdir(parents=True)
    write(tables/'staged_train.csv',combined,fields);write(tables/'proposed_additions.csv',additions,fields)
    write(tables/'input_features.csv',feature_rows,list(feature_rows[0]))
    (tables/'feature_schema.json').write_bytes(schema_path.read_bytes())
    # Preserve all10 screening attempts without disguising non-staged cases as missing data.
    provenance=[]
    selected_keys={(r['source_image_id'],r['variant']) for r in additions}
    for r in audit['attempts']:
        key=(r['image_id'],r['variant']);status='proposed_addition' if key in selected_keys else 'stress_only_not_staged' if r['clipped_pixels'] else 'held_not_staged'
        provenance.append(dict(image_id=r['image_id'],variant=r['variant'],staging_status=status,
            clipping=r['clipped_pixels'],diagnostic_screen_status=dispositions[key]['status'],
            original_attempt_file=str(audit_path.relative_to(ROOT))))
    (tables/'all_ten_attempts.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    (tables/'source_group_folds.json').write_text(json.dumps(dict(status='plans_only_no_models_fitted',folds=folds),indent=2),encoding='utf-8')
    plan=dict(version='controlled_expansion39_v1',status='Staged development experiment, not final dataset/model approval',
        baseline='Frozen31 row values preserved;39 input-only ten-feature vectors recomputed from baseline masks with frozen schema',
        methods=['no_correction','original31_brightness_tree','expanded39_brightness_tree'],
        next_comparison='For each of10sourcegroups, evaluate same39 held-source probes; baseline fits only remaining original31IDs, expanded fits remaining39IDs; frozen10features',
        settings=dict(max_depth=3,random_state=42,min_samples_leaf=1,target_scaling='none'),
        correction_mask='Existing additions-only boundary, fixed acrossmethods',
        exclusions='All previous holds remain out;6356dark/color held; no externaldev/reservedtest',
        reports='Pair and equal-source means, shared31probes versus new8, unchanged/mild controls and everyvariant separately; no finalholdout claim',
        source_status='New sources originally humanpending,final training_readyFalse; record Codexscreen caveats. Stage only, no humanlabel changes.',
        neck='No neck support generation or evaluation; face-and-neck request remains separate')
    (tables/'comparison_plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    summary=dict(status='staged_not_fitted',original_pairs=31,proposed_pairs=8,combined_pairs=39,source_groups=10,
        variant_counts=dict(Counter(r['variant'] for r in combined)),new_source_checks=checks,
        all_ten_attempt_counts=dict(Counter(r['staging_status'] for r in provenance)),
        duplicate_screen=dict(sources=10,threshold_hamming=4,candidate_links=links,identity_separation='unverified'),
        input_sha256=hashes,table_sha256={p.name:digest(p) for p in tables.iterdir() if p.is_file()},
        warning='No model fitting,source promotion in mastermanifest,production change or finalmethod claim.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    # Ensure existing row strings survive the new CSV unchanged.
    assert read(tables/'staged_train.csv')[:31]==prior
    (output/'review-index.md').write_text('# Proposed39-pair stage\n\nNo fitting. Existing31 preserved;8proposals.\n\n- [6356](../brightness_color_variants_v1/6356_variants.png)\n- [62676](../brightness_color_variants_v1/62676_variants.png)\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['status','original_pairs','proposed_pairs','combined_pairs','source_groups','variant_counts','all_ten_attempt_counts']}))


if __name__=='__main__':main()
