"""Build a portable, image-free development checkpoint from verified results."""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError('Output exists; choose a new directory')
    evidence, hashes = {}, {}
    for name in ['core_pipeline_check_v1', 'core_control_comparison_v1',
                 'core_feature_conflict_v1', 'core_source_readiness_v1']:
        folder = ROOT / 'outputs' / name
        summary_path, verification_path = folder / 'summary.json', folder / 'verification.json'
        verification = json.loads(verification_path.read_text(encoding='utf-8'))
        if verification['status'] != 'pass' or digest(summary_path) != verification['summary_sha256']:
            raise ValueError(f'Unverified or changed summary: {name}')
        evidence[name] = json.loads(summary_path.read_text(encoding='utf-8'))
        for p in [summary_path, verification_path]:
            hashes[p.relative_to(ROOT).as_posix()] = digest(p)
    core = evidence['core_pipeline_check_v1']
    comparison = evidence['core_control_comparison_v1']
    primary = [r for r in comparison['aggregate'] if r['scope'] == 'primary'
               and r['variant'] == 'all' and r['evaluation_kind'] == 'source_held_out']
    status = dict(status='development_checkpoint_not_final_validation',
        software=dict(attempts=len(core['records']), available=core['available'], failed=core['failed']),
        primary_source_held_out_comparison=primary,
        source_readiness=evidence['core_source_readiness_v1']['counts'],
        proposal_complete=False, operational_mst_available=False,
        open_requirements=['Validated operational MST method or documented approved amendment',
            'Correction quality: control-aware tree still worse than no correction',
            'Consistent data processing and reference quality before expanded training',
            'Face and visible-neck correction', 'Final dataset roles and evaluation splits',
            'Expert MOS and Android implementation/device evaluation'],
        limitations=['Selected exposed development sources; synthetic recovery from ordinary photos',
            'Not calibrated complexion truth or independent final performance',
            'Paint/makeup protection incomplete; CPM deferred',
            'No production model replacement or new cohort admission'],
        evidence_sha256=hashes, builder_sha256=digest(Path(__file__)))
    rows = ''.join(f'<tr><td>{html.escape(r["method"])}</td><td>{r["pairs"]}</td>'
                   f'<td>{r["sources"]}</td><td>{r["mean_ciede2000"]:.3f}</td>'
                   f'<td>{r["equal_source_mean_ciede2000"]:.3f}</td>'
                   f'<td>{r["worsened_pairs"]}</td></tr>' for r in primary)
    items = lambda values: ''.join('<li>' + html.escape(v) + '</li>' for v in values)
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>TrueHue development checkpoint</title><style>'
        'body{font:17px/1.55 system-ui;max-width:1000px;margin:40px auto;padding:0 20px;color:#172b36}'
        'table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;border:1px solid #bbc9cd;text-align:left}'
        '.notice{padding:16px;background:#fff2cf;border-left:5px solid #a46b00}h2{margin-top:32px}'
        '</style><h1>TrueHue development checkpoint</h1><p>28 October 2026</p>'
        '<p class="notice">Development demonstration. The thesis pipeline is incomplete: '
        'operational MST is unavailable and correction quality is insufficient for final adoption.</p>'
        f'<h2>Software execution</h2><p>{core["available"]} of {len(core["records"])} fixed known attempts '
        f'produce outputs; {core["failed"]} failure is retained. Successful execution does not establish correction accuracy.</p>'
        '<h2>Source-held-out correction comparison</h2>'
        '<p>Same 22 eligible development probes from six sources. Lower CIEDE2000 is better. '
        'The frozen runtime seen-source comparator is deliberately excluded from this table.</p>'
        '<table><tr><th>Method</th><th>Pairs</th><th>Sources</th><th>Pair mean</th>'
        '<th>Equal-source mean</th><th>Worsened pairs</th></tr>' + rows + '</table>'
        '<p>Controls improve the older recipe but remain worse than no correction. '
        'The saved-fold diagnostic found both conflicting synthetic targets near recorded measurements '
        'and sparse tree-routing support; no exact feature collisions or impossibility claim.</p>'
        '<h2>Existing data readiness</h2><p>114 known TRAIN sources inventoried; '
        '35 original pair acceptances across 10 sources. The proposed 32 regenerated candidates '
        'across nine sources retain processing and coverage concerns. No new core pairs admitted.</p>'
        '<h2>Unfinished requirements</h2><ul>' + items(status['open_requirements']) + '</ul>'
        '<h2>Interpretation limits</h2><ul>' + items(status['limitations']) + '</ul>'
        '<p>This image-free report can be viewed offline. checkpoint.json records the exact source-report hashes. '
        'It summarizes saved verified evidence; it does not rerun inference, tests or model fitting.</p></html>')
    # Create only after every input has passed its summary verification.
    args.output_dir.mkdir(parents=True)
    (args.output_dir / 'checkpoint.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    (args.output_dir / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps(dict(status=status['status'], output=str(args.output_dir.resolve()),
                         evidence_reports_verified=len(evidence)), indent=2))


if __name__ == '__main__':
    main()
