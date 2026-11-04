"""Independent composite, clipping, residual and saved prediction checks."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_counterfactual_coverage_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    summary=read(out/'summary.json');plan=read(out/'plan.json')
    assert len(summary['records'])==24 and contract(ROOT)[1]==summary['measurement_contract_sha256']
    for p,h in summary['input_sha256'].items():assert digest(ROOT/p)==h
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==summary['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),summary['measurement_contract_sha256'])
    # Fixed protocol settings repeated independently, rather than importing the generator.
    settings={'light':(.85,-20,5,-6,6),'medium':(.70,-35,8,-10,10),'dark':(.60,-45,10,-14,14)}
    checks=[]
    for row in summary['records']:
        pair=row['pair_id'];reference=rgb(ROOT/row['reference_path'])
        scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        g,bright,contrast,red,blue=settings[row['severity_probe']]
        raw=(np.power(reference.astype(float)/255,1/g)-.5)*(1+contrast/100)+.5+bright/255
        raw=raw+np.array([red,0,blue])/255
        generated=reference.copy();generated[scoring]=np.rint(np.clip(raw[scoring],0,1)*255).astype(np.uint8)
        image=rgb(out/'images'/(pair+'_input.png'));np.testing.assert_array_equal(image,generated)
        clipped=(raw<0)|(raw>1)
        assert row['clipping']['clipped_pixels']==int(np.any(clipped,axis=2)[scoring].sum())
        assert row['clipping']['clipped_channel_samples']==int(clipped[scoring].sum())
        assert row['clipping_fraction']==row['clipping']['clipped_pixels']/int(scoring.sum())
        assert image_errors(reference,image,scoring)==row['no_correction']
        if row['status']!='success':
            assert not any(k in row for k in ['features','parameters','learned','target_fit'])
            checks.append(dict(pair_id=pair,status=row['status']));continue
        mask=cv2.imread(str(out/'images'/(pair+'_mask.png')),0)>0
        stats=compute_masked_lab_statistics(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask.astype(np.uint8)*255,1000)
        assert stats['valid']
        assert {k:stats[v] for k,v in zip(FEATURES,FEATURE_KEYS)}==row['measurement']['features']
        assert row['features']['input_mst_index']==lookup.label(stats['ita_degrees'])-1
        tree=PortableTree(read(ROOT/f"outputs/table2_reviewed_expansion_evaluation_v1/fold_{row['fold_id']}/decision_tree.json"))
        np.testing.assert_allclose(tree.predict_one([row['features'][k] for k in MST_FEATURES]),row['parameters'],atol=1e-12,rtol=0)
        def replay(parameters):
            gamma,r,b=parameters
            transformed=np.rint(np.clip(np.power(image.astype(float)/255,1/gamma)*[r,1,b],0,1)*255).astype(np.uint8)
            result=image.copy();result[mask]=transformed[mask];return result
        for method,parameters in [('learned',row['parameters']),('oracle',row['target_fit']['parameters'])]:
            if parameters is None:continue
            result=rgb(out/'images'/(pair+'_'+method+'.png'))
            np.testing.assert_array_equal(result,replay(parameters))
            assert image_errors(reference,result,scoring)==row[method]
        fitted=row['target_fit']
        if fitted['parameters'] is not None:
            intersection=mask&scoring;x=image[intersection].astype(float)/255;y=reference[intersection].astype(float)/255
            gamma,r,b=fitted['parameters'];pred=np.clip(np.power(x,1/gamma)*[r,1,b],0,1)
            assert abs(float(np.sqrt(np.mean((pred-y)**2)))-fitted['float_rgb_rmse'])<1e-12
            assert fitted['selected_pixels']==int(intersection.sum())
        assert row['reference_mask_retention']==float((mask&scoring).sum()/scoring.sum())
        checks.append(dict(pair_id=pair,status='verified_prediction_and_target'))
    for severity,report in summary['aggregate'].items():
        subset=[r for r in summary['records'] if r['severity_probe']==severity]
        paired=[r for r in subset if 'oracle' in r and 'learned' in r]
        assert report['attempts']==len(subset)==8
        assert report['paired_metric_count']==len(paired)
        for method in ['no_correction','learned','oracle']:
            assert report[method+'_ciede2000']==float(np.mean([r[method]['ciede2000_source_mask'] for r in paired]))
    assert not set(plan['source_ids'])&{'51739','40048','42532','63870'}
    target.write_text(json.dumps(dict(status='pass',checks=checks,composites_and_clipping_recomputed=24,
        source_hashes_unchanged=True,models_fitted=0,training_admitted=0,summary_sha256=digest(out/'summary.json'),
        evidence_sha256={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:',len(checks),'counterfactual probes; independent pixels/clipping/features/predictions/residuals/metrics')


if __name__=='__main__':main()
