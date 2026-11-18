"""Independent split/action/routing and cached render/metric replay; no refits."""
from pathlib import Path
import hashlib,json,math,struct
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/relative_correction_loss_comparison_v1'
DESIGN=ROOT/'outputs/source_matched_restoration_design_v1'
PREP=ROOT/'outputs/source_matched_restoration_preparation_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(OUT/'execution_plan_PRIVATE.json');assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    rows={r['case_id']:r for r in read(PREP/'combined_rows_PRIVATE.json')};models=read(OUT/'models_PRIVATE.json');predictions=read(OUT/'predictions_PRIVATE.json')
    plan=read(DESIGN/'plan_PRIVATE.json');actions=plan['training']['tree']['actions'];names=plan['training']['tree']['feature_names'];split_options=0;nodes_checked=0
    def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)
    definitions={f['held_publisher_group']:f for f in read(PREP/'folds_PRIVATE.json')}
    model_by_group={f['definition']['held_publisher_group']:f for f in models}
    assert len(models)==7 and '904' not in model_by_group and len(predictions)==len({p['case_id'] for p in predictions})==35
    for fit in models:
        definition=fit['definition'];assert definition==definitions[definition['held_publisher_group']]
        train=[rows[c] for c in definition['fitting_cases']];assert len(train)==24
        assert all(r['publisher_group']!=definition['held_publisher_group'] and r['role']!='source' for r in train)
        x=[[f32(v) for v in r['input_vector_float32']] for r in train]
        scales=[1. if r['clean_identity_constraint'] else r['action_costs'][0] for r in train]
        assert all(scale>0 for scale in scales)
        assert fit['fitting_cost_scales']==dict(zip(definition['fitting_cases'],scales))
        cost=[[c/scale for c in r['action_costs']] for r,scale in zip(train,scales)]
        clean=[r['role']=='target' for r in train];tree=fit['model']['tree'];nodes=tree['nodes'];trace={r['node']:r for r in fit['model']['trace']}
        def optimum(ids):
            totals=[sum(cost[i][a] for i in ids) for a in range(14)]
            feasible=[a for a in range(14) if all(not clean[i] or cost[i][a]==0 for i in ids)]
            action=min(feasible,key=lambda a:(totals[a],a));return action,totals[action]
        for index,node in enumerate(nodes):
            record=trace[index];ids=record['rows'];action,parent=optimum(ids)
            assert record['action']==action;close(record['cost'],parent);nodes_checked+=1
            best=parent;expected=None
            if record['depth']<4 and len(ids)>1:
                for feature in range(16):
                    ordered=sorted(ids,key=lambda i:x[i][feature])
                    for k in range(len(ordered)-1):
                        lv,rv=x[ordered[k]][feature],x[ordered[k+1]][feature]
                        if lv==rv:continue
                        split_options+=1;left=ordered[:k+1];right=ordered[k+1:]
                        value=optimum(left)[1]+optimum(right)[1]
                        if value<best-1e-12*max(1.,abs(parent)):
                            best=value;expected=(feature,(lv+rv)/2,left,right)
            if expected is None:
                assert node['kind']=='leaf' and node['values']==actions[action]
            else:
                feature,threshold,left,right=expected
                assert node['kind']=='split' and node['feature']==feature;close(node['threshold'],threshold)
                assert set(trace[node['left']]['rows'])==set(left) and set(trace[node['right']]['rows'])==set(right)
                close(record['immediate_child_cost'],best)
    for p in predictions:
        row=rows[p['case_id']];fit=model_by_group[p['held_publisher_group']]
        assert row['publisher_group']==p['held_publisher_group'] and p['case_id'] in fit['definition']['evaluation_cases']
        nodes=fit['model']['tree']['nodes'];index=0;x=[f32(v) for v in row['input_vector_float32']]
        while nodes[index]['kind']=='split':
            n=nodes[index];index=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        controls=nodes[index]['values'];assert p['controls']==controls and p['leaf_id']==index and actions[p['action_index']]==controls
        with np.load(row['pixels_file'],allow_pickle=False) as pack:
            image=pack['input_rgb8'];target=pack['reference_rgb8'];alpha=pack['alpha'];mask=pack['scoring_mask'];protected=pack['protected']
            output=np.empty_like(image)
            for c,gain in enumerate((controls[1],1.,controls[2])):
                unit=image[:,:,c].astype(float)/255.
                corrected=np.minimum(1.,np.maximum(0.,np.power(unit,controls[0])*gain))
                output[:,:,c]=np.rint(255*(unit*(1-alpha)+corrected*alpha)).astype(np.uint8)
            stored=cv2.imread(str(OUT/p['case_id']/'output.png'))[:,:,::-1]
            np.testing.assert_array_equal(stored,output)
            assert sha(OUT/p['case_id']/'output.png')==p['output_sha256']
            assert sha(OUT/p['case_id']/'board.png')==p['board_sha256']
            assert np.array_equal(mask,alpha>0)
            base=float(np.abs(image[mask].astype(float)-target[mask]).sum())/(3*np.count_nonzero(mask))
            actual=float(np.abs(output[mask].astype(float)-target[mask]).sum())/(3*np.count_nonzero(mask))
            close(base,p['input_RGB_MAE']);close(actual,p['output_RGB_MAE']);close(actual,row['action_costs'][p['action_index']])
            target_lab=rgb2lab(target[mask]/255.)
            close(float(deltaE_ciede2000(rgb2lab(image[mask]/255.),target_lab).mean()),p['input_DE'])
            close(float(deltaE_ciede2000(rgb2lab(output[mask]/255.),target_lab).mean()),p['output_DE'])
            close(base-actual,p['RGB_improvement']);close(p['input_DE']-p['output_DE'],p['DE_improvement'])
            assert p['changed_pixels']==int(np.count_nonzero(np.any(output!=image,axis=2)))
            assert p['protected_unchanged']==bool(np.array_equal(output[protected],image[protected]))
            assert p['zero_alpha_unchanged']==bool(np.array_equal(output[alpha==0],image[alpha==0]))
    summary=read(OUT/'summary_PRIVATE.json');source=[p for p in predictions if p['role']=='source'];target=[p for p in predictions if p['role']=='target']
    for stored,key in [('source_input_RGB','input_RGB_MAE'),('source_output_RGB','output_RGB_MAE'),('source_input_DE','input_DE'),('source_output_DE','output_DE')]:
        close(summary[stored],sum(p[key] for p in source)/7)
    t=1e-12
    for metric in ('RGB','DE'):
        assert summary['source_'+metric+'_benefits']==sum(p[metric+'_improvement']>t for p in source)
        assert summary['source_'+metric+'_harms']==sum(p[metric+'_improvement']<-t for p in source)
    for recipe,m in summary['by_controlled_recipe'].items():
        own=[p for p in predictions if p['experimental_role']==recipe];assert len(own)==7
        for metric,field in [('RGB','RGB_MAE'),('DE','DE')]:
            close(m['input_'+metric],sum(p['input_'+field] for p in own)/7)
            close(m['output_'+metric],sum(p['output_'+field] for p in own)/7)
            assert m[metric+'_benefits']==sum(p[metric+'_improvement']>t for p in own)
            assert m[metric+'_harms']==sum(p[metric+'_improvement']<-t for p in own)
    previous=read(ROOT/'outputs/reviewed_correction_comparison_v1/summary_PRIVATE.json')
    close(summary['previous_source_RGB'],previous['source_output_RGB']);close(summary['previous_source_DE'],previous['source_output_DE'])
    checks=dict(full_coverage=set(p['case_id'] for p in predictions)==set(rows) and len(predictions)==35,
        all_controlled_recipes_RGB_improve=all(m['output_RGB']<m['input_RGB']-t for m in summary['by_controlled_recipe'].values()),
        all_controlled_recipes_DE_improve=all(m['output_DE']<m['input_DE']-t for m in summary['by_controlled_recipe'].values()),
        original_source_RGB_nonworse=summary['source_output_RGB']<=previous['source_output_RGB']+t,
        original_source_DE_nonworse=summary['source_output_DE']<=previous['source_output_DE']+t,
        identity_outputs_unchanged=all(p['changed_pixels']==0 for p in target),
        protection_preserved=all(p['protected_unchanged'] and p['zero_alpha_unchanged'] for p in predictions))
    assert checks==summary['checks'] and summary['development_checks_passed']==all(checks.values())
    assert summary['tree_fits']==7 and summary['edited_identity_outputs']==sum(p['changed_pixels']>0 for p in target)
    assert not summary['runtime_adopted'] and not summary['all_data_fit']
    assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    result=dict(passed=True,trees=7,nodes_checked=nodes_checked,split_options_checked=split_options,held_routes_checked=35,
        native_render_replays=35,RGB_and_standard_CIEDE2000_replays=35,all_frozen_checks_replayed=True,
        new_fits=0,new_model_calls=0,original_photo_reads=0,holdout_reads=0,
        summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
