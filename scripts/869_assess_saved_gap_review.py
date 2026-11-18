"""Unblind complete saved PRIMARY ratings; secondary metrics cannot rescue it."""
from pathlib import Path
import json,sys,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def assess_saved(public,saved,predictions,summary):
    spec=importlib.util.spec_from_file_location('accepted_review_assessment',ROOT/'scripts/850_assess_saved_oblique_review.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.assess(public,saved,predictions,summary['primary'])
    result.update(assessment_context='primary_approved_ear_support',fixed_diagnostic_can_rescue=False,
        interpretation='Exposed development only; no final/phone/tone/MOS completion claim')
    return result

def main():
    if len(sys.argv)!=2:raise SystemExit('Supply exact saved revision filename')
    name=sys.argv[1]
    if Path(name).name!=name or not name.endswith('.json'):raise ValueError('Revision filename only')
    out=ROOT/'outputs/histogram_gap_source_held_comparison_v1';read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    verification=read(out/'verification_PRIVATE.json');assert verification['passed']
    for rel,h in verification['artifact_sha256'].items():assert hashlib.sha256((out/rel).read_bytes()).hexdigest()==h
    result=assess_saved(read(out/'review_public.json'),read(out/'ratings'/name),read(out/'predictions_PRIVATE.json'),read(out/'summary_PRIVATE.json'))
    with (out/('assessment_'+name)).open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(result['development_status'])

if __name__=='__main__':main()
