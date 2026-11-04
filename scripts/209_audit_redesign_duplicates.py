"""Declared computational duplicate audit; no quality or correction inspection."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_preparation.source_partition import connected_groups


def main():
    source = ROOT / 'outputs/correction_data_redesign_v1'
    out = ROOT / 'outputs/correction_duplicate_audit_v1'
    if out.exists():
        raise FileExistsError(out)
    selection = json.loads((source / 'selection.json').read_text(encoding='utf-8'))
    candidates = {r['image_id']: r for r in selection['selected']}
    historical = set(selection['excluded_ids'])
    assert not historical.intersection(candidates)
    ids = sorted(historical | set(candidates))
    # Constrain every path before opening any image, including historical IDs.
    paths = {}
    raw_root = (ROOT / 'data/raw/FairFace').resolve()
    for image_id in ids:
        assert image_id.startswith('fairface__')
        path = (raw_root / image_id.split('__', 1)[1]).resolve()
        assert path.is_relative_to(raw_root) and path.suffix.lower() == '.jpg'
        if image_id in candidates:
            assert path == (ROOT / candidates[image_id]['relative_image_path']).resolve()
        paths[image_id] = path
    out.mkdir(parents=True)
    fingerprints, failures = [], []
    for image_id in ids:
        image = cv2.imread(str(paths[image_id]), cv2.IMREAD_COLOR)
        if image is None:
            failures.append(dict(image_id=image_id, reason='image_decode_failed'))
            continue
        digest = hashlib.sha256(str(image.shape).encode() + image.tobytes()).hexdigest()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thumbnail = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
        dhash = sum(int(bit) << i for i, bit in enumerate((thumbnail[:, 1:] > thumbnail[:, :-1]).ravel()))
        fingerprints.append(dict(image_id=image_id, decoded_sha256=digest, dhash64=f'{dhash:016x}'))
    links = []
    for index, a in enumerate(fingerprints):
        for b in fingerprints[index + 1:]:
            distance = (int(a['dhash64'], 16) ^ int(b['dhash64'], 16)).bit_count()
            exact = a['decoded_sha256'] == b['decoded_sha256']
            if exact or distance <= 4:
                links.append(dict(image_a=a['image_id'], image_b=b['image_id'], decoded_exact=exact, dhash_distance=distance))
    groups = connected_groups(ids, [(r['image_a'], r['image_b']) for r in links])
    failed = {r['image_id'] for r in failures}
    dispositions = []
    for group in groups:
        roles = {candidates[i]['role'] for i in group if i in candidates}
        conflict = bool(historical.intersection(group)) or len(roles) > 1
        for image_id in group:
            if image_id not in candidates:
                continue
            status = 'quarantine_decode_failure' if image_id in failed else ('quarantine_overlap' if conflict else 'screen_clear_unreviewed')
            dispositions.append(dict(image_id=image_id, role=candidates[image_id]['role'], duplicate_group=group[0],
                                     status=status, eligibility='not_admitted_for_fitting', subject_separation='not_verified'))
    def write(name, value):
        (out / name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    write('fingerprints.json', fingerprints)
    write('candidate_links.json', links)
    write('failures.json', failures)
    write('candidate_dispositions.json', sorted(dispositions, key=lambda r:r['image_id']))
    write('access_ledger.json', dict(phase='computational_duplicate_audit_only', image_decode_attempts=len(ids),
          successful_decodes=len(fingerprints), attempts_by_role=dict(Counter(candidates[i]['role'] if i in candidates else 'historical' for i in ids)),
          visual_reviews=0, feature_extractions=0, correction_predictions=0, model_fits=0,
          validation_test_quality_and_outcome_access='locked'))
    write('summary.json', dict(status='completed', candidates=len(candidates), historical_sources=len(historical),
          linked_pairs=len(links), decode_failures=len(failures), dispositions=dict(Counter(r['status'] for r in dispositions)),
          by_role={role:dict(Counter(r['status'] for r in dispositions if r['role']==role)) for role in sorted({r['role'] for r in dispositions})},
          protocol_sha256=hashlib.sha256((ROOT/'docs/correction-duplicate-audit-protocol.md').read_bytes()).hexdigest(),
          selection_sha256=hashlib.sha256((source/'selection.json').read_bytes()).hexdigest(),
          limitations='Duplicate screen only; no verified person separation, quality approval or fitting admission.'))
    print((out/'summary.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
