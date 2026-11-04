"""Validate/archive two actual photographer exports; never change source eligibility."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'outputs/photographer_reference_review_v1'


def validate_response(value,manifest,manifest_hash):
    if not isinstance(value,dict) or value.get('schema_version')!=manifest['schema_version'] or value.get('manifest_sha256')!=manifest_hash:
        raise ValueError('Review version/manifest mismatch')
    reviewer=value.get('reviewer_code')
    if reviewer not in manifest['reviewer_orders'] or value.get('photographer_self_declaration') is not True:
        raise ValueError('Known reviewer and actual photographer self-declaration required')
    ratings=value.get('ratings')
    if not isinstance(ratings,list) or any(not isinstance(r,dict) for r in ratings):raise ValueError('Ratings list required')
    expected=set(manifest['reviewer_orders'][reviewer])
    ids=[r.get('case_id') for r in ratings]
    if any(not isinstance(i,str) for i in ids) or len(ids)!=len(expected) or set(ids)!=expected:
        raise ValueError('All exact unique case IDs required')
    for row in ratings:
        for field,allowed in manifest['allowed'].items():
            if row.get(field) not in allowed:raise ValueError('Missing/invalid '+field)
        if not isinstance(row.get('notes',''),str):raise ValueError('Text notes required')
        if row['decision'] in ['uncertain','unsuitable'] and not row.get('notes','').strip():raise ValueError('Reason required')
    if not isinstance(value.get('session_notes',''),str):raise ValueError('Text session notes required')
    return reviewer


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--responses',type=Path,nargs=2,required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    if args.output_dir.exists():raise FileExistsError('Refusing existing review archive')
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'));identity=digest(PACKAGE/'manifest.json')
    verification=json.loads((PACKAGE/'verification.json').read_text(encoding='utf-8'))
    for name,h in verification['evidence_sha256'].items():
        if digest(PACKAGE/name)!=h:raise ValueError('Review package changed: '+name)
    values=[]
    for path in args.responses:
        payload=json.loads(path.read_text(encoding='utf-8'));reviewer=validate_response(payload,manifest,identity)
        values.append((reviewer,path,payload))
    if {v[0] for v in values}!={'P1','P2'}:raise ValueError('Two distinct reviewers P1/P2required; credentials/independence remain self-declared')
    args.output_dir.mkdir(parents=True)
    for reviewer,path,payload in values:
        (args.output_dir/(reviewer+'_original.json')).write_bytes(path.read_bytes())
    byreviewer={reviewer:{r['case_id']:r for r in payload['ratings']} for reviewer,path,payload in values}
    keys={r['case_id']:r for r in json.loads((PACKAGE/'researcher_key.json').read_text(encoding='utf-8'))['case_sources']}
    comparisons=[]
    for case in manifest['cases']:
        code=case['case_id'];a=byreviewer['P1'][code];b=byreviewer['P2'][code]
        comparisons.append(dict(case_id=code,source_image_id=keys[code]['source_image_id'],P1=a,P2=b,
            decision_agreement=a['decision']==b['decision'],adjudication='not_performed',training_eligibility_changed=False))
    report=dict(status='collected_development_reference_review_not_MOS',manifest_sha256=identity,comparisons=comparisons,
        original_sha256={reviewer:digest(path) for reviewer,path,payload in values},
        credentials_and_independence='Self-declared, not independently verified',automatic_admissions=0,model_fits=0)
    (args.output_dir/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Archived two reviews with disagreements preserved; no source/model changes.')


if __name__=='__main__':main()
