"""Import exact candidate-specific colour usefulness answers; preserve raw history."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--file',required=True,type=Path);args=parser.parse_args()
    review=ROOT/'outputs/wb_feature_colour_review_v1';out=ROOT/'outputs/wb_feature_colour_ratings_v1'
    if out.exists():raise FileExistsError(out)
    raw=args.file.read_bytes();data=json.loads(raw.decode('utf-8-sig'));manifest=read(review/'manifest_PRIVATE.json')
    assert data['schema']=='truehue_colour_usefulness_review_v1' and data['qa_fixture'] is False
    assert data['review_kind']=='colour_usefulness_and_appearance' and data['manifest_sha256']==sha(review/'manifest_PRIVATE.json')
    assert sha(ROOT/'outputs/wb_feature_direct_prediction_v1/verification.json')==manifest['run_verification_sha256']
    assert sha(ROOT/'outputs/wb_feature_identity_ratings_v1/assessment_PRIVATE.json')==manifest['identity_assessment_sha256']
    assert sha(ROOT/'outputs/wb_feature_identity_ratings_v1/raw_user_review_PRIVATE.json')==manifest['identity_raw_sha256']
    assert sha(ROOT/'docs/wb-feature-colour-usefulness-protocol-2026-11-16.md')==manifest['protocol_sha256']
    ids=[c['review_id'] for c in manifest['cases']];answers=data['answers'];assert len(ids)==11 and isinstance(answers,dict) and set(answers)<=set(ids)
    prefs=['candidate','input','no_useful_difference','uncertain'];looks=['acceptable','unwanted','uncertain']
    for a in answers.values():
        assert a['preference'] in [None,*prefs] and a['appearance'] in [None,*looks] and isinstance(a['note'],str)
    events=data['events'];assert isinstance(events,list)
    replay={}
    for e in events:
        assert e['review_id'] in ids
        if e['field']=='all':
            assert e['value']=='cleared';replay.pop(e['review_id'],None)
        else:
            assert e['field'] in ['preference','appearance'] and e['value'] in (prefs if e['field']=='preference' else looks)
            replay.setdefault(e['review_id'],{'preference':None,'appearance':None})[e['field']]=e['value']
    assert set(replay)==set(answers)
    assert all(all(replay[k][f]==a[f] for f in ['preference','appearance']) for k,a in answers.items())
    completed=[i for i in ids if i in answers and answers[i]['preference'] in prefs and answers[i]['appearance'] in looks]
    stopped=[i for i in ids if i in answers and answers[i]['appearance'] in ['unwanted','uncertain']]
    status='stopped_'+answers[stopped[0]]['appearance'] if stopped else 'complete_recorded' if len(completed)==11 else 'partial'
    assert data['status']==status
    result=dict(status=status,complete_cases=len(completed),total=11,preference_counts={v:sum(a['preference']==v for a in answers.values()) for v in prefs},
                appearance_counts={v:sum(a['appearance']==v for a in answers.values()) for v in looks},
                raw_sha256=hashlib.sha256(raw).hexdigest(),manifest_sha256=data['manifest_sha256'],
                event_replay_matches=True,model_ready=False,automatic_visual_pass=False)
    out.mkdir();(out/'raw_user_review_PRIVATE.json').write_bytes(raw);(out/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
