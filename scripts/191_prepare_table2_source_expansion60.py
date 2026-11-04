"""Freeze and process 60 new TRAIN development sources; no fitting or admission."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.training_manifest import LABEL_TO_GROUP
from src.distortion_generation.table2_composite import composite_rgb
from src.model_training.recovery_targets import fit_recovery_target

OUT=ROOT/'outputs/table2_source_expansion60_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    audit=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    with audit.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
    before=ledger.read_bytes();exposure=[json.loads(l) for l in before.decode('utf-8').splitlines() if l]
    exposed={r['image_id'] for r in exposure}
    forbidden_groups={r['duplicate_group_id'] for r in rows if r['partition']!='train'}
    pool=[r for r in rows if r['partition']=='train' and r['source_split']=='train'
        and r['source_suitability']=='hold_unreviewed_source' and r['processing_status']=='success'
        and r['known_pipeline_development_exposure']=='False' and r['original_visual_decision']=='pending'
        and r['controlled_source_decision']=='not_assessed_in_this_pass' and r['image_id'] not in exposed
        and r['duplicate_group_size']=='1' and r['duplicate_group_id'] not in forbidden_groups]
    assert len(pool)>=60 and len({r['image_id'] for r in pool})==len(pool)
    ordered=sorted(pool,key=lambda r:(float(r['mean_l_star']),r['image_id']))
    selected=[]
    for light,indices in enumerate(np.array_split(np.arange(len(ordered)),3),1):
        sub=sorted([ordered[int(i)] for i in indices],key=lambda r:(float(r['mean_b_star']),r['image_id']))
        for color,positions in enumerate(np.array_split(np.arange(len(sub)),2),1):
            cell=[sub[int(i)] for i in positions]
            assert len(cell)>=10
            chosen=sorted(cell,key=lambda r:(hashlib.sha256(('table2_expansion60_seed42/'+r['image_id']).encode()).hexdigest(),r['image_id']))[:10]
            selected.extend(dict(r,sampling_cell=f'L{light}_b{color}') for r in chosen)
    assert len(selected)==60 and len({r['duplicate_group_id'] for r in selected})==60
    config=get_config();spec,identity=contract(ROOT)
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==read(artifact.with_name('artifact_verification.json'))['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    paths=[Path(__file__),audit,artifact,ROOT/'docs/table2-source-expansion60-protocol.md',
        ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py',
        ROOT/'src/data_preparation/training_manifest.py',ROOT/'outputs/table2_reviewed_expansion_evaluation_v1/user_review.json']
    paths += [ROOT/p for p in spec['dependency_sha256']]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'boards').mkdir()
    (OUT/'prior_exposure_snapshot.jsonl').write_bytes(before)
    write(OUT/'plan.json',dict(status='frozen_before_image_reading',pool_count=len(pool),selected=selected,
        prior_exposure_sha256=hashlib.sha256(before).hexdigest(),planned_sources=60,planned_pairs=120,
        measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes,
        training_admitted=0,models_fitted=0))
    # Persist actual exposure BEFORE opening raw images; preserve earlier bytes.
    append=b'' if not before or before.endswith(b'\n') else b'\n'
    append+=''.join(json.dumps(dict(image_id=r['image_id'],partition='train',date='2026-10-28',
        reason='table2_source_expansion60_v1 fixed source/reference and MST-conditioned pair review',
        source_manifest='outputs/table2_source_expansion60_v1/plan.json'))+'\n' for r in selected).encode()
    with ledger.open('ab') as f:f.write(append)
    assert ledger.read_bytes()==before+append
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(im,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    def save(p,im):
        assert cv2.imwrite(str(p),im)
        assert np.array_equal(cv2.imread(str(p),cv2.IMREAD_UNCHANGED),im)
    def tile(im,label,mask=None):
        shown=im.copy()
        if mask is not None:
            m=mask>0;shown[m]=np.rint(.65*shown[m]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1)
        return shown
    records=[]
    try:
        for row in selected:
            name=Path(row['image_id']).stem;path=Path(row['image_path'])
            original_hash=digest(path)
            ref=measure(cv2.imread(str(path)),detector,masker)
            record=dict(source_id=name,image_id=row['image_id'],source_path=str(path),source_sha256=original_hash,
                partition='train',duplicate_group_id=row['duplicate_group_id'],sampling_cell=row['sampling_cell'],
                status='reference_failed',reference_measurement=ref.report,training_eligible=False,
                user_decision='pending',source_reference_suitability='pending',mask_scene_suitability='pending')
            panels=[]
            if ref.image is not None:
                save(OUT/'images'/(name+'_reference.png'),ref.image)
                panels=[tile(ref.image,name+' reference'),tile(ref.image,'Reference support',ref.mask)]
            if ref.mask is not None:save(OUT/'images'/(name+'_reference_mask.png'),ref.mask)
            if ref.report['status']=='success':
                label=lookup.label(ref.report['features']['input_ita_degrees']);group=LABEL_TO_GROUP[label]
                rgb=cv2.cvtColor(ref.image,cv2.COLOR_BGR2RGB);support=ref.mask>0
                transformed,_=composite_rgb(rgb,group);generated=rgb.copy();generated[support]=transformed[support]
                _,clipping=composite_rgb(rgb[support][:,None,:],group)
                bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR);current=measure(bgr,detector,masker)
                save(OUT/'images'/(name+'_input.png'),bgr)
                if current.mask is not None:save(OUT/'images'/(name+'_input_mask.png'),current.mask)
                record.update(status='distorted_failed',reference_mst_estimate=label,assigned_severity=group,
                    group_assignment_source='experimental_reference_ita_lookup',official_mst_label=None,
                    clipping=clipping,clipping_fraction=clipping['clipped_pixels']/int(support.sum()),input_measurement=current.report,
                    identity_features={**ref.report['features'],'input_mst_index':label-1})
                panels.extend([tile(bgr,group+' Table2 input'),tile(bgr,'Input support: '+current.report['status'],current.mask)])
                if current.report['status']=='success':
                    fit=fit_recovery_target(generated,rgb,current.mask>0,support)
                    record.update(target_fit=fit,input_features={**current.report['features'],
                        'input_mst_index':lookup.label(current.report['features']['input_ita_degrees'])-1},
                        reference_mask_retention=float(((current.mask>0)&support).sum()/support.sum()),
                        status='pending_review' if fit['parameters'] is not None else 'target_unavailable')
            assert digest(path)==original_hash
            if panels:save(OUT/'boards'/(name+'.png'),np.hstack(panels))
            records.append(record)
            with (OUT/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
            print(name,record['status'],record.get('assigned_severity',''),flush=True)
        assert hashes=={p:digest(ROOT/p) for p in hashes}
        assert ledger.read_bytes()==before+append
        from collections import Counter
        summary=dict(status='complete_pending_source_review',records=records,attempted_sources=60,
            statuses=dict(Counter(r['status'] for r in records)),severity_counts=dict(Counter(r.get('assigned_severity','unavailable') for r in records)),
            measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes,
            exposure_sha256=digest(ledger),exposure_records_added=60,models_fitted=0,training_admitted=0)
        write(OUT/'summary.json',summary)
        sections=[]
        for r in records:
            name=r['source_id'];severity=r.get('assigned_severity','unavailable');mst=r.get('reference_mst_estimate','unavailable')
            sections.append(f'<section><h2>{name} â€” {r["status"]}</h2><p>Experimental reference MST {mst}; {severity} severity. Clipped input-support fraction: {100*r.get("clipping_fraction",0):.1f}%.</p><img src="boards/{name}.png"></section>')
        (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>60-source expansion suitability</title><style>body{font:17px system-ui;margin:28px;background:#17191e;color:#eee}section{margin:30px 0;border-top:1px solid #777}img{max-width:100%}</style><h1>Fixed 60-source development expansion</h1><p>Review source/reference suitability and displayed processing: detail, major lighting/casts, cosmetics/occlusion, skin selection, hair/background/other-person inclusion. Green indicates selected support, not accuracy. Original photos are reconstruction references, not calibrated skin truth. No model predictions or fitting. Each successful reference supplies an unchanged control plus the displayed MST-conditioned distortion. Reply per source: accept / reject / uncertain, with concerns. Failures remain excluded; numerical success alone does not admit training.</p>'+''.join(sections),encoding='utf-8')
        print(json.dumps({k:summary[k] for k in ['statuses','severity_counts','training_admitted','models_fitted']},indent=2))
    except Exception as error:
        write(OUT/'failure.json',dict(error=str(error),completed=len(records)));raise


if __name__=='__main__':main()
