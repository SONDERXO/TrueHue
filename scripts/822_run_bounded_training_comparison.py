"""One frozen11-fold bounded search comparison; reuse first candidate unchanged."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.bounded_regression_search import search_tree
import gc
from skimage.color import rgb2lab,deltaE_ciede2000
from src.model_training.portable_tree import export_tree,PortableTree
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';OUT=ROOT/'outputs/bounded_training_comparison_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial comparison')
    frozen_path=ROOT/'outputs/bounded_training_comparison_design_v1/plan_PRIVATE.json';frozen=read(frozen_path)
    assert all(sha(p)==h for p,h in frozen['input_sha256'].items())
    receipt=read(P/'review_PRIVATE.json');assert receipt['passed'];bound=receipt['input_sha256'];assert all(sha(p)==h for p,h in bound.items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};folds=read(P/'folds_PRIVATE.json');plan=read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json')
    for r in rows.values():assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
    bound.update(frozen['input_sha256']);bound[str(frozen_path)]=sha(frozen_path)
    for rel in ['src/model_training/bounded_regression_search.py','src/model_training/portable_tree.py','outputs/bounded_regression_search_generated_check_v1/verification_PRIVATE.json','outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json','scripts/823_verify_bounded_training_comparison.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    qa=read(ROOT/'outputs/bounded_regression_search_generated_check_v1/verification_PRIVATE.json');assert qa['passed'] and all(sha(p)==h for p,h in qa['input_sha256'].items())
    bound[str(Path(__file__))]=sha(__file__);OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(planned_new_searches=10,reused_searches=1,planned_predictions=44,input_sha256=bound,all_data_fit=False,holdout_reads=0))
    models=[];preds=[]
    baselines={m['definition']['held_publisher_group']:m for m in read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json')}
    # Finish every search before rendering any held-photo prediction.
    for f in folds:
        group=f['held_publisher_group'];train=[rows[c] for c in f['fitting_cases']]
        assert len(train)==40 and all(r['publisher_group']!=group for r in train)
        assert baselines[group]['definition']==f
        folder=OUT/group;folder.mkdir()
        if group==frozen['reused_fold']:
            source=Path(frozen['reused_candidate_path']);assert sha(source)==frozen['reused_candidate_sha256']
            payload=read(source);stats=read(ROOT/'outputs/training_search_feasibility_v1/search_PRIVATE.json')
            (folder/'candidate_PRIVATE.json').write_bytes(source.read_bytes());reused=True
        else:
            print('Starting fixed training search',group,flush=True)
            result=search_tree([r['input_vector_float32'] for r in train],[r['nominal_controls'] for r in train],baselines[group]['tree'],max_depth=4,max_states=5000,max_seconds=60.)
            payload=result['tree'];stats=result['search'];write(folder/'candidate_PRIVATE.json',payload);reused=False
            del result;gc.collect()
        write(folder/'search_PRIVATE.json',stats)
        models.append(dict(definition=f,tree=payload,search=stats,reused_feasibility=reused,candidate_sha256=sha(folder/'candidate_PRIVATE.json')))
        write(OUT/'models_PRIVATE.json',models)
        print(group,'reused' if reused else 'searched',stats['status'],'SSE',stats['initial_SSE'],'->',stats['selected_SSE'],flush=True)
    assert len(models)==11 and sum(m['reused_feasibility'] for m in models)==1
    for model in models:
        f=model['definition'];tree=PortableTree(model['tree']);boards=[]
        for case in f['evaluation_cases']:
            r=rows[case];control=tree.predict_one(r['input_vector_float32'])
            with np.load(r['pixels_file'],allow_pickle=False) as pack:
                image=pack['input_rgb8'];ref=pack['reference_rgb8'];a=pack['alpha'];mask=pack['scoring_mask'];protect=pack['protected'];u=image/255.
                output=np.rint(255*(u*(1-a[:,:,None])+np.clip(u**control[0]*[control[1],1.,control[2]],0,1)*a[:,:,None])).astype(np.uint8)
                metrics={}
                for prefix,data in [('input',image),('output',output)]:
                    metrics[prefix+'_RGB']=float(np.abs(data[mask].astype(float)-ref[mask]).mean());metrics[prefix+'_DE']=float(deltaE_ciede2000(rgb2lab(data[mask]/255.),rgb2lab(ref[mask]/255.)).mean())
                dest=OUT/case;dest.mkdir();assert cv2.imwrite(str(dest/'output.png'),output[:,:,::-1]);head=np.full((32,768,3),255,np.uint8)
                cv2.putText(head,case+' | input / held output / original',(3,21),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                board=np.vstack([head,np.hstack([image,output,ref])[:,:,::-1]]);assert cv2.imwrite(str(dest/'board.png'),board);boards.append(board)
                preds.append(dict(case_id=case,held_publisher_group=f['held_publisher_group'],experimental_role=r['experimental_role'],controls=control,leaf_id=tree.leaf_id(r['input_vector_float32']),changed_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),protected_unchanged=bool(np.array_equal(output[protect],image[protect])),zero_alpha_unchanged=bool(np.array_equal(output[a==0],image[a==0])),output_sha256=sha(dest/'output.png'),**metrics))
            write(OUT/'predictions_PRIVATE.json',preds)
        assert cv2.imwrite(str(OUT/(f['held_publisher_group']+'_board.png')),np.vstack(boards))
    by_role={}
    for role in ['identity','exposure_under','exposure_over','colour_cool']:
        own=[p for p in preds if p['experimental_role']==role]
        by_role[role]={k:float(np.mean([p[k] for p in own])) for k in ['input_RGB','output_RGB','input_DE','output_DE']}
        by_role[role].update(cases=len(own),edited=sum(p['changed_pixels']>0 for p in own),RGB_harms=sum(p['output_RGB']>p['input_RGB']+1e-12 for p in own),DE_harms=sum(p['output_DE']>p['input_DE']+1e-12 for p in own))
    checks=dict(coverage=len(preds)==44,all_recipe_RGB_means_improve=all(by_role[k]['output_RGB']<by_role[k]['input_RGB'] for k in by_role if k!='identity'),all_recipe_DE_means_improve=all(by_role[k]['output_DE']<by_role[k]['input_DE'] for k in by_role if k!='identity'),identity_unchanged=by_role['identity']['edited']==0,protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in preds))
    parent=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json')
    checks['each_recipe_RGB_nonworse_saved_parent']=all(by_role[k]['output_RGB']<=parent['by_role'][k]['output_RGB']+1e-12 for k in by_role if k!='identity')
    checks['each_recipe_DE_nonworse_saved_parent']=all(by_role[k]['output_DE']<=parent['by_role'][k]['output_DE']+1e-12 for k in by_role if k!='identity')
    summary=dict(new_searches=10,reused_feasibility_searches=1,search_statuses={state:sum(m['search']['status']==state for m in models) for state in set(m['search']['status'] for m in models)},strictly_improved_training_folds=sum(m['search']['strict_improvement'] for m in models),parent_by_role=parent['by_role'],fits=11,predictions=44,attempted_roles=48,by_role=by_role,checks=checks,development_checks_passed=all(checks.values()),parameter_MAE=np.mean([np.abs(np.array(p['controls'])-rows[p['case_id']]['nominal_controls']) for p in preds],axis=0).tolist(),runtime_adopted=False,all_data_fit=False,original_photo_reads=0,image_model_calls=0,MST_fits=0,holdout_reads=0)
    assert all(sha(p)==h for p,h in bound.items());write(OUT/'summary_PRIVATE.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
