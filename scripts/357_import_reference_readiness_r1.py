"""Validate exact R1 decisions; preserve holds, never admit training rows."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(manifest, decisions, identity):
    if decisions.get('schema_version') != 'truehue_reference_readiness_r1_decisions':
        raise ValueError('Wrong decision schema')
    if decisions.get('manifest_sha256') != identity:
        raise ValueError('Manifest mismatch')
    rows = decisions['rows']
    expected = {r['image_id']: r for r in manifest['rows']}
    if len(rows) != len(expected) or {r['image_id'] for r in rows} != set(expected):
        raise ValueError('Missing, duplicate or unexpected IDs')
    result = []
    for row in rows:
        reference = expected[row['image_id']]
        d = row['decisions']
        if set(d) != set(reference['required']):
            raise ValueError('Changed required fields')
        held_source = d.get('source') in ('reject', 'uncertain')
        allowed = dict(lighting={'unknown', 'documented'},
            facial_hair={'absent', 'present', 'uncertain'}, covering={'absent', 'present', 'uncertain'},
            contamination={'absent', 'present', 'uncertain'})
        for field, value in d.items():
            if value == 'pending' and held_source:
                continue
            if value not in allowed.get(field, {'accept', 'reject', 'uncertain'}):
                raise ValueError('Invalid or incomplete decision: ' + field)
        notes = row.get('notes', '')
        if not isinstance(notes, str) or (d.get('lighting') == 'documented' and not notes.strip()):
            raise ValueError('Lighting evidence needs notes')
        source_ok = reference['source_retained'] or d.get('source') == 'accept'
        photographic_candidate = source_ok and all(d.get(f) == 'accept' for f in ['measurement', 'correction']) and d.get('contamination') == 'absent'
        result.append(dict(image_id=row['image_id'], decisions=d, notes=notes,
            retained_source_decision=reference['original_source_decision'],
            photographic_candidate=photographic_candidate,
            lighting_evidence_claimed=d.get('lighting') == 'documented',
            independent_lighting_verified=False, true_skin_colour_validated=False,
            disposition='photographic_candidate_only' if photographic_candidate else 'hold_or_reject',
            training_admitted=False))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('decisions', type=Path)
    args = parser.parse_args()
    folder = ROOT / 'outputs/reference_readiness_r1'
    out = ROOT / 'outputs/reference_readiness_r1_import'
    if out.exists():
        raise FileExistsError(out)
    raw = (folder / 'manifest.json').read_bytes()
    manifest = json.loads(raw)
    for path, digest in manifest['input_sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Bound evidence changed: ' + path)
    decision_raw = args.decisions.read_bytes()
    rows = validate(manifest, json.loads(decision_raw), hashlib.sha256(raw).hexdigest())
    summary = dict(status='readiness_only_not_training_admission', reviewed=len(rows),
        technical_holds=manifest['holds'], dispositions=dict(Counter(r['disposition'] for r in rows)),
        lighting_evidence_claims=sum(r['lighting_evidence_claimed'] for r in rows),
        independently_verified_lighting_references=0,
        decision_sha256=hashlib.sha256(decision_raw).hexdigest(),
        ready_for_training=False, reason='MST reliability and independent support remain unresolved')
    out.mkdir()
    (out / 'decisions.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (out / 'original_export.json').write_bytes(decision_raw)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
