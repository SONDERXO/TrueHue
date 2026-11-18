"""Bind dataset review metadata; stat only the predeclared PPR10K originals."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/dataset_reference_review_20261109_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve previous review artifacts')
    report = ROOT / 'docs/dataset-correction-reference-review-2026-11-09.md'
    inputs = [report, Path(__file__).resolve()]
    links = re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf-8'))
    for link in links:
        if not link.startswith('https://'):
            p = report.parent / link
            assert p.is_file(), link
            inputs.append(p)
    files = []
    groups = []
    cohorts = [('ppr10k_inspection_v1', 6), ('ppr10k_new_group_comparison_v1', 8)]
    for name, count in cohorts:
        folder = ROOT / 'outputs' / name
        manifest = folder / 'frozen_sample.json'
        inputs.append(manifest)
        sample = json.loads(manifest.read_text(encoding='utf-8'))
        assert len(sample['frames']) == count
        groups.extend(sample['groups'])
        for role in ['source', 'target_a']:
            directory = folder / 'originals' / role
            actual = list(directory.iterdir())
            assert len(actual) == count
            assert {p.stem for p in actual} == set(sample['frames'])
            for p in actual:
                assert p.is_file() and p.stat().st_size > 0
                files.append(dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size,
                                  check='existence/membership/size only; no image-byte read'))
    assert len(files) == 28 and len(set(groups)) == 10
    bound = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in inputs}
    result = dict(passed=True, paired_photos=14, publisher_groups=10,
        publisher_training_pairs=8, publisher_validation_pairs=6,
        original_files=files, metadata_sha256=bound,
        sources=[link for link in links if link.startswith('https://')],
        limitations='Historical image integrity/profile results reused, not freshly verified; no independent-person or training-admission claim.',
        image_byte_reads=0, new_fits=0, new_inference=0, holdout_reads=0,
        recommendation='Saved-record readiness assessment of existing eight publisher-training PPR10K pairs, not another fit or acquisition.')
    OUT.mkdir()
    (OUT / 'review_PRIVATE.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    for rel, h in bound.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h
    print('PASS: 14 existing pairs, 10 publisher groups, 28 nonempty originals;')
    print('local report links and', len(bound), 'metadata hashes verified; zero image-byte reads.')


if __name__ == '__main__':
    main()
