"""Apply exact-monochrome and explicit source rejection to existing train frames."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
from src.data_preparation.color_reference_quality import assess_color_reference


def main():
    parent=ROOT/'outputs/correction_training_preparation_v1';out=ROOT/'outputs/training_reference_color_audit_v1'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    reviews=ROOT/'outputs/focused_semantic_mask_review_import_v1/reconciled_reviews.json'
    annotations=json.loads(reviews.read_text(encoding='utf-8'))
    # Explicit source-unsuitability annotation, not every mask-only rejection.
    human_rejected={r['image_id'] for r in annotations if r['source_id']=='55166' and r['candidate_decision']=='reject'}
    assert human_rejected=={'fairface__train/55166.jpg'}
    reserved_path=ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json'
    reserved={r['image_id'] for r in json.loads(reserved_path.read_text(encoding='utf-8'))['sources']}
    rows=[json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=[r for r in rows if r['image_id'] not in reserved]
    verification=json.loads((parent/'verification.json').read_text(encoding='utf-8'))
    result=[]
    for r in rows:
        relative=f'images/{r["source_id"]}_reference.png';path=parent/relative
        assert digest(path)==verification['evidence_sha256'][relative]
        assessment=assess_color_reference(cv2.imread(str(path)),human_rejected=r['image_id'] in human_rejected)
        result.append(dict(image_id=r['image_id'],source_id=r['source_id'],reference_sha256=digest(path),**assessment))
    assert len(result)==406 and not reserved&{r['image_id'] for r in result}
    out.mkdir()
    (out/'source_dispositions.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    summary=dict(status='training_reference_quality_audit_only',sources=406,reserved_training_sources_skipped=12,
        dispositions=dict(Counter(r['status'] for r in result)),
        excluded_ids=[r['source_id'] for r in result if r['status']=='excluded_reference'],
        reserved_training_check_new_outcomes_inspected=False,validation_test_access=False,training_admissions=0,
        explicit_source_annotation_sha256=digest(reviews),attempts_sha256=digest(parent/'attempts.jsonl'))
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
