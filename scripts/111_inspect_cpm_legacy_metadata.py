"""Bounded static follow-up for the legacy torch checkpoint; no deserialization."""
import hashlib
import io
import json
from pathlib import Path
import pickletools
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
MAGIC=0x1950a86a20f9469cfc6c
EXPECTED_SHA='27421250269552f61a6c52581a73baf50cb3f4dee88c8403d87943b53a9ebfec'
LIMIT=16*1024*1024
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inspect_metadata(path):
    with Path(path).open('rb') as stream:head=stream.read(LIMIT)
    buffer=io.BytesIO(head);records=[]
    for index in range(5):
        start=buffer.tell();numbers=[];globals_seen=set();strings=set();count=0
        for op,arg,pos in pickletools.genops(buffer):
            count+=1
            if count>3000000:raise ValueError('Metadata opcode bound exceeded')
            if op.name=='GLOBAL':globals_seen.add(str(arg))
            if op.name in ['INT','LONG','LONG1','LONG4','BININT','BININT1','BININT2']:numbers.append(arg)
            if op.name in ['UNICODE','BINUNICODE','SHORT_BINUNICODE'] and isinstance(arg,str) and len(arg)<200:strings.add(arg)
        if index in [0,1]:
            expected=MAGIC if index==0 else 1001
            if numbers!=[expected] or globals_seen:raise ValueError('Not the expected torch legacy header')
        records.append(dict(stream=index,start=start,end=buffer.tell(),opcodes=count,serialized_globals=sorted(globals_seen),
            structural_strings=sorted(s for s in strings if any(t in s.lower() for t in ['resnet','unet','decoder','encoder','sigmoid','cuda','python3.']))[:100]))
    return dict(status='five_legacy_metadata_streams_statically_inspected',read_bound_bytes=LIMIT,
        metadata_end=buffer.tell(),opaque_remaining_bytes=Path(path).stat().st_size-buffer.tell(),streams=records,
        model_deserialized=False,serialized_globals_imported=False,tensors_materialized=False,
        limitation='Opcode evidence only; raw storage content, exact model behavior, CPU/export parity and calibrated protected-material semantics unverified')
def main():
    out=ROOT/'outputs/cpm_pattern_preflight_v1';previous=out/'summary.json'
    path=ROOT/get_config().MODELS_ROOT/'cpm_pattern_experimental_v1/pattern.pth'
    assert digest(path)==EXPECTED_SHA
    assert json.loads(previous.read_text())['inspection']['checkpoint_sha256']==EXPECTED_SHA
    tracked=[Path(__file__),previous,path,ROOT/'docs/cpm-material-preflight-protocol.md']
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    result=inspect_metadata(path);result.update(checkpoint_sha256=EXPECTED_SHA,input_sha256=hashes,
        adaptation='After initial non-ZIP discovery, inspect only bounded legacy metadata. This is static format investigation, not a new model accuracy experiment.',
        format_reference='https://github.com/pytorch/pytorch/blob/v1.6.0/torch/serialization.py')
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    (out/'legacy_metadata.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(status=result['status'],metadata_end=result['metadata_end'],opaque_remaining_bytes=result['opaque_remaining_bytes'],
        serialized_globals=result['streams'][3]['serialized_globals']),indent=2))
if __name__=='__main__':main()
