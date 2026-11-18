"""Independent serialized task/identity-alpha/native-projection checks, no models."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.labelled_measurement import verify,digest,write
from src.demo.photographic_reference_review import latest_preferences
from src.correction.seamless_blend import apply_blended
from src.model_training.aligned_correction_support import project_alpha


def main():
    out=ROOT/'outputs/photographic_support_tasks_v1';dest=out/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    check=read(out/'verification_PRIVATE.json');assert check['passed']
    assert all(digest(p)==h for p,h in check['input_sha256'].items())
    queue=read(out/'queue.json');assert len(queue['tasks'])==14 and len(queue['blocked'])==2
    assert all(r['frame']=='904_0' for r in queue['blocked'])
    style_queue=read(ROOT/'outputs/photographic_reference_review_v1/queue.json')['tasks']
    choices=latest_preferences(style_queue,ROOT/'outputs/photographic_reference_decisions_v1')
    assert len(choices)==8 and all(r['choice']=='suitable' for r in choices.values())
    cases=[]
    for row in queue['tasks']:
        folder=out/row['folder'];verify(folder);assert digest(folder/'manifest.json')==row['manifest_sha256']
        r=read(folder/'report.json');assert r['case_id']==row['case_id'] and r['frame']!='904_0'
        parent=ROOT/('outputs/ppr10k_native_pipeline_diagnostic_v1' if r['role']=='source' else 'outputs/ppr10k_expert_control_readiness_v1')/r['frame']
        image=cv2.imread(str(folder/'photo_used.png'));original=cv2.imread(str(parent/'input.png'))
        assert np.array_equal(image,original)
        m=cv2.imread(str(folder/'measurement_mask.png'),0);p=cv2.imread(str(folder/'protected_mask.png'),0);c=cv2.imread(str(folder/'correction_mask.png'),0)
        assert np.array_equal(m,cv2.imread(str(parent/'measurement_mask.png'),0))
        assert np.array_equal(p,cv2.imread(str(parent/'protected_normalized.png'),0))
        assert not np.any((c>0)&(p>0))
        rendered,alpha,_=apply_blended(image,c,(1.,1.,1.),face_width=r['face_width'],protected=p>0)
        assert np.array_equal(rendered,image)
        assert np.array_equal(alpha,np.load(parent/'alpha_normalized.npy',allow_pickle=False))
        native,native_p=project_alpha(alpha,p>0,r['input_bridge'])
        assert np.array_equal(native,np.load(parent/'alpha_native.npy',allow_pickle=False))
        assert np.array_equal(native_p,cv2.imread(str(parent/'protected_native.png'),0)>0)
        assert r['provided_mst_label'] is None and not r['training_admitted'] and not r['calibration_admitted']
        cases.append(r['case_id'])
    assert len(set(cases))==14 and len({c.split('__')[0] for c in cases})==7
    paths=[out/'queue.json',out/'method.json',out/'verification_PRIVATE.json',Path(__file__),
        ROOT/'src/demo/photographic_support.py',ROOT/'src/demo/photographic_support_window.py',
        ROOT/'src/demo/refinement_window.py',ROOT/'scripts/737_save_photographic_support.py',
        ROOT/'scripts/738_review_photographic_support.py',ROOT/'scripts/739_check_photographic_support_gui.py',
        ROOT/'tests/test_photographic_support.py',ROOT/'outputs/photographic_support_gui_check_v1/verification.json',
        ROOT/'review_photographic_support.cmd']
    write(dest,dict(passed=True,serialized_tasks=14,blocked_roles=2,accepted_appearances=8,
        exact_identity_alpha_native_projection_checks=14,calibration_fits=0,tree_fits=0,model_forwards=0,
        original_TIFF_reads=0,holdout_bytes_read=0,input_sha256={str(p):digest(p) for p in paths}))
    print('PASS: 14 exact masks/identity-alpha/native projections; 2 blocked904roles; 8 accepted target preferences.')


if __name__=='__main__':main()
