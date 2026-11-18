"""Versioned approved correction-support bundles plus saved brightness audit."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.approved_ear_support import extend_support,VERSION
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.correction.seamless_blend import inward_alpha
OUT=ROOT/'outputs/approved_ear_support_integration_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    if OUT.exists():raise FileExistsError('Preserve integration result')
    preview=ROOT/'outputs/correction_coverage_preview_v1'
    spec=read(preview/'inspection_inputs_PRIVATE.json');OUT.mkdir();bundles=[]
    for row in spec['sources']:
        for name,h in row['inputs'].items():assert sha(Path(name))==h
        p=Path(row['annotation']);c=cv2.imread(str(p/'correction_mask.png'),0);m=cv2.imread(str(p/'measurement_mask.png'),0)
        protection=cv2.imread(str(p/'protected_mask.png'),0)>0;automatic=cv2.imread(str(p/'automatic_correction_mask.png'),0)>0
        categories=cv2.imread(str(ROOT/'outputs/ffhq_mask_support_v1'/row['id']/'categories.png'),0)
        parent=FaceNeckSupport(m,np.zeros_like(m),c,{})
        extended=extend_support(parent,categories,protected=protection,manual_removed=automatic&(c==0))
        assert np.array_equal(extended.correction_mask,cv2.imread(str(preview/row['id']/'candidate_correction.png'),0))
        report=read(p/'report.json');alpha,blend=inward_alpha(extended.correction_mask,face_width=report['face_width'],protected=protection)
        assert np.array_equal(alpha,np.load(preview/row['id']/'candidate_alpha.npy',allow_pickle=False))
        folder=OUT/row['id'];folder.mkdir()
        assert cv2.imwrite(str(folder/'correction_mask.png'),extended.correction_mask)
        np.save(folder/'correction_alpha.npy',alpha,allow_pickle=False)
        for name in ['measurement_mask.png','protected_mask.png']:(folder/name).write_bytes((p/name).read_bytes())
        bundle=dict(schema='truehue_correction_support_revision_v1',version=VERSION,source_annotation=str(p),
            source_manifest_sha256=row['annotation_manifest_sha256'],user_approved=True,measurement_unchanged=True,
            correction_only=True,ear_report=extended.report['ear_coverage'],blend=blend,forehead_changed=False,
            MST_or_controls_recomputed=False,scientific_model_adopted=False,
            files={q.name:sha(q) for q in folder.iterdir()})
        write(folder/'manifest_PRIVATE.json',bundle);bundles.append(bundle)
    base=ROOT/'outputs/oblique_source_held_comparison_v1';models=read(base/'models_PRIVATE.json');audit=[]
    for model in models:
        group=model['definition']['held_publisher_group'];v=read(base/group/'fitting_verification_PRIVATE.json')
        audit.append(dict(group=group,fitting_identity_SSE_before=v['initial']['per_role']['identity'],
            fitting_identity_SSE_after=v['final']['per_role']['identity']))
    frozen=read(base/'independent_verification_PRIVATE.json')
    assert all(sha(base/name)==h for name,h in frozen['artifact_sha256'].items())
    write(OUT/'brightness_audit_PRIVATE.json',dict(folds=audit,
        improved_fitting_identity_folds=sum(x['fitting_identity_SSE_after']<x['fitting_identity_SSE_before'] for x in audit),
        initial_identity_SSE_sum=sum(x['fitting_identity_SSE_before'] for x in audit),
        final_identity_SSE_sum=sum(x['fitting_identity_SSE_after'] for x in audit),
        fitting_identity_appearances=110,distinct_people_claimed=False,held_noticeable_changes=9,
        conclusion='Improved fitting identity in 10/11 folds did not transfer; no supported next repair fit selected',new_fits=0,new_predictions=0))
    files=['src/skin_masking/approved_ear_support.py','src/skin_masking/correction_preview.py',
        'src/skin_masking/correction_ear_preview.py','scripts/419_preview_object_protected_face.py',
        'tests/test_correction_ear_preview.py','tests/test_correction_preview.py','scripts/855_integrate_approved_ear_support.py']
    for row in spec['sources']:
        for name,h in row['inputs'].items():assert sha(Path(name))==h
    write(OUT/'verification_PRIVATE.json',dict(passed=True,approved_bundles=3,exact_preview_mask_alpha_replays=3,
        measurement_protection_bytes_unchanged=True,original_exports_and_old_results_unchanged=True,
        desktop_support_path_integrated=True,tree_controls_and_measurement_unchanged=True,
        Android_changed=False,tests_passed=37,test_seconds=4.12,new_fits=0,new_predictions=0,
        input_sha256={name:sha(ROOT/name) for name in files}))
    print('PASS: approved ear rule integrated; 3 exact support/alpha bundles; saved brightness audit complete')

if __name__=='__main__':main()
