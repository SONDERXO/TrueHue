"""Independently verify fixed selection, exposure accounting and saved pairs."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.data_preparation.training_manifest import LABEL_TO_GROUP


def main():
    out=ROOT/'outputs/table2_source_expansion24_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');data=read(out/'summary.json')
    before=(out/'prior_exposure_snapshot.jsonl').read_bytes()
    assert hashlib.sha256(before).hexdigest()==plan['prior_exposure_sha256']
    ledger=(ROOT/'data/manifests/development_exposure_additions.jsonl').read_bytes()
    assert ledger.startswith(before) and hashlib.sha256(ledger).hexdigest()==data['exposure_sha256']
    additions=[json.loads(l) for l in ledger[len(before):].decode().splitlines() if l]
    assert len(additions)==24 and {r['image_id'] for r in additions}=={r['image_id'] for r in plan['selected']}
    exposed={json.loads(l)['image_id'] for l in before.decode().splitlines() if l}
    with (ROOT/'data/manifests/controlled_development_v1/source_audit.csv').open(encoding='utf-8-sig',newline='') as f:master=list(csv.DictReader(f))
    banned={r['duplicate_group_id'] for r in master if r['partition']!='train'}
    pool=[r for r in master if r['partition']=='train' and r['source_split']=='train'
        and r['source_suitability']=='hold_unreviewed_source' and r['processing_status']=='success'
        and r['known_pipeline_development_exposure']=='False' and r['original_visual_decision']=='pending'
        and r['controlled_source_decision']=='not_assessed_in_this_pass' and r['image_id'] not in exposed
        and r['duplicate_group_size']=='1' and r['duplicate_group_id'] not in banned]
    assert len(pool)==plan['pool_count']==170
    # Independent integer partition lengths instead of np.array_split.
    def chunks(items,n):
        q,remainder=divmod(len(items),n);start=0;result=[]
        for i in range(n):
            end=start+q+(i<remainder);result.append(items[start:end]);start=end
        return result
    ids=[]
    for light,group in enumerate(chunks(sorted(pool,key=lambda r:(float(r['mean_l_star']),r['image_id'])),3),1):
        for color,cell in enumerate(chunks(sorted(group,key=lambda r:(float(r['mean_b_star']),r['image_id'])),2),1):
            chosen=sorted(cell,key=lambda r:(hashlib.sha256(('table2_expansion24_seed42/'+r['image_id']).encode()).hexdigest(),r['image_id']))[:4]
            ids.extend((r['image_id'],f'L{light}_b{color}') for r in chosen)
    assert ids==[(r['image_id'],r['sampling_cell']) for r in plan['selected']]
    assert len(ids)==24 and len(set(i for i,c in ids))==24
    assert not {i for i,c in ids}&exposed
    assert len({r['duplicate_group_id'] for r in plan['selected']})==24
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert contract(ROOT)[1]==data['measurement_contract_sha256']
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),data['measurement_contract_sha256'])
    settings={'light':(.85,-20,5,-6,6),'medium':(.70,-35,8,-10,10),'dark':(.60,-45,10,-14,14)}
    counts=dict(references=0,distortions=0,valid_measurements=0,target_residuals=0)
    seen=set()
    for r in data['records']:
        name=r['source_id'];assert r['image_id'] in {i for i,c in ids}
        assert not r['training_eligible'] and r['user_decision']=='pending'
        source=Path(r['source_path']);assert digest(source)==r['source_sha256']
        original=cv2.imread(str(source));square=cv2.resize(original,(256,256),interpolation=cv2.INTER_LINEAR)
        saved=cv2.imread(str(out/'images'/(name+'_reference.png')))
        np.testing.assert_array_equal(square,saved)
        pixel_hash=hashlib.sha256(square.tobytes()).hexdigest()
        assert pixel_hash not in seen,'Unexpected exact decoded duplicate in selected sources'
        seen.add(pixel_hash);counts['references']+=1
        if r['reference_measurement']['status']!='success':continue
        mask=cv2.imread(str(out/'images'/(name+'_reference_mask.png')),0)
        def verify_measurement(image,mask,report):
            assert set(np.unique(mask))<={0,255}
            stats=compute_masked_lab_statistics(image,mask,1000)
            assert stats['valid'] and int(np.count_nonzero(mask))==report['skin_pixels']
            assert {k:stats[v] for k,v in zip(FEATURES,FEATURE_KEYS)}==report['features']
            counts['valid_measurements']+=1
        verify_measurement(saved,mask,r['reference_measurement'])
        label=lookup.label(r['reference_measurement']['features']['input_ita_degrees'])
        assert label==r['reference_mst_estimate'] and LABEL_TO_GROUP[label]==r['assigned_severity']
        support=mask>0;rgb=cv2.cvtColor(saved,cv2.COLOR_BGR2RGB)
        g,bri,con,red,blue=settings[r['assigned_severity']]
        raw=((rgb.astype(float)/255)**(1/g)-.5)*(1+con/100)+.5+bri/255+np.array([red,0,blue])/255
        generated=rgb.copy();generated[support]=np.rint(np.clip(raw[support],0,1)*255).astype(np.uint8)
        current=cv2.imread(str(out/'images'/(name+'_input.png')))
        np.testing.assert_array_equal(generated,cv2.cvtColor(current,cv2.COLOR_BGR2RGB))
        clipped=(raw<0)|(raw>1)
        assert r['clipping']['clipped_pixels']==int(clipped.any(axis=2)[support].sum())
        assert r['clipping']['clipped_channel_samples']==int(clipped[support].sum())
        counts['distortions']+=1
        if r['input_measurement']['status']!='success':continue
        im=cv2.imread(str(out/'images'/(name+'_input_mask.png')),0)
        verify_measurement(current,im,r['input_measurement'])
        assert r['input_features']['input_mst_index']==lookup.label(r['input_measurement']['features']['input_ita_degrees'])-1
        fit=r['target_fit']
        if fit['parameters'] is None:continue
        common=support&(im>0);x=generated[common].astype(float)/255;y=rgb[common].astype(float)/255
        gamma,red,blue=fit['parameters'];pred=np.clip(x**(1/gamma)*[red,1,blue],0,1)
        assert abs(float(np.sqrt(np.mean((pred-y)**2)))-fit['float_rgb_rmse'])<1e-12
        assert fit['selected_pixels']==int(common.sum());counts['target_residuals']+=1
    assert len(data['records'])==24
    target.write_text(json.dumps(dict(status='pass',counts=counts,selection_independently_reproduced=True,
        previous_exposure_bytes_preserved=True,exposure_records_added=24,duplicate_groups_separated=True,
        training_admitted=0,models_fitted=0,summary_sha256=digest(out/'summary.json'),
        review_sha256=digest(out/'review.html'),evidence_sha256={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(counts))


if __name__=='__main__':main()
