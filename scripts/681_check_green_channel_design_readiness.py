"""Design metadata and synthetic generator checks; never reads photo/mask bytes."""
from pathlib import Path
import hashlib,json,sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.photographic_target_diagnostic import case_matrix,distort
OUT=ROOT/'outputs/green_channel_design_readiness_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve design readiness')
    bound={}
    def read(path):
        path=ROOT/path;bound[str(path)]=sha(path);return json.loads(path.read_text())
    model=read('outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    v=read('outputs/colour_nonharm_models_v1/verification_PRIVATE.json')
    assert v['passed'] and v['model_sha256']==sha(ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    aligned=read('outputs/aligned_correction_preparation_v1/results_PRIVATE.json')
    expanded=read('outputs/expanded_correction_inputs_v1/results_PRIVATE.json')
    plan=read('outputs/expanded_correction_training_plan_v1/plan_PRIVATE.json')
    metadata={r['case_id']:r for r in aligned['records']+expanded['records']}
    ids=set(model['full']['training_cases'])
    assert len(ids)==890 and len(model['feature_names'])==12
    reserved={r['case_id'] for r in model['full']['reserved_clean_vectors']}
    assert len(reserved)==20 and not ids&set(model['reserved_all_conditions'])
    assert all(set(f['training_cases'])<=ids and not set(f['training_cases'])&set(model['reserved_all_conditions']) for f in model['folds'])
    groups={metadata[c]['subject_id'] for c in ids}
    assert not groups&set(plan['closed_holdout_keys'])
    for f in model['folds']:
        assert all(metadata[c]['subject_id']!=f['held_key'] for c in f['training_cases'])
    assets=[]
    for cid in sorted(ids|reserved):
        r=metadata[cid];assert r['status']=='available'
        mask=Path(r['measurement_native_path']).parent/'measurement_mask.png'
        if cid.startswith('diversity_') and cid.endswith('__clean'):
            image=Path(r['scene_path']).parent/'input.png'
        else:image=mask.parent/'input.png'
        assets.append(dict(case_id=cid,role='fitting' if cid in ids else 'reserved_clean',
            subject_id=r['subject_id'],image_path=str(image),mask_path=str(mask),
            image_exists=image.is_file(),mask_exists=mask.is_file(),
            inherited_image_sha256=model['input_sha256'].get(str(image)),
            inherited_mask_sha256=model['input_sha256'].get(str(mask))))
    # Artificial pixels only; no cv2/image decoder or real photo reads.
    ramp=np.arange(256,dtype=np.uint8).reshape(16,16)
    artificial=np.stack([255-ramp,ramp,np.roll(ramp,5,axis=1)],axis=2)
    tests=[]
    for scope,alpha in [('full',np.ones((16,16),float)),('blended',np.linspace(0,1,256).reshape(16,16))]:
        for case in case_matrix():
            output,_,_=distort(artificial,alpha,case)
            again,_,_=distort(artificial,alpha,case);assert np.array_equal(output,again)
            changes=int(np.count_nonzero(output[:,:,1]!=artificial[:,:,1]))
            colour=case['scenario']=='color'
            if colour or case['scenario']=='clean':assert changes==0
            else:assert changes>0
            def features(im):
                q=np.percentile(im[:,:,1],[10,50,90],method='linear')
                return [*map(float,q),float(np.log((q[2]+1)/(q[0]+1)))]
            if colour:assert features(output)==features(artificial)
            tests.append(dict(alpha_scope=scope,recipe=case['id'],changed_green_samples=changes,
                              colour_green_identity=colour and changes==0,deterministic=True))
    for rel in ['docs/green-channel-correction-design-2026-11-09.md','scripts/681_check_green_channel_design_readiness.py',
        'src/model_training/photographic_target_diagnostic.py','src/distortion_generation/core_colour_recipe.py',
        'src/distortion_generation/directional_exposure_recipe.py','src/distortion_generation/development_roles.py',
        'src/distortion_generation/table2_composite.py','src/model_training/colour_nonharm_action_tree.py',
        'src/model_training/facial_brightness_features.py','src/model_training/chroma_distribution.py',
        'src/model_training/facial_endpoint_features.py']:
        p=ROOT/rel;bound[str(p)]=sha(p)
    summary=dict(full_fitting_conditions=len(ids),fitting_originals=len({c.split('__',1)[0] for c in ids}),
        fitting_publisher_groups=len(groups),reserved_clean_conditions=len(reserved),
        cached_image_mask_pairs=len(assets),missing_cached_files=sum(not a['image_exists'] or not a['mask_exists'] for a in assets),
        images_with_inherited_hash=sum(a['inherited_image_sha256'] is not None for a in assets),
        masks_with_inherited_hash=sum(a['inherited_mask_sha256'] is not None for a in assets),
        synthetic_recipe_checks=len(tests),synthetic_colour_identity_checks=sum(t['colour_green_identity'] for t in tests),
        feature_extraction_run=False,model_fits=0,photo_or_mask_byte_reads=0,holdout_image_reads=0)
    assert summary['missing_cached_files']==0
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();p=OUT/'readiness_PRIVATE.json'
    p.write_text(json.dumps(dict(summary=summary,assets=assets,synthetic_checks=tests,input_sha256=bound,
        disposition='Design selected; metadata and generator checks pass. Actual-input feature correctness/behaviour remains pending. Not fit-ready yet.'),indent=2))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,scope='metadata joins/roles/path existence and artificial recipe checks only',
        readiness_sha256=sha(p),source_hashes=len(bound),photo_or_mask_byte_reads=0,holdout_image_reads=0),indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
