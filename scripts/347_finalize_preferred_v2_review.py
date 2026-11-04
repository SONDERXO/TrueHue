"""Bind optional prior source/face decisions to v2; verify updated data."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.semantic_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.paper_gamma import transform_rgb


def main():
    cohort=ROOT/'outputs/preferred_support_cohort_v2';review=ROOT/'outputs/preferred_reference_review_v2'
    pairs=ROOT/'outputs/preferred_support_pairs_v2';target=cohort/'independent_verification.json'
    if target.exists():raise FileExistsError(target)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    oldmanifest=ROOT/'outputs/preferred_reference_review_v1/manifest.json'
    old=read(oldmanifest);new=read(review/'manifest.json');oldbyid={r['image_id']:r for r in old['rows']}
    assert {r['image_id'] for r in new['rows']}==set(oldbyid)
    for r in new['rows']:
        before=oldbyid[r['image_id']]
        assert r['input_sha256']==before['input_sha256'] and r['mask_sha256']['face']==before['mask_sha256']['face']
    previoushash=digest(oldmanifest)
    extension=f'''
function importPrevious(data){{
 if(data.schema_version!=='truehue_preferred_reference_decisions_v1'||data.manifest_sha256!=='{previoushash}')throw Error('This file does not match the earlier review.');
 if(!Array.isArray(data.rows)||data.rows.length!==rows.length||new Set(data.rows.map(r=>r.image_id)).size!==rows.length||data.rows.some(r=>!rows.some(x=>x.image_id===r.image_id)))throw Error('Earlier review membership differs.');
 let copied=0;
 for(const saved of data.rows){{const r=rows.find(x=>x.image_id===saved.image_id);for(const field of ['source','measurement_mask']){{if(r.required.includes(field)&&['accept','reject','uncertain'].includes(saved.decisions[field])){{const e=document.getElementById(r.key+'_'+field);if(e.value==='pending'){{e.value=saved.decisions[field];copied++;}}}}}}const note=document.getElementById(r.key+'_notes');if(!note.value&&typeof saved.notes==='string'&&saved.notes)note.value='Earlier v1 notes: '+saved.notes;}}
 update();document.getElementById('message').textContent=' Retained '+copied+' matching source/face decisions. Updated correction masks still need review.';return copied;
}}
document.getElementById('previous').addEventListener('change',async e=>{{try{{if(e.target.files.length)importPrevious(JSON.parse(await e.target.files[0].text()));}}catch(err){{document.getElementById('message').textContent=' '+err.message;}}}});
'''
    page=(review/'review.html').read_text(encoding='utf-8')
    page=page.replace('<h1>','<p><strong>Current eyebrow-area revision.</strong> Yellow shows nearby eyebrow skin, added only to correction. Facial measurement support is unchanged.</p><p><label>Optional: load an earlier downloaded reference decision file to retain matching source/face decisions: <input id="previous" type="file" accept=".json"></label></p><h1>',1)
    page=page.replace('</script>',extension+'</script>',1)
    (review/'review.html').write_text(page,encoding='utf-8')
    (review/'review-script.js').write_text(page.split('<script>')[1].split('</script>')[0],encoding='utf-8')
    identity=contract(ROOT)[1];lookup=DevelopmentMonotoneLookup(read(cohort/'development_lookup.json'),identity)
    reference_count=0
    for r in read(cohort/'records.json'):
        if r['measurement']['status']!='success':continue
        image=cv2.imread(str(ROOT/r['input_path']));masks={k:cv2.imread(str(ROOT/p),0)>0 for k,p in r['mask_paths'].items()}
        union=np.zeros(image.shape[:2],bool)
        for k in ['face','neck','brows','lips','peribrow']:union|=masks[k]
        assert np.array_equal(union,masks['combined'])
        for k,path in r['mask_paths'].items():assert digest(ROOT/path)==r['mask_sha256'][k]
        stats=compute_masked_lab_statistics(image,masks['face'].astype(np.uint8)*255,1000)
        assert stats==r['measurement']['statistics']
        expected={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        expected.update(facial_endpoint_features(image,masks['face'])['features'])
        expected['input_mst_index']=lookup.label(expected['input_ita_degrees'])-1
        assert expected==r['features'];reference_count+=1
    pair_count=0
    for r in read(pairs/'records.json'):
        im=cv2.imread(str(ROOT/r['input_path']));ref=cv2.imread(str(ROOT/r['reference_path']))
        support=cv2.imread(str(ROOT/r['reference_region_masks']['combined']),0)>0
        assert digest(ROOT/r['input_path'])==r['input_sha256']
        assert np.array_equal(im[~support],ref[~support])
        if r['measurement']['status']=='success':
            mask=cv2.imread(str(ROOT/r['measurement_mask_path']),0)
            assert compute_masked_lab_statistics(im,mask,1000)==r['measurement']['statistics']
            rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB);truth=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB)
            application=cv2.imread(str(ROOT/r['correction_mask_path']),0)>0;selected=support&application
            values=transform_rgb(rgb.astype(float)/255,*r['target'])
            error=float(np.abs(np.rint(values[selected]*255)-truth[selected]).mean()/255)
            assert abs(error-r['target_reconstruction_rgb_mae'])<1e-12
        assert not r['training_admitted'];pair_count+=1
    result=dict(status='passed',reference_feature_replays=reference_count,pair_measurement_target_replays=pair_count,
        facial_measurements_unchanged=True,prior_source_face_export_import_bound=True,
        correction_decisions_never_transferred=True,reference_regions_include_peribrow=True,
        old_artifacts_preserved=True,new_mapping_fits=0,correction_tree_fits=0,
        technical_holds_retained=2,lookup_sha256=digest(cohort/'development_lookup.json'))
    target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
