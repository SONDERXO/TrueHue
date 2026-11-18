"""Capacity comparison: independent saved portable/renderer checks, no fitting."""
from collections import Counter
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1';CAND=ROOT/'outputs/correction_capacity_comparison_v2';OUT=ROOT/'outputs/correction_capacity_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    v=read(CAND/'results_PRIVATE.json');old=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    folds={f['held_key']:f for f in v['folds']};basefolds={f['held_key']:f for f in old['folds']}
    for key,f in folds.items():
        assert f['training_cases']==basefolds[key]['training_cases']
        y=np.array([rows[k]['target'] for k in f['training_cases']])
        np.testing.assert_allclose(y.mean(axis=0),f['normalization']['fitting_target_mean'],atol=1e-12,rtol=0)
        np.testing.assert_allclose(y.std(axis=0),f['normalization']['fitting_population_std'],atol=1e-12,rtol=0)
    count=0;changed=Counter();splits=Counter();boards=[]
    for f in v['folds']:
        for node in f['tree']['nodes']:
            if node['kind']=='split':splits[v['feature_names'][node['feature']]]+=1
    for r in v['records']:
        if r['status']=='unavailable_original':continue
        row=rows[r['case_id']];folder=PARENT/row['source_case'];pair=folder/row['case']['id']
        image=cv2.imread(str(pair/'input.png'));mask=cv2.imread(str(folder/'mask.png'),0)>0
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);ref=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB)
        if r['parameters'] is not None:
            assert PortableTree(folds[r['subject_id']]['tree']).predict_one(r['features'])==r['parameters']
            output=render_rgb8(rgb,mask.astype(float),r['parameters'])
        else:output=rgb
        saved=cv2.cvtColor(cv2.imread(str(CAND/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
        assert np.array_equal(output,saved) and np.array_equal(output[~mask],rgb[~mask]) and metrics(output,ref,mask)==r['candidate_metrics']
        previous=cv2.cvtColor(cv2.imread(str(pair/'prediction.png')),cv2.COLOR_BGR2RGB)
        changed[r['layer']]+=not np.array_equal(saved,previous);count+=1
        if r['layer']=='clean':
            panel=np.concatenate([cv2.resize(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),(160,160),interpolation=cv2.INTER_NEAREST) for im in [ref,previous,saved]],axis=1)
            title=np.full((26,480,3),255,np.uint8);cv2.putText(title,row['source_case']+' original / baseline / feature candidate',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.37,(0,0,0),1);boards.append(np.concatenate([title,panel]))
    for path,h in read(CAND/'input_sha256_PRIVATE.json').items():assert sha(Path(path))==h
    for path,h in read(CAND/'sha256.json').items():assert sha(CAND/path)==h
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'clean_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    report=dict(renderer_and_metric_replays=count,changed_images_from_baseline=dict(changed),split_feature_counts=dict(splits),fitting_normalizations=10,refits=0,all_bound_sources_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
