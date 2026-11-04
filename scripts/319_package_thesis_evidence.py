"""Export saved aggregate evidence only; no fitting, inference or photo access."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/thesis_evidence_package_20261030_v1'
TABLES=ROOT/'docs/thesis-results-tables-2026-10-30.md'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    for name,sha in manifest['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in manifest['package_sha256'].items():assert digest(OUT/name)==sha,name
    assert digest(TABLES)==manifest['tables_document_sha256']
    with (OUT/'correction_aggregates.csv').open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    evidence=json.loads((OUT/'correction_aggregates.json').read_text())
    assert len(rows)==len(evidence)
    for actual,expected in zip(rows,evidence):
        for key in ['cycle','method','scope']:assert actual[key]==expected[key]
        for key in ['cases','sources']:assert int(actual[key])==expected[key]
        for key in ['case_weighted_ciede2000','source_equal_ciede2000']:
            assert float(actual[key])==expected[key]
    print('PASS: package/source hashes, generated document and full-precision CSV/JSON parity;',len(rows),'correction aggregates.')


def main():
    if OUT.exists() or TABLES.exists():raise FileExistsError('Refusing existing evidence package or generated document')
    sources={}
    def read(relative):
        path=ROOT/relative;sources[relative]=digest(path)
        return json.loads(path.read_text(encoding='utf-8'))
    primary=read('outputs/reviewed_primary_comparison_v1/summary.json')
    broader=read('outputs/broader_source_comparison_v1/summary.json')
    pv=read('outputs/reviewed_primary_comparison_v1/verification.json')
    bv=read('outputs/broader_source_comparison_v1/verification.json')
    assert pv['status']==bv['status']=='pass'
    assert sources['outputs/reviewed_primary_comparison_v1/summary.json']==pv['evidence_sha256']['summary.json']
    assert sources['outputs/broader_source_comparison_v1/summary.json']==bv['evidence_sha256']['summary.json']
    mst=read('outputs/mst_evidence_audit_20261030_v1/audit.json')
    original_mst=read('outputs/mst_monotone_square256_v1/summary.json')
    assert mst['monotone_overall']==original_mst['metrics']['overall']
    for relative,sha in mst['input_sha256'].items():assert digest(ROOT/relative)==sha,relative
    data=[];seen=set()
    for r in primary['aggregates']:
        data.append(dict(cycle='primary105',method=r['method'],scope=r['scope'],cases=r['pairs'],sources=r['sources'],
            case_weighted_ciede2000=r['mean_ciede2000'],source_equal_ciede2000=r['source_equal_ciede2000']))
        if r['scope'] not in seen:
            data.append(dict(cycle='primary105',method='no_correction',scope=r['scope'],cases=r['pairs'],sources=r['sources'],
                case_weighted_ciede2000=r['no_correction'],source_equal_ciede2000=r['source_equal_no_correction']))
            seen.add(r['scope'])
    for r in broader['aggregates']:
        data.append(dict(cycle='broader121',method=r['method'],scope=r['scope'],cases=r['cases'],sources=r['sources'],
            case_weighted_ciede2000=r['case_weighted'],source_equal_ciede2000=r['source_equal']))
    assert len({(r['cycle'],r['method'],r['scope']) for r in data})==len(data)
    m=mst['monotone_overall'];mapping=[]
    for name in ['ordinal_mae','equal_subject_mae','exact_accuracy','within_one_accuracy']:
        mapping.append(dict(metric=name,candidate=m['candidate'][name],same_row_median=m['paired_baseline'][name],
            attempts=m['attempts'],predictions=m['available_predictions'],subjects=m['subjects'],processing_failures=m['processing_failures']))
    OUT.mkdir()
    def write_json(name,payload):(OUT/name).write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
    def write_csv(name,rows):
        with (OUT/name).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write_json('correction_aggregates.json',data);write_csv('correction_aggregates.csv',data)
    write_json('mst_metrics.json',mapping);write_csv('mst_metrics.csv',mapping)
    decisions=dict(primary_candidate_adopted=False,expanded_candidate_adopted=False,
        primary_clean_failures=primary['gates']['primary_candidate']['harmed_clean_ids'],
        broader_clean_failures=broader['clean_failures'],broader_failed_gates=[k for k,v in broader['gates'].items() if not v],
        mst_final_validated=False,mst_actual_output_range=mst['actual_lookup_output_range'],
        correction_demo='Older ten-source baseline5/fold1, failed quality gate; no model switch.',
        parser_beard_work='On hold pending adviser discussion',reserved_evaluation='Locked against fitting/tuning; historical duplicate auditing disclosed',
        new_model_fits=0,new_inference=0,raw_photos_included=False,independent_final_validation=False)
    assert not primary['gates']['primary_candidate']['passed'] and not broader['passed']
    write_json('decisions.json',decisions)
    lines=['# TrueHue results tables — 30 October 2026','',
        'Generated from saved aggregate summaries by script319. Lower CIEDE2000 is better. '
        'Compare methods within a matched evaluation set; differences between the105- and121-case totals are not isolated treatment effects.',
        '', '## Correction comparisons','',
        '| Cycle | Scope | Method | Cases | Sources | Case-weighted CIEDE2000 | Source-equal CIEDE2000 |',
        '|---|---|---|---:|---:|---:|---:|']
    for r in data:
        lines.append('| '+ ' | '.join([r['cycle'],r['scope'],r['method'],str(r['cases']),str(r['sources']),
            format(r['case_weighted_ciede2000'],'.3f'),format(r['source_equal_ciede2000'],'.3f')])+' |')
    lines+=['','Primary105 methods: frozen_endpoint_baseline is the retained endpoint reference; primary_candidate is the rejected normal-data candidate. '
        'Broader121 methods: A is endpoint, B is prior primary, C is expanded primary. no_correction preserves each input.',
        '', '## Clean-image safety','', '| Cycle | Reference changed | Candidate changed | Decision |',
        '|---|---:|---:|---|','| Primary105 | 1/26 | 3/26 | Candidate not adopted |',
        '| Broader121 | A:2/32; B:3/32 | C:4/32 | Candidate not adopted |',
        '', '## MST held-subject development evaluation','',
        '| Metric | Monotone mapping | Same-row median baseline |','|---|---:|---:|']
    for r in mapping:
        percent=r['metric'].endswith('accuracy')
        fmt=lambda value:format(value*100,'.2f')+'%' if percent else format(value,'.3f')
        lines.append('| '+r['metric']+' | '+fmt(r['candidate'])+' | '+fmt(r['same_row_median'])+' |')
    lines+=['','418 attempts,396 predictions,15 measured subjects,22 processing failures. '
        '180 measured images lacked same-category fitting-subject support. The packaged lookup emits labels1–9, not10. '
        'All figures are disclosed development evidence; neither mapping nor correction is finally validated.',
        '', '## Provenance and use','',
        'Full-precision CSV/JSON tables and a source/file checksum manifest are in '
        '`outputs/thesis_evidence_package_20261030_v1/`. This package contains aggregates, not photographs, model weights or individual predictions. '
        'The local result galleries remain separate. No fitting or inference was performed to prepare these tables.',
        '', '[Methods/results draft](thesis-methods-results-draft.md) · '
        '[MST limitations](mst-evidence-checkpoint-2026-10-30.md) · '
        '[Adviser decisions](adviser-decision-brief-2026-10-30.md)', '']
    TABLES.write_text('\n'.join(lines),encoding='utf-8')
    # Snapshot only selected prose, never source images, code/models or raw manifests.
    docs=['thesis-methods-results-draft.md','mst-evidence-checkpoint-2026-10-30.md',
        'adviser-decision-brief-2026-10-30.md','controlled-reference-capture-proposal.md',
        'demo-reporting-update-2026-10-30.md','thesis-results-tables-2026-10-30.md']
    (OUT/'documents').mkdir()
    for name in docs:
        source=ROOT/'docs'/name;sources['docs/'+name]=digest(source)
        (OUT/'documents'/name).write_bytes(source.read_bytes())
    readme='''# Local thesis evidence package

Start with documents/thesis-methods-results-draft.md and the generated results
tables. CSV/JSON files preserve full precision; Markdown rounds for reading.
decisions.json preserves failure/nonadoption status. Both correction cycles
failed their predeclared safety gates. MST remains experimental.

This is a local review package, not a final thesis submission or validated
release. No files were sent or published. It contains no photographs, model
weights, participant-level predictions, credentials or absolute source paths.
External local gallery links mentioned in copied prose may require the original
workspace; this package does not embed those images. Read the documents in the
workspace for their complete cross-references.

Verify from the project root:
venv\\Scripts\\python.exe scripts/319_package_thesis_evidence.py --verify

Independent final evaluation, final MST validation, neck correction and Android
integration remain unfinished. Parser/beard work and new correction trials stay
paused. The adviser brief and capture protocol are discussion drafts.
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    sources['scripts/319_package_thesis_evidence.py']=digest(Path(__file__))
    manifest=dict(schema_version='truehue_thesis_evidence_v1',source_sha256=sources,
        tables_document_sha256=digest(TABLES),new_fits=0,new_inference=0,new_test_suite_run=False,
        package_sha256={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()})
    write_json('manifest.json',manifest);verify()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true')
    verify() if parser.parse_args().verify else main()
