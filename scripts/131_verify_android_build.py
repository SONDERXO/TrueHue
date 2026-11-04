"""Record SDK revisions and verify the actual debug APK/test/lint artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--jdk', type=Path, default=Path('C:/Program Files/Android/openjdk/jdk-21.0.8'))
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    sdk = ROOT / 'outputs/android_toolchain/sdk'
    packages = []
    for path in ['cmdline-tools/19.0', 'platforms/android-35', 'build-tools/34.0.0', 'platform-tools']:
        folder = sdk / path
        properties = folder / 'source.properties'
        assert properties.is_file(), path
        packages.append(dict(path=path, source_properties=properties.read_text(), sha256=digest(properties)))
    app = ROOT / 'android-app/app'
    apk = app / 'build/outputs/apk/debug/app-debug.apk'
    assert apk.is_file()
    signature = subprocess.run([str(args.jdk / 'bin/java.exe'), '-jar',
                               str(sdk / 'build-tools/34.0.0/lib/apksigner.jar'),
                               'verify', '--verbose', str(apk)],
                              check=True, capture_output=True, text=True).stdout
    assert signature.startswith('Verifies')
    asset = app / 'src/main/assets/decision_tree.json'
    with zipfile.ZipFile(apk) as zipped:
        assert 'AndroidManifest.xml' in zipped.namelist() and 'classes.dex' in zipped.namelist()
        assert zipped.read('assets/decision_tree.json') == asset.read_bytes()
        assert zipped.read('assets/decision_tree.sha256').decode().strip() == digest(asset)
    reports = sorted((app / 'build/test-results/testDebugUnitTest').glob('TEST-*.xml'))
    assert reports, 'Missing actual unit test results'
    count = 0
    for report in reports:
        suite = ET.parse(report).getroot()
        assert int(suite.get('failures', 0)) == int(suite.get('errors', 0)) == 0
        assert int(suite.get('skipped', 0)) == 0
        count += int(suite.get('tests'))
    assert count >= 14
    lint_path = app / 'build/reports/lint-results-debug.xml'
    lint = ET.parse(lint_path).getroot()
    issues = [dict(id=i.get('id'), severity=i.get('severity'), message=i.get('message')) for i in lint.findall('issue')]
    assert not any(i['severity'] in ('Error', 'Fatal') for i in issues)
    result = dict(status='debug_apk_built_unit_tests_and_lint_pass',
                  apk=str(apk.relative_to(ROOT)), apk_sha256=digest(apk), apk_bytes=apk.stat().st_size,
                  unit_tests_passed=count, lint_issues=issues, sdk_packages=packages,
                  packaged_tree_sha256=digest(asset), device_tested=False,
                  apk_signature_verified=True, android_loader_compiled=True,
                  image_pipeline_integrated=False, mst_available=False, proposal_complete=False,
                  limitation='Existing UI scaffold plus verified tree component; not full image correction or final model quality.',
                  report_sha256={str(p.relative_to(ROOT)): digest(p) for p in reports + [lint_path]})
    args.output_dir.mkdir(parents=True)
    (args.output_dir / 'apk_signature.txt').write_text(signature)
    (args.output_dir / 'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('sdk_packages', 'report_sha256', 'lint_issues')}, indent=2))


if __name__ == '__main__':
    main()
