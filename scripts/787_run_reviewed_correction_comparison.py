"""One fixed photographic-supervision correction comparison, seven fits only."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
DESIGN=ROOT/'outputs/reviewed_correction_comparison_design_v1'
OUT=ROOT/'outputs/reviewed_correction_comparison_v1'
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
    receipt=read(DESIGN/'review_PRIVATE.json');assert receipt['passed']
    bound=dict(receipt['input_sha256']);assert all(sha(p)==h for p,h in bound.items())
    plan=read(DESIGN/'plan_PRIVATE.json');rows=read(DESIGN/'rows_PRIVATE.json');folds=read(DESIGN/'folds_PRIVATE.json')
    indexed={r['case_id']:r for r in rows};names=plan['candidate']['feature_names'];actions=plan['candidate']['actions']
    assert len(rows)==14 and sum(f['fit_required'] for f in folds)==7
    for r in rows:
        assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
    for p in (Path(__file__),ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/portable_tree.py'):
        bound[str(p)]=sha(p)
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(planned_fits=7,planned_predictions=14,attempted_roles=16,
        input_sha256=bound,all_data_fit=False,new_MST_fits=0,new_image_model_calls=0,original_photo_reads=0,holdout_reads=0))
    fitted=[];predictions=[]
    for fold in folds:
        if not fold['fit_required']:continue
        training=[indexed[c] for c in fold['fitting_cases']]
        assert len(training)==12 and all(r['publisher_group']!=fold['held_publisher_group'] for r in training)
        model=fit_action_tree([r['input_vector_float32'] for r in training],[r['action_costs'] for r in training],
            np.array([r['role']=='target' for r in training],bool),actions,names,max_depth=4)
        entry=dict(definition=fold,model=model);fitted.append(entry)
        write(OUT/'models_PRIVATE.json',fitted)
        tree=PortableTree(model['tree'])
        for case in fold['evaluation_cases']:
            r=indexed[case];controls=tree.predict_one(r['input_vector_float32']);action=actions.index(controls)
            folder=OUT/case;folder.mkdir()
            with np.load(r['pixels_file'],allow_pickle=False) as pack:
                image=pack['input_rgb8'];target=pack['reference_rgb8'];alpha=pack['alpha'];scoring=pack['scoring_mask'];protected=pack['protected']
                assert np.array_equal(scoring,alpha>0)
                x=image.astype(float)/255.;a=alpha[:,:,None]
                corrected=np.clip(x**controls[0]*[controls[1],1.,controls[2]],0,1)
                output=np.rint(255*(x*(1-a)+corrected*a)).astype(np.uint8)
                base_rgb=float(np.abs(image[scoring].astype(float)-target[scoring]).mean())
                out_rgb=float(np.abs(output[scoring].astype(float)-target[scoring]).mean())
                assert np.isclose(base_rgb,r['identity_cost'],rtol=1e-11,atol=1e-11)
                assert np.isclose(out_rgb,r['action_costs'][action],rtol=1e-11,atol=1e-11)
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
            predictions.append(dict(case_id=case,publisher_group=r['publisher_group'],role=r['role'],held_publisher_group=fold['held_publisher_group'],
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
    checks=dict(full_coverage=len(predictions)==len({p['case_id'] for p in predictions})==14,
        source_RGB_improves=mean(source,'output_RGB_MAE')<mean(source,'input_RGB_MAE')-tol,
        source_DE_improves=mean(source,'output_DE')<mean(source,'input_DE')-tol,
        identity_outputs_unchanged=all(p['changed_pixels']==0 for p in identity),
        protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in predictions))
    summary=dict(tree_fits=len(fitted),held_role_predictions=len(predictions),attempted_roles=16,unavailable_roles=['904_0__source','904_0__target'],
        source_input_RGB=mean(source,'input_RGB_MAE'),source_output_RGB=mean(source,'output_RGB_MAE'),
        source_input_DE=mean(source,'input_DE'),source_output_DE=mean(source,'output_DE'),
        source_RGB_benefits=sum(p['RGB_improvement']>tol for p in source),source_RGB_harms=sum(p['RGB_improvement']<-tol for p in source),
        source_DE_benefits=sum(p['DE_improvement']>tol for p in source),source_DE_harms=sum(p['DE_improvement']<-tol for p in source),
        edited_identity_outputs=sum(p['changed_pixels']>0 for p in identity),
        split_features=dict(Counter(names[n['feature']] for f in fitted for n in f['model']['tree']['nodes'] if n['kind']=='split')),
        checks=checks,development_checks_passed=all(checks.values()),runtime_adopted=False,training_admitted=False,calibration_admitted=False,
        all_data_fit=False,new_MST_fits=0,new_image_model_calls=0,original_photo_reads=0,holdout_reads=0)
    write(OUT/'summary_PRIVATE.json',summary)
    for start in range(0,14,2):
        sheet=np.vstack([cv2.imread(str(OUT/p['case_id']/'board.png')) for p in predictions[start:start+2]])
        assert cv2.imwrite(str(OUT/f'sheet_{start//2:02d}.png'),sheet)
    blank=np.full((200,768,3),255,np.uint8)
    cv2.putText(blank,'904 source + target UNAVAILABLE: intended-person pairing failed',(8,60),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),1)
    cv2.putText(blank,'No fit/output; retained in 16-role attempt ledger.',(8,100),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),1)
    assert cv2.imwrite(str(OUT/'blocked_904.png'),blank)
    assert all(sha(p)==h for p,h in bound.items())
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
