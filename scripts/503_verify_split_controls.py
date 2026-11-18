"""Independent head leaves/normalization, frozen gate and paired image replay."""
from collections import defaultdict
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.model_training.whole_scene_features import SCENE_FEATURES
PARENT=ROOT/'outputs/whole_scene_correction_v1';GATE=ROOT/'outputs/benefit_aware_gate_v1';CAND=ROOT/'outputs/split_control_comparison_v1';OUT=ROOT/'outputs/split_control_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    v=read(CAND/'results_PRIVATE.json');source=read(PARENT/'results_PRIVATE.json');sf={f['held_key']:f for f in source['folds']}
    rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')};gates={r['case_id']:r for r in read(GATE/'results_PRIVATE.json')['records']}
    folds={f['held_key']:f for f in v['folds']};traces=leaves=norms=0
    for held,fold in folds.items():
        assert fold['training_cases']==sf[held]['training_cases']
        expected=[t['features']+[rows[t['case_id']]['scene_features'][k] for k in SCENE_FEATURES] for t in sf[held]['training_feature_trace']]
        assert expected==fold['training_features'] and all(rows[k]['subject_id']!=held for k in fold['training_cases'])
        y=np.array([rows[k]['target'] for k in fold['training_cases']]);payload=fold['model']
        for name,columns in [('gamma',[0]),('gains',[1,2])]:
            art=payload['heads'][name];tree=PortableTree(art['tree']);values=y[:,columns]
            np.testing.assert_allclose(values.mean(axis=0),art['normalization']['mean'],atol=1e-12,rtol=0)
            np.testing.assert_allclose(values.std(axis=0),art['normalization']['population_std'],atol=1e-12,rtol=0);norms+=1
            groups=defaultdict(list)
            for i,vector in enumerate(expected):groups[tree.leaf_id(vector)].append(i);traces+=1
            for leaf,indices in groups.items():np.testing.assert_allclose(values[indices].mean(axis=0),art['tree']['nodes'][leaf]['values'],atol=1e-12,rtol=0);leaves+=1
    first={}
    for row in sorted(rows.values(),key=lambda r:r['source_case']):first.setdefault(row['subject_id'],row['source_case'])
    boards=[];replays=0;frozen=0
    for r in v['records']:
        row=rows[r['case_id']];inspect=row['case']['id']=='clean' or row['source_case']==first[row['subject_id']] and row['case']['id'] in ['colour_cool','colour_warm','exposure_under','stress_combined_under']
        if r['status']=='unavailable_original':
            if inspect:
                scene=cv2.imread(str(PARENT/row['source_case']/row['case']['id']/'scene_input.png'));board=np.full((156,768,3),255,np.uint8);board[:128,:128]=cv2.resize(scene,(128,128));cv2.putText(board,r['case_id']+' unavailable original',(135,30),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append(board)
            continue
        assert r['gate']==gates[r['case_id']]['gate'];frozen+=1
        folder=PARENT/row['source_case'];pair=folder/row['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
        ref=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
        if r['features'] is not None:
            payload=folds[r['subject_id']]['model'];gamma=PortableTree(payload['heads']['gamma']['tree']).predict_one(r['features']);gains=PortableTree(payload['heads']['gains']['tree']).predict_one(r['features']);parameters=gamma+gains
            assert parameters==r['paths']['split_ungated']['parameters']
        else:parameters=None
        apply=r['gate'] is not None and r['gate']['apply_correction'];gated=parameters if apply and parameters is not None else [1.,1.,1.]
        assert gated==r['paths']['split_gated']['parameters'];outputs={}
        for method,params in [('split_ungated',parameters),('split_gated',gated)]:
            output=render_rgb8(image,mask.astype(float),params) if params is not None else image.copy();stored=cv2.cvtColor(cv2.imread(str(CAND/method/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
            assert np.array_equal(output,stored) and np.array_equal(output[~mask],image[~mask]) and metrics(stored,ref,mask)==r['paths'][method]['metrics'];replays+=1;outputs[method]=stored
            if method=='split_gated' and not apply:assert np.array_equal(output,image)
        if inspect:
            joint=cv2.cvtColor(cv2.imread(str(pair/'face_plus_scene.png')),cv2.COLOR_BGR2RGB);jointgate=cv2.cvtColor(cv2.imread(str(GATE/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
            images=[ref,image,joint,outputs['split_ungated'],jointgate,outputs['split_gated']]
            board=np.concatenate([cv2.resize(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),(128,128),interpolation=cv2.INTER_NEAREST) for im in images],axis=1);title=np.full((28,768,3),255,np.uint8)
            cv2.putText(title,r['case_id']+' ref/input/joint/split/jointGate/splitGate',(2,20),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append(np.concatenate([title,board]))
    for n,h in read(CAND/'input_sha256_PRIVATE.json').items():assert sha(Path(n))==h
    for n,h in read(CAND/'sha256.json').items():assert sha(CAND/n)==h
    assert replays==812 and len(boards)==70
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'contact_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    report=dict(head_training_route_checks=traces,head_leaf_mean_checks=leaves,head_normalization_checks=norms,
        frozen_gate_records=frozen,paired_renderer_metric_replays=replays,preselected_boards=len(boards),refits=0,source_hashes_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
