"""Exact-bound reference judgments, without fitting or variant admission."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.semantic_measurement import contract


def main():
    p=argparse.ArgumentParser();p.add_argument('export',type=Path)
    p.add_argument('--manifest',type=Path);p.add_argument('--output-dir',type=Path);args=p.parse_args()
    out=args.output_dir or ROOT/'outputs/preferred_reference_review_import_v1'
    if out.exists():raise FileExistsError(out)
    mp=args.manifest or ROOT/'outputs/preferred_reference_review_v1/manifest.json';raw=mp.read_bytes();manifest=json.loads(raw)
    data=json.loads(args.export.read_text(encoding='utf-8'))
    if data.get('schema_version')!='truehue_preferred_reference_decisions_v1' or data.get('manifest_sha256')!=hashlib.sha256(raw).hexdigest():
        raise ValueError('Exact review export and manifest binding required')
    if manifest['measurement_contract_sha256']!=contract(ROOT)[1]:raise ValueError('Measurement contract mismatch')
    ids=[r['image_id'] for r in data['rows']]
    if len(ids)!=len(set(ids)) or set(ids)!={r['image_id'] for r in manifest['rows']}:raise ValueError('Exact unique membership required')
    saved={r['image_id']:r for r in data['rows']};records=[]
    for row in manifest['rows']:
        review=saved[row['image_id']];d=review['decisions']
        if set(d)!=set(row['required']) or any(v not in ['pending','accept','reject','uncertain'] for v in d.values()):raise ValueError('Wrong decision fields')
        source_held=d.get('source') in ['reject','uncertain']
        if not source_held and any(v=='pending' for v in d.values()):raise ValueError('Incomplete reference review')
        if not isinstance(review.get('notes',''),str):raise ValueError('Text notes required')
        for path,sha in [(row['input_path'],row['input_sha256'])]+[(p,row['mask_sha256'][k]) for k,p in row['mask_paths'].items()]:
            resolved=(ROOT/path).resolve()
            if not resolved.is_relative_to(ROOT) or hashlib.sha256(resolved.read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed file changed')
        records.append(dict(image_id=row['image_id'],kind=row['kind'],decisions=d,notes=review.get('notes',''),
            reference_preparation_eligible=not source_held and all(v=='accept' for v in d.values()),
            training_admitted=False,variant_masks_approved=False,
            original_source_decision=row['original_source_decision']))
    out.mkdir();(out/'decisions.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    summary=dict(status='reference_decisions_imported_not_training_admission',rows=len(records),
        preparation_eligible=sum(r['reference_preparation_eligible'] for r in records),
        held=sum(not r['reference_preparation_eligible'] for r in records),
        export_sha256=hashlib.sha256(args.export.read_bytes()).hexdigest(),model_fits=0)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
