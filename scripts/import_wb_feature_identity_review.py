"""Preserve manifest-bound user answers, never fabricate or overwrite ratings."""
import argparse
import json
from pathlib import Path
from wb_feature_direct_workflow import ROOT,read,write,sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--file',required=True,type=Path);args=parser.parse_args()
    review=ROOT/'outputs/wb_feature_identity_review_v1';out=ROOT/'outputs/wb_feature_identity_ratings_v1'
    if out.exists():raise FileExistsError(out)
    raw=args.file.read_bytes();data=json.loads(raw.decode('utf-8-sig'));manifest=read(review/'manifest_PRIVATE.json')
    assert data['schema']=='truehue_identity_review_v1' and data['qa_fixture'] is False
    assert data['review_kind']=='identity_no_unwanted_change' and data['manifest_sha256']==sha(review/'manifest_PRIVATE.json')
    assert sha(ROOT/'outputs/wb_feature_direct_prediction_v1/verification.json')==manifest['source_verification_sha256']
    ids=[c['review_id'] for c in manifest['cases']];answers=data['answers'];assert len(ids)==11 and isinstance(answers,dict) and set(answers)<=set(ids)
    allowed=['acceptable','unwanted','uncertain'];assert all(a['value'] in allowed and isinstance(a['note'],str) for a in answers.values())
    assert isinstance(data['events'],list)
    assert all(e['review_id'] in ids and e['value'] in allowed+['cleared'] for e in data['events'])
    bad=[i for i in ids if i in answers and answers[i]['value']!='acceptable']
    expected='stopped_'+answers[bad[0]]['value'] if bad else 'complete_acceptable' if len(answers)==11 else 'partial'
    assert data['status']==expected
    out.mkdir();(out/'raw_user_review_PRIVATE.json').write_bytes(raw)
    write(out/'assessment_PRIVATE.json',dict(status=expected,answered=len(answers),counts={v:sum(a['value']==v for a in answers.values()) for v in allowed},
          raw_file_sha256=sha(args.file),manifest_sha256=data['manifest_sha256'],model_ready=False,correction_usefulness_not_assessed=True))
    print(expected)

if __name__=='__main__':main()
