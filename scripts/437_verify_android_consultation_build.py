"""Verify consultation APK, unchanged model assets and actual local check reports."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'android-app/app'
OUT=ROOT/'outputs/android_consultation_20261105_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    apk=APP/'build/outputs/apk/debug/app-debug.apk'
    manifest=json.loads((APP/'src/main/assets/development_pipeline/manifest.json').read_text())
    with ZipFile(apk) as archive:
        for name,digest in manifest['assets_sha256'].items():
            assert hashlib.sha256(archive.read('assets/development_pipeline/'+name)).hexdigest()==digest
        assert archive.read('assets/development_pipeline/manifest.json')==(APP/'src/main/assets/development_pipeline/manifest.json').read_bytes()
        assert not any(n.startswith('assets/') and n.lower().endswith(('.jpeg','.jpg','.png')) for n in archive.namelist())
    suites=[ET.parse(p).getroot() for p in (APP/'build/test-results/testDebugUnitTest').glob('TEST-*.xml')]
    assert suites and all(int(s.get(k,0))==0 for s in suites for k in ['errors','failures','skipped'])
    issues=ET.parse(APP/'build/reports/lint-results-debug.xml').getroot().findall('issue')
    assert not any(i.get('severity') in ['Error','Fatal'] for i in issues)
    sdk=ROOT/'outputs/android_toolchain/sdk';jdk=Path('C:/Program Files/Android/openjdk/jdk-21.0.8')
    signature=subprocess.run([str(jdk/'bin/java.exe'),'-jar',str(sdk/'build-tools/34.0.0/lib/apksigner.jar'),'verify','--verbose',str(apk)],check=True,capture_output=True,text=True).stdout
    permissions=subprocess.run([str(sdk/'build-tools/34.0.0/aapt.exe'),'dump','permissions',str(apk)],check=True,capture_output=True,text=True).stdout
    assert 'android.permission.INTERNET' not in permissions
    report=dict(apk=str(apk),apk_sha256=sha(apk),apk_bytes=apk.stat().st_size,
        JVM_tests=sum(int(s.get('tests')) for s in suites),lint_errors=0,lint_warnings=sum(i.get('severity')=='Warning' for i in issues),
        packaged_model_assets_match_manifest=True,dataset_images_packaged=False,internet_permission=False,
        device_tests_this_update=False,visual_device_verification=False,
        pipeline_or_model_updated=False,signature_verified=True,verification_script_sha256=sha(Path(__file__)))
    OUT.mkdir();(OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'signature.txt').write_text(signature,encoding='utf-8')
    (OUT/'permissions.txt').write_text(permissions,encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
