"""Independently refit30trees, replay90outputs and create a matched gallery."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree,export_tree
from src.data_preparation.controlled_training_table import TARGETS
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/direct_gamma_regression_comparison_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');summary=read(out/'summary.json');records=read(out/'predictions.json')
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    assert len(records)==90
    refits=0;outputs=0;historical_parity=0
    for fold in plan['folds']:
        training=[r for r in plan['rows'] if r['pair_id'] in fold['train_pair_ids']]
        held=[r for r in plan['rows'] if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert not {r['source_image_id'] for r in training}&{r['source_image_id'] for r in held}
        assert not {r['duplicate_group_id'] for r in training}&{r['duplicate_group_id'] for r in held}
        folder=out/f'fold_{fold["fold_id"]}'
        x=np.array([[r[k] for k in plan['features']] for r in training],float)
        for method in plan['methods']:
            y=np.array([[r[k] for k in TARGETS] if method=='legacy_refit' else plan['converted_targets'][r['pair_id']] for r in training],float)
            expected=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,y),plan['features'],list(TARGETS),{})
            payload=read(folder/f'{method}.json');assert payload['nodes']==expected['nodes']
            if method=='legacy_refit':
                historical=read(ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1'/f'fold_{fold["fold_id"]}/baseline5.json')
                assert historical['nodes']==payload['nodes'];historical_parity+=1
            model=PortableTree(payload);refits+=1
            for row in held:
                record=next(r for r in records if r['pair_id']==row['pair_id'] and r['method']==method)
                prediction=model.predict_one([row[k] for k in plan['features']])
                assert prediction==record['raw_parameters']
    (out/'boards').mkdir()
    def panel(im,title):
        shown=cv2.copyMakeBorder(im,28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown
    sections=[]
    for row in plan['rows']:
        image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        panels=[panel(cv2.cvtColor(reference,cv2.COLOR_RGB2BGR),'Reference'),panel(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),'Uncorrected input')]
        for method in ['no_correction','legacy_refit','paper_gamma_refit']:
            r=next(r for r in records if r['pair_id']==row['pair_id'] and r['method']==method)
            output=image.copy()
            if method=='legacy_refit':output=apply_correction(image,mask,r['raw_parameters'])
            elif method=='paper_gamma_refit':output[mask]=np.rint(transform_rgb(image.astype(float)/255,*r['paper_parameters'])[mask]*255).astype(np.uint8)
            path=out/f'fold_{r["fold_id"]}'/(row['pair_id']+'_'+method+'.png')
            assert digest(path)==r['output_sha256']
            np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
            metrics=image_errors(reference,output,scoring)
            for key,value in metrics.items():
                if value is None:assert r[key] is None
                else:assert abs(value-r[key])<1e-12
            if method!='no_correction':panels.append(panel(cv2.cvtColor(output,cv2.COLOR_RGB2BGR),method))
            outputs+=1
        board=out/'boards'/(row['pair_id']+'.png');assert cv2.imwrite(str(board),np.hstack(panels))
        sections.append(f'<section><h2>{html.escape(row["pair_id"])}</h2><p>Held source; same input, masks and features. Original concern: {html.escape(row.get("review_concern","") or "none recorded")}.</p><img loading="lazy" src="boards/{row["pair_id"]}.png"></section>')
    for aggregate in summary['aggregates']:
        values=[r for r in records if r['method']==aggregate['method'] and (aggregate['scope']=='all' or (r['variant']=='identity')==(aggregate['scope']=='identity'))]
        assert len(values)==aggregate['pairs']
        assert abs(np.mean([r['ciede2000_source_mask'] for r in values])-aggregate['mean_ciede2000'])<1e-12
        assert sum(r['changed_input_pixels']>0 for r in values)==aggregate['changed_pairs']
    assert not summary['gates']['paper_gamma_refit']['passed']
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Matched gamma-regression comparison</title><style>body{font:17px system-ui;background:#171923;color:#eee;margin:28px}img{max-width:100%}section{border-top:1px solid #666;margin:24px 0}</style><h1>Same15sources: direct-gamma training comparison</h1><p>Historical exposed development set; not final evaluation. Overall reconstruction improves but5/15clean photos are still changed. No demo model replacement or new mask approvals.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',independent_regression_refits=refits,historical_baseline_tree_parity=historical_parity,
        reconstructed_predictions_pixels_and_metrics=outputs,source_group_separation_verified=True,
        quality_gate_passed=False,active_demo_changed=False,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:30independent refits,15historical baseline trees match,90outputs/metrics reconstructed;no demo change.')


if __name__=='__main__':main()
