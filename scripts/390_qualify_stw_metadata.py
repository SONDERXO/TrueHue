"""Read-only STW metadata overlap/release audit; never opens photographs."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/stw_qualification_v1'


def main():
    if (OUT / 'qualification.json').exists(): raise FileExistsError('Audit exists')
    inputs = ['outputs/dast_sample_readiness_v1/stw-all-annotated-data.csv',
              'outputs/correction_data_redesign_v1/selection.json',
              'outputs/correction_duplicate_audit_v1/candidate_dispositions.json',
              'outputs/independent_source_inventory_v1/fairface_inventory.json',
              'data/manifests/development_exposure_additions.jsonl',
              'outputs/dast_sample_readiness_v1/stw-source.json']
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs}
    rows = list(csv.DictReader((ROOT / inputs[0]).open(encoding='utf-8-sig', newline='')))
    allocation = json.loads((ROOT / inputs[1]).read_text())['selected']
    duplicate = json.loads((ROOT / inputs[2]).read_text())
    exposure = json.loads((ROOT / inputs[3]).read_text())
    additional = [json.loads(line) for line in (ROOT / inputs[4]).read_text().splitlines() if line.strip()]
    roles = {r['image_id']: r['role'] for r in allocation}
    duplicate_byid = {r['image_id']: r for r in duplicate}
    exposed = {r['image_id'] for r in exposure if r.get('exposure_evidence')}
    exposed.update(r['image_id'] for r in additional if r.get('image_id'))
    groups = defaultdict(set)
    for r in duplicate: groups[r['duplicate_group']].add(r['image_id'])
    labels, raw_tokens, aliases = defaultdict(set), defaultdict(set), defaultdict(set)
    paths, source_counts, class_counts = Counter(), Counter(), Counter()
    fair_rows = []
    for r in rows:
        assert set(r['class']) <= set('0123456789') and 1 <= int(r['class']) <= 10
        labels[r['new_tokens']].add(r['class'])
        raw_tokens[(r['dataset'], r['tokens'])].add(r['new_tokens'])
        aliases[r['new_tokens'].strip().casefold()].add(r['new_tokens'])
        paths[r['paths']] += 1; source_counts[r['dataset']] += 1; class_counts[r['class']] += 1
        if r['dataset'] != 'FairFace': continue
        parts = PurePosixPath(r['paths'].replace('\\', '/')).parts
        matches = [i for i, value in enumerate(parts[:-1]) if value in {'train', 'val'}]
        assert len(matches) == 1
        i = matches[0]; assert i == len(parts)-2
        key = f'fairface__{parts[i]}/{parts[-1]}'
        rec = dict(stw_path=r['paths'], canonical_source_id=key, stw_provider_key=r['new_tokens'],
                   frozen_role=roles.get(key), recorded_development_exposure=key in exposed,
                   label_not_merged=True, pixel_access=False, independence='not_verified')
        known = duplicate_byid.get(key)
        if known:
            rec['duplicate_group'] = known['duplicate_group']
            rec['duplicate_status'] = known['status']
            rec['known_group_members'] = sorted(groups[known['duplicate_group']])
        fair_rows.append(rec)
    counts = Counter(r['frozen_role'] or 'not_in_frozen600' for r in fair_rows)
    support = Counter(next(iter(values)) for values in labels.values() if len(values) == 1)
    assert len(rows) == 42312 and len(paths) == 42312 and len(fair_rows) == 1031
    report = dict(csv_rows=len(rows), unique_paths=len(paths), provider_identity_keys=len(labels),
        distinct_source_token_keys=len(raw_tokens), whitespace_casefold_keys=len(aliases),
        provider_key_label_conflicts=sum(len(v)>1 for v in labels.values()),
        source_token_multi_provider_keys=sum(len(v)>1 for v in raw_tokens.values()),
        repeated_paths=sum(n-1 for n in paths.values()), image_label_counts=dict(class_counts),
        provider_key_label_counts=dict(support), source_counts=dict(source_counts),
        fairface_rows=len(fair_rows), fairface_frozen_role_overlap=dict(counts),
        fairface_recorded_exposed=sum(r['recorded_development_exposure'] for r in fair_rows),
        fairface_known_duplicate_dispositions=sum('duplicate_group' in r for r in fair_rows),
        fairface_person_ids_are_image_based=True,
        paper_claim=dict(images=42313, people=3564),
        discrepancy_resolution='unresolved; no deletion, relabelling or identity merging used to force agreement',
        actual_independent_people_verified=False, actual_skin_admitted=0, source_licence_admission=False,
        decision='NO_GO_FOR_IMAGE_PROCESSING_OR_CALIBRATION_NOW',
        scope='Readiness only; source access/terms and release identity reconciliation unresolved',
        reserved_photo_access=False, new_photo_downloads=0, inference=0, fits=0)
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    (OUT / 'qualification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (OUT / 'fairface_overlap.json').write_text(json.dumps(fair_rows, indent=2), encoding='utf-8')
    (OUT / 'input_sha256.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
