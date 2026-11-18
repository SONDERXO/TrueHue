"""Import user colour usefulness/appearance answers; no automated visual PASS."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/frozen_neighbour_exposure_ratings_v1'
REVIEW=ROOT/'outputs/frozen_neighbour_exposure_review_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--file',required=True,type=Path);args=parser.parse_args()
    if OUT.exists():raise FileExistsError('Preserve prior imported review')
    data=json.loads(args.file.read_text(encoding='utf-8-sig'))
    manifest=json.loads((REVIEW/'manifest_PRIVATE.json').read_text(encoding='utf-8'))
    assert data['schema']=='truehue_exposure_usefulness_review_v1' and data['qa_fixture'] is False
    assert data['review_kind']=='exposure_usefulness_and_appearance' and data['manifest_sha256']==sha(REVIEW/'manifest_PRIVATE.json')
    prefs=['candidate','input','no_useful_difference','uncertain'];looks=['acceptable','unwanted','uncertain']
    ids=[r['review_id'] for r in manifest['cases']];assert len(ids)==8
    answers=data['answers'];assert isinstance(answers,dict) and set(answers)<=set(ids)
    for a in answers.values():
        assert a['preference'] is None or a['preference'] in prefs
        assert a['appearance'] is None or a['appearance'] in looks
        assert isinstance(a['note'],str)
    bad=[i for i in ids if i in answers and answers[i]['appearance'] in ['unwanted','uncertain']]
    complete=sum(i in answers and answers[i]['preference'] in prefs and answers[i]['appearance'] in looks for i in ids)
    expected='stopped_'+answers[bad[0]]['appearance'] if bad else 'complete_recorded' if complete==8 else 'partial'
    assert data['status']==expected
    assert sha(ROOT/'outputs/frozen_neighbour_identity_ratings_v1/assessment_PRIVATE.json')==manifest['identity_assessment_sha256']
    assert sha(ROOT/'outputs/frozen_block_neighbour_prediction_v1/verification_PRIVATE.json')==manifest['run_verification_sha256']
    assert sha(ROOT/'outputs/frozen_neighbour_colour_ratings_v2/assessment_PRIVATE.json')==manifest['colour_assessment_sha256']
    result=dict(status=expected,cases_complete=complete,total=8,
        preference_counts={v:sum(a['preference']==v for a in answers.values()) for v in prefs},
        appearance_counts={v:sum(a['appearance']==v for a in answers.values()) for v in looks},
        raw_user_file_sha256=sha(args.file),manifest_sha256=data['manifest_sha256'],
        visual_pass_not_automatically_assigned=True,model_ready=False,
        exposure_usefulness_unreviewed=44-complete,darker_skin_qualification_unresolved=True,
        next_stage='stop_for_user_explanation_no_refit_or_rerating' if bad else 'interpret_all_usefulness_outcomes_before_next_review_design' if complete==8 else 'await_remaining_user_answers')
    OUT.mkdir();(OUT/'raw_user_review_PRIVATE.json').write_bytes(args.file.read_bytes())
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
