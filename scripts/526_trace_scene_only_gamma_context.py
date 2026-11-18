"""Scene-only gamma-route context without inventing missing facial features."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.whole_scene_features import scene_features
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    O=ROOT/'outputs/recovered_false_correction_diagnosis_v1';output=O/'scene_only_gamma_context_PRIVATE.json'
    if output.exists():raise FileExistsError(output)
    M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';P=ROOT/'outputs/detector_appearance_merged_v1/results_PRIVATE.json';E=ROOT/'outputs/detector_appearance_correction_v1/results_PRIVATE.json';m=read(M);tree=m['split']['heads']['gamma']['tree'];preds={r['case_id']:r for r in read(E)['records']}
    sources=[r for r in read(P)['records'] if r['source_case']=='eval_22'];assert len(sources)==14
    bindings={str(p):sha(p) for p in [M,P,E,Path(__file__),ROOT/'src/model_training/whole_scene_features.py']};records=[]
    for s in sources:
        path=Path(s['source_path']);bindings[str(path)]=sha(path);rgb=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB);features=scene_features(rgb);node=0;route=[]
        while tree['nodes'][node]['kind']=='split':
            n=tree['nodes'][node];name=m['feature_names'][n['feature']]
            if name not in features:break
            value=float(np.float32(features[name]));left=value<=n['threshold'];route.append(dict(node=node,feature=name,value_float32=value,threshold=n['threshold'],branch='left' if left else 'right'));node=n['left'] if left else n['right']
        resolved=tree['nodes'][node]['kind']=='leaf';gamma=tree['nodes'][node]['values'][0] if resolved else None;prior=preds[s['case_id']]
        if gamma is not None and prior['features'] is not None:assert gamma==prior['paths']['input_ungated']['parameters'][0]
        records.append(dict(case_id=s['case_id'],scene_features=features,route=route,scene_only_path_resolved=resolved,gamma_leaf=node if resolved else None,gamma=gamma,actual_full_feature_prediction_available=prior['features'] is not None,NOT_full_prediction_if_facial_measurement_missing=prior['features'] is None))
    output.write_text(json.dumps(dict(records=records,input_sha256=bindings,new_fits=0,new_image_model_inference=0),indent=2),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items())
    for r in records:
        if r['case_id'].endswith('__clean') or r['case_id'].endswith('__colour_warm'):print(json.dumps(r,indent=2))
if __name__=='__main__':main()
