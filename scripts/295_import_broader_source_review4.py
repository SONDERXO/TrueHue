"""Import the pending four-source review when its actual export is available."""
import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate
from src.utilities.config import get_config


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--export',type=Path)
    args=parser.parse_args()
    base=ROOT/get_config().OUTPUTS_ROOT
    source=base/'broader_source_reference_review4_v1'
    export=args.export or source/'truehue_additional_source4_judgments.json'
    out=base/'broader_source_reference_review4_import_v1'
    if not export.is_file():
        print(json.dumps(dict(status='pending_actual_user_export',expected_path=str(export),decisions_inferred=0)))
        return
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[str(p)]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    spec=read(source/'spec.json');payload=read(export)
    verification=read(source/'verification.json')
    assert digest(source/'spec.json')==verification['output_sha256']['spec.json']
    module_spec=importlib.util.spec_from_file_location('review_import',ROOT/'scripts/290_import_source_reference_review3.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    reviews=module.validate(payload,spec)
    manifest=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    dispositions={r['image_id']:r for r in read(base/'correction_duplicate_audit_v1/candidate_dispositions.json')}
    saved=read(base/'correction_training_preparation_v1/verification.json')['evidence_sha256']
    previous={r['image_id'] for r in read(base/'additional_source_reference_review3_import_v1/reconciled_reviews.json')}
    rows=[]
    for r in spec['sources']:
        image_id=r['image_id'];training_candidate(image_id,manifest,policy)
        assert image_id not in previous and dispositions[image_id]['status']=='screen_clear_unreviewed'
        board=(source/r['board_url']).resolve()
        folder=base/'correction_training_preparation_v1'
        assert board.is_relative_to(folder/'boards')
        assert digest(board)==r['board_sha256']==saved[board.relative_to(folder).as_posix()]
        hashes[str(board)]=digest(board)
        evidence={}
        for suffix in ['reference.png','reference_mask.png','input.png','input_mask.png']:
            p=folder/'images'/f'{r["source_id"]}_{suffix}'
            assert digest(p)==saved[p.relative_to(folder).as_posix()]
            evidence[p.relative_to(ROOT).as_posix()]=digest(p);hashes[str(p)]=digest(p)
        judgments=reviews[image_id]
        rows.append(dict(image_id=image_id,source_id=r['source_id'],role='train',
            duplicate_group=dispositions[image_id]['duplicate_group'],judgments=judgments,
            review_spec_sha256=spec['spec_sha256'],board_sha256=r['board_sha256'],
            exact_image_and_mask_sha256=evidence,
            reference_judgments_accepted=all(judgments[s]['decision']=='accept' for s in ['reference_suitability','reference_mask']),
            displayed_stress_mask_accepted=judgments['displayed_stress_mask']['decision']=='accept',
            clipping_fraction=r['clipping_fraction'],future_variant_approval='not_granted',training_admitted=False))
    assert len(rows)==4
    hashes[str(Path(__file__))]=digest(Path(__file__))
    hashes[str(ROOT/'scripts/290_import_source_reference_review3.py')]=digest(ROOT/'scripts/290_import_source_reference_review3.py')
    assert all(digest(Path(p))==sha for p,sha in hashes.items())
    summary=dict(status='scoped_annotations_imported_not_training_admission',sources=4,
        decisions=dict(Counter(j['decision'] or 'pending' for r in rows for j in r['judgments'].values())),
        judgments_with_notes=sum(bool(j['notes']) for r in rows for j in r['judgments'].values()),
        future_variants_approved=0,training_admissions=0,model_fits=0,reserved_role_access=0)
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    for name,value in [('reconciled_reviews.json',rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',input_sha256=hashes,
        evidence_sha256={p.name:digest(p) for p in out.iterdir()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
