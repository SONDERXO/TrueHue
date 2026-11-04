"""Independent portable inference/pixel replay and matched stress denominators."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/development_mst_stress_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');data=read(out/'summary.json');cases={r['case_id']:r for r in plan['cases']}
    folders={'baseline5':'table2_reviewed_ten_source_evaluation_v1','chroma9':'table2_chroma_distribution_comparison_v1','clean-leaf':'table2_clean_leaf_policy_v1'}
    original_plan=read(ROOT/'outputs/table2_clean_leaf_policy_v1/plan.json')
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert len(data['records'])==102 and len(cases)==34
    successes=0;failures=[]
    for record in data['records']:
        case=cases[record['case_id']];folder=out/case['case_id']/record['method'];report=read(folder/'report.json')
        assert record['fold_id']==plan['source_folds'][case['source_id']]
        fold=next(f for f in original_plan['folds'] if f['fold_id']==record['fold_id'])
        assert all(not p.startswith(case['source_id']+'__') for p in fold['train_pair_ids'])
        assert any(p.startswith(case['source_id']+'__') for p in fold['inner_validation_pair_ids'])
        image=cv2.imread(str(ROOT/case['input_path']));reference=cv2.cvtColor(cv2.imread(str(ROOT/case['reference_path'])),cv2.COLOR_BGR2RGB)
        score=cv2.imread(str(ROOT/case['reference_mask_path']),0)>0
        assert image_errors(reference,cv2.cvtColor(image,cv2.COLOR_BGR2RGB),score)==record['no_correction']
        if not record['success']:
            assert case['case_id']=='75027__dark' and report['failed_stage']=='face_detection'
            assert report['mst'] is None and report['parameters'] is None and report['features'] is None
            assert not (folder/'corrected.png').exists() and record['metrics'] is None
            failures.append(dict(case_id=case['case_id'],method=record['method']));continue
        assert report['status']=='development_experimental_mst' and not report['quality_gate_passed']
        model=PortableTree(read(ROOT/'outputs'/folders[record['method']]/f"fold_{record['fold_id']}/decision_tree.json"))
        assert model.predict_one(report['features'])==report['parameters']
        mask=cv2.imread(str(folder/'measurement_mask.png'),0)
        np.testing.assert_array_equal(mask,cv2.imread(str(ROOT/case['input_mask_path']),0))
        g,r,b=report['parameters'];rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        raw=np.rint(np.clip((rgb.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
        corrected=rgb.copy();corrected[mask>0]=raw[mask>0]
        actual=cv2.cvtColor(cv2.imread(str(folder/'corrected.png')),cv2.COLOR_BGR2RGB)
        np.testing.assert_array_equal(actual,corrected)
        assert image_errors(reference,actual,score)==record['metrics'];successes+=1
    assert successes==99 and len(failures)==3
    for scope,methods in data['aggregate'].items():
        sets=[]
        for method,summary in methods.items():
            attempted=[r for r in data['records'] if r['scope']==scope and r['method']==method]
            successful=[r for r in attempted if r['success']];sets.append({r['case_id'] for r in successful})
            assert summary['attempted']==len(attempted) and summary['successful']==len(successful)
            assert summary['corrected_ciede2000']==float(np.mean([r['metrics']['ciede2000_source_mask'] for r in successful]))
            assert summary['no_correction_ciede2000']==float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in successful]))
            assert summary['harmed_cases']==[r['case_id'] for r in successful if r['metrics']['ciede2000_source_mask']>r['no_correction']['ciede2000_source_mask']]
        assert sets[0]==sets[1]==sets[2]
    (out/'boards').mkdir();sections=[]
    for source in sorted({c['source_id'] for c in cases.values()}):
        strips=[]
        for case in [c for c in cases.values() if c['source_id']==source]:
            images=[(ROOT/case['input_path'],case['scope']+' input')]
            for method in folders:
                corrected=out/case['case_id']/method/'corrected.png'
                images.append((corrected if corrected.exists() else ROOT/case['input_path'],method if corrected.exists() else method+' UNAVAILABLE'))
            panels=[]
            for p,label in images:
                im=cv2.imread(str(p));im=cv2.copyMakeBorder(im,24,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(im,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1);panels.append(im)
            strips.append(np.hstack(panels))
        path=out/'boards'/(source+'.png');assert cv2.imwrite(str(path),np.vstack(strips))
        sections.append(f'<h2>{source}</h2><img src="boards/{source}.png">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Integrated pipeline stress check</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Same-input integrated stress comparison</h1><p>Fixed held-source folds; no new fitting. Counterfactual severity is not complexion coverage. UNAVAILABLE panels show inputs, not predictions. These candidates still fail quality gates.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_inference_calls=102,verified_outputs=99,verified_failures=failures,
        matched_method_denominators=True,correct_held_source_folds=True,independent_portable_predictions_pixels_metrics=True,
        original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:102 calls,99 independently reconstructed outputs,3 retained failures,matched method denominators')


if __name__=='__main__':main()
