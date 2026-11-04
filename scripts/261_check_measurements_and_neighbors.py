"""Input measurement parity and source-held clean/distorted neighbor audit."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.square_measurement import contract
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.evaluation.feature_target_diagnostic import neighbor_diagnostic


def main():
    out=ROOT/'outputs/measurement_neighbor_audit_v1';parent=ROOT/'outputs/accepted_clean_control_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(parent/'plan.json');assert read(parent/'verification.json')['status']=='pass'
    for path,digest in plan['input_sha256'].items():assert sha(ROOT/path)==digest
    _,identity=contract(ROOT);assert identity==plan['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    rows={r['pair_id']:r for r in plan['rows']};vectors={}
    for pair,r in rows.items():
        image=cv2.imread(str(ROOT/r['input_path']));mask=cv2.imread(str(ROOT/r['input_mask_path']),0)
        statistics=compute_masked_lab_statistics(image,mask,1000);assert statistics['valid']
        features={f:float(statistics[k]) for f,k in zip(FEATURES,FEATURE_KEYS)}
        features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features=={k:r[k] for k in plan['features']}
        vectors[pair]=[features[k] for k in plan['features']]
    predictions={r['pair_id']:r for r in read(parent/'predictions.json') if r['method']=='new_clean_sources'}
    records=[]
    for fold in plan['folds']:
        fitting=fold['historical_train_ids']+fold['new_control_train_ids']
        assert len(set(fitting))==len(fitting)
        x=np.array([vectors[p] for p in fitting]);targets=[rows[p]['paper_target'] for p in fitting]
        for pair in fold['held_pair_ids']:
            row=rows[pair]
            assert row['source_image_id'] not in {rows[p]['source_image_id'] for p in fitting}
            neighborhoods={}
            for name,axes in [('Lab3',[0,1,2]),('Lab_ITA_MST5',list(range(5)))]:
                result=neighbor_diagnostic(fitting,x,targets,vectors[pair],row['paper_target'],axes)
                active=np.array(result['active_axes']);scale=np.array(result['fit_population_std'])
                # Independently recompute every descriptive distance/ranking.
                selected=x[:,axes];valid=scale>0
                expected=np.linalg.norm((selected[:,valid]-np.array(vectors[pair])[active])/scale[valid],axis=1)
                ranking=sorted(range(len(fitting)),key=lambda i:(float(expected[i]),fitting[i]))
                assert [fitting[i] for i in ranking]==[r['pair_id'] for r in result['ranking']]
                for near in result['ranking']:
                    assert abs(near['distance']-expected[fitting.index(near['pair_id'])])<1e-12
                clean=next(r for r in result['ranking'] if rows[r['pair_id']]['variant']=='identity')
                distorted=next(r for r in result['ranking'] if rows[r['pair_id']]['variant']!='identity')
                neighborhoods[name]=dict(nearest_clean=clean,nearest_distorted=distorted,
                    distorted_strictly_closer=distorted['distance']<clean['distance'],
                    fit_population_std=result['fit_population_std'],constant_axes=result['constant_axes'])
            records.append(dict(pair_id=pair,variant=row['variant'],cohort=row['cohort'],
                changed_by_augmented_tree=predictions[pair]['changed_input_pixels']>0,neighborhoods=neighborhoods))
    assert len(records)==41
    counts=[]
    for name in ('Lab3','Lab_ITA_MST5'):
        for scope,part in [('clean',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity'])]:
            counts.append(dict(distance=name,scope=scope,pairs=len(part),
                nearest_distorted=sum(r['neighborhoods'][name]['distorted_strictly_closer'] for r in part)))
    collisions=[]
    ordered=list(rows)
    for i,a in enumerate(ordered):
        for b in ordered[i+1:]:
            if rows[a]['source_image_id']==rows[b]['source_image_id']:continue
            if np.array_equal(np.array(vectors[a],np.float32),np.array(vectors[b],np.float32)):
                collisions.append(dict(a=a,b=b,different_targets=rows[a]['paper_target']!=rows[b]['paper_target']))
    out.mkdir()
    summary=dict(status='verified_descriptive_audit_only',remeasured_input_vectors=41,counts=counts,
        exact_float32_cross_source_collisions=collisions,records=records,
        limitation='Fitting-standardized Euclidean distance is descriptive, not a confidence metric or proof that these features cannot learn. ITA and MST are derived from Lab and add correlated weighting.',
        new_predictions=0,active_demo_changed=False,reserved_data_access=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',exact_feature_and_lookup_parity=41,
        independently_checked_distance_rankings=82,source_separation_verified=True,
        summary_sha256=sha(out/'summary.json'),producer_sha256=sha(Path(__file__)),
        inputs_sha256=plan['input_sha256']),indent=2),encoding='utf-8')
    print(json.dumps(dict(counts=counts,exact_collisions=len(collisions),measurement_vectors_verified=41)))


if __name__=='__main__':main()
