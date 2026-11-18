"""Small pinned wheel overlay; never changes the existing torch environment."""
from pathlib import Path
import sys,json,hashlib,urllib.request,subprocess,importlib.metadata,platform
from pip._vendor.packaging.tags import sys_tags
from pip._vendor.packaging.utils import parse_wheel_filename
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/fiqa_tiny_runtime_v1'
PACKAGES={'timm':'1.0.9','huggingface-hub':'0.25.1','safetensors':'0.4.5','PyYAML':'6.0.2',
          'packaging':'24.1','requests':'2.32.3','tqdm':'4.66.5','certifi':'2024.8.30',
          'charset-normalizer':'3.3.2','idna':'3.10','urllib3':'2.2.3','colorama':'0.4.6'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def inventory():return {d.metadata['Name']:d.version for d in importlib.metadata.distributions()}

def download():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir();(OUT/'wheels').mkdir();write(OUT/'existing_environment.json',inventory())
    tags={t:i for i,t in enumerate(sys_tags())};records=[];total=0
    try:
        for name,version in PACKAGES.items():
            with urllib.request.urlopen('https://pypi.org/pypi/'+name+'/'+version+'/json',timeout=20) as r:
                body=r.read(524289);assert len(body)<=524288
            meta=json.loads(body);choices=[]
            for f in meta['urls']:
                if f['packagetype']!='bdist_wheel':continue
                _,_,_,wheel_tags=parse_wheel_filename(f['filename'])
                ranks=[tags[t] for t in wheel_tags if t in tags]
                if ranks:choices.append((min(ranks),f['filename'],f))
            assert choices,'No compatible binary wheel: '+name
            f=min(choices,key=lambda x:x[:2])[2];assert f['size']<=8*1024**2
            target=OUT/'wheels'/f['filename'];assert target.parent==OUT/'wheels'
            with urllib.request.urlopen(f['url'],timeout=25) as r,target.open('xb') as out:
                n=0
                while chunk:=r.read(65536):
                    n+=len(chunk);total+=len(chunk)
                    if total>16*1024**2 or n>f['size']:raise ValueError('Wheel ceiling exceeded')
                    out.write(chunk)
            assert n==f['size'] and sha(target)==f['digests']['sha256']
            records.append(dict(package=name,version=version,path=target.relative_to(OUT).as_posix(),bytes=n,sha256=sha(target),url=f['url']))
        write(OUT/'wheel_receipt.json',dict(passed=True,bytes=total,records=records,Python=platform.python_version(),
              protocol_sha256=sha(ROOT/'docs/face-underexposure-pilot-protocol-2026-11-17.md')))
        print('PASS12compatible PyPI wheels,verified bytes='+str(total)+'; existing environment unchanged.')
    except Exception as exc:write(OUT/'download_failure.json',dict(error=repr(exc),bytes=total,completed_packages=len(records)));raise

def install():
    site=OUT/'site'
    if site.exists():raise FileExistsError(site)
    receipt=json.loads((OUT/'wheel_receipt.json').read_text(encoding='utf-8'))
    old=json.loads((OUT/'existing_environment.json').read_text(encoding='utf-8'));assert inventory()==old
    wheels=[]
    for r in receipt['records']:
        p=OUT/r['path'];assert sha(p)==r['sha256'];wheels.append(str(p))
    subprocess.run([sys.executable,'-m','pip','install','--no-index','--no-deps','--no-compile','--target',str(site),*wheels],check=True)
    assert inventory()==old
    write(OUT/'installation.json',dict(passed=True,isolated_site=site.relative_to(ROOT).as_posix(),existing_environment_unchanged=True,
          wheels_receipt_sha256=sha(OUT/'wheel_receipt.json'),script_sha256=sha(Path(__file__)),
          site_files={p.relative_to(site).as_posix():sha(p) for p in sorted(site.rglob('*')) if p.is_file()}))
    print('PASS offline overlay installed; existing torch/torchvision/environment unchanged.')

if __name__=='__main__':{'download':download,'install':install}[sys.argv[1]]()
