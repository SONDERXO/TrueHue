"""Exactly one fixed CPU forward per available frozen aligned image."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import segmentation_models_pytorch as smp
from safetensors.torch import load_file
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/faceocc_diagnostic_v1';path=out/'inference.json'
    if path.exists() or any((out/'logits').iterdir()):raise FileExistsError('Inference artifacts exist; no rerun')
    raw=(out/'plan.json').read_bytes();plan=json.loads(raw)
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert all(digest(p)==h for p,h in plan['input_sha256'].items())
    torch.set_num_threads(2)
    model=smp.Unet(encoder_name='resnet18',encoder_depth=5,encoder_weights=None,
        decoder_use_norm='batchnorm',decoder_channels=(256,128,64,32,16),
        decoder_attention_type=None,decoder_interpolation='nearest',in_channels=3,classes=1,activation=None)
    model.load_state_dict(load_file(str(ROOT/'models/faceocc_candidate_v1/model.safetensors'),device='cpu'),strict=True);model.eval()
    mean=np.array([.485,.456,.406],np.float32);std=np.array([.229,.224,.225],np.float32)
    records=[]
    for row in plan['attempts']:
        if 'aligned_path' not in row:continue
        rec=dict(image_id=row['image_id'],status='failed')
        try:
            image=np.asarray(Image.open(row['aligned_path']).convert('RGB'),dtype=np.float32)
            assert image.shape==(256,256,3)
            tensor=torch.from_numpy(np.ascontiguousarray(((image/255-mean)/std).transpose(2,0,1)[None]))
            with torch.inference_mode():logits=model(tensor).cpu().numpy()
            assert logits.shape==(1,1,256,256) and np.isfinite(logits).all()
            target=out/'logits'/('case_'+str(row['case_index'])+'.npy');np.save(target,logits[0,0])
            rec.update(status='success',logits_path=target.relative_to(out).as_posix(),logits_sha256=digest(target))
        except Exception as error:rec['reason']=str(error)
        records.append(rec)
        with (out/'inference_records.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
        print(str(row['case_index'])+': '+rec['status'],flush=True)
    assert all(digest(p)==h for p,h in plan['input_sha256'].items())
    path.write_text(json.dumps(dict(plan_sha256=hashlib.sha256(raw).hexdigest(),records=records,
        forwards=len(records),fits=0),indent=2))


if __name__=='__main__':main()
