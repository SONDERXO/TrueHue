"""Acquire one pinned author checkpoint; inspect ZIP/pickle opcodes, never load."""
from pathlib import Path
import hashlib,json,urllib.request,zipfile,pickletools,shutil,traceback
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/segface_package_inventory_v1'
DEST=ROOT/'models/segface_mobilenet_candidate_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists() or DEST.exists():raise FileExistsError('Preserve partial/completed acquisition')
    selection_path=ROOT/'outputs/segface_route_selection_v1/selection_PRIVATE.json'
    selection=json.loads(selection_path.read_text());weight=selection['weight']
    receipt=json.loads((selection_path.parent/'verification_PRIVATE.json').read_text())
    assert receipt['passed'] and receipt['selection_sha256']==sha(selection_path)
    for name,item in selection['source_snapshots'].items():assert sha(selection_path.parent/'source_snapshot'/name)==item['sha256']
    url=f"https://huggingface.co/kartiknarayan/SegFace/resolve/{weight['revision']}/{weight['path']}"
    OUT.mkdir();DEST.mkdir();partial=DEST/'model_299.pt.partial'
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'TrueHue-research-artifact-inventory'})
        with urllib.request.urlopen(request,timeout=60) as response,partial.open('xb') as target:
            copied=0
            while True:
                block=response.read(1024*1024)
                if not block:break
                copied+=len(block);assert copied<=weight['published_bytes']
                target.write(block)
        assert copied==weight['published_bytes'] and sha(partial)==weight['published_sha256']
        path=DEST/'model_299.pt';partial.rename(path)
        with zipfile.ZipFile(path) as archive:
            entries=archive.infolist();assert archive.testzip() is None
            pk=[p for p in entries if p.filename.endswith('/data.pkl') or p.filename=='data.pkl'];assert len(pk)==1
            assert pk[0].file_size<10*1024*1024
            payload=archive.read(pk[0]);strings=[];globals_seen=[];ops=0
            for opcode,arg,pos in pickletools.genops(payload):
                ops+=1
                if opcode.name in ('BINUNICODE','SHORT_BINUNICODE','UNICODE') and isinstance(arg,str):strings.append(arg)
                if opcode.name=='GLOBAL':globals_seen.append(arg)
            assert 'state_dict_backbone' in strings
        shutil.copyfile(selection_path.parent/'source_snapshot/LICENSE',DEST/'LICENSE.source-MIT.txt')
        result=dict(downloaded=True,author_revision=weight['revision'],author_path=weight['path'],
            download_url=url,checkpoint_path=str(path),bytes=copied,sha256=sha(path),author_digest_matches=True,
            zip_entries=len(entries),zip_crc_passed=True,pickle_metadata_bytes=len(payload),
            pickle_opcodes_inspected=ops,observed_pickle_globals=sorted(set(globals_seen)),
            observed_state_dict_backbone_name=True,observed_strings=strings,
            selection_sha256=sha(selection_path),script_sha256=sha(Path(__file__)),
            model_loaded=False,tensor_shapes_verified=False,dependency_installs=0,model_forwards=0,
            private_image_reads=0,holdout_image_reads=0,
            limitation='Archive CRC and pickle opcodes only. No unpickling, tensor loading, key/shape completeness or security certification.')
        p=OUT/'inventory_PRIVATE.json';p.write_text(json.dumps(result,indent=2))
        (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,inventory_sha256=sha(p),checkpoint_sha256=sha(path),scope='author byte/hash match and nonexecuting archive inventory only'),indent=2))
        print(json.dumps({k:v for k,v in result.items() if k!='observed_strings'},indent=2))
    except Exception:
        (OUT/'failure_PRIVATE.json').write_text(json.dumps(dict(failure=traceback.format_exc(),partial_preserved=str(partial),download_url=url),indent=2));raise
if __name__=='__main__':main()
