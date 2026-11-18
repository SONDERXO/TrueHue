"""Independent bounded-search fitting/routing and44 working-grid image replays;0 refits."""
from pathlib import Path
import json,hashlib,math,struct
from fractions import Fraction
from collections import defaultdict
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/bounded_training_comparison_v1'
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]

def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};models=read(OUT/'models_PRIVATE.json');predictions=read(OUT/'predictions_PRIVATE.json')
    folds={f['held_publisher_group']:f for f in read(P/'folds_PRIVATE.json')};by_group={f['definition']['held_publisher_group']:f for f in models}
    assert len(models)==11 and len(predictions)==len({p['case_id'] for p in predictions})==44
    baselines={m['definition']['held_publisher_group']:m for m in read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json')}
    frozen=read(ROOT/'outputs/bounded_training_comparison_design_v1/plan_PRIVATE.json')
    def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)
    nodes_checked=0;fitting_route_checks=0;fit_checks=[]
    def training_cost(payload,train):
        nonlocal nodes_checked,fitting_route_checks
        nodes=payload['nodes'];members=defaultdict(list);pending=[(0,0)];seen=set()
        while pending:
            i,d=pending.pop();assert i not in seen and d<=4;seen.add(i);n=nodes[i];nodes_checked+=1
            if n['kind']=='split':
                assert 0<=n['feature']<16;pending.extend([(n['left'],d+1),(n['right'],d+1)])
            else:assert len(n['values'])==3 and all(v>0 and math.isfinite(v) for v in n['values'])
        assert len(seen)==len(nodes)
        paths={}
        for r in train:
            x=[f32(v) for v in r['input_vector_float32']];i=0
            while nodes[i]['kind']=='split':
                paths.setdefault(i,[]).append(r);n=nodes[i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
            members[i].append(r);fitting_route_checks+=1
        total=Fraction();exported=Fraction()
        for i,n in enumerate(nodes):
            if n['kind']=='leaf':
                own=members[i];assert own
                for j in range(3):
                    y=[Fraction.from_float(float(r['nominal_controls'][j])) for r in own];mean=sum(y,Fraction())/len(y)
                    close(n['values'][j],float(mean));total+=sum(((v-mean)**2 for v in y),Fraction());exported+=sum(((v-Fraction.from_float(float(n['values'][j])))**2 for v in y),Fraction())
            else:
                values=[f32(r['input_vector_float32'][n['feature']]) for r in paths[i]]
                low=max(v for v in values if v<=n['threshold']);high=min(v for v in values if v>n['threshold'])
                assert high>low+1e-7;close(n['threshold'],(low+high)/2)
        return float(total),float(exported)
    for fit in models:
        f=fit['definition'];group=f['held_publisher_group'];assert f==folds[group] and f==baselines[group]['definition']
        train=[rows[c] for c in f['fitting_cases']];assert len(train)==40 and all(r['publisher_group']!=group for r in train)
        assert fit['tree']['feature_names']==baselines[group]['tree']['feature_names']
        before,_=training_cost(baselines[group]['tree'],train);after,serialized=training_cost(fit['tree'],train);stats=fit['search']
        close(before,stats['initial_SSE']);close(after,stats['selected_SSE']);close(serialized,stats['exported_float_SSE']);assert after<=before+1e-12
        assert stats['expanded_states']<=5000 and stats['partial_states_cached']==0 and stats['state_limit']==5000 and stats['time_limit_seconds']==60
        assert stats['global_lower_bound']<=stats['best_found_SSE']<=stats['initial_SSE']
        if stats['status']=='budget_limited':assert not stats['optimality_certified'] and stats['global_lower_bound']==0
        candidate_path=OUT/group/'candidate_PRIVATE.json';assert sha(candidate_path)==fit['candidate_sha256'] and read(candidate_path)==fit['tree']
        assert read(OUT/group/'search_PRIVATE.json')==stats
        if group==frozen['reused_fold']:
            assert fit['reused_feasibility'] and sha(candidate_path)==frozen['reused_candidate_sha256']
            assert stats==read(ROOT/'outputs/training_search_feasibility_v1/search_PRIVATE.json')
        else:assert not fit['reused_feasibility']
        fit_checks.append(dict(group=group,initial_SSE=before,selected_SSE=after,serialized_SSE=serialized,status=stats['status'],incumbent_preserved=not stats['strict_improvement']))
    for p in predictions:
        r=rows[p['case_id']];f=by_group[p['held_publisher_group']];assert p['case_id'] in f['definition']['evaluation_cases']
        nodes=f['tree']['nodes'];index=0;x=[f32(v) for v in r['input_vector_float32']]
        while nodes[index]['kind']=='split':
            n=nodes[index];index=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        control=nodes[index]['values'];assert control==p['controls'] and index==p['leaf_id']
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha=pack['alpha'];mask=pack['scoring_mask'];protect=pack['protected'];output=np.empty_like(image)
            for c,gain in enumerate([control[1],1.,control[2]]):
                u=image[:,:,c]/255.;corrected=np.minimum(1.,np.maximum(0.,np.power(u,control[0])*gain));output[:,:,c]=np.rint(255*(u*(1-alpha)+corrected*alpha)).astype(np.uint8)
            np.testing.assert_array_equal(output,cv2.imread(str(OUT/p['case_id']/'output.png'))[:,:,::-1]);assert sha(OUT/p['case_id']/'output.png')==p['output_sha256']
            for prefix,data in [('input',image),('output',output)]:
                close(p[prefix+'_RGB'],float(np.abs(data[mask].astype(float)-ref[mask]).sum())/(3*np.count_nonzero(mask)))
                close(p[prefix+'_DE'],float(deltaE_ciede2000(rgb2lab(data[mask]/255.),rgb2lab(ref[mask]/255.)).mean()))
            assert p['changed_pixels']==int(np.count_nonzero(np.any(output!=image,axis=2)))
            assert p['protected_unchanged']==bool(np.array_equal(output[protect],image[protect]))
            assert p['zero_alpha_unchanged']==bool(np.array_equal(output[alpha==0],image[alpha==0]))
    summary=read(OUT/'summary_PRIVATE.json')
    for role,record in summary['by_role'].items():
        own=[p for p in predictions if p['experimental_role']==role];assert len(own)==record['cases']==11
        for k in ['input_RGB','output_RGB','input_DE','output_DE']:close(record[k],sum(p[k] for p in own)/11)
        assert record['edited']==sum(p['changed_pixels']>0 for p in own)
        for m in ['RGB','DE']:assert record[m+'_harms']==sum(p['output_'+m]>p['input_'+m]+1e-12 for p in own)
    by=summary['by_role'];checks=dict(coverage=len(predictions)==44,all_recipe_RGB_means_improve=all(by[k]['output_RGB']<by[k]['input_RGB'] for k in by if k!='identity'),all_recipe_DE_means_improve=all(by[k]['output_DE']<by[k]['input_DE'] for k in by if k!='identity'),identity_unchanged=by['identity']['edited']==0,protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in predictions))
    parent=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json');assert summary['parent_by_role']==parent['by_role']
    checks['each_recipe_RGB_nonworse_saved_parent']=all(by[k]['output_RGB']<=parent['by_role'][k]['output_RGB']+1e-12 for k in by if k!='identity')
    checks['each_recipe_DE_nonworse_saved_parent']=all(by[k]['output_DE']<=parent['by_role'][k]['output_DE']+1e-12 for k in by if k!='identity')
    assert summary['new_searches']==10 and summary['reused_feasibility_searches']==1 and sum(m['reused_feasibility'] for m in models)==1
    assert summary['checks']==checks and summary['development_checks_passed']==all(checks.values())
    np.testing.assert_allclose(summary['parameter_MAE'],np.mean([np.abs(np.array(p['controls'])-rows[p['case_id']]['nominal_controls']) for p in predictions],axis=0),rtol=1e-12,atol=1e-12)
    dest.write_text(json.dumps(dict(passed=True,trees=11,nodes_checked=nodes_checked,fitting_route_checks=fitting_route_checks,per_fold_fitting_verification=fit_checks,first_candidate_exactly_reused=True,held_routes_and_native_render_metric_checks=44,new_fits=0,original_photo_reads=0,holdout_reads=0,summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print(dest.read_text())

if __name__=='__main__':main()
