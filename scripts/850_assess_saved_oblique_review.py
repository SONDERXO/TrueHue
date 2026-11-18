"""Unblind only a complete, durably saved review; never change original ratings."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.oblique_comparison_review import validate

def assess(public,saved,predictions,summary):
    if not validate(public,saved):raise ValueError('Save every initial rating before unblinding')
    mapping={p['review_id']:p for p in predictions};concerns=[];useful=set();outcomes=[]
    for case in public['cases']:
        rating=saved['ratings'][case['id']];p=mapping[case['id']]
        if case['kind']=='identity':
            outcome=rating['identity']
            if outcome!='no_noticeable_change':concerns.append(case['id'])
        else:
            choice=rating['preference'];artifact=rating['artifact']
            outcome='output_preferred' if choice==p['output_panel'] else ('input_preferred' if choice in ['A','B'] else choice)
            if outcome=='output_preferred':useful.add(p['role'])
            if outcome in ['input_preferred','both_unacceptable','cannot_judge'] or artifact in [p['output_panel'],'both','cannot_judge']:
                concerns.append(case['id'])
        outcomes.append(dict(review_id=case['id'],case_id=p['case_id'],outcome=outcome,original_rating=rating))
    families={'exposure_under','exposure_over','colour_cool'}
    numeric=all(summary['by_role'][r]['source_equal_DE_improvement']>0 for r in families)
    return dict(development_status='PASS' if numeric and families<=useful and not concerns else 'NOTREADY',
        numeric_families_pass=numeric,useful_families=sorted(useful),concerns=concerns,outcomes=outcomes,
        final_model_ready=False,scope='Exposed development only; original saved ratings preserved')

def main():
    if len(sys.argv)!=2:raise SystemExit('Supply exact saved ratings revision filename')
    name=sys.argv[1]
    if Path(name).name!=name or not name.endswith('.json'):raise ValueError('Revision filename only')
    out=ROOT/'outputs/oblique_source_held_comparison_v1'
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    assert read(out/'independent_verification_PRIVATE.json')['passed']
    result=assess(read(out/'review_public.json'),read(out/'ratings'/name),read(out/'predictions_PRIVATE.json'),read(out/'summary_PRIVATE.json'))
    dest=out/('assessment_'+name)
    with dest.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(result['development_status'])

if __name__=='__main__':main()
