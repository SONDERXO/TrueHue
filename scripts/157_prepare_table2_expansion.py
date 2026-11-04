"""Fixed six-source processing, target verification and pending review."""
import base64
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

SOURCE_IDS=['40048','42532','63870','67583','83205','84364']


def main():
    out=ROOT/'outputs/table2_stress_expansion_v1'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    audit_path=ROOT/'outputs/core_source_readiness_v1/summary.json'
    audit=json.loads(audit_path.read_text());verification=json.loads(audit_path.with_name('verification.json').read_text())
    assert digest(audit_path)==verification['summary_sha256']
    master_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    assert digest(master_path)==audit['input_sha256'][master_path.relative_to(ROOT).as_posix()]
    prior_path=ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json'
    assert digest(prior_path)==audit['input_sha256'][prior_path.relative_to(ROOT).as_posix()]
    with master_path.open(encoding='utf-8-sig',newline='') as f:master={r['image_id']:r for r in csv.DictReader(f)}
    history={r['image_id']:r for r in audit['sources']}
    selected=[]
    for name in SOURCE_IDS:
        key=f'fairface__train/{name}.jpg';row=master[key];old=history[key]
        assert row['partition']=='train'
        # Master exposure predates the fixed60 review; later actual decisions,
        # not that stale boolean, establish historical exposure here.
        assert len(old['original_pair_decisions'])==5
        assert 'identity_control' in old['accepted_variants']
        assert not any(r['decision'] in ['reject','uncertain'] for r in old['original_pair_decisions'])
        selected.append(dict(source_id=name,image_id=key,source_path=row['image_path'],duplicate_group_id=row['duplicate_group_id'],
            historical_decisions=old['original_pair_decisions'],historical_readiness_reason=old['readiness_reason']))
    config=get_config();spec,identity=contract(ROOT)
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    artifact_check=json.loads(artifact.with_name('artifact_verification.json').read_text())
    assert digest(artifact)==artifact_check['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(json.loads(artifact.read_text()),identity)
    tracked=[audit_path,master_path,prior_path,artifact,Path(__file__),ROOT/'docs/table2-stress-expansion-protocol.md',
        ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py']+[Path(r['source_path']) for r in selected]
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in tracked}
    out.mkdir(parents=True)
    def write(path,value):path.write_text(json.dumps(value,indent=2),encoding='utf-8')
    write(out/'plan.json',dict(status='frozen_before_processing',sources=selected,input_sha256=hashes,
        measurement_contract_sha256=identity,lookup_sha256=digest(artifact),planned_attempts=12,training_admitted=0))
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    evidence={};records=[];sections=[]
    def save(path,image):
        assert cv2.imwrite(str(path),image)
        assert np.array_equal(cv2.imread(str(path),cv2.IMREAD_UNCHANGED),image)
        evidence[path.relative_to(out).as_posix()]=digest(path)
    def tile(frame,mask,title):
        frame=frame.copy()
        if mask is not None:
            green=np.zeros_like(frame);green[:,:,1]=255
            frame[mask>0]=cv2.addWeighted(frame,.65,green,.35,0)[mask>0]
        frame=cv2.copyMakeBorder(frame,24,0,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
        cv2.putText(frame,title,(4,17),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1);return frame
    for source in selected:
        name=source['source_id'];ref=measure(cv2.imread(source['source_path']),detector,masker)
        row=dict(**source,reference_measurement=ref.report,training_eligible=False,review_status='pending',
            reference_mst_estimate=None,assigned_severity=None,input_measurement=None,target_fit=None,
            status='reference_measurement_failed')
        records.append(row)
        if ref.image is None:continue
        save(out/f'{name}_reference.png',ref.image)
        panels=[tile(ref.image,None,name+' reference'),tile(ref.image,ref.mask,'reference mask')]
        if ref.mask is not None:save(out/f'{name}_reference_mask.png',ref.mask)
        if ref.report['status']=='success':
            label=lookup.label(ref.report['features']['input_ita_degrees']);group=LABEL_TO_GROUP[label]
            selected_mask=ref.mask>0;rgb=cv2.cvtColor(ref.image,cv2.COLOR_BGR2RGB)
            distorted,_=composite_rgb(rgb,group);generated=rgb.copy();generated[selected_mask]=distorted[selected_mask]
            _,clipping=composite_rgb(rgb[selected_mask][:,None,:],group)
            input_bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR);current=measure(input_bgr,detector,masker)
            save(out/f'{name}_input.png',input_bgr)
            if current.mask is not None:save(out/f'{name}_input_mask.png',current.mask)
            row.update(reference_mst_estimate=label,assigned_severity=group,
                group_assignment_source='experimental_reference_ita_lookup',official_mst_label=None,
                input_measurement=current.report,clipping=clipping,status='distorted_measurement_failed')
            panels.extend([tile(input_bgr,None,group+' Table 2 input'),tile(input_bgr,current.mask,'input mask '+current.report['status'])])
            if current.report['status']=='success':
                row['input_features']={**current.report['features'],'input_mst_index':lookup.label(current.report['features']['input_ita_degrees'])-1}
                fit=fit_recovery_target(generated,rgb,current.mask>0,selected_mask);row['target_fit']=fit
                write(out/f'{name}_target_fit.json',fit);evidence[f'{name}_target_fit.json']=digest(out/f'{name}_target_fit.json')
                row['status']='pending_review' if fit['parameters'] is not None else 'target_fit_unavailable'
                if fit['parameters'] is not None:
                    support=(current.mask>0)&selected_mask;x=generated[support].astype(float)/255;y=rgb[support].astype(float)/255
                    g,r,b=fit['parameters'];residual=np.sqrt(np.mean((np.clip(x**(1/g)*[r,1,b],0,1)-y)**2))
                    assert abs(float(residual)-fit['float_rgb_rmse'])<1e-12
                    assert int(support.sum())==fit['selected_pixels']
        board=out/f'{name}_review.png';save(board,np.hstack(panels))
        encoded=base64.b64encode(board.read_bytes()).decode()
        sections.append(f'<section><h2>{name}: estimated MST {row["reference_mst_estimate"]}, {row["assigned_severity"]} severity</h2>'
            f'<p>Status: {row["status"]}. Prior decisions remain recorded; these new masks await review.</p>'
            f'<img alt="Reference and input with their masks" src="data:image/png;base64,{encoded}"></section>')
    for p,h in hashes.items():assert digest(ROOT/p)==h
    for p,h in evidence.items():assert digest(out/p)==h
    report=dict(status='complete_pending_user_review',sources=records,planned_attempts=12,
        reference_successes=sum(r['reference_measurement']['status']=='success' for r in records),
        distorted_successes=sum((r['input_measurement'] or {}).get('status')=='success' for r in records),
        available_targets=sum(r['status']=='pending_review' for r in records),training_admitted=0,
        measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes,evidence_sha256=evidence)
    write(out/'summary.json',report)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Table 2 expansion review</title>'
        '<style>body{font:17px system-ui;max-width:1150px;margin:30px auto;padding:12px}img{width:100%}section{margin-top:36px;border-top:1px solid #aaa}</style>'
        '<h1>Six-source expansion: exact mask and scene review</h1><p>Each board shows reference, reference mask, '
        'Table 2 input, and input mask. Green means selected skin. Check skin coverage, holes, hair, eyes, '
        'mouth and background contamination. Check that another person is not included. Reply accept, reject or '
        'uncertain per source and retain any concerns. Acceptance does not validate MST estimates or skin-color truth. '
        'No training follows until these changed masks are reviewed.</p>'+''.join(sections),encoding='utf-8')
    write(out/'verification.json',dict(status='pass',summary_sha256=digest(out/'summary.json'),review_sha256=digest(out/'review.html'),
        all_original_hashes_unchanged=True,png_roundtrips_checked=True,available_target_residuals_recomputed=True))
    print(json.dumps({k:report[k] for k in ['status','reference_successes','distorted_successes','available_targets','training_admitted']}))


if __name__=='__main__':main()
