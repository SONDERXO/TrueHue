"""Exactly five SegFace forwards on fixed reviewed normalized inputs."""
from pathlib import Path
import json,hashlib,sys,socket,urllib.request
import numpy as np
from PIL import Image
import torch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/segface_fixed_masks_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed private forwards')
    loader=ROOT/'outputs/segface_loader_check_v1';v=read(loader/'verification_PRIVATE.json');assert v['passed']
    for p,h in v['staged_source_sha256'].items():assert sha(p)==h
    weights=ROOT/'models/segface_mobilenet_candidate_v1/model_299.pt';assert sha(weights)==v['checkpoint_sha256']
    P=ROOT/'outputs/aligned_correction_preparation_v1';rows=read(P/'results_PRIVATE.json')['records']
    bindings_path=ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json';bindings=read(bindings_path)
    inherited=read(P/'final_input_sha256_PRIVATE.json')
    bound={str(p):sha(p) for p in [Path(__file__),loader/'verification_PRIVATE.json',weights,P/'results_PRIVATE.json',bindings_path,ROOT/'docs/segface-fixed-mask-comparison-protocol-2026-11-09.md']}
    bound.update(v['staged_source_sha256']);attempts=[]
    for key,b in bindings.items():
        r=next(r for r in rows if r['recipe']=='clean' and r['source_sha256']==b['source_sha256'])
        folder=Path(r['scene_path']).parent
        if not (folder/'landmarks.npy').exists():
            attempts.append(dict(review_id=key,case_id=r['case_id'],status='retained_landmark_failure'));continue
        image=folder/'input.png';assert sha(image)==inherited[str(image)];bound[str(image)]=sha(image)
        attempts.append(dict(review_id=key,case_id=r['case_id'],image_path=str(image),status='ready'))
    assert len(attempts)==6 and sum(r['status']=='ready' for r in attempts)==5
    def reject(*a,**k):raise RuntimeError('Network disabled in fixed private inference')
    urllib.request.urlopen=reject;torch.hub.download_url_to_file=reject;socket.socket.connect=reject
    sys.path.insert(0,str(loader/'source'))
    from network.models.segface_celeb import SegFaceCeleb
    torch.set_num_threads(2);model=SegFaceCeleb(512,'mobilenet')
    state=torch.load(weights,map_location='cpu',weights_only=True)['state_dict_backbone']
    result=model.load_state_dict(state,strict=True);assert not result.missing_keys and not result.unexpected_keys;model.eval()
    remap=np.array([0,14,1,16,7,8,2,3,4,5,10,11,13,12,17,6,18,9,15],np.uint8)
    assert len(set(remap.tolist()))==19 and remap[2]==1 and remap[10]==10 and remap[15]==6
    OUT.mkdir();(OUT/'frozen_plan_PRIVATE.json').write_text(json.dumps(dict(attempts=attempts,input_sha256=bound),indent=2))
    records=[];forwards=0
    for r in attempts:
        if r['status']!='ready':records.append(r);continue
        folder=OUT/r['review_id'];folder.mkdir()
        rgb=np.asarray(Image.open(r['image_path']).convert('RGB').resize((512,512),Image.Resampling.BICUBIC)).copy()
        x=torch.from_numpy(rgb.transpose(2,0,1).copy()).float()/255.
        x=(x-torch.tensor([.485,.456,.406])[:,None,None])/torch.tensor([.229,.224,.225])[:,None,None]
        with torch.inference_mode():logits=model(x[None],None,None)
        forwards+=1;assert logits.shape==(1,19,512,512) and torch.isfinite(logits).all()
        np.save(folder/'logits.npy',logits[0].numpy(),allow_pickle=False)
        labels=logits.argmax(1)[0].numpy().astype(np.uint8)
        categories=remap[np.asarray(Image.fromarray(labels).resize((256,256),Image.Resampling.NEAREST))]
        np.save(folder/'categories.npy',categories,allow_pickle=False)
        record=dict(r,status='success',logits_path=str(folder/'logits.npy'),categories_path=str(folder/'categories.npy'))
        records.append(record);(folder/'forward_PRIVATE.json').write_text(json.dumps(record,indent=2));print(r['review_id'],'forward complete',flush=True)
    assert forwards==5 and all(sha(p)==h for p,h in bound.items())
    (OUT/'inference_PRIVATE.json').write_text(json.dumps(dict(records=records,forwards=forwards,input_sha256=bound,holdout_image_reads=0,adopted=False),indent=2))
if __name__=='__main__':main()
