"""Prepare a text-only thesis handoff from repository files and named aggregate evidence.

Does not traverse data/, models/, outputs/ or locked allocations. Only the exact
aggregate files below are read from outputs; all archive members come from Git's
tracked/unignored source paths. Personal appeal material stays local.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'output/thesis-web-handoff-2026-11-18'
DOCS = ROOT / 'docs/thesis'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def text(path):
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16'), 'utf-16'
    try:
        return raw.decode('utf-8-sig'), 'utf-8'
    except UnicodeDecodeError:
        return raw.decode('cp1252'), 'cp1252'


def repository_paths():
    data = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT)
    return sorted(set(p.decode('utf-8') for p in data.split(b'\0') if p))


def eligible(path):
    parts = Path(path).parts
    return (parts[0] not in {'data', 'models', 'outputs', 'output', 'tmp', '.git'}
            and 'appeal' not in path.lower() and '.kotlin' not in parts
            and Path(path).suffix.lower() in {'.md', '.py', '.json', '.txt', '.js', '.cjs', '.html', '.cmd',
                '.kt', '.kts', '.xml', '.yml', '.yaml', '.csv', '.tsv', '.ps1', '.toml', '.properties',
                '.gradle', '.bat', '.gitignore', '.code-workspace'}
            or path in {'.gitignore', 'LICENSE', 'gradlew', 'android-app/gradlew'})


def main():
    if DEST.exists():
        raise FileExistsError('Preserve this dated handoff; use a new destination for another update')
    DOCS.mkdir(exist_ok=True)
    snapshot = dict(checkpoint='2026-11-18', kind='Selected aggregate evidence, not raw data or final qualification',
                    model_ready=False, studies={})
    specs = {
        'wb314': ('outputs/wb_feature_direct_prediction_v1/summary.json', ['by_role', 'role_gates', 'added_colour_benefit', 'candidate_numeric_eligible', 'baseline_numeric_eligible']),
        'exposure_eight_rereview': ('outputs/wb_feature_exposure_rereview_ratings_v1/assessment_PRIVATE.json', ['status', 'complete_cases', 'total', 'preference_counts', 'appearance_counts', 'raw_sha256']),
        'remaining_nine_under_review': ('outputs/wb_feature_remaining_under_ratings_v1/assessment_PRIVATE.json', ['status', 'complete_cases', 'total', 'preference_counts', 'appearance_counts', 'raw_sha256']),
        'whole_pure_under_review': ('outputs/wb_feature_remaining_under_ratings_v1/combined_pure_under_assessment.json', ['cases', 'expected_role_cases', 'complete', 'preference_counts', 'appearance_counts']),
        'actual_piq_head': ('outputs/piq23_actual_head_v1/summary.json', ['Train', 'Test', 'narrow_quality_screen_pass']),
        'actual_piq_correction': ('outputs/piq23_probe_correction_prediction_v1/summary.json', ['by_role', 'role_gates', 'under_improvement', 'colour_nonworse', 'numerical_eligible', 'identity_changed']),
        'actual_piq_cue_audit': ('outputs/piq23_probe_correction_prediction_v1/independent_audit.json', ['passed', 'cue_splits', 'models_using_cues', 'numerical_eligible']),
        'complete_ppr': ('outputs/ppr_full_pipeline_prediction_v1/summary.json', ['by_role', 'role_gates', 'under_improvement', 'colour_nonworse', 'numerical_eligible', 'identity_changed', 'decision']),
    }
    for name, (source, keys) in specs.items():
        p = ROOT / source
        data = json.loads(p.read_text(encoding='utf-8'))
        selected = {k: data[k] for k in keys}
        if name == 'actual_piq_head':
            for split in ['Train', 'Test']:
                selected[split] = {k: v for k, v in selected[split].items() if k != 'per_scene'}
        snapshot['studies'][name] = dict(local_source=source, source_sha256=sha(p), values=selected)
    write_json(DOCS / 'evidence-snapshot.json', snapshot)

    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    documents = [p for p in paths if p.startswith('docs/') and p.endswith('.md') and p != 'docs/thesis/document-index.md']
    lines = ['# Complete research document index', '',
             'Generated from the current source checkout. Read [THESIS_START_HERE.md](../../THESIS_START_HERE.md) first.',
             'Titles identify records; they do not certify completion or supersede later results. Local artifact paths inside records are not published evidence files.', '',
             'Personal appeal-letter material is excluded. Original file encodings are preserved in Git; the upload text uses decoded UTF-8 copies.', '']
    for p in documents:
        value, _ = text(ROOT / p)
        title = next((s.lstrip('# ').strip() for s in value.splitlines() if s.startswith('# ')), Path(p).stem)
        title = title.replace('[', '(').replace(']', ')').replace('\n', ' ')
        relative = Path(p).relative_to('docs').as_posix()
        lines.append(f'- [{title}](../{relative}) — `{p}`')
    (DOCS / 'document-index.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    syntax_errors = []
    encodings = []
    secret_findings = []
    checks = {
        'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})',
        'openai_key': r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
        'aws_key': r'\bAKIA[0-9A-Z]{16}\b',
    }
    for p in paths:
        content, encoding = text(ROOT / p)
        if encoding != 'utf-8':
            encodings.append(dict(path=p, encoding=encoding))
        for kind, pattern in checks.items():
            if re.search(pattern, content):
                secret_findings.append(dict(path=p, kind=kind))
        if p.endswith('.py'):
            try:
                ast.parse(content, filename=p)
            except SyntaxError as error:
                syntax_errors.append(dict(path=p, line=error.lineno, error=error.msg))
    if secret_findings:
        raise RuntimeError('Publication scan needs review: ' + json.dumps(secret_findings))
    if syntax_errors:
        raise RuntimeError('Python syntax errors: ' + json.dumps(syntax_errors))

    report = dict(checkpoint='2026-11-18', publication_scope='Research documentation/source on development branch; not a validated release',
                  indexed_documents=len(documents), source_python_files=sum(p.endswith('.py') for p in paths),
                  syntax_errors=syntax_errors, high_confidence_secret_findings=secret_findings,
                  historical_non_UTF8_files_preserved=encodings,
                  focused_checks=dict(tests=['tests/test_correction_preview.py', 'tests/test_manual_refinement.py', 'tests/test_demo_current_masking.py'],
                                      result='28 passed in 5.11s', note='Generated-fixture software tests; not scientific model qualification. First sandbox run had temp-directory permission errors.'),
                  source_data_and_models_included=False, locked_allocations_accessed=False,
                  original_proposal_and_current_editable_manuscript_included=False,
                  personal_appeal_material_included=False)
    write_json(DOCS / 'publication-check.json', report)
    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    entries = [dict(path=p, bytes=(ROOT / p).stat().st_size, sha256=sha(ROOT / p)) for p in paths]
    write_json(DOCS / 'file-manifest.json', dict(files=entries, note='Manifest excludes itself; checks raw local bytes before Git line-ending conversion.'))
    paths.append('docs/thesis/file-manifest.json')

    DEST.mkdir(parents=True)
    context_paths = ['THESIS_START_HERE.md', 'docs/thesis/chatgpt-writing-prompt.md', 'docs/thesis/research-map.md',
                     'docs/thesis/evidence-snapshot.json', 'docs/thesis/publication-check.json', 'AGENTS.md']
    context_paths += [p for p in paths if p.startswith('docs/') and p.endswith('.md') and p not in context_paths]
    # Keep each text part well below the official 2M-token ceiling even under the
    # conservative one-token-per-UTF8-byte bound. This is not a tokenizer estimate.
    pieces = []
    current = 'TRUEHUE THESIS HANDOFF — 2026-11-18\nRead THESIS_START_HERE.md first. Historical records can be superseded.\n'
    for p in context_paths:
        content, encoding = text(ROOT / p)
        section = f'\n\n===== FILE: {p} | original_encoding={encoding} | sha256={sha(ROOT / p)} =====\n{content}\n===== END FILE =====\n'
        if len((current + section).encode('utf-8')) > 1_400_000 and current:
            pieces.append(current)
            current = 'TRUEHUE THESIS HANDOFF CONTINUATION — read part01 and THESIS_START_HERE.md first.\n'
        current += section
    if current:
        pieces.append(current)
    for i, content in enumerate(pieces, 1):
        (DEST / f'TrueHue-thesis-context-part{i:02d}.txt').write_text(content, encoding='utf-8')
    with zipfile.ZipFile(DEST / 'TrueHue-research-source-2026-11-18.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(paths)):
            archive.write(ROOT / p, p)
    write_json(DEST / 'verification.json', dict(passed=True, source_files=len(set(paths)), documents=len(documents),
               text_parts=len(pieces), parts={p.name: sha(p) for p in DEST.glob('*.txt')},
               source_zip_sha256=sha(DEST / 'TrueHue-research-source-2026-11-18.zip'),
               raw_datasets_photos_weights_private_outputs_included=False))
    print(json.dumps(dict(passed=True, documents=len(documents), source_files=len(set(paths)),
                         python_syntax_files=report['source_python_files'], text_parts=len(pieces),
                         historical_encodings_preserved=len(encodings), delivery=str(DEST)), indent=2))


if __name__ == '__main__':
    main()
