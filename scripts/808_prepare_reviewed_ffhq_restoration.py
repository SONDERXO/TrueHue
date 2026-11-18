"""Fixed44 working-grid restoration records; no learners or image models."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.distortion_generation.development_roles import core_exposure
from src.distortion_generation.core_colour_recipe import render_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.shared_core_mst import predict_score
from src.model_training.whole_scene_features import scene_features
from src.model_training.green_distribution_features import green_distribution_features
from src.demo.manual_refinement import verify_export
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
OUT=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve preparation')
    design=ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json';plan=read(design)
    audit=ROOT/'outputs/reviewed_ffhq_support_audit_v1';receipt=read(audit/'review_PRIVATE.json')
    bound=dict(plan['input_sha256']);bound.update(receipt['input_sha256']);bound[str(design)]=sha(design)
    mapping_path=ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json';mapping=read(mapping_path);bound[str(mapping_path)]=sha(mapping_path)
    for rel in ['src/distortion_generation/development_roles.py','src/distortion_generation/core_colour_recipe.py','src/ita_estimation/compute_ita.py','src/ita_estimation/shared_core_mst.py','src/model_training/whole_scene_features.py','src/model_training/green_distribution_features.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    bases=read(audit/'audit_PRIVATE.json')['latest'];assert len(bases)==11
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(input_sha256=bound,original_photo_reads=0,image_model_calls=0,new_mapping_fits=0,tree_fits=0))
    write(OUT/'mapping_application_PRIVATE.json',dict(mapping_artifact_sha256=sha(mapping_path),original_mapping_core_sha256=mapping['measurement_core_sha256'],original_mapping_contract_sha256=mapping['feature_control_contract_sha256'],outer_application='reviewed_FFHQ_whole_frame256_manual_support',empirical_transfer_validated=False,coefficients_rebound=False,calibration_admitted=False))
    rows=[]
    for base in bases:
        folder=Path(base['annotation']);verify_export(folder);assert sha(folder/'manifest.json')==base['manifest_sha256']
        for p in folder.iterdir():bound[str(p)]=sha(p)
        report=read(folder/'report.json');ident=report['input_bridge']['original_source_id'];clean=cv2.imread(str(folder/'photo_used.png'))[:,:,::-1]
        m=cv2.imread(str(folder/'measurement_mask.png'),0);c=cv2.imread(str(folder/'correction_mask.png'),0);p=cv2.imread(str(folder/'protected_mask.png'),0)>0
        alpha=np.load(folder/'correction_alpha.npy',allow_pickle=False);panels=[]
        recipes=[dict(id='identity',gamma=1.,red_gain=1.,blue_gain=1.)]+plan['recipes']
        for recipe in recipes:
            role=recipe['id'];case='ffhq_'+ident+'__'+role;dest=OUT/case;dest.mkdir()
            if role=='identity':image=clean.copy();forward=dict(clipped_channel_samples=0)
            elif role.startswith('exposure_'):image,forward=core_exposure(clean,np.ones((256,256)),'medium',recipe['direction'])
            else:image,forward=render_rgb(clean,np.ones((256,256)),'medium','cool','none')
            q=recipe;g=q['gamma'];target=[1/g,q['red_gain']**(-1/g),q['blue_gain']**(-1/g)]
            stats=compute_masked_lab_statistics(image[:,:,::-1].copy(),m,1000)
            row=dict(case_id=case,publisher_group='ffhq_source_'+ident,role='identity' if role=='identity' else 'controlled_distortion',experimental_role=role,recipe=recipe,nominal_controls=target,forward_report=forward,statistics=stats,status='unavailable',generated_fixture=False,synthetic_controlled_derivative=role!='identity',user_reviewed_derivative=False,mask_origin='actual_reviewed_reference' if role=='identity' else 'propagated_same_geometry',provided_mst_label=None,annotation=str(folder),annotation_manifest_sha256=base['manifest_sha256'],method_sha256=report['method_sha256'],training_admitted=False,calibration_admitted=False,empirical_mst_transfer_validated=False)
            np.savez_compressed(dest/'paired_pixels.npz',input_rgb8=image,reference_rgb8=clean,alpha=alpha,protected=p,scoring_mask=alpha>0,measurement_mask=m,correction_mask=c)
            row.update(pixels_file=str(dest/'paired_pixels.npz'),pixels_sha256=sha(dest/'paired_pixels.npz'))
            if stats['valid']:
                features={'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']};green=green_distribution_features(image[:,:,::-1].copy(),m);assert green['valid'];features.update(green['features']);features.update(scene_features(image))
                pred=predict_score(mapping,stats['ita_degrees'],measurement_core_sha256=mapping['measurement_core_sha256'],feature_control_contract_sha256=mapping['feature_control_contract_sha256'])
                features['input_mst_score']=pred['score'];row.update(status='available',features=features,input_vector_float32=np.asarray([features[n] for n in plan['feature_names']],np.float32).tolist(),mst_prediction=pred)
            write(dest/'record_PRIVATE.json',row);rows.append(row);panels.append(image[:,:,::-1])
        header=np.full((30,1024,3),255,np.uint8)
        for i,q in enumerate(recipes):cv2.putText(header,ident+' '+q['id'],(i*256+3,20),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
        assert cv2.imwrite(str(OUT/('base_'+ident+'.png')),np.vstack([header,np.hstack(panels)]))
    write(OUT/'rows_PRIVATE.json',rows)
    folds=[dict(held_publisher_group=g,fitting_cases=[r['case_id'] for r in rows if r['publisher_group']!=g and r['status']=='available'],evaluation_cases=[r['case_id'] for r in rows if r['publisher_group']==g],fit_required=True) for g in sorted({r['publisher_group'] for r in rows})]
    write(OUT/'folds_PRIVATE.json',folds)
    write(OUT/'role_ledger_PRIVATE.json',[dict(case_id=r['case_id'],status=r['status']) for r in rows]+[dict(case_id='ffhq_29863__'+role,status='excluded_user_underexposed_reference') for role in ['identity','exposure_under','exposure_over','colour_cool']])
    assert len(rows)==44 and len(folds)==11 and all(sha(p)==h for p,h in bound.items())
    summary=dict(bases=11,attempted_source_roster=12,role_attempts=48,prepared_rows=44,available=sum(r['status']=='available' for r in rows),mapping_applications=sum(r['status']=='available' for r in rows),mapping_fits=0,tree_fits=0,original_photo_reads=0,holdout_reads=0,MST_score_range=[min(r['features']['input_mst_score'] for r in rows if r['status']=='available'),max(r['features']['input_mst_score'] for r in rows if r['status']=='available')],endpoint_clips=sum(r.get('mst_prediction',{}).get('endpoint_clipped',False) for r in rows),forward_float_clipping=sum(r['forward_report']['clipped_channel_samples'] for r in rows))
    write(OUT/'summary_PRIVATE.json',summary);write(OUT/'input_sha256_PRIVATE.json',bound);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
