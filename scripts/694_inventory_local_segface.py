"""Verify user-supplied checkpoint; ZIP and pickle opcode inspection only."""
from pathlib import Path
import hashlib,json,zipfile,pickletools,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/segface_local_inventory_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve inventory')
    source=ROOT/'outputs/segface_route_selection_v1/selection_PRIVATE.json'
    selection=json.loads(source.read_text());w=selection['weight']
    path=ROOT/'models/segface_mobilenet_candidate_v1/model_299.pt'
    assert path.stat().st_size==w['published_bytes'] and sha(path)==w['published_sha256']
    with zipfile.ZipFile(path) as archive:
        entries=archive.infolist();assert archive.testzip() is None
        pk=[p for p in entries if p.filename.endswith('/data.pkl') or p.filename=='data.pkl'];assert len(pk)==1 and pk[0].file_size<10*1024*1024
        payload=archive.read(pk[0]);strings=[];globals_seen=[];ops=0
        for op,arg,pos in pickletools.genops(payload):
            ops+=1
            if op.name in ('BINUNICODE','SHORT_BINUNICODE','UNICODE') and isinstance(arg,str):strings.append(arg)
            if op.name=='GLOBAL':globals_seen.append(arg)
        assert 'state_dict_backbone' in strings
    license_path=path.parent/'LICENSE.source-MIT.txt'
    if not license_path.exists():shutil.copyfile(source.parent/'source_snapshot/LICENSE',license_path)
    assert sha(license_path)==selection['source_snapshots']['LICENSE']['sha256']
    result=dict(user_supplied=True,checkpoint_path=str(path),bytes=path.stat().st_size,sha256=sha(path),author_digest_matches=True,
        zip_entries=len(entries),zip_crc_passed=True,pickle_metadata_bytes=len(payload),pickle_opcodes_inspected=ops,
        observed_pickle_globals=sorted(set(globals_seen)),observed_strings=strings,
        observed_state_dict_backbone_name=True,selection_sha256=sha(source),script_sha256=sha(Path(__file__)),
        previous_failed_acquisition_preserved=True,model_loaded=False,tensor_shapes_verified=False,
        dependency_installs=0,model_forwards=0,private_image_reads=0,holdout_image_reads=0,
        limitation='No unpickling or tensor load. Metadata presence does not establish key/shape completeness, safety or accuracy.')
    OUT.mkdir();p=OUT/'inventory_PRIVATE.json';p.write_text(json.dumps(result,indent=2))
    receipt=dict(passed=True,inventory_sha256=sha(p),checkpoint_sha256=sha(path),scope='author size/hash, ZIP CRC and nonexecuting opcode inspection')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='observed_strings'},indent=2))
if __name__=='__main__':main()
