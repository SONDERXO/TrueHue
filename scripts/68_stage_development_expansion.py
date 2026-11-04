"""Stage nine proposed pairs alongside frozen22; no fitting or final admission."""
import csv
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
    config=get_config();version='controlled_expansion31_v1'
    output=ROOT/config.OUTPUTS_ROOT/version;tables=ROOT/'data/manifests'/version
    if output.exists() or tables.exists():raise FileExistsError('Staging outputs exist')
    old_path=ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv'
    prior=read(old_path);fields=list(prior[0])
    if len(prior)!=22:raise ValueError('Expected frozen22')
    source_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources={r['image_id']:r for r in read(source_path)}
    parent=ROOT/'outputs/candidate_variants_v1';policy_path=ROOT/'data/manifests/candidate_variants_v1/policy.json'
    audit_path=parent/'summary.json';audit=json.loads(audit_path.read_text());policy=json.loads(policy_path.read_text())
    disposition_path=policy_path.with_name('screen_disposition.json')
    dispositions={(r['image_id'],r['variant']):r for r in json.loads(disposition_path.read_text())['pairs']}
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
    exposure={json.loads(line)['image_id'] for line in ledger.read_text().splitlines() if line}
    proposed=[r for r in audit['attempts'] if Path(r['image_id']).stem in ['14272','84897'] and r['clipped_pixels']==0]
    assert len(proposed)==9 and len({r['image_id'] for r in proposed})==2
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
    hashes={str(p):digest(p) for p in tracked}
    additions=[];checks=[]
    for record in proposed:
        image_id=record['image_id'];source=sources[image_id];ident=Path(image_id).stem;stem=ident+'_'+record['variant']
        if source['partition']!='train' or source['source_split']!='train' or image_id not in exposure:raise ValueError('Allocation/exposure mismatch')
        if not record['estimators']['baseline']['valid'] or not record['estimators']['baseline']['retention']['screen_pass']:
            raise ValueError('Staging invalid or quality-held baseline features')
        assert dispositions[(image_id,record['variant'])]['status']=='screen_pass_pending_review'
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
            reference_path=reference_path.relative_to(ROOT).as_posix(),parent_pair_id='candidate_variants_v1/'+stem,
            historical_table_use='screen_pass_pending_review',image_width=256,image_height=256,
            intended_use='controlled_development_not_final_thesis',feature_source='saved_distorted_input_only',
            input_processing_status='success',input_exclusion_reason=stats['reason'],
            pair_status='staged_development_candidate_not_final_approval',table_use='train',
            development_selection='nine_proposed_expansion_pairs_pending_final_source_eligibility',
            correction_mask_path=support_path.relative_to(ROOT).as_posix(),parent_table=policy_path.relative_to(ROOT).as_posix())
        row.update(zip(FEATURES,[stats[k] for k in FEATURE_KEYS]));row.update(zip(TARGETS,[target[k] for k in ['gamma','red_gain','blue_gain']]))
        additions.append(row);checks.append(dict(pair_id=row['pair_id'],source_image_id=image_id,original_human_decision=source['original_visual_decision'],
            final_training_ready=source['training_ready'],baseline_features_recomputed=True,clipped_pixels=0,
            caveat='14272facialhair/jaw/lighting or84897downwardpose/boundary caveats retained; development staging only'))
    combined=prior+additions
    assert len(combined)==len({r['pair_id'] for r in combined})==31
    assert len({r['source_image_id'] for r in combined})==8
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
    folds=source_group_folds(combined)
    assert len(folds)==8
    assert hashes=={p:digest(p) for p in hashes},'Prior artifacts changed'
    output.mkdir(parents=True);tables.mkdir(parents=True)
    write(tables/'staged_train.csv',combined,fields);write(tables/'proposed_additions.csv',additions,fields)
    # Preserve all20 screening attempts without disguising non-staged cases as missing data.
    provenance=[]
    selected_keys={(r['source_image_id'],r['variant']) for r in additions}
    for r in audit['attempts']:
        key=(r['image_id'],r['variant']);status='proposed_addition' if key in selected_keys else 'stress_only_not_staged' if r['clipped_pixels'] else 'held_not_staged'
        provenance.append(dict(image_id=r['image_id'],variant=r['variant'],staging_status=status,
            clipping=r['clipped_pixels'],diagnostic_screen_status=dispositions[key]['status'],
            original_attempt_file=str(audit_path.relative_to(ROOT))))
    (tables/'all_twenty_attempts.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    (tables/'source_group_folds.json').write_text(json.dumps(dict(status='plans_only_no_models_fitted',folds=folds),indent=2),encoding='utf-8')
    plan=dict(version='controlled_expansion31_v1',status='Staged development experiment, not final dataset/model approval',
        baseline='Frozen22rows copied as field values; new9recomputed baseline HSV/YCrCb features, not YCrCb feature substitution',
        methods=['no_correction','original22_controls_tree','expanded31_controls_tree'],
        next_comparison='For each of8sourcegroups, evaluate same held-source probes; baseline fits only remaining original22IDs, expanded fits remaining31IDs',
        settings=dict(max_depth=3,random_state=42,min_samples_leaf=1,target_scaling='none'),
        correction_mask='Existing additions-only boundary, fixed acrossmethods',
        exclusions='Original8held remain out;3705/39108 all variants not staged;39108/84897bright clipped cases stress-only; no externaldev/reservedtest',
        reports='Pair and equal-source means, shared22probes versus new9, unchanged/mild controls and everyvariant separately; no finalholdout claim',
        source_status='New sources originally humanpending,final training_readyFalse; record Codexscreen caveats. Stage only, no humanlabel changes.',
        neck='No neck support generation or evaluation; face-and-neck request remains separate')
    (tables/'comparison_plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    summary=dict(status='staged_not_fitted',original_pairs=22,proposed_pairs=9,combined_pairs=31,source_groups=8,
        variant_counts=dict(Counter(r['variant'] for r in combined)),new_source_checks=checks,
        all_twenty_attempt_counts=dict(Counter(r['staging_status'] for r in provenance)),
        duplicate_screen=dict(sources=8,threshold_hamming=4,candidate_links=links,identity_separation='unverified'),
        input_sha256=hashes,table_sha256={p.name:digest(p) for p in tables.iterdir() if p.is_file()},
        warning='No model fitting,source promotion in mastermanifest,production change or finalmethod claim.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    # Ensure existing row strings survive the new CSV unchanged.
    assert read(tables/'staged_train.csv')[:22]==prior
    (output/'review-index.md').write_text('# Proposed31-pair development stage\n\nNo fitting. Existing22unchanged; proposed14272five and84897fourunclipped.\n\n- [14272variant evidence](../candidate_variants_v1/14272_variants.png)\n- [84897variant evidence](../candidate_variants_v1/84897_variants.png)\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['status','original_pairs','proposed_pairs','combined_pairs','source_groups','variant_counts','all_twenty_attempt_counts']}))


if __name__=='__main__':main()
