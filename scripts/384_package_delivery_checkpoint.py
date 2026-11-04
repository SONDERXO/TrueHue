"""Aggregate-only local thesis/delivery snapshot; no inference, fitting or uploads."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/delivery_checkpoint_20261101_v1'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify():
    manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    assert all(digest(ROOT/p)==h for p,h in manifest['source_sha256'].items())
    assert all(digest(OUT/p)==h for p,h in manifest['package_sha256'].items())
    rows=json.loads((OUT/'metrics.json').read_text())
    with (OUT/'metrics.csv').open(encoding='utf-8-sig',newline='') as f:table=list(csv.DictReader(f))
    assert len(rows)==len(table)
    for saved,actual in zip(rows,table):
        for key in ['component','scope','metric','unit']:assert str(saved[key])==actual[key]
        assert float(saved['value'])==float(actual['value'])
    with zipfile.ZipFile(OUT/'evidence.zip') as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(manifest['package_sha256'])|{'manifest.json'}
        assert all(Path(name).suffix in {'.md','.json','.csv','.html','.txt'} for name in z.namelist())
        assert all(hashlib.sha256(z.read(name)).hexdigest()==h for name,h in manifest['package_sha256'].items())
    print('Verified source/snapshot hashes, CSV/JSON parity and aggregate-only archive.')


def main():
    if OUT.exists():raise FileExistsError(OUT)
    hashes={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))}
    def read(rel):hashes[rel]=digest(ROOT/rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    mst=read('outputs/nostril_mst_calibration_v4/summary.json')['metrics']['overall']
    first=read('outputs/faceocc_diagnostic_v1/verification.json')
    broad=read('outputs/faceocc_light_comparison_v1/verification.json')
    human=read('outputs/faceocc_light_conclusion_v1/summary.json')
    service=read('outputs/faceocc_development_service_v1/verification.json')
    feasible=read('outputs/faceocc_mst_feasibility_v1/decision.json')
    android=read('outputs/android_reliability_20261031_v1/verification.json')
    apk=ROOT/android['apk_path'];assert digest(apk)==android['apk_sha256']
    hashes[android['apk_path']]=digest(apk)
    xml_path=ROOT/'outputs/android_reliability_20261031_v1/native_tests_0.xml'
    hashes[str(xml_path.relative_to(ROOT)).replace('\\','/')]=digest(xml_path)
    assert digest(xml_path)==android['files']['native_tests_0.xml']
    xml=ET.parse(xml_path).getroot();tests=list(xml.iter('testcase'))
    assert len(tests)==6 and not any(list(t.iter('failure'))+list(t.iter('error'))+list(t.iter('skipped')) for t in tests)
    metrics=[]
    def metric(component,scope,name,value,unit):metrics.append(dict(component=component,scope=scope,metric=name,value=value,unit=unit))
    for key in ['attempts','subjects','measured','processing_failures']:
        metric('nostril_MST','exposed_15subject_development',key,mst[key],'count')
    for name in ['ordinal_mae','equal_subject_mae','exact_accuracy','within_one_accuracy']:
        metric('nostril_MST','same393photos_candidate',name,mst['candidate'][name],
            'category_steps' if 'mae' in name else 'fraction')
        metric('nostril_MST','same393photos_median_baseline',name,mst['paired_baseline'][name],
            'category_steps' if 'mae' in name else 'fraction')
    metric('FaceOcc','first_sparse_diagnostic','paired_masks',first['mask_feature_replays'],'count')
    metric('FaceOcc','first_sparse_diagnostic','non_skin_marks_remaining',first['known_non_skin_marks_still_selected'],'of_4_marks')
    metric('FaceOcc','first_sparse_diagnostic','skin_marks_retained',first['known_skin_marks_retained'],'of_2_marks')
    for name in ['attempts','paired_outputs','remaining_failures']:
        metric('FaceOcc','broader_qualitative',name,broad[name],'count')
    for choice in ['faceocc','similar','previous']:
        metric('FaceOcc','four_actual_user_judgments','preference_'+choice,human['preference_counts'].get(choice,0),'of_4_cases')
    metric('FaceOcc','saved_service_parity','exact_replays',service['exact_mask_feature_aligned_replays'],'of_35_available')
    metric('FaceOcc','saved_service_parity','failure_guards',service['failed_parent_guards'],'of_14_failures')
    for name in ['matching_mst_attempts','matching_technical_measurements','matching_subjects','current_matching_calibration_admitted']:
        metric('FaceOcc_MST','readiness_only',name,feasible[name],'count')
    metric('Android','saved_API35_x86_64_emulator','native_tests_passed',android['native_tests_passed'],'count')
    metric('Android','saved_JVM_tests','tests_passed',android['local_JVM_tests_passed'],'count')
    claims=[dict(component='Python previews',established='Whole-face+neck support, inward blending and hole repair',
        limitation='Illustrative settings; not reliable automatic correction'),
        dict(component='FaceOcc measurement',established='Experimental candidate; diagnostic gains and saved parity',
        limitation='Skin loss/occlusion and independent validation unresolved; not in deployed demos'),
        dict(component='MST',established='Reproducible exposed held-subject development results',
        limitation='Unreliable; no matching FaceOcc lookup or new training'),
        dict(component='Android',established='Existing offline experimental baseline, emulator flow and bounded tests',
        limitation='Not FaceOcc/newwhole-face-neck; no physical-phone/general parity or validated correction'),
        dict(component='Expert appraisal',established='Google Form/refinement policy recorded',
        limitation='No responses or final MOS claimed')]
    docs=['delivery-checkpoint-2026-11-01.md','thesis-results-addendum-2026-11-01.md','panel-change-register.md',
        'adopted-masking-design-2026-11-01.md','reference-r1-and-continuity-results-2026-11-01.md',
        'nostril-mst-calibration-results-2026-11-01.md','faceocc-comparison-evidence-2026-11-01.md',
        'faceocc-light-review-results-2026-11-01.md','faceocc-qualitative-conclusion-2026-11-01.md',
        'faceocc-development-service-results-2026-11-01.md','faceocc-mst-feasibility-decision-2026-11-01.md',
        'android-integration-2026-10-31.md','android-emulator-check-2026-10-31.md','android-reliability-check-2026-10-31.md']
    OUT.mkdir();(OUT/'documents').mkdir()
    for name in docs:
        path=ROOT/'docs'/name;hashes['docs/'+name]=digest(path)
        (OUT/'documents'/name).write_bytes(path.read_bytes())
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    with (OUT/'metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(metrics[0]));writer.writeheader();writer.writerows(metrics)
    (OUT/'claims.json').write_text(json.dumps(claims,indent=2))
    (OUT/'README.txt').write_text('TrueHue local evidence checkpoint,1November2026.\nAggregate values and document snapshots only; no raw photos, model weights, APK or individual prediction records.\nNot a submitted thesis or validated product. Earlier documents retain dated context and some workspace-only links. Start with index.html and delivery checkpoint.\nCurrentAPKchecksum checked against saved record; tests are historical evidence, not rerun by packaging.\nVerify from workspace: venv\\Scripts\\python.exe scripts/384_package_delivery_checkpoint.py --verify\n',encoding='utf-8')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrueHue delivery checkpoint</title><style>body{font:18px/1.5 system-ui;max-width:1100px;margin:auto;padding:24px}td,th{padding:12px;border:1px solid #bbb}table{border-collapse:collapse}</style><h1>TrueHue —1November2026 evidence checkpoint</h1><p>Engineering and development evidence. Reliable MST and final automatic correction remain unfinished. This local package contains no raw photos or model files.</p><table><tr><th>Component</th><th>Established</th><th>Limit</th></tr>'+''.join('<tr>'+''.join('<td>'+html.escape(r[k])+'</td>' for k in ['component','established','limitation'])+'</tr>' for r in claims)+'</table><p><a href="metrics.csv">Scoped aggregate metrics CSV</a> · <a href="metrics.json">Metrics JSON</a></p><h2>Document snapshots</h2><ul>'+''.join('<li><a href="documents/'+name+'">'+html.escape(name)+'</a></li>' for name in docs)+'</ul><p>Document references outside this snapshot may require the original workspace. No new experiment, APKbuild or phone test was performed.</p></html>'
    (OUT/'index.html').write_text(page,encoding='utf-8')
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    package={str(p.relative_to(OUT)).replace('\\','/'):digest(p) for p in OUT.rglob('*') if p.is_file()}
    (OUT/'manifest.json').write_text(json.dumps(dict(source_sha256=hashes,package_sha256=package,
        apk_sha256=android['apk_sha256'],native_xml_cases_checked=6,aggregate_rows=len(metrics),
        no_raw_data_or_model_files_embedded=True,new_inference=False,new_fits=False),indent=2))
    with zipfile.ZipFile(OUT/'evidence.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in list(package)+['manifest.json']:z.write(OUT/name,name)
    verify()
    print('Saved aggregate-only archive: '+str(OUT/'evidence.zip'))


if __name__=='__main__':verify() if '--verify' in sys.argv else main()
