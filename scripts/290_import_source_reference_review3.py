"""Import exact scoped judgments without admitting sources or fitting models."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate
from src.utilities.config import get_config


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(payload,spec):
    clean={k:v for k,v in spec.items() if k!='spec_sha256'}
    expected=hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if expected!=spec['spec_sha256']:raise ValueError('Specification content hash mismatch')
    if payload.get('schema_version')!='truehue_source_reference_review_v1' or payload.get('spec_sha256')!=expected:
        raise ValueError('Export does not match exact review specification')
    reviews=payload.get('reviews')
    if not isinstance(reviews,dict) or set(reviews)!={r['image_id'] for r in spec['sources']}:
        raise ValueError('Exact reviewed source membership required')
    for image_id,entry in reviews.items():
        if not isinstance(entry,dict) or set(entry)!=set(spec['scopes']):raise ValueError('Exact judgment scopes required')
        for scope,value in entry.items():
            if not isinstance(value,dict) or value.get('decision') not in {'','accept','reject','uncertain'} or not isinstance(value.get('notes'),str):
                raise ValueError('Invalid scoped judgment')
    return reviews


def main():
    base=ROOT/get_config().OUTPUTS_ROOT
    source=base/'additional_source_reference_review3_v1'
    out=base/'additional_source_reference_review3_import_v1'
    if out.exists():raise FileExistsError(out)
    paths=[source/'spec.json',source/'truehue_additional_source3_judgments.json',
        source/'verification.json',base/'correction_data_redesign_v1/selection.json',
        base/'correction_data_redesign_v1/access_policy.json',
        base/'correction_duplicate_audit_v1/candidate_dispositions.json',
        base/'correction_training_preparation_v1/attempts.jsonl',
        base/'correction_training_preparation_v1/verification.json',Path(__file__)]
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    spec,payload=read(paths[0]),read(paths[1]);reviews=validate(payload,spec)
    assert digest(paths[0])==read(paths[2])['output_sha256']['spec.json']
    manifest,policy=read(paths[3]),read(paths[4])
    dispositions={r['image_id']:r for r in read(paths[5])}
    attempts={r['image_id']:r for r in map(json.loads,paths[6].read_text().splitlines())}
    saved=read(paths[7])['evidence_sha256']
    assert digest(paths[6])==saved['attempts.jsonl']
    rows=[]
    for r in spec['sources']:
        image_id=r['image_id'];training_candidate(image_id,manifest,policy)
        assert dispositions[image_id]['status']=='screen_clear_unreviewed'
        board=(source/r['board_url']).resolve()
        assert board.is_relative_to(base/'correction_training_preparation_v1/boards')
        assert digest(board)==r['board_sha256']==saved[board.relative_to(base/'correction_training_preparation_v1').as_posix()]
        hashes[board.relative_to(ROOT).as_posix()]=digest(board)
        a=attempts[image_id]
        exact_evidence={}
        for suffix in ['reference.png','reference_mask.png','input.png','input_mask.png']:
            p=base/'correction_training_preparation_v1/images'/f'{r["source_id"]}_{suffix}'
            assert digest(p)==saved[p.relative_to(base/'correction_training_preparation_v1').as_posix()]
            exact_evidence[p.relative_to(ROOT).as_posix()]=digest(p)
        hashes.update(exact_evidence)
        judgments=reviews[image_id]
        rows.append(dict(image_id=image_id,source_id=r['source_id'],role='train',
            duplicate_group=dispositions[image_id]['duplicate_group'],
            judgments=judgments,review_spec_sha256=spec['spec_sha256'],
            board_sha256=r['board_sha256'],exact_image_and_mask_sha256=exact_evidence,
            reference_judgments_accepted=all(judgments[s]['decision']=='accept' for s in ['reference_suitability','reference_mask']),
            displayed_stress_mask_accepted=judgments['displayed_stress_mask']['decision']=='accept',
            original_processing_status=a['status'],clipping_fraction=a['clipping_fraction'],
            reference_color_truth='dataset_reconstruction_reference_not_calibrated_skin_truth',
            future_variant_approval='not_granted',training_admitted=False))
    summary=dict(status='scoped_annotations_imported_not_training_admission',sources=len(rows),
        judgments=sum(len(r['judgments']) for r in rows),
        decisions=dict(Counter(j['decision'] or 'pending' for r in rows for j in r['judgments'].values())),
        judgments_with_notes=sum(bool(j['notes']) for r in rows for j in r['judgments'].values()),
        reference_approved_with_notes=sum(r['reference_judgments_accepted'] and bool(r['judgments']['reference_mask']['notes']) for r in rows),
        preserved_stress_cases=sum(r['clipping_fraction']>0 for r in rows),
        new_training_admissions=0,model_fits=0,raw_image_decodes=0,reserved_role_access=0)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    out.mkdir()
    (out/'original_user_export.json').write_bytes(paths[1].read_bytes())
    for name,value in [('reconciled_reviews.json',rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',verified_scoped_judgments=9,
        source_guard_and_duplicate_screen=True,exact_boards_and_four_derivatives_per_source=True,
        input_sha256=hashes,evidence_sha256={p.name:digest(p) for p in out.iterdir()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
