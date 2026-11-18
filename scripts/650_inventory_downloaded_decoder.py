"""Inert ZIP/pickle opcode inventory; never unpickle or execute downloaded code."""
from pathlib import Path
from collections import Counter
import hashlib,json,zipfile,pickletools,shutil
ROOT=Path(__file__).resolve().parents[1];SOURCE=Path(r'C:\Users\NYTHAN\Downloads\dinov3\decoder.ckpt');DEST=ROOT/'models/dinov3_face_parser_candidate_v1/decoder.ckpt';OUT=ROOT/'outputs/dinov3_decoder_inventory_v1'
def main():
    if DEST.exists() or OUT.exists():raise FileExistsError('Preserve inventory')
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    with zipfile.ZipFile(SOURCE) as z:
        entries=z.infolist();names=[i.filename for i in entries];assert len(names)==len(set(names))
        assert all(not n.startswith(('/','\\')) and '..' not in Path(n).parts for n in names)
        pi=next(i for i in entries if i.filename.endswith('/data.pkl'));assert pi.file_size<16*1024*1024
        raw=z.read(pi);ops=list(pickletools.genops(raw));assert ops[-1][0].name=='STOP'
        strings=[v for op,v,_ in ops if op.name in ('BINUNICODE','SHORT_BINUNICODE','UNICODE')]
        keys=[s for s in strings if s.startswith(('encoder.','decoder.'))]
        globals_=sorted({v for op,v,_ in ops if op.name=='GLOBAL'})
        assert 'encoder.cnn.layers.0.weight' in keys and 'decoder.final_conv.2.weight' in keys
        assert not any(k.startswith('encoder.dinov3.') for k in keys)
        # CRC validates archive bytes only; it does not establish trust or safe execution.
        assert z.testzip() is None
    digest=sha(SOURCE);shutil.copy2(SOURCE,DEST);assert sha(DEST)==digest
    OUT.mkdir();r=dict(source=str(SOURCE),destination=str(DEST),bytes=SOURCE.stat().st_size,sha256=digest,
        zip_entries=len(entries),archive_crc_pass=True,pickle_metadata_bytes=len(raw),named_weight_keys=len(keys),
        named_key_prefixes=dict(Counter('.'.join(k.split('.')[:2]) for k in keys)),named_weight_keys_list=keys,
        pickle_globals_observed=globals_,backbone_named_keys_present=False,exact_tensor_shapes_verified=False,
        no_pickle_deserialization=True,research_permission_status='Backbone approved by user; separate decoder/code permission not yet supplied',
        new_inference=0,new_fits=0,holdout_image_reads=0,script_sha256=sha(Path(__file__)))
    (OUT/'inventory_PRIVATE.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('named_weight_keys_list','named_key_prefixes')},indent=2))
if __name__=='__main__':main()
