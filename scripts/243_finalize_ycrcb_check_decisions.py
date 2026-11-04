"""Apply the three explicit pending-source rejections without changing history."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATEMENT='2879: reject both panels have bad mask, 38620: reject panel 3 captures hair in face mask compared to panel 6 which had good exclusions, 7526: reject, panel 3 has captured hair in mask but both has good facial coverage, panel 3 needs improvement on exclusions.'
REASONS={
    '2879':'both panels have bad mask',
    '38620':'panel 3 captures hair in face mask compared to panel 6 which had good exclusions',
    '7526':'panel 3 has captured hair in mask but both has good facial coverage, panel 3 needs improvement on exclusions.',
}


def main():
    parent=ROOT/'outputs/ycrcb_training_check_clarification_v1'
    out=ROOT/'outputs/ycrcb_training_check_final_reviews_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    rows=read(parent/'reconciled_reviews.json');changes=[]
    for row in rows:
        name=row['source_id']
        if name not in REASONS:continue
        assert row['decision']=='' and row['decision_completion']=='pending'
        changes.append(dict(source_id=name,previous_decision='',clarified_decision='reject',reason=REASONS[name]))
        row.update(decision='reject',decision_completion='selected',clarification_issues=[],
            clarification_statement=STATEMENT,clarified_reason=REASONS[name],previous_export_decision='')
    assert len(changes)==3 and all(r['decision'] in {'accept','reject','uncertain'} for r in rows)
    counts=dict(Counter(r['decision'] for r in rows))
    assert counts=={'reject':16,'accept':4}
    out.mkdir()
    records=[('clarification.json',dict(user_statement_verbatim=STATEMENT,changes=changes,prior_reviews_sha256=digest(parent/'reconciled_reviews.json'))),
        ('reconciled_reviews.json',rows),
        ('summary.json',dict(status='check_review_complete_no_policy_promotion',sources=20,decision_counts=counts,pending_decisions=0,
            accepted_ids=[r['source_id'] for r in rows if r['decision']=='accept'],
            conclusion='Current evidence does not support global promotion of this frozen mask policy.',
            candidate_tuned_on_check=False,training_admissions=0,mst_lookup_calls=0,models_fitted=0,policy_promoted=False))]
    for name,value in records:(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',only_three_pending_decisions_resolved=True,
        original_notes_and_prior_exports_preserved=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(records[-1][1],indent=2))


if __name__=='__main__':main()
