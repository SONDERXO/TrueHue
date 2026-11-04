"""Verify built Android artifacts; never label unrun device tests as passing."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/android_integration_20261031_v1'
    if out.exists():raise FileExistsError(out)
    app=ROOT/'android-app/app';apk=app/'build/outputs/apk/debug/app-debug.apk'
    tests_apk=app/'build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
    assert apk.is_file() and tests_apk.is_file()
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    assets=app/'src/main/assets/development_pipeline';manifest=json.loads((assets/'manifest.json').read_text())
    with ZipFile(apk) as z:
        for name,expected in manifest['assets_sha256'].items():
            assert hashlib.sha256(z.read('assets/development_pipeline/'+name)).hexdigest()==expected
        assert z.read('assets/development_pipeline/manifest.json')==(assets/'manifest.json').read_bytes()
        assert not any(name.startswith('assets/') and name.lower().endswith(('.png','.jpg','.jpeg')) for name in z.namelist())
        native=[name for name in z.namelist() if name.startswith('lib/') and name.endswith('.so')]
        assert any('libopencv_java5.so' in name for name in native)
        assert any('libmediapipe_tasks_jni.so' in name for name in native)
    reports=sorted((app/'build/test-results/testDebugUnitTest').glob('TEST-*.xml'));assert reports
    count=0
    for path in reports:
        suite=ET.parse(path).getroot();assert all(int(suite.get(k,0))==0 for k in ['failures','errors','skipped'])
        count+=int(suite.get('tests'))
    assert count>=18
    lint_path=app/'build/reports/lint-results-debug.xml'
    issues=[dict(id=r.get('id'),severity=r.get('severity'),message=r.get('message')) for r in ET.parse(lint_path).getroot().findall('issue')]
    assert not any(r['severity'] in ['Fatal','Error'] for r in issues)
    sdk=ROOT/'outputs/android_toolchain/sdk';jdk=Path('C:/Program Files/Android/openjdk/jdk-21.0.8')
    signature=subprocess.run([str(jdk/'bin/java.exe'),'-jar',str(sdk/'build-tools/34.0.0/lib/apksigner.jar'),'verify','--verbose',str(apk)],check=True,capture_output=True,text=True).stdout
    assert signature.startswith('Verifies')
    permissions=subprocess.run([str(sdk/'build-tools/34.0.0/aapt.exe'),'dump','permissions',str(apk)],check=True,capture_output=True,text=True).stdout
    assert 'android.permission.INTERNET' not in permissions
    assert 'android.permission.WRITE_EXTERNAL_STORAGE' not in permissions
    sources=[p for p in (app/'src').rglob('*') if p.is_file() and p.suffix in ['.kt','.java','.xml','.json'] and '/assets/' not in p.as_posix()]
    sources.extend([ROOT/'android-app/app/build.gradle.kts',ROOT/'scripts/321_prepare_android_pipeline_assets.py',Path(__file__)])
    result=dict(status='integration_apks_built_jvm_tests_and_lint_pass_device_pending',
        apk_path=apk.relative_to(ROOT).as_posix(),apk_sha256=sha(apk),apk_bytes=apk.stat().st_size,
        instrumentation_apk_sha256=sha(tests_apk),unit_tests_passed=count,
        fixtures=dict(tree_vectors=20,mst_queries=47,reciprocal_gamma_pixels=111),
        lint_issues=issues,native_libraries=native,signature_verified=True,no_internet_permission=True,
        experimental=True,baseline='Python-demo baseline5/fold1',tree_sha256=manifest['assets_sha256']['baseline5.json'],
        lookup_sha256=manifest['assets_sha256']['mst_lookup.json'],new_model_fits=0,python_demo_changed=False,
        image_pipeline_wired=True,device_tested=False,instrumentation_tests_executed=False,
        cross_platform_full_path_pixel_parity=False,scientific_model_validated=False,proposal_complete=False,
        pending=['Phone/emulator native execution and gallery/save/failure UI checks.','Fixed development photo pixel-parity instrumentation test.','Device performance measurement.','Correction quality, final MST validation and neck requirements.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        report_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in reports+[lint_path]})
    out.mkdir();(out/'signature.txt').write_text(signature);(out/'permissions.txt').write_text(permissions)
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','apk_bytes','apk_sha256','unit_tests_passed','fixtures','device_tested','new_model_fits']},indent=2))


if __name__=='__main__':main()
