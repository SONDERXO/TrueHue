"""Same451available evaluation vectors; fixed extraction, no inference or fitting."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.green_distribution_features import green_distribution_features,ADDITIONS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
OUT=ROOT/'outputs/evaluation_green_features_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial preparation')
    source=ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json';m=read(source)
    prep=ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json';rows={r['case_id']:r for r in read(prep)['records']}
    f=ROOT/'outputs/fitting_green_features_v1';v=read(f/'verification_with_metadata_PRIVATE.json')
    assert v['passed'] and v['features_sha256']==sha(f/'features_PRIVATE.json')
    assessment=read(f/'assessment_PRIVATE.json');assert assessment['technical_preparation_passed']
    bound={str(p):sha(p) for p in [source,prep,f/'verification_with_metadata_PRIVATE.json',f/'features_PRIVATE.json',f/'assessment_PRIVATE.json',f/'prepared_vectors_PRIVATE.json',Path(__file__),ROOT/'src/model_training/green_distribution_features.py',ROOT/'docs/green-channel-correction-design-2026-11-09.md']}
    records=[]
    for p in m['predictions']:
        r=rows[p['case_id']]
        if p['features'] is None:
            assert r['status']!='available';records.append(dict(case_id=p['case_id'],features=None));continue
        folder=Path(r['scene_path']).parent;ip=folder/'input.png';mp=folder/'measurement_mask.png'
        for path in (ip,mp):
            assert sha(path)==m['input_sha256'][str(path)];bound[str(path)]=sha(path)
        image=cv2.imread(str(ip));mask=cv2.imread(str(mp),0)
        raw=compute_masked_lab_statistics(image,mask,1000);assert raw['valid']
        for name in ('mean_l_star','mean_a_star','mean_b_star','ita_degrees'):assert raw[name]==r['raw_features']['input_'+name]
        value=green_distribution_features(image,mask);assert value['valid']
        records.append(dict(case_id=p['case_id'],image_path=str(ip),mask_path=str(mp),features=value['features'],skin_pixels=value['skin_pixels']))
    assert len(records)==756 and sum(r['features'] is not None for r in records)==451
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir()
    (OUT/'features_PRIVATE.json').write_text(json.dumps(dict(records=records,feature_names=list(ADDITIONS),input_sha256=bound,new_forwards=0,new_fits=0,holdout_image_reads=0),indent=2))
    print('Prepared451available,305unavailable,756attempts; no fits or forwards')
if __name__=='__main__':main()
