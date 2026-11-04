"""Preserve exact completed mask review and check six accepted pair additions."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.data_preparation.redesign_access import training_candidate
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS


def main():
    parent=ROOT/'outputs/distorted_mask_review11_v1';out=ROOT/'outputs/distorted_mask_review11_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=read(parent/'manifest.json');export=parent/'truehue_distorted_mask_review11_decisions.json';review=read(export)
    assert review['schema_version']=='truehue_distorted_mask_review11_v1'
    assert review['manifest_sha256']==sha(parent/'manifest.json')
    assert review['review_scope']=='exact_original_rule_distorted_input_mask_only'
    for path,digest in read(parent/'verification.json')['evidence_sha256'].items():assert sha(parent/path)==digest
    assert set(review['reviews'])=={r['image_id'] for r in manifest['rows']}
    prepared=ROOT/'outputs/correction_training_preparation_v1';hashes=read(prepared/'verification.json')['evidence_sha256']
    sources={r['image_id']:r for r in map(json.loads,(prepared/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    prior=read(ROOT/'outputs/accepted_clean_control_comparison_v1/plan.json')
    controls={r['source_image_id']:r for r in prior['rows'] if r['cohort']=='new_clean'}
    allocation=ROOT/'outputs/correction_data_redesign_v1'
    dispositions={r['image_id']:r for r in read(ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json')}
    _,identity=contract(ROOT);assert identity==manifest['measurement_contract_sha256']==prior['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    reconciled=[];added=[]
    for item in manifest['rows']:
        image_id=item['image_id'];entry=review['reviews'][image_id]
        assert entry['decision'] in ('accept','reject','uncertain') and isinstance(entry['notes'],str)
        reconciled.append(dict(image_id=image_id,source_id=item['source_id'],**entry,review_scope=review['review_scope']))
        if entry['decision']!='accept':continue
        training_candidate(image_id,read(allocation/'selection.json'),read(allocation/'access_policy.json'))
        assert dispositions[image_id]['status']=='screen_clear_unreviewed'
        original=sources[image_id];name=original['source_id'];control=controls[image_id]
        assert original['input_measurement']['status']=='success' and original['target_fit']['status']=='available_approximate_target'
        assert original['reference_measurement']['status']=='success' and original['duplicate_group_id']==control['duplicate_group_id']
        paths={k:f'images/{name}_{k}.png' for k in ('input','input_mask','reference','reference_mask')}
        for path in paths.values():assert sha(prepared/path)==hashes[path]
        assert sha(prepared/paths['input'])==item['input_sha256'] and sha(prepared/paths['input_mask'])==item['input_mask_sha256']
        image=cv2.imread(str(prepared/paths['input']));mask=cv2.imread(str(prepared/paths['input_mask']),0)
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features==original['input_features']
        target=original['target_fit']['parameters'];assert np.isfinite(target).all() and min(target)>0
        added.append(dict(pair_id=name+'__reviewed_distorted',source_image_id=image_id,duplicate_group_id=control['duplicate_group_id'],
            variant='reviewed_distorted',cohort='new_distorted',partition='train',paper_target=[1/target[0],*target[1:]],
            **{k+'_path':str((prepared/v).relative_to(ROOT)) for k,v in paths.items()},
            input_sha256=item['input_sha256'],input_mask_sha256=item['input_mask_sha256'],
            measurement_contract_sha256=identity,mask_review='accept',exact_review_notes=entry['notes'],
            clipping_fraction=original['clipping_fraction'],target_fit=original['target_fit'],**features))
    assert len(added)==6 and sum(r['decision']=='reject' for r in reconciled)==5
    assert {r['pair_id'].split('__')[0] for r in added}==set('20648 56839 34227 85815 72400 34458'.split())
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    for name,value in [('reconciled_reviews.json',reconciled),('accepted_pairs.json',added)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',accepted=6,rejected=5,pending=0,
        accepted_with_notes=sum(bool(r['exact_review_notes']) for r in added),manifest_sha256=sha(parent/'manifest.json'),
        original_export_sha256=sha(export),source_role_and_feature_checks=True,
        measurement_contract_sha256=identity,active_demo_changed=False,
        evidence_sha256={p.name:sha(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print('Imported 6 accept / 5 reject; six exact distorted pairs pass technical admission, notes preserved.')


if __name__=='__main__':main()
