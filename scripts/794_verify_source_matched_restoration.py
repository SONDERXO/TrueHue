"""Independent transforms/features/map/cost/native-support replay; no fitting."""
from pathlib import Path
import hashlib,json,math,bisect
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/source_matched_restoration_preparation_v1'
DESIGN=ROOT/'outputs/source_matched_restoration_design_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    plan=read(DESIGN/'plan_PRIVATE.json');bases=read(DESIGN/'bases_PRIVATE.json');rows=read(OUT/'new_rows_PRIVATE.json')
    original=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')
    combined=read(OUT/'combined_rows_PRIVATE.json');assert combined[:14]==original and combined[14:]==rows
    assert len(rows)==len({r['case_id'] for r in rows})==21 and len(combined)==35
    mapping=read(ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json');actions=plan['training']['tree']['actions'];names=plan['training']['tree']['feature_names']
    def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11),(a,b)
    def quantile(values,p):
        ordered=np.sort(values.ravel());position=(len(ordered)-1)*p;i=math.floor(position);part=position-i
        return float(ordered[i])*(1-part)+float(ordered[min(i+1,len(ordered)-1)])*part
    checked=0;new_endpoints={}
    for base in bases:
        assert sha(base['pixels_file'])==base['pixels_sha256']
        annotation=Path(base['annotation_folder']);mask=cv2.imread(str(annotation/'measurement_mask.png'),0)
        with np.load(base['pixels_file'],allow_pickle=False) as package:
            clean=package['input_rgb8'];alpha=package['alpha'];protected=package['protected'];scoring=package['scoring_mask']
            assert np.array_equal(clean,package['reference_rgb8'])
            for recipe in plan['generation']['recipes']:
                row=next(r for r in rows if r['publisher_group']==base['publisher_group'] and r['experimental_role']==recipe['id'])
                folder=OUT/row['case_id'];assert sha(row['pixels_file'])==row['pixels_sha256']
                with np.load(row['pixels_file'],allow_pickle=False) as pack:
                    image=pack['input_rgb8'];reference=pack['reference_rgb8']
                    np.testing.assert_array_equal(reference,clean)
                    for key in ('alpha','protected','scoring_mask','measurement_mask','correction_mask'):
                        np.testing.assert_array_equal(pack[key],package[key])
                    assert np.array_equal(scoring,alpha>0) and not alpha[protected].any()
                    expected=np.empty_like(clean)
                    for channel,gain in enumerate((recipe['red_gain'],1.,recipe['blue_gain'])):
                        expected[:,:,channel]=np.rint(np.power(clean[:,:,channel].astype(float)/255.,recipe['gamma'])*gain*255).astype(np.uint8)
                    np.testing.assert_array_equal(image,expected)
                    np.testing.assert_array_equal(image,cv2.imread(str(folder/'input_rgb8.png'))[:,:,::-1])
                    assert sha(folder/'input_rgb8.png')==row['full_input_sha256']
                    assert row['forward_report']['clipped_channel_samples']==0
                    count=int(np.count_nonzero(((image==0)|(image==255))&(clean>0)&(clean<255)))
                    assert count==row['forward_report']['new_endpoint_channel_samples']
                    new_endpoints[row['case_id']]=count
                    if recipe['id']=='exposure_under':assert np.all(image<=clean)
                    elif recipe['id']=='exposure_over':assert np.all(image>=clean)
                    else:
                        assert np.all(image[:,:,0]<=clean[:,:,0]);np.testing.assert_array_equal(image[:,:,1:],clean[:,:,1:])
                    l,t,r,b=base['input_bridge']['native_bounds']
                    normalized=cv2.resize(image[t:b,l:r,::-1].copy(),(256,256),interpolation=cv2.INTER_LINEAR)
                    np.testing.assert_array_equal(normalized,cv2.imread(str(folder/'normalized_input.png')))
                    assert sha(folder/'normalized_input.png')==row['normalized_input_sha256']
                    assert sha(folder/'measurement_mask.png')==row['measurement_mask_sha256']==sha(annotation/'measurement_mask.png')
                    encoded=cv2.cvtColor(normalized,cv2.COLOR_BGR2LAB).astype(np.float32)
                    encoded[:,:,0]*=100/255;encoded[:,:,1:]-=128
                    selected=encoded[mask>0];means=[round(float(selected[:,i].mean()),4) for i in range(3)]
                    ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
                    features=dict(zip(('input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees'),[*means,ita]))
                    green=normalized[:,:,1][mask>0];q=[quantile(green,p) for p in (.1,.5,.9)]
                    features.update(dict(zip(('input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast'),[*q,math.log((q[2]+1)/(q[0]+1))])))
                    channelmeans=[float(image[:,:,i].astype(np.uint64).sum())/(image.shape[0]*image.shape[1]) for i in range(3)]
                    light=cv2.cvtColor(image[:,:,::-1].copy(),cv2.COLOR_BGR2LAB)[:,:,0].astype(np.float32)*(100/255)
                    q=[quantile(light,p) for p in (.1,.5,.9)]
                    features.update(dict(zip(('scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90','scene_any_zero_fraction','scene_any_full_fraction'),
                        [math.log((channelmeans[0]+1)/(channelmeans[1]+1)),math.log((channelmeans[2]+1)/(channelmeans[1]+1)),*q,
                         float(np.count_nonzero(np.min(image,axis=2)==0))/light.size,float(np.count_nonzero(np.max(image,axis=2)==255))/light.size])))
                    xs,ys=mapping['ita_knots'],mapping['mst_score_knots']
                    if ita<=xs[0]:score=ys[0]
                    elif ita>=xs[-1]:score=ys[-1]
                    else:
                        k=bisect.bisect_right(xs,ita)-1;score=ys[k]+(ys[k+1]-ys[k])*(ita-xs[k])/(xs[k+1]-xs[k])
                    features['input_mst_score']=score
                    for f,v in features.items():close(v,row['features'][f])
                    assert row['input_vector_float32']==np.array([features[f] for f in names],np.float32).tolist()
                    assert row['mst_prediction']['outside_fitting_support']==(ita<xs[0] or ita>xs[-1])
                    costs=[]
                    for gamma,red,blue in actions:
                        rendered=np.empty_like(image)
                        for channel,gain in enumerate((red,1.,blue)):
                            unit=image[:,:,channel].astype(float)/255.
                            corrected=np.clip(np.power(unit,gamma)*gain,0,1)
                            rendered[:,:,channel]=np.rint(255*(unit*(1-alpha)+corrected*alpha)).astype(np.uint8)
                        assert np.array_equal(rendered[protected],image[protected]) and np.array_equal(rendered[alpha==0],image[alpha==0])
                        costs.append(float(np.abs(rendered[scoring].astype(float)-clean[scoring]).mean()));checked+=1
                    for actual,recorded in zip(costs,row['action_costs']):close(actual,recorded)
                    assert row['oracle_action_index']==min(range(14),key=lambda i:(costs[i],i))
                    assert row['synthetic_controlled_derivative'] and not row['generated_fixture'] and not row['user_reviewed_derivative']
                    assert not row['automatic_detection'] and row['mask_origin']=='propagated_same_geometry'
                    assert not row['training_admitted'] and not row['calibration_admitted'] and row['status']=='available'
    assert checked==294 and read(OUT/'folds_PRIVATE.json')==read(DESIGN/'folds_PRIVATE.json')
    summary=read(OUT/'summary_PRIVATE.json');assert summary['available_new_rows']==21 and summary['tree_fits']==0 and summary['MST_fits']==0
    assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    report=dict(passed=True,exact_generated_image_replays=21,actual_input_geometry_mask_checks=21,feature_values_replayed=336,
        independent_MST_arithmetic_replays=21,full_native_action_render_costs=294,protected_zeroalpha_invariants=294,
        original14rows_unchanged=True,folds_unchanged=True,new_endpoint_counts=new_endpoints,
        new_fits=0,new_model_calls=0,original_photo_reads=0,holdout_reads=0,
        summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:21exact images/21geometry-mask/336features/21mapping/294native costs+protection;old14rows andfolds unchanged.')


if __name__=='__main__':main()
