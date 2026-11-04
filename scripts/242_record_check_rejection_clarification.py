"""Apply only the two explicitly clarified rejections; preserve three blanks."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/ycrcb_training_check_review_import_v1'
    out=ROOT/'outputs/ycrcb_training_check_clarification_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    rows=read(parent/'reconciled_reviews.json');changes=[]
    for row in rows:
        if row['source_id'] not in {'7571','37974'}:continue
        assert row['decision']=='accept'
        changes.append(dict(source_id=row['source_id'],previous_decision='accept',clarified_decision='reject'))
        row.update(decision='reject',decision_completion='selected',accepted_with_notes=False,
            clarification_issues=[],clarification_statement='Okay, reject them both',
            previous_export_decision='accept')
    assert len(changes)==2
    assert {r['source_id'] for r in rows if r['decision']==''}=={'2879','38620','7526'}
    counts=dict(Counter(r['decision'] if r['decision'] else 'pending' for r in rows))
    out.mkdir()
    clarification=dict(user_statement_verbatim='Okay, reject them both',
        interpretation='Both refers to7571and37974, the two acceptance confirmations in the immediately preceding question.',
        changes=changes,unchanged_pending_ids=['2879','38620','7526'],prior_reviews_sha256=digest(parent/'reconciled_reviews.json'))
    for name,value in [('clarification.json',clarification),('reconciled_reviews.json',rows),
        ('summary.json',dict(status='two_rejections_clarified_three_decisions_pending',sources=20,decision_counts=counts,
            pending_ids=['2879','38620','7526'],training_admissions=0,policy_promoted=False,models_fitted=0))]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',only_explicit_two_decisions_changed=True,
        original_export_preserved=True,three_blank_decisions_preserved=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(counts))


if __name__=='__main__':main()
