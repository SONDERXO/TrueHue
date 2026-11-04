"""Exact-mask review import; acceptance never automatically admits training."""
import hashlib
import json


def reconcile(manifest_bytes, export, root, expected_contract):
    manifest = json.loads(manifest_bytes)
    if export.get('schema_version') != 'truehue_semantic_reference_mask_decisions_v1':
        raise ValueError('Semantic mask export required')
    if export.get('manifest_sha256') != hashlib.sha256(manifest_bytes).hexdigest():
        raise ValueError('Review manifest mismatch')
    if manifest.get('measurement_contract_sha256') != expected_contract or export.get('measurement_contract_sha256') != expected_contract:
        raise ValueError('Measurement contract mismatch')
    rows = manifest['rows']; decisions = export.get('rows', [])
    ids = [r['case_id'] for r in decisions]
    if len(ids) != len(set(ids)) or set(ids) != {r['case_id'] for r in rows}:
        raise ValueError('Exact unique review membership required')
    byid = {r['case_id']: r for r in decisions}; result = []
    for row in rows:
        review = byid[row['case_id']]
        for key in ('source_image_id', 'source_sha256', 'mask_sha256'):
            if review.get(key) != row[key]:
                raise ValueError('Decision file binding mismatch')
        for pathkey, hashkey in [('source_path', 'source_sha256'), ('mask_path', 'mask_sha256')]:
            path = (root / row[pathkey]).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError('Review path outside workspace')
            if hashlib.sha256(path.read_bytes()).hexdigest() != row[hashkey]:
                raise ValueError('Reviewed file changed')
        decision = review.get('decision')
        if decision not in ('accept', 'reject', 'uncertain'):
            raise ValueError('Finish all six decisions; pending entries cannot be imported')
        if not isinstance(review.get('notes', ''), str):
            raise ValueError('Text notes required')
        if row['source_role'] != 'train':
            raise ValueError('Only training-role masks permitted')
        result.append(dict(case_id=row['case_id'], source_image_id=row['source_image_id'],
            source_sha256=row['source_sha256'], mask_sha256=row['mask_sha256'],
            mask_decision=decision, notes=review.get('notes', ''),
            old_source_decision=row['prior_source_decision'],
            exact_reference_mask_accepted=decision == 'accept',
            training_admitted=False, distorted_mask_approval=False,
            reference_lighting_validated=False, measurement_contract_sha256=expected_contract))
    return result
