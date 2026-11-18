"""Match saved candidate/parent results and hashes; no fits or visual claims."""
from pathlib import Path
from collections import Counter
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs/bounded_training_comparison_v1';P=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=O/'matched_assessment_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve assessment')
    verification=read(O/'verification_PRIVATE.json');assert verification['passed']
    parent_receipt=read(P/'review_PRIVATE.json')
    parent_prediction_path=P/'predictions_PRIVATE.json'
    assert parent_receipt['input_sha256'][str(parent_prediction_path.relative_to(ROOT))]==sha(parent_prediction_path)
    parent={r['case_id']:r for r in read(P/'predictions_PRIVATE.json')};new=read(O/'predictions_PRIVATE.json');summary=read(O/'summary_PRIVATE.json');models=read(O/'models_PRIVATE.json')
    assert len(parent)==len(new)==44
    changes=[];same=[]
    for r in new:
        old=parent[r['case_id']]
        assert r['experimental_role']==old['experimental_role'] and r['held_publisher_group']==old['held_publisher_group']
        assert abs(r['input_RGB']-old['input_RGB'])<1e-11 and abs(r['input_DE']-old['input_DE'])<1e-11
        assert sha(O/r['case_id']/'output.png')==r['output_sha256']
        if r['output_sha256']==old['output_sha256']:same.append(r['case_id'])
        else:changes.append(dict(case_id=r['case_id'],role=r['experimental_role'],old_controls=old['controls'],new_controls=r['controls'],old_RGB=old['output_RGB'],new_RGB=r['output_RGB'],old_DE=old['output_DE'],new_DE=r['output_DE'],input_RGB=r['input_RGB'],input_DE=r['input_DE']))
    matched={}
    for role in summary['by_role']:
        own=[r for r in new if r['experimental_role']==role];matched[role]={}
        for metric in ['RGB','DE']:
            diff=[r['output_'+metric]-parent[r['case_id']]['output_'+metric] for r in own]
            matched[role][metric]=dict(better=sum(d<-1e-12 for d in diff),worse=sum(d>1e-12 for d in diff),same=sum(abs(d)<=1e-12 for d in diff))
    names=models[0]['tree']['feature_names'];features=Counter(names[n['feature']] for m in models for n in m['tree']['nodes'] if n['kind']=='split')
    totals=dict(initial_SSE=sum(m['search']['initial_SSE'] for m in models),selected_SSE=sum(m['search']['selected_SSE'] for m in models),strictly_improved_folds=sum(m['search']['strict_improvement'] for m in models),reused_folds=sum(m['reused_feasibility'] for m in models),new_searches=sum(not m['reused_feasibility'] for m in models),status_counts=dict(Counter(m['search']['status'] for m in models)),limit_reasons=dict(Counter(m['search']['limit_reason'] for m in models)),training_appearances=440,distinct_original_photo_groups=11)
    result=dict(passed_verification=True,development_checks_passed=summary['development_checks_passed'],exact_same_output_cases=same,changed_output_cases=changes,matched_by_role=matched,training_search_summary=totals,split_features=dict(features),fresh_visual_review_recorded=False,parent_review_sha256=sha(P/'review_PRIVATE.json'),parent_predictions_sha256=sha(parent_prediction_path),candidate_predictions_sha256=sha(O/'predictions_PRIVATE.json'),assessor_sha256=sha(__file__),new_fits=0,new_predictions=0,holdout_reads=0)
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['changed_output_cases','exact_same_output_cases']},indent=2));print('Exact same outputs:',len(same),'changed:',len(changes))

if __name__=='__main__':main()
