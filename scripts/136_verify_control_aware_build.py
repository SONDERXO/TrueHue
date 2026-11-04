"""Independently replay candidate leaf means, image math, metrics and hold status."""
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES,TARGETS


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    build=ROOT/'outputs/control_aware_model_build_v1'; replay=ROOT/'outputs/control_aware_candidate_replay_v1'
    report=json.loads((build/'build_report.json').read_text()); summary=json.loads((replay/'summary.json').read_text())
    for mapping in [report['input_sha256'],summary['input_sha256']]:
        assert all(digest(ROOT/p)==h for p,h in mapping.items())
    assert all(digest(build/p)==h for p,h in report['artifact_sha256'].items())
    manifest=json.loads((build/'fit_manifest.json').read_text()); rows=manifest['rows']
    assert len(rows)==len({r['pair_id'] for r in rows})==22
    assert not set(manifest['held_diagnostic_ids']) & {r['pair_id'] for r in rows}
    model=load_model(str(build/'decision_tree.joblib')); tree=model.tree_
    x=np.array([[float(r[k]) for k in FEATURES] for r in rows],dtype=np.float32)
    y=np.array([[float(r[k]) for k in TARGETS] for r in rows])
    assignments=[]
    for row,vector in zip(rows,x):
        gamma,red,blue=[float(row['distortion_'+k]) for k in ['gamma','red_gain','blue_gain']]
        target=[1/gamma,math.pow(red,-gamma),math.pow(blue,-gamma)]
        assert all(abs(a-b)<1e-12 for a,b in zip(target,[float(row[k]) for k in TARGETS]))
        node=0
        while tree.children_left[node]!=tree.children_right[node]:
            node=int(tree.children_left[node] if float(vector[tree.feature[node]])<=tree.threshold[node] else tree.children_right[node])
        assignments.append(node)
    assert assignments==model.apply(x).tolist()
    for leaf in set(assignments):
        members=y[np.asarray(assignments)==leaf]
        mean=[math.fsum(members[:,i])/len(members) for i in range(3)]
        np.testing.assert_allclose(tree.value[leaf,:,0],mean,rtol=0,atol=1e-15)
        assert tree.n_node_samples[leaf]==len(members)
    assert tree.n_node_samples[0]==22
    assert model.get_params()['max_depth']==3 and model.get_params()['random_state']==42
    # Recompute the gate from individual held-source predictions, not its aggregate table.
    comparison=json.loads((ROOT/'outputs/core_control_comparison_v1/summary.json').read_text())
    ids=set(comparison['eligible_ids']); assert ids=={r['pair_id'] for r in rows}
    primary=[p for p in comparison['predictions'] if p['pair_id'] in ids]
    means={}
    for method in ['no_correction','with_controls']:
        group=[p for p in primary if p['method']==method]
        means[method]=(math.fsum(p['ciede2000_source_mask'] for p in group)/len(group),
            np.mean([np.mean([p['ciede2000_source_mask'] for p in group if p['source_image_id']==s]) for s in {p['source_image_id'] for p in group}]))
    original={p['pair_id']:p for p in primary if p['method']=='no_correction'}
    harms={variant:sum(p['ciede2000_source_mask']>original[p['pair_id']]['ciede2000_source_mask']+1e-12
        for p in primary if p['method']=='with_controls' and p['variant']==variant)
        for variant in ['identity_control','mild_bright_exposure']}
    checks=dict(pair_mean_improves=means['with_controls'][0]<means['no_correction'][0],
        equal_source_mean_improves=means['with_controls'][1]<means['no_correction'][1],
        no_unchanged_harm=harms['identity_control']==0,no_mild_harm=harms['mild_bright_exposure']==0)
    assert checks==report['quality_gate']['checks'] and not all(checks.values())
    assert report['quality_gate']['status']=='held_quality_failure'
    core=json.loads((ROOT/'outputs/core_pipeline_check_v1/summary.json').read_text())
    cases={r['pair_id']:r for r in core['records']}; available=0
    # Input/source/scoring paths are frozen in the original CSV manifests.
    import csv
    metadata={}
    for name in ['train','development_validation','clipped_stress','excluded_pairs']:
        with (ROOT/'data/manifests/controlled_training_v2'/(name+'.csv')).open(newline='',encoding='utf-8-sig') as f:
            metadata.update({r['pair_id']:r for r in csv.DictReader(f)})
    for record in summary['records']:
        pair=record['pair_id'];old=cases[pair]
        if record['candidate_metrics'] is None:
            assert old['metrics'] is None and record['original_failed_stage']==old['failed_stage'];continue
        row=metadata[pair]
        vector=np.array([[record['features'][k] for k in FEATURES]])
        parameters=model.predict(vector)[0];np.testing.assert_array_equal(parameters,record['parameters'])
        image=cv2.imread(str(ROOT/row['input_path']))[:,:,::-1].copy()
        reference=cv2.imread(row['source_path'])[:,:,::-1].copy()
        mask=cv2.imread(str(ROOT/'outputs/core_pipeline_check_v1/cases'/pair/'correction_mask.png'),0)>0
        scoring=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        gamma,red,blue=parameters
        transformed=np.rint(np.clip(np.power(image.astype(float)/255,1/gamma)*[red,1,blue],0,1)*255).astype(np.uint8)
        expected=image.copy();expected[mask]=transformed[mask]
        saved=cv2.imread(str(replay/record['corrected_path']))[:,:,::-1].copy()
        np.testing.assert_array_equal(saved,expected);np.testing.assert_array_equal(saved[~mask],image[~mask])
        delta=deltaE_ciede2000(rgb2lab(reference.astype(float)/255),rgb2lab(saved.astype(float)/255))
        assert abs(float(delta[scoring].mean())-record['candidate_metrics']['ciede2000_source_mask'])<1e-12
        assert abs(float(np.abs(reference.astype(float)-saved.astype(float))[scoring].mean()/255)-record['candidate_metrics']['rgb_mae_source_mask'])<1e-12
        available+=1
    assert available==summary['available']==37 and summary['failed']==1
    assert all(digest(ROOT/p)==h for p,h in report['input_sha256'].items())
    result=dict(status='pass',fit_rows_checked=22,leaf_means_checked=len(set(assignments)),
        new_verification_fits=0,images_and_metrics_replayed=37,original_failure_retained=True,
        recipe_gate_recomputed_from_individual_source_held_out_predictions=True,quality_hold_preserved=True,
        original_model_inputs_and_android_asset_unchanged=True,
        build_report_sha256=digest(build/'build_report.json'),replay_summary_sha256=digest(replay/'summary.json'),
        verifier_sha256=digest(Path(__file__)),
        replay_artifact_sha256={p.relative_to(replay).as_posix():digest(p) for p in replay.rglob('*') if p.is_file() and p.name!='verification.json'})
    (replay/'verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='replay_artifact_sha256'},indent=2))


if __name__=='__main__':main()
