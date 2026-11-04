"""Prepare six approved saved cases; no generation, optimizer or tree fitting."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.facial_endpoint_features import facial_endpoint_features,ADDITIONS
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters,transform_rgb


def main():
    base=ROOT/get_config().OUTPUTS_ROOT
    out=base/'reviewed_source_evidence29_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    imported=base/'additional_source_reference_review3_import_v1'
    verify=read(imported/'verification.json')
    for name,sha in verify['evidence_sha256'].items():assert digest(imported/name)==sha
    approved=read(imported/'reconciled_reviews.json')
    historical=base/'reviewed_primary_comparison_v1'
    old_verify=read(historical/'verification.json')
    old=read(historical/'plan.json');old_features=read(historical/'features.json')
    for name in ['plan.json','features.json']:assert digest(historical/name)==old_verify['evidence_sha256'][name]
    manifest=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    attempts_path=base/'correction_training_preparation_v1/attempts.jsonl'
    hashes[attempts_path.relative_to(ROOT).as_posix()]=digest(attempts_path)
    attempts={r['image_id']:r for r in map(json.loads,attempts_path.read_text().splitlines())}
    _,identity=contract(ROOT)
    assert identity==old['measurement_contract_sha256']=='051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73'
    lookup_path=base/'mst_monotone_square256_v1/development_lookup.json'
    lookup=DevelopmentMonotoneLookup(read(lookup_path),identity)
    feature_names=list(FEATURES)+['input_mst_index']+list(ADDITIONS)
    assert feature_names==old['features']
    existing_sources={r['source_image_id'] for r in old['rows']}
    assert len(old['rows'])==105 and len(existing_sources)==26
    assert not existing_sources & {r['image_id'] for r in approved}
    rows=[]
    for r in old['rows']:
        rows.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],
            duplicate_group_id=r['duplicate_group_id'],evidence_origin='completed_primary_comparison',
            stratum='original_control' if r['variant']=='identity' else 'primary' if r['cohort']=='primary' else 'clipped_stress',
            features=old_features[r['pair_id']],target_direct_gamma_red_blue=r['paper_target'],
            input_path=r['input_path'],input_mask_path=r['input_mask_path'],
            input_sha256=r['input_sha256'],input_mask_sha256=r['input_mask_sha256'],
            previous_fit_membership_is_historical=True,new_fitting_admitted=False))
    out.mkdir();new=[];operator_checks=[]
    for source in approved:
        training_candidate(source['image_id'],manifest,policy)
        assert source['reference_judgments_accepted'] and source['displayed_stress_mask_accepted']
        a=attempts[source['image_id']];sid=source['source_id']
        assert a['status']=='pending_review' and a['target_fit']['status']=='available_approximate_target'
        folder=base/'correction_training_preparation_v1/images'
        decoded={}
        for suffix in ['reference.png','reference_mask.png','input.png','input_mask.png']:
            p=folder/f'{sid}_{suffix}';relative=p.relative_to(ROOT).as_posix()
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=source['image_id'],role='train',file=relative,
                    phase='approved_saved_case_feature_assembly',raw_source_opened=False))+'\n')
            assert digest(p)==source['exact_image_and_mask_sha256'][relative]
            hashes[relative]=digest(p)
            decoded[suffix]=cv2.imread(str(p),cv2.IMREAD_GRAYSCALE if 'mask' in suffix else cv2.IMREAD_COLOR)
            assert decoded[suffix] is not None
        for variant,image_key,mask_key,saved_features in [('identity','reference.png','reference_mask.png',a['identity_features']),('saved_composite_stress','input.png','input_mask.png',a['input_features'])]:
            image=decoded[image_key];mask=decoded[mask_key]>0
            statistics=compute_masked_lab_statistics(image,mask,1000);assert statistics['valid']
            f={name:float(statistics[key]) for name,key in zip(FEATURES,FEATURE_KEYS)}
            f['input_mst_index']=lookup.label(f['input_ita_degrees'])-1
            assert f==saved_features
            extra=facial_endpoint_features(image,mask);assert extra['valid'];f.update(extra['features'])
            assert set(f)==set(feature_names)
            if variant=='identity':target=[1.,1.,1.]
            else:
                legacy=a['target_fit']['parameters'];converted=legacy_to_paper_parameters(*legacy)
                target=[converted['gamma'],converted['red_gain'],converted['blue_gain']]
                rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255
                direct=transform_rgb(rgb,*target)
                reciprocal=np.clip(np.power(rgb,1/legacy[0])*[legacy[1],1.,legacy[2]],0,1)
                assert np.array_equal(direct,reciprocal)
                operator_checks.append(dict(source_id=sid,legacy_parameters=legacy,direct_parameters=target,
                    maximum_curve_difference=float(np.max(np.abs(direct-reciprocal)))))
            row=dict(pair_id=sid+'__reviewed_'+variant,source_image_id=source['image_id'],
                duplicate_group_id=source['duplicate_group'],evidence_origin='exact_three_source_review',
                stratum='original_control' if variant=='identity' else 'clipped_stress',
                features=[f[k] for k in feature_names],target_direct_gamma_red_blue=target,
                target_semantics='identity' if variant=='identity' else 'saved_approximate_RGB_fit_reciprocal_gamma_converted',
                clipping_fraction=0 if variant=='identity' else a['clipping_fraction'],
                input_path=(folder/f'{sid}_{image_key}').relative_to(ROOT).as_posix(),
                input_mask_path=(folder/f'{sid}_{mask_key}').relative_to(ROOT).as_posix(),
                input_sha256=digest(folder/f'{sid}_{image_key}'),input_mask_sha256=digest(folder/f'{sid}_{mask_key}'),
                exact_user_judgments=source['judgments'],new_fitting_admitted=False)
            new.append(row)
    rows.extend(new)
    assert len(rows)==111 and len({r['pair_id'] for r in rows})==111
    assert len({r['source_image_id'] for r in rows})==29
    assert len({r['input_sha256'] for r in rows})==111
    spec=dict(status='assembled_evidence_not_fitting_plan',features=feature_names,
        measurement_contract_sha256=identity,lookup_sha256=digest(lookup_path),
        mst_status='experimental_not_final_validated',rows=rows,
        new_source_count=3,new_original_controls=3,new_clipped_stress_cases=3,
        new_primary_cases=0,new_fits_authorized=False,
        limitations=['All29sources are development-exposed; this registry is not a final test.',
            'No new primary exposure or color examples; the three new distortions remain clipped stress.',
            'Old saved26fold trees cannot be treated as a matched baseline for new29source folds.',
            'Mask approvals retain background/holes concerns and are not calibrated skin-color truth.'])
    for p in [Path(__file__),ROOT/'src/model_training/facial_endpoint_features.py',ROOT/'src/distortion_generation/paper_gamma.py']:
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    for name,value in [('registry.json',spec),('new_reviewed_rows.json',new),('operator_checks.json',operator_checks)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    result=dict(status='pass',historical_rows_reused_without_replay=105,new_feature_vectors=6,
        distinct_sources=29,registry_cases=111,new_reference_controls=3,new_clipped_stress_cases=3,
        direct_gamma_conversion_checks=3,model_fits=0,optimizer_fits=0,variants_generated=0,
        raw_source_decodes=0,reserved_pixel_access=0,new_fitting_admissions=0,input_sha256=hashes,
        evidence_sha256={p.name:digest(p) for p in out.iterdir()})
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['input_sha256','evidence_sha256']},indent=2))


if __name__=='__main__':main()
