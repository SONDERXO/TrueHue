"""Summarise verified saved comparisons for the completion-strategy review."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/model_completion_strategy_v1'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve strategy review')
    stages=dict(previous_exception='facial_veto_exception_comparison_v1',
        global_nonharm='colour_nonharm_comparison_v1',fixed_structure='fixed_structure_nonharm_comparison_v1',
        local_refinement='local_nonharm_refinement_comparison_v1')
    evidence={};bound={str(Path(__file__)):sha(Path(__file__))};data={}
    for stage,folder in stages.items():
        base=ROOT/'outputs'/folder
        paths=[base/name for name in ('results_PRIVATE.json','verification_PRIVATE.json','assessment_PRIVATE.json')]
        result,verification,assessment=[read(p) for p in paths]
        assert verification['passed'] and verification['result_sha256']==sha(paths[0])
        assert not assessment['all_requirements_pass']
        bound.update({str(p):sha(p) for p in paths});data[stage]=result
        evidence[stage]=dict(all_requirements_pass=assessment['all_requirements_pass'],
            failed_requirements=[k for k,v in assessment['acceptance'].items() if not v],
            candidate={co:{layer:s['methods']['candidate'] for layer,s in layers.items()} for co,layers in result['summary'].items()})
    assert [r['candidate'] for r in data['local_refinement']['records']]==[r['candidate'] for r in data['previous_exception']['records']]
    aligned={co:{layer:s['methods']['parent'] for layer,s in layers.items()} for co,layers in data['local_refinement']['summary'].items()}
    reports=['local-nonharm-refinement-results-2026-11-09.md','training-exposure-colour-audit-2026-11-09.md',
        'remaining-correction-failure-audit-2026-11-08.md','remaining-correction-decision-trace-2026-11-09.md',
        'parser-suitability-decision-2026-11-08.md','desktop-current-masking-integration-2026-11-07.md',
        'decoder-permission-evidence-2026-11-08.md']
    for name in reports:
        p=ROOT/'docs'/name;bound[str(p)]=sha(p)
    for name in ['src/demo/service.py','src/demo/research_progress.py']:
        p=ROOT/name;bound[str(p)]=sha(p)
    result=dict(comparisons=evidence,aligned_acceptance_comparator=aligned,
        local_refinement_exact_previous_candidate_records=756,
        disposition='No reviewed candidate qualifies for adoption. Pause incremental repairs; follow bounded completion plan.',
        input_sha256=bound,new_fits=0,new_predictions=0,image_reads=0,holdout_image_reads=0)
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir();p=OUT/'review_PRIVATE.json';p.write_text(json.dumps(result,indent=2))
    receipt=dict(passed=True,comparison_receipts_checked=4,all_four_candidates_fail=True,
        review_sha256=sha(p),source_hashes=len(bound),new_fits=0,image_reads=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
