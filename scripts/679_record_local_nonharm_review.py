"""Record completed exhaustive changed-output review and exact prior parity."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree,float32
OUT=ROOT/'outputs/local_nonharm_refinement_comparison_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    target=OUT/'review_receipt_PRIVATE.json';assert not target.exists()
    c=read(OUT/'changes_PRIVATE.json');d=read(OUT/'results_PRIVATE.json');v=read(OUT/'verification_PRIVATE.json')
    assert v['passed'] and sha(OUT/'results_PRIVATE.json')==v['result_sha256']
    previous=read(ROOT/'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')
    assert c['exact_previous_exception_outputs_and_metrics']==756
    for a,b in zip(d['records'],previous['records'],strict=True):
        assert a['case_id']==b['case_id'] and a['candidate']==b['candidate']
    m=read(ROOT/'outputs/local_nonharm_refinement_models_v1/models_PRIVATE.json');f=m['full']
    p=next(p for p in m['predictions'] if p['case_id']=='eval_02__stress_color_none')
    i=f['training_cases'].index('diversity_017__stress_color_none');n=f['local_refinement']['node'];node=f['pre_veto_model']['tree']['nodes'][n]
    k=node['feature'];tree=PortableTree(f['pre_veto_model']['tree'])
    bx=f['training_features'][i];ex=p['features']
    assert float32(bx[k])>node['threshold'] and float32(ex[k])<=node['threshold']
    assert tree.leaf_id(bx)==node['right'] and tree.leaf_id(ex)==node['left']
    assert len(c['boards'])==37 and len(c['sheets'])==10
    receipt=dict(completed=True,visual_review='Primary assistant viewed all 37 changed boards on all 10 contact sheets using view_image on 9 November 2026.',
        selection=c['selection'],changed_decisions=37,unchanged_vs_fixed_structure=719,
        exact_previous_exception_outputs_and_metric_records=756,
        observations='Restored brightening also restores visible fragmented facial/neck boundaries and the known harmful stress brightening. No mask change or dense mask-quality claim.',
        source_review_reuse='Prior review reused only for exact pixel-and-metric matches; every changed decision versus fixed structure additionally viewed.',
        diagnostic=dict(selection='Previously documented stress harm, explanatory outcome-selected trace; not a tuning input',
            case_id=p['case_id'],node=n,feature=m['feature_names'][k],threshold=node['threshold'],
            fitting_blocker_feature_float32=float32(bx[k]),evaluation_feature_float32=float32(ex[k]),
            blocker_leaf=tree.leaf_id(bx),evaluation_leaf=tree.leaf_id(ex),parameters=p['parameters']),
        reviewed_sheet_sha256={p:sha(p) for p in c['sheets']},reviewed_board_sha256={p:sha(p) for p in c['boards']},
        result_sha256=sha(OUT/'results_PRIVATE.json'),changes_sha256=sha(OUT/'changes_PRIVATE.json'),
        holdout_image_reads=0,adopted=False)
    target.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt['diagnostic'],indent=2))
if __name__=='__main__':main()
