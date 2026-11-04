"""Metadata-only bounded audit. No photo upload, dataset download or inference."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/explicit_facial_hair_inventory_v1'
REPOS={
    'jseobyun/FaceParsing':'bb649e99424ea988ca2bec8b5a3c8e8ca33f3f2e',
    'IFrajtag/Facial_hair_segmentation_analysis':'144f9449b4fca54fee5bb44e96879610deadff26',
    'Charlie2802/Beard-Segmentation-Final':'6bda7d891e2bf6be21afe6cdb00ab2db77e0827b',
}


def main():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    evidence=[]
    def fetch(name,url):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'TrueHue-research-metadata-audit'})
            with urllib.request.urlopen(request,timeout=25) as response:raw=response.read()
            (OUT/name).write_bytes(raw)
            evidence.append(dict(file=name,url=url,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
            return json.loads(raw) if name.endswith('.json') else raw.decode('utf-8')
        except Exception as error:
            evidence.append(dict(file=name,url=url,error=str(error)))
            return None
    candidates=[]
    for repo,revision in REPOS.items():
        stem=repo.replace('/','__')
        metadata=fetch(stem+'_repo.json','https://api.github.com/repos/'+repo)
        tree=fetch(stem+'_tree.json','https://api.github.com/repos/'+repo+'/git/trees/'+revision+'?recursive=1')
        releases=fetch(stem+'_releases.json','https://api.github.com/repos/'+repo+'/releases')
        files=[] if tree is None else [r['path'] for r in tree['tree'] if r['type']=='blob']
        weights=[p for p in files if p.lower().endswith(('.onnx','.pt','.pth','.ckpt','.h5','.safetensors'))]
        readme='README.md' if repo.startswith('jseobyun') else ('README_BEARD.md' if repo.startswith('Charlie') else 'data/dataset_1_training_ffhq/README.md')
        fetch(stem+'_readme.txt','https://raw.githubusercontent.com/'+repo+'/'+revision+'/'+readme)
        candidates.append(dict(repository=repo,revision=revision,repository_license=None if metadata is None else metadata.get('license'),
            tree_truncated=None if tree is None else tree.get('truncated'),weight_files_in_tree=weights,
            release_assets=[] if releases is None else [a['name'] for r in releases for a in r['assets']]))
    fetch('dinov3_backbone.json','https://huggingface.co/api/models/facebook/dinov3-vitb16-pretrain-lvd1689m')
    fetch('segformer_config.json','https://huggingface.co/jonathandinu/face-parsing/raw/main/config.json')
    payload=dict(created_utc=datetime.now(timezone.utc).isoformat(),candidates=candidates,evidence=evidence,
        selected_for_inference=None,reason='No verified accessible, suitably licensed complete explicit-beard checkpoint identified in this bounded audit.',
        roboflow_project='https://universe.roboflow.com/phd-witpb/facial_hair-8quxg',
        roboflow_status='Explicit beard and mustache instance classes; public page gives API-key deployment. Local weight access and weight license not verified. Dataset CC BY 4.0 is not sufficient evidence for weight licensing.',
        preferred_mask_changed=False,correction_demo_changed=False,photos_opened=0,photos_uploaded=0,reserved_evaluation_accesses=0,
        new_inference_runs=0,new_test_suite_run=False,stop_repeating_easy_portrait=True)
    (OUT/'inventory.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print('Saved',OUT/'inventory.json','; metadata records',len(evidence))


if __name__=='__main__':main()
