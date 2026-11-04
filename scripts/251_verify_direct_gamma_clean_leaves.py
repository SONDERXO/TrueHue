"""Independently rebuild leaf membership, outputs and summaries."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/direct_gamma_clean_leaf_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    parent=ROOT/'outputs/direct_gamma_regression_comparison_v1';original_plan=read(parent/'plan.json')
    rows={r['pair_id']:r for r in original_plan['rows']};features=original_plan['features']
    records=read(out/'predictions.json');summary=read(out/'summary.json');controls=0
    for fold in original_plan['folds']:
        fid=fold['fold_id'];old=read(parent/f'fold_{fid}/paper_gamma_refit.json');new=read(out/f'fold_{fid}/tree.json')
        tree=PortableTree(old);candidate=PortableTree(new)
        training=[rows[p] for p in fold['train_pair_ids']]
        for index,(before,after) in enumerate(zip(old['nodes'],new['nodes'])):
            if before['kind']=='split':assert before==after;continue
            identities=[r for r in training if r['variant']=='identity' and tree.leaf_id([r[k] for k in features])==index]
            assert after['values']==([1.,1.,1.] if identities else before['values'])
        for row in training:
            if row['variant']=='identity':assert candidate.predict_one([row[k] for k in features])==[1.,1.,1.];controls+=1
    (out/'boards').mkdir();sections=[]
    def panel(im,title):
        shown=cv2.copyMakeBorder(im,28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1);return shown
    for record in records:
        row=rows[record['pair_id']];fid=record['fold_id'];model=PortableTree(read(out/f'fold_{fid}/tree.json'))
        assert model.predict_one([row[k] for k in features])==record['parameters']
        image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        output=image.copy();output[mask]=np.rint(transform_rgb(image.astype(float)/255,*record['parameters'])[mask]*255).astype(np.uint8)
        path=out/f'fold_{fid}'/(record['pair_id']+'.png');assert digest(path)==record['output_sha256']
        np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
        assert not np.any(output[~mask]!=image[~mask])
        actual=image_errors(reference,output,score)
        for key,value in actual.items():
            if value is None:assert record['metrics'][key] is None
            else:assert abs(value-record['metrics'][key])<1e-12
        raw=cv2.imread(str(parent/f'fold_{fid}'/(record['pair_id']+'_paper_gamma_refit.png')))
        board=np.hstack([panel(cv2.cvtColor(reference,cv2.COLOR_RGB2BGR),'Reference'),panel(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),'Uncorrected'),panel(raw,'Direct gamma tree'),panel(cv2.cvtColor(output,cv2.COLOR_RGB2BGR),'Protected leaves')])
        assert cv2.imwrite(str(out/'boards'/(record['pair_id']+'.png')),board)
        sections.append(f'<section><h2>{html.escape(record["pair_id"])}</h2><p>Fixed-source error: uncorrected {record["no_correction_error"]:.3f}; direct tree {record["unprotected_error"]:.3f}; protected {record["metrics"]["ciede2000_source_mask"]:.3f}.</p><img loading="lazy" src="boards/{record["pair_id"]}.png"></section>')
    assert controls==210 and len(records)==30
    harms=[r['pair_id'] for r in records if r['variant']=='identity' and r['changed_input_pixels']>0]
    assert harms==summary['harmed_identity_ids']==['75027__identity']
    for scope,metrics in summary['aggregates'].items():
        selected=[r for r in records if scope=='all' or (r['variant']=='identity')==(scope=='identity')]
        assert abs(np.mean([r['metrics']['ciede2000_source_mask'] for r in selected])-metrics['protected'])<1e-12
    assert not summary['gate']['passed']
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Fitting-control protection comparison</title><style>body{font:17px system-ui;background:#171923;color:#eee;margin:28px}img{max-width:100%}section{border-top:1px solid #666;margin:24px 0}</style><h1>Same15sources: protected direct-gamma tree</h1><p>Harmed clean controls5→1,but correction benefit is reduced.75027still fails;candidate is not promoted. This is exposed development evidence, not final testing.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_tree_exports=15,verified_fitting_controls=controls,
        reconstructed_outputs_and_metrics=30,source_split_policy_unchanged=True,remaining_harmed_clean='75027',
        active_demo_changed=False,evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:15protected trees,210fitting controls,30held outputs/metrics;one held-clean failure retained.')


if __name__=='__main__':main()
