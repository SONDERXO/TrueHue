"""Extend the existing registry using only the newly accepted exact cases."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters,transform_rgb


def main():
    base=ROOT/get_config().OUTPUTS_ROOT;out=base/'reviewed_source_evidence32_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    parent=base/'reviewed_source_evidence29_v1';old=read(parent/'registry.json')
    pv=read(parent/'verification.json');assert digest(parent/'registry.json')==pv['evidence_sha256']['registry.json']
    imported=base/'broader_source_reference_review4_import_v1';iv=read(imported/'verification.json')
    for name,sha in iv['evidence_sha256'].items():assert digest(imported/name)==sha
    reviews=read(imported/'reconciled_reviews.json')
    approved=[r for r in reviews if r['reference_judgments_accepted'] and r['displayed_stress_mask_accepted']]
    held=[r for r in reviews if r not in approved]
    assert {r['source_id'] for r in approved}=={'63509','42965','77101'}
    assert {r['source_id'] for r in held}=={'58800'}
    manifest=read(base/'correction_data_redesign_v1/selection.json');policy=read(base/'correction_data_redesign_v1/access_policy.json')
    attempts_path=base/'correction_training_preparation_v1/attempts.jsonl'
    hashes[attempts_path.relative_to(ROOT).as_posix()]=digest(attempts_path)
    attempts={r['image_id']:r for r in map(json.loads,attempts_path.read_text().splitlines())}
    _,identity=contract(ROOT);assert identity==old['measurement_contract_sha256']
    lookup_path=base/'mst_monotone_square256_v1/development_lookup.json'
    assert digest(lookup_path)==old['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(lookup_path),identity)
    existing={r['source_image_id'] for r in old['rows']}
    assert not existing & {r['image_id'] for r in approved}
    out.mkdir();new=[];checks=[]
    for source in approved:
        training_candidate(source['image_id'],manifest,policy)
        a=attempts[source['image_id']];sid=source['source_id'];decoded={}
        assert a['status']=='pending_review' and a['target_fit']['status']=='available_approximate_target'
        folder=base/'correction_training_preparation_v1/images'
        for suffix in ['reference.png','reference_mask.png','input.png','input_mask.png']:
            p=folder/f'{sid}_{suffix}';relative=p.relative_to(ROOT).as_posix()
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=source['image_id'],role='train',file=relative,
                    phase='accepted_four_source_review_feature_assembly',raw_source_opened=False))+'\n')
            assert digest(p)==source['exact_image_and_mask_sha256'][relative];hashes[relative]=digest(p)
            decoded[suffix]=cv2.imread(str(p),cv2.IMREAD_GRAYSCALE if 'mask' in suffix else cv2.IMREAD_COLOR)
            assert decoded[suffix] is not None
        for variant,image_key,mask_key,saved in [('identity','reference.png','reference_mask.png',a['identity_features']),('saved_composite_stress','input.png','input_mask.png',a['input_features'])]:
            image=decoded[image_key];mask=decoded[mask_key]>0
            stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
            features={name:float(stats[key]) for name,key in zip(FEATURES,FEATURE_KEYS)}
            features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1;assert features==saved
            endpoints=facial_endpoint_features(image,mask);assert endpoints['valid'];features.update(endpoints['features'])
            target=[1.,1.,1.]
            if variant!='identity':
                legacy=a['target_fit']['parameters'];converted=legacy_to_paper_parameters(*legacy)
                target=[converted['gamma'],converted['red_gain'],converted['blue_gain']]
                rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255
                direct=transform_rgb(rgb,*target);reciprocal=np.clip(np.power(rgb,1/legacy[0])*[legacy[1],1.,legacy[2]],0,1)
                assert np.array_equal(direct,reciprocal)
                checks.append(dict(source_id=sid,legacy_parameters=legacy,direct_parameters=target,maximum_curve_difference=0.))
            ip=folder/f'{sid}_{image_key}';mp=folder/f'{sid}_{mask_key}'
            new.append(dict(pair_id=sid+'__reviewed_'+variant,source_image_id=source['image_id'],
                duplicate_group_id=source['duplicate_group'],evidence_origin='exact_four_source_review',
                stratum='original_control' if variant=='identity' else 'clipped_stress',
                features=[features[k] for k in old['features']],target_direct_gamma_red_blue=target,
                target_semantics='identity' if variant=='identity' else 'saved_approximate_RGB_fit_reciprocal_gamma_converted',
                clipping_fraction=0 if variant=='identity' else a['clipping_fraction'],
                input_path=ip.relative_to(ROOT).as_posix(),input_mask_path=mp.relative_to(ROOT).as_posix(),
                input_sha256=digest(ip),input_mask_sha256=digest(mp),exact_user_judgments=source['judgments'],new_fitting_admitted=False))
    rows=old['rows']+new
    assert len(rows)==len({r['pair_id'] for r in rows})==len({r['input_sha256'] for r in rows})==117
    assert len({r['source_image_id'] for r in rows})==32
    registry=dict(old,rows=rows,new_source_count=6,new_original_controls=6,new_clipped_stress_cases=6,
        new_primary_cases=0,new_fits_authorized=False,excluded_reviewed_sources=held,
        limitations=['All32sources are development-exposed; not a final test.',
            'All six additional saved distortions remain clipped stress; new-source primary data are missing.',
            'No distinct-person or validated dark-tone coverage claim.',
            'Old26fold trees cannot be reused as matched32source folds.'])
    for p in [Path(__file__),ROOT/'src/model_training/facial_endpoint_features.py',ROOT/'src/distortion_generation/paper_gamma.py']:
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    for name,value in [('registry.json',registry),('new_reviewed_rows.json',new),('operator_checks.json',checks),('excluded_reviews.json',held)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    result=dict(status='pass',reused_without_replay=111,new_feature_vectors=6,registry_cases=117,source_groups=32,
        strata=dict(Counter(r['stratum'] for r in rows)),excluded_source_ids=['58800'],
        direct_gamma_conversion_checks=3,new_fitting_admissions=0,model_fits=0,optimizer_fits=0,
        variants_generated=0,raw_source_decodes=0,reserved_pixel_access=0,input_sha256=hashes,
        evidence_sha256={p.name:digest(p) for p in out.iterdir()})
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['input_sha256','evidence_sha256']},indent=2))


if __name__=='__main__':main()
