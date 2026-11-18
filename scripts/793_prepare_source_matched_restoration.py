"""Prepare exactly21 controlled derivatives and costs; no learner imports/fits."""
from pathlib import Path
import hashlib,json,sys
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.demo.labelled_measurement import verify
from src.distortion_generation.development_roles import core_exposure
from src.distortion_generation.core_colour_recipe import render_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.shared_core_mst import predict_score
from src.model_training.whole_scene_features import scene_features
from src.model_training.green_distribution_features import green_distribution_features
from src.model_training.aligned_correction_support import blended_action_costs

DESIGN=ROOT/'outputs/source_matched_restoration_design_v1'
OUT=ROOT/'outputs/source_matched_restoration_preparation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')


def main():
    if OUT.exists():raise FileExistsError('Preserve previous or partial preparation')
    receipt=read(DESIGN/'review_PRIVATE.json');assert receipt['passed']
    bound=dict(receipt['input_sha256']);assert all(sha(p)==h for p,h in bound.items())
    plan=read(DESIGN/'plan_PRIVATE.json');bases=read(DESIGN/'bases_PRIVATE.json')
    old=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')
    mapping_path=ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json';mapping=read(mapping_path);bound[str(mapping_path)]=sha(mapping_path)
    actions=plan['training']['tree']['actions'];names=plan['training']['tree']['feature_names']
    for base in bases:
        assert sha(base['pixels_file'])==base['pixels_sha256'];bound[base['pixels_file']]=base['pixels_sha256']
        annotation=Path(base['annotation_folder']);verify(annotation)
        assert sha(annotation/'manifest.json')==base['annotation_manifest_sha256']
        for name in ('manifest.json','measurement_mask.png','photo_used.png'):
            bound[str(annotation/name)]=sha(annotation/name)
    for relative in ('src/distortion_generation/development_roles.py','src/distortion_generation/core_colour_recipe.py',
        'src/ita_estimation/compute_ita.py','src/ita_estimation/shared_core_mst.py','src/model_training/whole_scene_features.py',
        'src/model_training/green_distribution_features.py','src/model_training/aligned_correction_support.py'):
        p=ROOT/relative;bound[str(p)]=sha(p)
    bound[str(Path(__file__))]=sha(Path(__file__))
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(authorized_derivatives=21,bases=7,new_mapping_fits=0,
        planned_mapping_applications=21,planned_action_costs=294,tree_fits=0,image_model_calls=0,original_photo_reads=0,input_sha256=bound))
    prepared=[]
    for base in bases:
        annotation=Path(base['annotation_folder']);mask=cv2.imread(str(annotation/'measurement_mask.png'),0)
        with np.load(base['pixels_file'],allow_pickle=False) as pack:
            clean=pack['input_rgb8'];reference=pack['reference_rgb8'];assert np.array_equal(clean,reference)
            alpha=pack['alpha'];protected=pack['protected'];scoring=pack['scoring_mask'];native_measurement=pack['measurement_mask'];correction=pack['correction_mask']
            assert np.array_equal(scoring,alpha>0) and not alpha[protected].any()
            bridge=base['input_bridge'];left,top,right,bottom=bridge['native_bounds']
            clean_norm=cv2.resize(clean[top:bottom,left:right,::-1].copy(),(256,256),interpolation=cv2.INTER_LINEAR)
            np.testing.assert_array_equal(clean_norm,cv2.imread(str(annotation/'photo_used.png')))
            base_panels=[clean_norm]
            labels=['existing accepted reference']
            for recipe in plan['generation']['recipes']:
                case=base['publisher_group']+'_0__matched_'+recipe['id'];folder=OUT/case;folder.mkdir()
                ones=np.ones(clean.shape[:2],float)
                if recipe['id'].startswith('exposure_'):
                    image,forward=core_exposure(clean,ones,'medium',recipe['direction'])
                else:image,forward=render_rgb(clean,ones,'medium','cool','none')
                assert forward['clipped_channel_samples']==0
                normalized=cv2.resize(image[top:bottom,left:right,::-1].copy(),(256,256),interpolation=cv2.INTER_LINEAR)
                stats=compute_masked_lab_statistics(normalized,mask,1000)
                record=dict(case_id=case,publisher_group=base['publisher_group'],role='controlled_distortion',experimental_role=recipe['id'],
                    base_case_id=base['base_case_id'],source_kind='controlled_derivative_of_existing_accepted_reference',
                    generated_fixture=False,synthetic_controlled_derivative=True,mask_origin='propagated_same_geometry',
                    user_reviewed_derivative=False,automatic_detection=False,provided_mst_label=None,
                    input_bridge=bridge,base_pixels_sha256=base['pixels_sha256'],base_annotation_manifest_sha256=base['annotation_manifest_sha256'],
                    recipe=recipe,forward_report=forward,statistics=stats,clean_identity_constraint=False,
                    training_admitted=False,calibration_admitted=False,qualified_for_runtime=False,empirical_mst_transfer_validated=False,
                    mapping_artifact_sha256=sha(mapping_path),measurement_core_sha256=mapping['measurement_core_sha256'],
                    feature_control_contract_sha256=mapping['feature_control_contract_sha256'],status='unavailable')
                assert cv2.imwrite(str(folder/'input_rgb8.png'),image[:,:,::-1])
                assert cv2.imwrite(str(folder/'normalized_input.png'),normalized)
                (folder/'measurement_mask.png').write_bytes((annotation/'measurement_mask.png').read_bytes())
                np.savez_compressed(folder/'paired_pixels.npz',input_rgb8=image,reference_rgb8=clean,alpha=alpha,protected=protected,
                    scoring_mask=scoring,measurement_mask=native_measurement,correction_mask=correction)
                record.update(pixels_file=str(folder/'paired_pixels.npz'),pixels_sha256=sha(folder/'paired_pixels.npz'),
                    normalized_input_sha256=sha(folder/'normalized_input.png'),measurement_mask_sha256=sha(folder/'measurement_mask.png'),
                    full_input_sha256=sha(folder/'input_rgb8.png'),features=None,action_costs=None)
                if stats['valid']:
                    features={'input_'+k:stats[k] for k in ('mean_l_star','mean_a_star','mean_b_star','ita_degrees')}
                    greens=green_distribution_features(normalized,mask);assert greens['valid'];features.update(greens['features'])
                    features.update(scene_features(image))
                    prediction=predict_score(mapping,features['input_ita_degrees'],measurement_core_sha256=mapping['measurement_core_sha256'],
                        feature_control_contract_sha256=mapping['feature_control_contract_sha256'])
                    features['input_mst_score']=prediction['score']
                    costs=blended_action_costs(image,clean,alpha,scoring,actions);best=int(np.argmin(costs))
                    record.update(status='available',features=features,input_vector_float32=np.array([features[n] for n in names],np.float32).tolist(),
                        mst_prediction=prediction,action_costs=costs,identity_cost=costs[0],oracle_cost=costs[best],
                        oracle_action_index=best,oracle_direct_controls=actions[best],target_aware_supervision_not_prediction=True)
                else:record['reason']=stats['reason']
                write(folder/'record_PRIVATE.json',record);prepared.append(record)
                write(OUT/'new_rows_PRIVATE.json',prepared)
                base_panels.append(normalized);labels.append(recipe['id'])
            # Actual normalized inputs, no new mask/user approval inferred from this board.
            header=np.full((32,1024,3),255,np.uint8)
            for i,label in enumerate(labels):cv2.putText(header,label,(i*256+4,21),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
            assert cv2.imwrite(str(OUT/('base_'+base['publisher_group']+'.png')),np.vstack([header,np.hstack(base_panels)]))
    assert len(prepared)==21
    combined=old+prepared;assert len(combined)==len({r['case_id'] for r in combined})==35
    write(OUT/'combined_rows_PRIVATE.json',combined)
    write(OUT/'role_ledger_PRIVATE.json',read(DESIGN/'role_ledger_PRIVATE.json'))
    write(OUT/'folds_PRIVATE.json',read(DESIGN/'folds_PRIVATE.json'))
    available=[r for r in prepared if r['status']=='available']
    summary=dict(new_derivatives=21,reference_bases=7,available_new_rows=len(available),unavailable_new_rows=21-len(available),
        available_combined_rows=14+len(available),attempted_roles=40,blocked904_roles=5,
        new_MST_mapping_applications=len(available),MST_fits=0,new_action_cost_values=14*len(available),
        MST_score_range=[min(r['features']['input_mst_score'] for r in available),max(r['features']['input_mst_score'] for r in available)] if available else None,
        outside_mapping_support=sum(r['mst_prediction']['outside_fitting_support'] for r in available),
        old14rows_unchanged=combined[:14]==old,tree_fits=0,correction_predictions=0,image_model_calls=0,original_photo_reads=0,
        holdout_reads=0,runtime_adopted=False,training_admitted=False,calibration_admitted=False)
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'summary_PRIVATE.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
