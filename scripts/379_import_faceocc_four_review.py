"""Exact-bound four-case qualitative decisions; no automatic model adoption."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def validate(manifest,export,identity):
    if export.get('schema_version')!='truehue_faceocc_four_decisions_v1' or export.get('manifest_sha256')!=identity:
        raise ValueError('Wrong schema/manifest')
    rows=export['rows'];expected={r['image_id'] for r in manifest['rows']}
    if len(rows)!=4 or {r['image_id'] for r in rows}!=expected:raise ValueError('Exact four IDs required')
    fields={'old_unwanted','new_unwanted','useful_skin_lost','preference'}
    for r in rows:
        if set(r.get('decisions',{}))!=fields or not isinstance(r.get('notes'),str):raise ValueError('Missing fields/notes')
        for field,value in r['decisions'].items():
            allowed={'previous','faceocc','similar','uncertain','unavailable'} if field=='preference' else {'yes','no','uncertain','unavailable'}
            if value not in allowed:raise ValueError('Invalid/incomplete judgment')
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('decisions',type=Path);args=p.parse_args()
    folder=ROOT/'outputs/faceocc_four_review_v1';out=ROOT/'outputs/faceocc_four_review_import_v1'
    if out.exists():raise FileExistsError(out)
    raw=(folder/'manifest.json').read_bytes();manifest=json.loads(raw)
    for r in manifest['rows']:
        if r['board_path'] and hashlib.sha256((ROOT/r['board_path']).read_bytes()).hexdigest()!=r['board_sha256']:
            raise ValueError('Review board changed')
    decisions=args.decisions.read_bytes();rows=validate(manifest,json.loads(decisions),hashlib.sha256(raw).hexdigest())
    out.mkdir();(out/'original_export.json').write_bytes(decisions)
    (out/'decisions.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(dict(status='qualitative_user_judgments_imported',cases=4,
        export_sha256=hashlib.sha256(decisions).hexdigest(),manifest_sha256=hashlib.sha256(raw).hexdigest(),
        pixel_accuracy_claim=False,adopted=False),indent=2))
    print('Four qualitative decisions imported; no automatic adoption.')


if __name__=='__main__':main()
