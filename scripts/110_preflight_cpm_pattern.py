"""Bounded download and static ZIP/pickle-opcode inspection; never load a model."""
import argparse
import hashlib
import json
from pathlib import Path
import pickletools
import sys
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config

MAX_BYTES=256*1024*1024
REVISION='101b1ff6a4275b6da434ca5658533eb232d57fa8'
CHECKPOINT_ID='1ciy8INrxMQufDodT4a89KxrpZn4le4ud'
URL='https://drive.usercontent.google.com/download?id='+CHECKPOINT_ID+'&export=download&confirm=t'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def static_archive(path):
    result=dict(model_deserialized=False,tensor_inference=False,checkpoint_sha256=digest(path),bytes=path.stat().st_size)
    if not zipfile.is_zipfile(path):return {**result,'status':'unsupported_non_zip_no_unpickling_attempted'}
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist();result['members']=len(infos)
        pickles=[i for i in infos if i.filename.endswith('/data.pkl') or i.filename=='data.pkl']
        if len(pickles)!=1 or pickles[0].file_size>16*1024*1024:raise ValueError('Expected one bounded data.pkl')
        data=archive.read(pickles[0]);globals_seen=set();strings=[];operations=0
        for op,arg,pos in pickletools.genops(data):
            operations+=1
            if operations>3000000:raise ValueError('Pickle opcode bound exceeded')
            if op.name=='GLOBAL':globals_seen.add(str(arg))
            if op.name in ['UNICODE','BINUNICODE','SHORT_BINUNICODE'] and isinstance(arg,str) and len(arg)<150:strings.append(arg)
        result.update(status='static_archive_inspected_no_model_load',pickle_member=pickles[0].filename,
            pickle_bytes=len(data),pickle_opcodes=operations,serialized_globals=sorted(globals_seen),
            structural_strings=sorted({s for s in strings if any(t in s.lower() for t in ['encoder','decoder','resnet','activation','sigmoid','unet'])})[:100],
            tensor_storage_members=sum('/data/' in i.filename for i in infos),
            limitation='GLOBAL names/strings are serialization evidence, not proof of tensor behavior, actual calibrated labels, CPU/export parity or rights')
    return result
def download(target):
    partial=target.with_suffix('.part')
    if partial.exists():raise FileExistsError('Existing partial retained; inspect before a separately named retry')
    request=urllib.request.Request(URL,headers={'User-Agent':'TrueHue-thesis-static-model-preflight/1'})
    with urllib.request.urlopen(request,timeout=45) as response:
        kind=response.headers.get('Content-Type','');length=response.headers.get('Content-Length')
        if 'html' in kind.lower():raise ValueError('Download returned HTML/interstitial; no model saved')
        if length and int(length)>MAX_BYTES:raise ValueError('Checkpoint exceeds256MiB bound')
        total=0
        with partial.open('xb') as stream:
            while True:
                block=response.read(1024*1024)
                if not block:break
                total+=len(block)
                if total>MAX_BYTES:raise ValueError('Stream exceeds256MiB bound; partial retained')
                stream.write(block)
        if total<1024:raise ValueError('Unexpected short response; partial retained')
        with partial.open('rb') as stream:prefix=stream.read(100).lstrip().lower()
        if prefix.startswith((b'<!doctype html',b'<html')):raise ValueError('HTML payload; partial retained')
        metadata=dict(url=URL,final_url=response.geturl(),content_type=kind,content_length=length,downloaded_bytes=total)
    partial.rename(target);return metadata
def main():
    args=argparse.ArgumentParser();args.add_argument('--offline',action='store_true');args=args.parse_args()
    out=ROOT/'outputs/cpm_pattern_preflight_v1';source=json.loads((out/'source_manifest.json').read_text())
    assert source['revision']==REVISION
    model_dir=ROOT/get_config().MODELS_ROOT/'cpm_pattern_experimental_v1';model_dir.mkdir(exist_ok=True)
    target=model_dir/'pattern.pth'
    tracked=[Path(__file__),ROOT/'docs/cpm-material-preflight-protocol.md',out/'source_manifest.json',
        ROOT/'outputs/material_failure_attribution_v1/summary.json',ROOT/'outputs/material_failure_attribution_v1/verification.json',
        ROOT/'outputs/paint_protection_validation_v1/readiness.json',ROOT/'data/manifests/face_boundary_reference_v1/original_export.json',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/development_exposure_additions.jsonl']
    tracked.extend(ROOT/r['local'] for r in source['sources'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    attempts=[];metadata=None;inspection=None
    if not target.exists() and not args.offline:
        try:metadata=download(target)
        except (OSError,ValueError) as error:attempts.append(dict(status='download_unavailable',error=type(error).__name__+': '+str(error)))
    if target.exists():
        try:inspection=static_archive(target)
        except (ValueError,zipfile.BadZipFile) as error:inspection=dict(status='static_inspection_unavailable',error=str(error),checkpoint_sha256=digest(target),bytes=target.stat().st_size,model_deserialized=False)
    else:inspection=dict(status='checkpoint_not_downloaded',model_deserialized=False)
    result=dict(date='2026-10-27',status='preflight_complete_no_image_inference',repository_revision=REVISION,
        checkpoint_author_url='https://drive.google.com/file/d/'+CHECKPOINT_ID+'/view',checkpoint_path=str(target.relative_to(ROOT)),
        download=metadata,download_attempts=attempts,inspection=inspection,input_sha256=hashes,
        readiness=dict(image_inference=False,adoption=False,training=False,reasons=[
            'UV texture mapping must be specified/reproduced; raw portrait resize is a domain change',
            'Training encoder preprocessing differs from published transfer get_mask scaling',
            'Published pattern-only/combined transfer thresholds differ from training metrics; no protection cutoff selected',
            'CPU/ONNX parity, model operator/size/latency and coordinate restoration unverified',
            'Actual material-reference adjudication/representativeness unresolved',
            'Code license is distinct from checkpoint/data provenance; preserve author restrictions']),
        new_study_images_viewed=0,new_image_inference=0,new_candidate_masks=0,training_pairs_regenerated=0,models_fitted=0)
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['status','download_attempts','inspection']},indent=2))
if __name__=='__main__':main()
