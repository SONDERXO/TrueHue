"""Pin the selected public route and inspected source snapshots; no model run."""
from pathlib import Path
import json,hashlib,ast,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/segface_route_selection_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=OUT/'selection_PRIVATE.json';assert not target.exists()
    source=OUT/'source_snapshot';commit='9416628e7b5a3e4b9a1068b8467bdc0cf0be7a7d'
    files=['LICENSE','README.md','datasets/celebamask_hq.py','test.py','inference.py','network/__init__.py','network/models/segface_celeb.py']
    assert 'MIT License' in (source/'LICENSE').read_text()
    labels=['background','neck','skin','cloth','l_ear','r_ear','l_brow','r_brow','l_eye','r_eye','nose','mouth','l_lip','u_lip','hair','eye_g','hat','ear_r','neck_l']
    tree=ast.parse((source/'datasets/celebamask_hq.py').read_text())
    suffixes=[ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Constant) and False]
    lists=[ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.List) and all(isinstance(x,ast.Constant) and isinstance(x.value,str) for x in n.elts)]
    assert labels[1:] in lists
    assert 'mobilenet_v3_large(pretrained=True)' in (source/'network/models/segface_celeb.py').read_text()
    assert "checkpoint['state_dict_backbone']" in (source/'test.py').read_text()
    versions={}
    for name in ['torch','torchvision','timm','onnxruntime']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    snapshots={p:dict(url=f'https://github.com/Kartik-3004/SegFace/blob/{commit}/{p}',sha256=sha(source/p)) for p in files}
    result=dict(selected_candidate='SegFace MobileNetV3-Large CelebAMask-HQ 512',
        selection_stage='permitted public route selected; checkpoint/interface/quality not yet verified locally',
        code_repository='https://github.com/Kartik-3004/SegFace',code_commit=commit,code_license='MIT',
        model_repository='https://huggingface.co/kartiknarayan/SegFace',model_card_declared_license='MIT',
        model_card_observation_url='https://huggingface.co/kartiknarayan/SegFace/raw/main/README.md',
        model_card_observation_date='2026-11-09',model_card_historical_revision_verified=False,
        weight=dict(path='mobilenet_celeba_512/model_299.pt',revision='7c6077ee6b09c0ea63ac15c5b4184db52637da78',
            published_sha256='4d67ea7d8c33849272b293b421fa3d20d54d9987f1bca8c1ef0eebe4534993e8',published_bytes=84928824,
            observation_url='https://huggingface.co/kartiknarayan/SegFace/commit/7c6077ee6b09c0ea63ac15c5b4184db52637da78',downloaded=False,local_hash_verified=False),
        class_names=labels,explicit_beard_class=False,explicit_frame_lens_split=False,
        preprocessing=dict(colour='RGB',resolution=[512,512],image_resize='PIL bicubic',
            mean=[.485,.456,.406],std=[.229,.224,.225],output='bilinear logits align_corners=False then argmax'),
        installed_distributions=versions,automatic_backbone_download_must_be_disabled=True,
        source_snapshots=snapshots,selection_document_sha256=sha(ROOT/'docs/segface-masking-route-selection-2026-11-09.md'),
        script_sha256=sha(Path(__file__)),new_model_runs=0,private_image_reads=0,holdout_image_reads=0,
        dependency_installs=0,uploads=0,adopted=False)
    target.write_text(json.dumps(result,indent=2))
    receipt=dict(passed=True,scope='source/licence/schema selection checks only; no weight/package/accuracy qualification',
        snapshot_files=len(files),selection_sha256=sha(target),new_model_runs=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
if __name__=='__main__':main()
