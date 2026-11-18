"""Record completed exhaustive visual review and descriptive saved-output checks."""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/fixed_structure_nonharm_comparison_v1'

def main():
    read = lambda p: json.loads(p.read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    target = OUT / 'review_receipt_PRIVATE.json'
    assert not target.exists()
    changes = read(OUT / 'changes_PRIVATE.json')
    verified = read(OUT / 'verification_PRIVATE.json')
    assert verified['passed']
    assert sha(OUT / 'results_PRIVATE.json') == verified['result_sha256']
    d = read(OUT / 'results_PRIVATE.json')
    old = {r['case_id']: r for r in read(ROOT / 'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')['records']}
    global_rows = {r['case_id']: r for r in read(ROOT / 'outputs/colour_nonharm_comparison_v1/results_PRIVATE.json')['records']}
    changed = [r for r in d['records'] if r['candidate']['parameters'] != old[r['case_id']]['candidate']['parameters']]
    scored = [r for r in changed if r['reference_available']]
    counts = {name: sum(op(r['candidate']['region_metrics']['rgb8_mae_codes'], old[r['case_id']]['candidate']['region_metrics']['rgb8_mae_codes']) for r in scored)
              for name, op in [('better', lambda a,b:a<b), ('worse', lambda a,b:a>b), ('equal', lambda a,b:a==b)]}
    recovered = []
    for r in d['records']:
        if r['layer'] != 'core' or not r['reference_available']:
            continue
        key = 'rgb8_mae_codes'
        base = r['input_region_metrics'][key]
        if old[r['case_id']]['candidate']['region_metrics'][key] < base and global_rows[r['case_id']]['candidate']['region_metrics'][key] >= base:
            assert r['candidate']['region_metrics'][key] < base
            recovered.append(r['case_id'])
    assert len(changed) == 37 and len(scored) == 34 and len(recovered) == 6
    assert len(changes['sheets']) == 10 and len(changes['boards']) == 37
    receipt = dict(completed=True, selection=changes['selection'],
        visual_review='Primary assistant viewed all 10 change sheets, covering all 37 changed boards, via view_image on 9 November 2026.',
        observations='Many underexposed outputs remain darker than prior correction; partial facial/neck support and visible boundaries remain. No new dense mask-quality claim.',
        changed_decisions=37, changed_originals=len({r['case_id'].split('__')[0] for r in changed}),
        changed_scored=34, changed_without_reference=3, RGB_vs_previous=counts,
        recovered_benefits_lost_by_global_refit=recovered,
        unchanged_outputs_and_metric_records=719,
        unchanged_review='Prior review reused only after script 669 proved exact output pixels and candidate metric dictionaries.',
        reviewed_sheet_sha256={p:sha(Path(p)) for p in changes['sheets']},
        changed_board_sha256={p:sha(Path(p)) for p in changes['boards']},
        changes_sha256=sha(OUT/'changes_PRIVATE.json'), result_sha256=sha(OUT/'results_PRIVATE.json'),
        new_split_fits=0, holdout_image_reads=0, adopted=False)
    target.write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k:v for k,v in receipt.items() if 'sha256' not in k}, indent=2))

if __name__ == '__main__':
    main()
