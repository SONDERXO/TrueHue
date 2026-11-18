"""One paper-aligned nominal-control regression baseline; seven fits only."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import export_tree
DESIGN=ROOT/'outputs/source_matched_restoration_design_v1'
PREP=ROOT/'outputs/source_matched_restoration_preparation_v1'
OUT=ROOT/'outputs/nominal_control_regression_comparison_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')


def panel(rgb):
    height,width=rgb.shape[:2];scale=min(256/width,384/height)
    image=cv2.resize(rgb,(round(width*scale),round(height*scale)),interpolation=cv2.INTER_AREA)
    out=np.full((384,256,3),40,np.uint8);y=(384-image.shape[0])//2;x=(256-image.shape[1])//2
    out[y:y+image.shape[0],x:x+image.shape[1]]=image
    return out


def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial comparison; no automatic refit')
    frozen_path=ROOT/'outputs/nominal_control_regression_design_v1/plan_PRIVATE.json'
    frozen=read(frozen_path);assert all(sha(p)==h for p,h in frozen['input_sha256'].items())
    receipt=read(PREP/'review_PRIVATE.json');assert receipt['passed']
    bound=dict(receipt['input_sha256']);bound.update(frozen['input_sha256']);bound[str(frozen_path)]=sha(frozen_path);assert all(sha(p)==h for p,h in bound.items())
    plan=read(DESIGN/'plan_PRIVATE.json');rows=read(PREP/'combined_rows_PRIVATE.json');folds=read(PREP/'folds_PRIVATE.json')
    indexed={r['case_id']:r for r in rows};names=plan['training']['tree']['feature_names'];actions=plan['training']['tree']['actions']
    assert len(rows)==35 and sum(f['fit_required'] for f in folds)==7
    for r in rows:
        assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
    for p in (ROOT/'outputs/reviewed_correction_comparison_v1/summary_PRIVATE.json',Path(__file__),ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/portable_tree.py'):
        bound[str(p)]=sha(p)
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(planned_fits=7,planned_predictions=35,attempted_roles=40,
        input_sha256=bound,all_data_fit=False,new_MST_fits=0,new_image_model_calls=0,original_photo_reads=0,holdout_reads=0))
    fitted=[];predictions=[]
    for fold in folds:
        if not fold['fit_required']:continue
        training=[indexed[c] for c in fold['fitting_cases']]
        assert len(training)==24 and all(r['publisher_group']!=fold['held_publisher_group'] for r in training)
        assert all(r['role']!='source' for r in training)
        def nominal(r):
            if r['role']=='target':return [1.,1.,1.]
            q=r['recipe'];g=q['gamma'];return [1/g,q['red_gain']**(-1/g),q['blue_gain']**(-1/g)]
        targets=[nominal(r) for r in training]
        estimator=DecisionTreeRegressor(max_depth=4,random_state=42,min_samples_leaf=1,criterion='squared_error',splitter='best')
        estimator.fit(np.asarray([r['input_vector_float32'] for r in training],np.float32),targets)
        payload=export_tree(estimator,names,['gamma','red_gain','blue_gain'],dict(objective='unweighted_nominal_direct_control_squared_error',runtime_adopted=False))
        model=dict(tree=payload)
        entry=dict(definition=fold,model=model,fitting_nominal_targets=dict(zip(fold['fitting_cases'],targets)));fitted.append(entry)
        write(OUT/'models_PRIVATE.json',fitted)
        tree=PortableTree(model['tree'])
        for case in fold['evaluation_cases']:
            r=indexed[case];controls=tree.predict_one(r['input_vector_float32']);action=None
            np.testing.assert_allclose(controls,estimator.predict(np.asarray([r['input_vector_float32']],np.float32))[0],rtol=0,atol=0)
            folder=OUT/case;folder.mkdir()
            experimental_role=r.get('experimental_role','original_source' if r['role']=='source' else 'identity')
            with np.load(r['pixels_file'],allow_pickle=False) as pack:
                image=pack['input_rgb8'];target=pack['reference_rgb8'];alpha=pack['alpha'];scoring=pack['scoring_mask'];protected=pack['protected']
                assert np.array_equal(scoring,alpha>0)
                x=image.astype(float)/255.;a=alpha[:,:,None]
                corrected=np.clip(x**controls[0]*[controls[1],1.,controls[2]],0,1)
                output=np.rint(255*(x*(1-a)+corrected*a)).astype(np.uint8)
                base_rgb=float(np.abs(image[scoring].astype(float)-target[scoring]).mean())
                out_rgb=float(np.abs(output[scoring].astype(float)-target[scoring]).mean())
                assert np.isclose(base_rgb,r['identity_cost'],rtol=1e-11,atol=1e-11)
                reference_lab=rgb2lab(target[scoring].astype(float)/255.)
                base_de=float(deltaE_ciede2000(rgb2lab(image[scoring].astype(float)/255.),reference_lab).mean())
                out_de=float(deltaE_ciede2000(rgb2lab(output[scoring].astype(float)/255.),reference_lab).mean())
                protected_ok=bool(np.array_equal(output[protected],image[protected]));zero_ok=bool(np.array_equal(output[alpha==0],image[alpha==0]))
                changed=int(np.count_nonzero(np.any(output!=image,axis=2)))
                assert cv2.imwrite(str(folder/'output.png'),output[:,:,::-1])
                shown=np.hstack([panel(image),panel(output),panel(target)])[:,:,::-1].copy()
                header=np.full((40,768,3),255,np.uint8)
                cv2.putText(header,case+' | input / held-tree output / reference',(5,17),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
                cv2.putText(header,f'RGB {base_rgb:.3f} -> {out_rgb:.3f} | DE {base_de:.3f} -> {out_de:.3f}',(5,34),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                assert cv2.imwrite(str(folder/'board.png'),np.vstack([header,shown]))
            predictions.append(dict(case_id=case,publisher_group=r['publisher_group'],role=r['role'],experimental_role=experimental_role,held_publisher_group=fold['held_publisher_group'],
                controls=controls,action_index=action,leaf_id=tree.leaf_id(r['input_vector_float32']),
                input_RGB_MAE=base_rgb,output_RGB_MAE=out_rgb,input_DE=base_de,output_DE=out_de,
                RGB_improvement=base_rgb-out_rgb,DE_improvement=base_de-out_de,changed_pixels=changed,
                protected_unchanged=protected_ok,zero_alpha_unchanged=zero_ok,
                oracle_action_index=r['oracle_action_index'],oracle_RGB_cost=r['oracle_cost'],
                missed_oracle_benefit=r['oracle_cost']<base_rgb-1e-12 and out_rgb>=base_rgb-1e-12,
                output_sha256=sha(folder/'output.png'),board_sha256=sha(folder/'board.png')))
            write(OUT/'predictions_PRIVATE.json',predictions)
        print('Completed held group',fold['held_publisher_group'],flush=True)
    source=[p for p in predictions if p['role']=='source'];identity=[p for p in predictions if p['role']=='target'];tol=1e-12
    mean=lambda group,k:float(np.mean([p[k] for p in group]))
    by_recipe={}
    for recipe in ('exposure_under','exposure_over','colour_cool'):
        group=[p for p in predictions if p['experimental_role']==recipe]
        assert len(group)==7
        by_recipe[recipe]=dict(attempts=7,input_RGB=mean(group,'input_RGB_MAE'),output_RGB=mean(group,'output_RGB_MAE'),
            input_DE=mean(group,'input_DE'),output_DE=mean(group,'output_DE'),RGB_benefits=sum(p['RGB_improvement']>tol for p in group),
            RGB_harms=sum(p['RGB_improvement']<-tol for p in group),DE_benefits=sum(p['DE_improvement']>tol for p in group),DE_harms=sum(p['DE_improvement']<-tol for p in group))
    previous_path=ROOT/'outputs/reviewed_correction_comparison_v1/summary_PRIVATE.json'
    previous=read(previous_path)
    checks=dict(full_coverage=len(predictions)==len({p['case_id'] for p in predictions})==35,
        all_controlled_recipes_RGB_improve=all(m['output_RGB']<m['input_RGB']-tol for m in by_recipe.values()),
        all_controlled_recipes_DE_improve=all(m['output_DE']<m['input_DE']-tol for m in by_recipe.values()),
        original_source_RGB_nonworse=mean(source,'output_RGB_MAE')<=previous['source_output_RGB']+tol,
        original_source_DE_nonworse=mean(source,'output_DE')<=previous['source_output_DE']+tol,
        identity_outputs_unchanged=all(p['changed_pixels']==0 for p in identity),
        protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in predictions))
    summary=dict(tree_fits=len(fitted),held_role_predictions=len(predictions),attempted_roles=40,
        unavailable_roles=[r['case_id'] for r in read(PREP/'ready_role_ledger_PRIVATE.json') if r['publisher_group']=='904'],
        by_controlled_recipe=by_recipe,source_input_RGB=mean(source,'input_RGB_MAE'),source_output_RGB=mean(source,'output_RGB_MAE'),
        source_input_DE=mean(source,'input_DE'),source_output_DE=mean(source,'output_DE'),
        previous_source_RGB=previous['source_output_RGB'],previous_source_DE=previous['source_output_DE'],
        source_RGB_benefits=sum(p['RGB_improvement']>tol for p in source),source_RGB_harms=sum(p['RGB_improvement']<-tol for p in source),
        source_DE_benefits=sum(p['DE_improvement']>tol for p in source),source_DE_harms=sum(p['DE_improvement']<-tol for p in source),
        edited_identity_outputs=sum(p['changed_pixels']>0 for p in identity),
        split_features=dict(Counter(names[n['feature']] for f in fitted for n in f['model']['tree']['nodes'] if n['kind']=='split')),
        checks=checks,development_checks_passed=all(checks.values()),runtime_adopted=False,training_admitted=False,calibration_admitted=False,
        all_data_fit=False,new_MST_fits=0,new_image_model_calls=0,original_photo_reads=0,holdout_reads=0)
    summary['fitting_objective']='unweighted_nominal_direct_control_squared_error'
    known=[p for p in predictions if p['role']!='source']
    summary['parameter_MAE_known_28']=np.mean([np.abs(np.asarray(p['controls'])-nominal(indexed[p['case_id']])) for p in known],axis=0).tolist()
    summary['parameter_MAE_by_role']={role:np.mean([np.abs(np.asarray(p['controls'])-nominal(indexed[p['case_id']])) for p in known if p['experimental_role']==role],axis=0).tolist() for role in ('identity','exposure_under','exposure_over','colour_cool')}
    summary['blue_targets_constant_one']=True
    summary['saved_raw_loss_parent_summary']=read(ROOT/'outputs/source_matched_restoration_comparison_v1/summary_PRIVATE.json')
    write(OUT/'summary_PRIVATE.json',summary)
    # Full-frame outputs remain saved; detail boards make the actual correction region inspectable.
    geometries={r['case_id']:r['input_bridge'] for r in read(ROOT/'outputs/reviewed_photographic_pixels_v1/records_PRIVATE.json')['records']}
    for p in predictions:
        r=indexed[p['case_id']]
        bridge=r.get('input_bridge',geometries.get(p['case_id']))
        l,t,rr,b=bridge['native_bounds']
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            own=pack['input_rgb8'];reference=pack['reference_rgb8']
            output=cv2.imread(str(OUT/p['case_id']/'output.png'))[:,:,::-1]
            tiles=[cv2.resize(a[t:b,l:rr],(256,256),interpolation=cv2.INTER_LINEAR) for a in (own,output,reference)]
            header=np.full((32,768,3),255,np.uint8)
            cv2.putText(header,p['case_id']+' | input / held output / reference',(4,21),cv2.FONT_HERSHEY_SIMPLEX,.41,(0,0,0),1)
            assert cv2.imwrite(str(OUT/p['case_id']/'detail_board.png'),np.vstack([header,np.hstack(tiles)[:,:,::-1]]))
    for group in sorted({p['publisher_group'] for p in predictions}):
        own=[p for p in predictions if p['publisher_group']==group]
        sheet=np.vstack([cv2.imread(str(OUT/p['case_id']/'detail_board.png')) for p in own])
        assert len(own)==5 and cv2.imwrite(str(OUT/('group_'+group+'.png')),sheet)
    blank=np.full((160,768,3),255,np.uint8)
    cv2.putText(blank,'904: source, identity and3derivatives UNAVAILABLE',(8,60),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),1)
    cv2.putText(blank,'No matching accepted base; no fit. Retained in40attempts.',(8,100),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),1)
    assert cv2.imwrite(str(OUT/'blocked_904.png'),blank)
    assert all(sha(p)==h for p,h in bound.items())
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
