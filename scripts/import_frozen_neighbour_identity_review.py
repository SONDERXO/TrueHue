"""Validate a user-supplied saved review without generating or replacing ratings."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/frozen_neighbour_identity_ratings_v1'
REVIEW=ROOT/'outputs/frozen_neighbour_identity_review_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--file',required=True,type=Path);args=parser.parse_args()
    if OUT.exists():raise FileExistsError('Preserve prior imported ratings')
    data=json.loads(args.file.read_text(encoding='utf-8-sig'))
    manifest=json.loads((REVIEW/'manifest_PRIVATE.json').read_text(encoding='utf-8'))
    assert data['schema']=='truehue_identity_review_v1' and data['qa_fixture'] is False
    assert data['review_kind']=='identity_no_unwanted_change'
    assert data['manifest_sha256']==sha(REVIEW/'manifest_PRIVATE.json')
    ids=[c['review_id'] for c in manifest['cases']];assert len(ids)==11
    answers=data['answers'];assert isinstance(answers,dict) and set(answers)<=set(ids)
    allowed=['acceptable','unwanted','uncertain']
    assert all(a['value'] in allowed and isinstance(a['note'],str) for a in answers.values())
    bad=[i for i in ids if i in answers and answers[i]['value']!='acceptable']
    expected='stopped_'+answers[bad[0]]['value'] if bad else 'complete_acceptable' if len(answers)==11 else 'partial'
    assert data['status']==expected
    assert sha(ROOT/'outputs/frozen_block_neighbour_prediction_v1/verification_PRIVATE.json')==manifest['source_verification_sha256']
    result=dict(status=expected,answered=len(answers),total=11,
        counts={v:sum(a['value']==v for a in answers.values()) for v in allowed},
        user_file_sha256=sha(args.file),manifest_sha256=data['manifest_sha256'],
        model_ready=False,correction_usefulness_not_assessed=True,darker_skin_qualification_unresolved=True,
        next_stage='bounded_nonidentity_usefulness_review_design' if expected=='complete_acceptable' else 'stop_for_user_explanation_no_refit_or_rerating' if bad else 'await_remaining_user_answers')
    OUT.mkdir();(OUT/'raw_user_review_PRIVATE.json').write_bytes(args.file.read_bytes())
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
