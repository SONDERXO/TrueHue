"""Independent arithmetic replay of the saved single-case diagnosis."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
O=ROOT/'outputs/recovered_false_correction_diagnosis_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if (O/'verification_PRIVATE.json').exists():raise FileExistsError('Already verified')
    v=read(O/'diagnosis_PRIVATE.json');m=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json');assert all(sha(Path(p))==h for p,h in read(O/'input_sha256_PRIVATE.json').items());assert all(sha(O/n)==h for n,h in read(O/'sha256.json').items())
    vector=[v['features'][n] if n in v['features'] else v['scene_features'][n] for n in m['feature_names']]
    gate=m['gate'];terms=[(x-a)/b*c for x,a,b,c in zip(vector,gate['mean'],gate['scale'],gate['coefficient'])]
    assert abs(sum(terms)+gate['intercept']-v['gate']['logit'])<1e-12
    for a,b in zip(terms,v['gate']['contributions']):assert abs(a-b['logit_term'])<1e-12
    for name in ['gamma','gains']:
        tree=m['split']['heads'][name]['tree'];route=v['heads'][name]['route'];node=0
        for step in route:
            n=tree['nodes'][node];left=float(np.float32(vector[n['feature']]))<=n['threshold'];assert step['node']==node and step['branch']==('left' if left else 'right');node=n['left'] if left else n['right']
        assert node==v['heads'][name]['leaf'] and tree['nodes'][node]['values']==v['heads'][name]['prediction']
    source=next(r for r in read(ROOT/'outputs/detector_appearance_merged_v1/results_PRIVATE.json')['records'] if r['case_id']==v['case_id']);folder=Path(source['artifact_root']);mask=cv2.imread(str(folder/'native_grid.png'),0)>0;ref=cv2.imread(str(ROOT/'outputs/frozen_split_subject_check_v1/eval_22/source.jpeg'));image=cv2.imread(source['source_path'])
    for name,report in v['component_replays'].items():
        output=cv2.imread(str(O/(name+'.png')));error=np.abs(output.astype(np.int16)-ref.astype(np.int16));assert abs(float(error[mask].mean())-report['own_predicted_region_NOTskin_truth']['rgb8_mae_codes'])<1e-12;assert abs(float(error.mean())-report['full_scene']['rgb8_mae_codes'])<1e-12;assert np.array_equal(output[~mask],image[~mask])
    before=v['component_replays']['neutral'];after=v['component_replays']['full'];delta=(after['own_predicted_region_NOTskin_truth']['rgb8_mae_codes']-before['own_predicted_region_NOTskin_truth']['rgb8_mae_codes'])*mask.sum()/mask.size
    assert abs(delta-(after['full_scene']['rgb8_mae_codes']-before['full_scene']['rgb8_mae_codes']))<1e-12
    (O/'verification_PRIVATE.json').write_text(json.dumps(dict(gate_terms=12,tree_routes=2,component_rgb_error_replays=4,own_to_full_error_delta_verified=True,source_hashes_unchanged=True,new_fits=0,new_inference=0),indent=2),encoding='utf-8');print('Verified12gate terms,2routes,4independent RGB errors and exact region-to-scene error delta.')
if __name__=='__main__':main()
