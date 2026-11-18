"""One matching LUT retrieval/safe inspection/bounded official CPU build."""
from pathlib import Path
import sys,json,hashlib,zipfile,shutil,subprocess,os,time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/ppr_full_pipeline_assets_v1'
sys.path.insert(0,str(ROOT/'scripts'))
MEMBER='pretrained_models/mask_noglc_a/LUTs_-1.pth'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)

def retrieve():
    import check_ppr_parameter_archive as remote_zip
    if (OUT/'LUTs_-1.pth').exists() or (OUT/'lut_receipt.json').exists():raise FileExistsError('Existing LUT attempt')
    auth=read(OUT/'user_authorization.json');assert auth['matching_lut_only']
    remote_zip.CAP=4*1024**2;r=remote_zip.Ranges()
    try:
        old=read(ROOT/'outputs/ppr_parameter_access_v1/archive_metadata.json')
        assert r.size==old['archive_bytes']==261433127
        expected=next(i for i in old['entries'] if i['name']==MEMBER)
        with zipfile.ZipFile(r) as archive:
            matches=[i for i in archive.infolist() if i.filename==MEMBER];assert len(matches)==1
            z=matches[0]
            assert (z.file_size,z.compress_size,z.CRC)==(expected['size'],expected['compressed'],expected['crc'])
            payload=archive.read(z)
        assert len(payload)==2157507 and r.transferred<4*1024**2
        with (OUT/'LUTs_-1.pth').open('xb') as f:f.write(payload)
        write(OUT/'lut_receipt.json',dict(passed=True,member=MEMBER,bytes=len(payload),sha256=sha(OUT/'LUTs_-1.pth'),
              transferred_bytes=r.transferred,archive_bytes=r.size,crc=z.CRC,authorization_sha256=sha(OUT/'user_authorization.json'),
              protocol_sha256=sha(ROOT/'docs/ppr-full-pipeline-assessment-protocol-2026-11-17.md')))
        print('PASS one matching LUT state retrieved/ZIPCRC/hash; no other assets/photos.')
    except Exception as exc:write(OUT/'retrieval_failure.json',dict(error=repr(exc),transferred_bytes=r.transferred));raise

def inspect():
    import torch
    torch.set_num_threads(2);r=read(OUT/'lut_receipt.json');assert r['passed'] and sha(OUT/'LUTs_-1.pth')==r['sha256']
    state=torch.load(OUT/'LUTs_-1.pth',map_location='cpu',weights_only=True)
    assert isinstance(state,dict) and set(state)==set('12345')
    info={}
    for k in '12345':
        assert isinstance(state[k],dict) and set(state[k])=={'LUT'}
        t=state[k]['LUT'];assert isinstance(t,torch.Tensor) and t.dtype==torch.float32 and tuple(t.shape)==(3,33,33,33)
        assert torch.isfinite(t).all()
        info[k]=dict(shape=list(t.shape),minimum=float(t.min()),maximum=float(t.max()))
    write(OUT/'lut_inspection.json',dict(passed=True,safe_weights_only=True,states=info,checkpoint_sha256=r['sha256'],actual_image_calls=0))
    print('PASS five finite native-shaped float32LUTstates; zero image calls.')

def build():
    import torch
    assert read(OUT/'lut_inspection.json')['passed']
    build=OUT/'build'
    if build.exists():
        # The original launcher failed before starting setup.py or the compiler.
        failure=build/'activation_failure.json'
        if not failure.is_file() or read(failure)['native_builds_started']!=0 or (build/'build.log').exists():
            raise FileExistsError('Existing build attempt')
        write(build/'launcher_repair.json',dict(native_builds_started=0,
              preserved_failure_sha256=sha(failure),repair='Pass cmd.exe command string without CRT backslash-escaping its quoted batch path.'))
    source=build/'source';(source/'src').mkdir(parents=True,exist_ok=True)
    old=ROOT/'outputs/technical_plan_reassessment_2026_11_17/source'
    shutil.copyfile(old/'setup.py',source/'setup.py');shutil.copyfile(old/'trilinear.cpp',source/'src/trilinear.cpp')
    shutil.copyfile(OUT/'source/trilinear.h',source/'src/trilinear.h')
    native=build/'native';obj=build/'obj';vcvars=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat')
    assert vcvars.is_file() and not torch.cuda.is_available()
    activation=subprocess.run('cmd.exe /d /s /c call "'+str(vcvars)+'" >nul && set',capture_output=True,text=True,timeout=30)
    assert activation.returncode==0,'Developer environment activation failed'
    env=dict(os.environ)
    for line in activation.stdout.splitlines():
        if '=' in line and not line.startswith('='):
            k,v=line.split('=',1);env[k]=v
    env.update(DISTUTILS_USE_SDK='1',MSSdk='1',MAX_JOBS='1',PYTHONDONTWRITEBYTECODE='1')
    start=time.monotonic();log=build/'build.log';command=[sys.executable,'-B',str(source/'setup.py'),'build_ext','--build-lib',str(native),'--build-temp',str(obj)]
    timed_out=False
    with log.open('xb') as stream:
        p=subprocess.Popen(command,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:code=p.wait(timeout=300)
        except subprocess.TimeoutExpired:
            timed_out=True
            subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True,check=False)
            code=p.wait(timeout=15)
    elapsed=time.monotonic()-start
    extensions=list(native.glob('trilinear*.pyd')) if native.exists() else []
    success=not timed_out and code==0 and len(extensions)==1
    record=dict(passed=success,exit_code=code,timed_out=timed_out,elapsed_seconds=elapsed,max_seconds=300,
                log_sha256=sha(log),official_sources_unchanged=True,core_packages_changed=False,
                extension=None if not success else extensions[0].relative_to(ROOT).as_posix(),
                extension_sha256=None if not success else sha(extensions[0]),
                source_sha256={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()})
    write(OUT/'build_receipt.json',record)
    print(record)
    if not success:raise RuntimeError('Official CPU build failed; fixed assessment stops, no backend/port retry')

if __name__=='__main__':{'retrieve':retrieve,'inspect':inspect,'build':build}[sys.argv[1]]()
