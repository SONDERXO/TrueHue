"""Verify final local links/artifacts, export detailed counts, retain visual QA."""
import csv
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/paint_protection_validation_v1';summary=json.loads((out/'summary.json').read_text())
    verify=json.loads((out/'verification.json').read_text());assert verify['status']=='pass'
    assert verify['summary_sha256']==digest(out/'summary.json')
    assert all(digest(ROOT/p)==h for p,h in summary['input_sha256'].items())
    assert all(digest(ROOT/p)==h for p,h in verify['artifact_sha256'].items())
    manifest=json.loads((ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json').read_text())
    assert len(manifest['inventory'])==114
    for row in manifest['inventory']:
        assert row['partition']=='train' and row['prior_development_exposure']
        assert digest(ROOT/row['source_path'])==row['source_sha256']
    assert digest(ROOT/'data/manifests/face_boundary_reference_v1/original_export.json')=='3e4915b76bb1799fc23bbdedf20162f8757760d05520fe916a2bae4d5a8b9553'
    ready=json.loads((out/'readiness.json').read_text());assert ready['training_pairs_regenerated']==ready['models_fitted']==0
    rows=[]
    for r in summary['records']:
        for stage,arms in r['stages'].items():
            for arm,item in arms.items():
                for name,region in item['protected_regions'].items():
                    rows.append(dict(case=r['key'],stage=stage,arm=arm,region=name,reference_type='unchanged_user' if name.startswith('user_') else 'provisional_codex',**region))
    with (out/'protected_region_counts.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    html=(out/'review.html').read_text(encoding='utf-8');links=re.findall(r'(?:src|href)="([^"]+)"',html)
    assert all((out/p).is_file() for p in links)
    raw=(out/'pytest.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    assert '481 passed in 11.58s' in log and 'failed' not in log
    contacts=sorted((out/'contacts').glob('*.png'));assert len(contacts)==17
    qa=dict(status='All17 full stage/contact boards inspected by Codex; all448 available masks and unavailable panels included',
        inspected_frames=[p.stem for p in contacts],parameter_or_region_changes_after_predictions=False,
        notes='Cosmetic/forehead overlap, dark/color measurement gaps and remaining paint confirmed. Contamination witnesses remain diagnostic only; prior holds retained.',
        contacts_sha256={str(p.relative_to(ROOT)):digest(p) for p in contacts})
    (out/'visual_qa.json').write_text(json.dumps(qa,indent=2))
    files=[p for p in out.iterdir() if p.is_file() and p.name!='final_verification.json']+contacts
    result=dict(status='pass',input_hashes_unchanged=True,inventory_source_hashes_verified=114,prior_verified_artifacts_unchanged=True,
        gallery_local_links_checked=len(links),region_count_rows=len(rows),pytest='481 passed in11.58s; explicit workspace basetemp',
        finalizer_sha256=digest(Path(__file__)),artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in files})
    (out/'final_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
