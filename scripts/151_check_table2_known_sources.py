"""Frozen six-source Table2 capacity diagnostic, never training admission."""
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
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.table2_composite import composite_rgb,SETTINGS
from src.model_training.recovery_targets import fit_recovery_target


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out=ROOT/'outputs/table2_known_source_feasibility_v1'
    if out.exists():raise FileExistsError(out)
    manifest=ROOT/'outputs/control_aware_model_build_v1/fit_manifest.json'
    rows=json.loads(manifest.read_text())['rows']
    sources=sorted({r['source_path'] for r in rows})
    if len(sources)!=6 or any(r['partition']!='train' or not r['source_image_id'].startswith('fairface__') for r in rows):
        raise ValueError('Frozen source cohort differs')
    config=get_config();spec,identity=contract(ROOT)
    folder=ROOT/'outputs/mst_monotone_square256_v1'
    artifact=folder/'development_lookup.json'
    checksum=digest(artifact)
    if checksum!=json.loads((folder/'artifact_verification.json').read_text())['lookup_sha256']:
        raise ValueError('Lookup checksum mismatch')
    lookup=DevelopmentMonotoneLookup(json.loads(artifact.read_text()),identity)
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def mask(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    tracked=[manifest,artifact,ROOT/'docs/table2-known-source-feasibility-protocol.md',Path(__file__),
             ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py']+[Path(p) for p in sources]
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in tracked}
    out.mkdir(parents=True)
    (out/'plan.json').write_text(json.dumps(dict(source_paths=sources,planned_probes=18,input_sha256=hashes,
        measurement_contract_sha256=identity,lookup_sha256=checksum,training_admission=False),indent=2))
    records=[];references=[];files={};checks=[]
    def save(path,image):
        if not cv2.imwrite(str(path),image):raise IOError(path)
        if not np.array_equal(cv2.imread(str(path),cv2.IMREAD_UNCHANGED),image):raise ValueError('PNG roundtrip mismatch')
        files[path.relative_to(out).as_posix()]=digest(path)
    def tile(image,selected,title):
        result=image.copy()
        if selected is not None:
            overlay=np.zeros_like(result);overlay[:,:,1]=255
            result[selected>0]=cv2.addWeighted(result,.65,overlay,.35,0)[selected>0]
        result=cv2.copyMakeBorder(result,24,0,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
        cv2.putText(result,title,(5,17),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        return result
    for source in sources:
        name=Path(source).stem
        ref=measure(cv2.imread(source),detector,mask)
        references.append(dict(source_path=source,report=ref.report))
        tiles=[tile(ref.image,ref.mask,'reference '+name)]
        if ref.report['status']=='success':
            save(out/f'{name}_reference.png',ref.image);save(out/f'{name}_reference_mask.png',ref.mask)
        for group in SETTINGS:
            record=dict(source_path=source,severity_probe=group,assigned_tone_group=None,training_admitted=False)
            records.append(record)
            if ref.report['status']!='success':
                record['status']='reference_measurement_failed';continue
            selected=ref.mask>0;rgb=cv2.cvtColor(ref.image,cv2.COLOR_BGR2RGB)
            transformed,_=composite_rgb(rgb,group)
            _,clipping=composite_rgb(rgb[selected][:,None,:],group)
            generated=rgb.copy();generated[selected]=transformed[selected]
            bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
            current=measure(bgr,detector,mask)
            save(out/f'{name}_{group}_input.png',bgr)
            if current.mask is not None:save(out/f'{name}_{group}_mask.png',current.mask)
            tiles.append(tile(bgr,current.mask,group+' '+current.report['status']))
            record.update(status=current.report['status'],clipping=clipping,input_measurement=current.report)
            if current.report['status']!='success':continue
            label=lookup.label(current.report['features']['input_ita_degrees'])
            record['experimental_input_features']={**current.report['features'],'input_mst_index':label-1}
            fitted=fit_recovery_target(generated,rgb,current.mask>0,selected)
            record['target_fit']=fitted
            if fitted['parameters'] is not None:
                support=(current.mask>0)&selected
                x=generated[support].astype(float)/255;y=rgb[support].astype(float)/255
                gamma,red,blue=fitted['parameters']
                predicted=np.clip(x**(1/gamma)*[red,1,blue],0,1)
                error=float(np.sqrt(np.mean((predicted-y)**2)))
                if abs(error-fitted['float_rgb_rmse'])>1e-12:raise ValueError('Independent fit residual mismatch')
                checks.append(dict(source=name,severity=group,independent_rmse=error))
        save(out/f'{name}_review.png',np.hstack(tiles))
    if any(digest(ROOT/p)!=h for p,h in hashes.items()):raise ValueError('Original input changed')
    if any(digest(out/p)!=h for p,h in files.items()):raise ValueError('Saved evidence changed')
    result=dict(status='complete_diagnostic_only',planned_probes=18,records=records,references=references,
        successful_measurements=sum(r['status']=='success' for r in records),
        clipped_probes=sum(r.get('clipping',{}).get('clipped_pixels',0)>0 for r in records),
        available_targets=len(checks),training_admitted=0,final_validated=False,
        measurement_contract_sha256=identity,lookup_sha256=checksum,input_sha256=hashes,evidence_sha256=files)
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    (out/'verification.json').write_text(json.dumps(dict(status='pass',summary_sha256=digest(out/'summary.json'),
        independent_residual_checks=checks,png_roundtrips=len(files),original_hashes_unchanged=True),indent=2))
    print(json.dumps({k:result[k] for k in ['status','planned_probes','successful_measurements','clipped_probes','available_targets','training_admitted']}))


if __name__=='__main__':main()
