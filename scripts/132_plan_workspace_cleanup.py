"""Inventory disposable generated files; deletion is a separate checked PS step."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/workspace_cleanup_20261028_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    tracked = set(subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, check=True,
                                 capture_output=True).stdout.decode().split('\0'))
    candidates = {}

    def add(path, reason):
        if path.exists():
            candidates[path] = reason

    add(ROOT / '.pytest_cache', 'pytest discovery/history cache')
    for path in (ROOT / 'outputs').iterdir():
        if path.is_dir() and (path.name.startswith('pytest_') or '_pytest_' in path.name or path.name.endswith('_full_tests_v1')):
            add(path, 'old pytest temporary workspace; final test counts/reports retained elsewhere')
    for name in ['intermediates', 'tmp', 'kotlin', 'generated']:
        add(ROOT / 'android-app/app/build' / name, 'rebuildable Android intermediate; APK/reports/test-results retained')
    add(ROOT / 'outputs/android_toolchain/commandlinetools-win-13114758_latest.zip',
        'verified SDK installer archive; installed SDK and provenance retained')
    add(ROOT / 'outputs/android_toolchain/gradle-threads.txt', 'one-off successful-build diagnostic thread dump')
    # Avoid scanning datasets, installed SDK/Gradle trees and Git internals.
    prune = {ROOT / n for n in ['.git', 'data', 'models', 'outputs/android_toolchain', 'android-app/app/build']}
    for directory, dirs, files in os.walk(ROOT, followlinks=False):
        parent = Path(directory)
        dirs[:] = [n for n in dirs if parent / n not in prune
                   and not (parent / n).is_symlink() and not (parent / n).is_junction()]
        if parent in candidates:
            dirs[:] = []
            continue
        if '__pycache__' in dirs:
            add(parent / '__pycache__', 'regenerable Python bytecode cache')
            dirs.remove('__pycache__')
        if 'pytest_tmp' in dirs and parent.is_relative_to(ROOT / 'outputs'):
            add(parent / 'pytest_tmp', 'nested pytest temporary workspace')
            dirs.remove('pytest_tmp')
    # Remove redundant children of already selected directories.
    paths = sorted(candidates, key=lambda p: (len(p.parts), str(p)))
    selected = []
    for path in paths:
        if not any(path.is_relative_to(p) for p in selected):
            selected.append(path)
    records = []
    for path in selected:
        assert path.resolve().is_relative_to(ROOT.resolve()) and path.resolve() != ROOT.resolve()
        assert not path.is_symlink() and not path.is_junction()
        files = [path] if path.is_file() else list(p for p in path.rglob('*') if p.is_file())
        if path.is_dir():
            assert not any(p.is_symlink() or p.is_junction() for p in path.rglob('*')), path
        relative = path.relative_to(ROOT).as_posix()
        assert not any(t == relative or t.startswith(relative + '/') for t in tracked if t), relative
        records.append(dict(path=relative, absolute_path=str(path.resolve()), reason=candidates[path],
                            files=len(files), bytes=sum(p.stat().st_size for p in files)))
    # Protect every non-disposable development/evidence file and freeze its hash.
    # Raw data, model assets and installed dependencies are outside all delete paths.
    protected = {}
    for folder in ['src', 'scripts', 'tests', 'docs', 'data/manifests', 'models', 'outputs']:
        start = ROOT / folder
        for directory, dirs, names in os.walk(start, followlinks=False):
            parent = Path(directory)
            dirs[:] = [n for n in dirs if parent / n not in selected
                       and parent / n != ROOT / 'outputs/android_toolchain'
                       and not (parent / n).is_symlink() and not (parent / n).is_junction()]
            for name in names:
                p = parent / name
                if p in selected or p.suffix.lower() in {'.pyc', '.pyo'}:
                    continue
                # Preserve original reports, images, masks, labels and fitted models.
                protected[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    for p in [ROOT / 'AGENTS.md', ROOT / 'README.md', ROOT / '.gitignore',
              ROOT / 'pyproject.toml', ROOT / 'requirements.txt']:
        protected[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    OUT.mkdir()
    plan = dict(status='audited_disposable_generated_files_only', root=str(ROOT.resolve()),
                candidates=records, files=sum(r['files'] for r in records),
                bytes=sum(r['bytes'] for r in records), protected_sha256=protected,
                retained=['datasets and raw sources', 'all model artifacts including deferred CPM',
                          'review decisions, manifests, masks and historical experiment evidence',
                          'source, scripts, tests and thesis docs', 'venv and installed SDK/Gradle dependencies',
                          'built APK and Android test/lint reports', 'unique helper scripts under tmp'])
    (OUT / 'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
    print(json.dumps(dict(targets=len(records), files=plan['files'], mib=round(plan['bytes']/1048576, 2),
                         protected_files=len(protected)), indent=2))


if __name__ == '__main__':
    main()
