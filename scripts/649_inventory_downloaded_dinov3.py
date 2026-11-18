"""Validate inert safetensors structure and copy user-downloaded package; no loading."""
from pathlib import Path
import json,struct,hashlib,shutil,math
ROOT=Path(__file__).resolve().parents[1];SOURCE=Path(r'C:\Users\NYTHAN\Downloads\dinov3');DEST=ROOT/'models/dinov3_face_parser_candidate_v1';OUT=ROOT/'outputs/dinov3_package_inventory_v1'
def main():
    if DEST.exists() or OUT.exists():raise FileExistsError('Preserve candidate inventory')
    names=['model.safetensors','config.json','preprocessor_config.json','LICENSE.md','README.md']
    assert all((SOURCE/n).is_file() for n in names)
    config=json.loads((SOURCE/'config.json').read_text());assert config['model_type']=='dinov3_vit' and config['hidden_size']==768 and config['patch_size']==16 and config['num_hidden_layers']==12
    path=SOURCE/'model.safetensors'
    with path.open('rb') as f:
        size=struct.unpack('<Q',f.read(8))[0];assert 0<size<16*1024*1024;header=json.loads(f.read(size))
    payload=path.stat().st_size-8-size;ranges=[];parameters=0
    for key,t in header.items():
        if key=='__metadata__':continue
        assert t['dtype']=='F32' and all(isinstance(v,int) and v>=0 for v in t['shape'])
        a,b=t['data_offsets'];assert 0<=a<=b<=payload and b-a==math.prod(t['shape'])*4
        ranges.append((a,b));parameters+=math.prod(t['shape'])
    ranges.sort();assert ranges[0][0]==0 and ranges[-1][1]==payload and all(a[1]==b[0] for a,b in zip(ranges,ranges[1:]))
    assert header['embeddings.patch_embeddings.weight']['shape']==[768,3,16,16]
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    hashes={n:sha(SOURCE/n) for n in names};DEST.mkdir()
    for n in names:shutil.copy2(SOURCE/n,DEST/n);assert sha(DEST/n)==hashes[n]
    OUT.mkdir();receipt=dict(source=str(SOURCE),destination=str(DEST),files={n:dict(bytes=(DEST/n).stat().st_size,sha256=hashes[n]) for n in names},tensor_count=len(ranges),parameter_elements=parameters,
        safetensors_layout_valid=True,format='Hugging Face DINOv3ViTModel; not original torch.hub state dict',access_status='User reports official access granted and manually downloaded files',
        official_remote_digest_independently_verified=False,decoder_present=False,new_inference=0,new_fits=0,holdout_image_reads=0)
    (DEST/'local_provenance_PRIVATE.json').write_text(json.dumps(receipt,indent=2));(OUT/'inventory_PRIVATE.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
