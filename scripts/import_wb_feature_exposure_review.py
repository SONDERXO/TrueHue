"""Preserve candidate-specific exposure answers and event history verbatim."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--file',required=True,type=Path);args=parser.parse_args()
    review=ROOT/'outputs/wb_feature_exposure_review_v1';out=ROOT/'outputs/wb_feature_exposure_ratings_v1'
    if out.exists():raise FileExistsError(out)
    raw=args.file.read_bytes();data=json.loads(raw.decode('utf-8-sig'));manifest=read(review/'manifest_PRIVATE.json')
    assert data['schema']=='truehue_exposure_usefulness_review_v1' and data['qa_fixture'] is False
    assert data['review_kind']=='exposure_usefulness_and_appearance' and data['manifest_sha256']==sha(review/'manifest_PRIVATE.json')
    bindings={'source_verification_sha256':'outputs/wb_feature_direct_prediction_v1/verification.json',
              'identity_assessment_sha256':'outputs/wb_feature_identity_ratings_v1/assessment_PRIVATE.json',
              'colour_raw_sha256':'outputs/wb_feature_colour_ratings_v1/raw_user_review_PRIVATE.json',
              'colour_user_correction_sha256':'outputs/wb_feature_colour_user_correction_v1/user_correction_PRIVATE.json',
              'colour_corrected_assessment_sha256':'outputs/wb_feature_colour_user_correction_v1/assessment_PRIVATE.json',
              'protocol_sha256':'docs/wb-feature-exposure-usefulness-protocol-2026-11-16.md'}
    for field,path in bindings.items():assert sha(ROOT/path)==manifest[field]
    assert sha(review/'selection_PRIVATE.json')==manifest['selection_sha256']
    ids=[c['review_id'] for c in manifest['cases']];answers=data['answers'];assert len(ids)==8 and isinstance(answers,dict) and set(answers)<=set(ids)
    prefs=['candidate','input','no_useful_difference','uncertain'];looks=['acceptable','unwanted','uncertain']
    for a in answers.values():assert a['preference'] in [None,*prefs] and a['appearance'] in [None,*looks] and isinstance(a['note'],str)
    replay={};assert isinstance(data['events'],list)
    for e in data['events']:
        assert e['review_id'] in ids
        if e['field']=='all':
            assert e['value']=='cleared';replay.pop(e['review_id'],None)
        else:
            assert e['field'] in ['preference','appearance'] and e['value'] in (prefs if e['field']=='preference' else looks)
            replay.setdefault(e['review_id'],{'preference':None,'appearance':None})[e['field']]=e['value']
    assert set(replay)==set(answers) and all(all(replay[k][f]==a[f] for f in ['preference','appearance']) for k,a in answers.items())
    completed=[i for i in ids if i in answers and answers[i]['preference'] in prefs and answers[i]['appearance'] in looks]
    stopped=[i for i in ids if i in answers and answers[i]['appearance'] in ['unwanted','uncertain']]
    status='stopped_'+answers[stopped[0]]['appearance'] if stopped else 'complete_recorded' if len(completed)==8 else 'partial'
    assert data['status']==status
    result=dict(status=status,complete_cases=len(completed),total=8,preference_counts={v:sum(a['preference']==v for a in answers.values()) for v in prefs},
                appearance_counts={v:sum(a['appearance']==v for a in answers.values()) for v in looks},
                raw_sha256=hashlib.sha256(raw).hexdigest(),manifest_sha256=data['manifest_sha256'],event_replay_matches=True,
                remaining_exposure_cases_unreviewed=36,model_ready=False,automatic_visual_pass=False)
    out.mkdir();(out/'raw_user_review_PRIVATE.json').write_bytes(raw);(out/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
