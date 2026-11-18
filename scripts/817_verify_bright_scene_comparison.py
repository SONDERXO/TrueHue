"""Independent training SSE/means/routing and44 native working-grid replays."""
from pathlib import Path
import json,hashlib,math,struct
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/bright_scene_cue_comparison_v1'
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
    additions=read(ROOT/'outputs/bright_scene_cue_readiness_v1/records_PRIVATE.json')
    assert len(additions)==44
    for a in additions:
        r=rows[a['case_id']];assert r['input_vector_float32']==a['input_vector_float32_18'][:16];r['input_vector_float32']=a['input_vector_float32_18']
    expected_names=read(ROOT/'outputs/bright_scene_cue_comparison_design_v1/plan_PRIVATE.json')['feature_names']
    assert all(f['tree']['feature_names']==expected_names for f in models)
    nodes_checked=0;split_options=0
    def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)
    for fit in models:
        f=fit['definition'];assert f==folds[f['held_publisher_group']]
        train=[rows[c] for c in f['fitting_cases']];assert len(train)==40 and all(r['publisher_group']!=f['held_publisher_group'] for r in train)
        x=[[f32(v) for v in r['input_vector_float32']] for r in train];targets=np.array([r['nominal_controls'] for r in train]);nodes=fit['tree']['nodes']
        def loss(ids):
            v=targets[ids];return float(((v-v.mean(axis=0))**2).sum())
        def walk(index,ids,depth):
            nonlocal nodes_checked,split_options
            nodes_checked+=1;node=nodes[index];parent=loss(ids)
            best=parent
            if depth<4:
                for feature in range(18):
                    ordered=sorted(ids,key=lambda i:x[i][feature])
                    for k in range(len(ordered)-1):
                        if x[ordered[k+1]][feature]<=x[ordered[k]][feature]+1e-7:continue
                        split_options+=1
                        best=min(best,loss(ordered[:k+1])+loss(ordered[k+1:]))
            if node['kind']=='leaf':
                np.testing.assert_allclose(node['values'],targets[ids].mean(axis=0),rtol=1e-12,atol=1e-12)
                assert parent-best<1e-10
            else:
                assert depth<4
                left=[i for i in ids if x[i][node['feature']]<=node['threshold']]
                right=[i for i in ids if i not in left];assert left and right
                achieved=loss(left)+loss(right)
                close(achieved,best)
                lo=max(x[i][node['feature']] for i in left);hi=min(x[i][node['feature']] for i in right)
                close(node['threshold'],(lo+hi)/2)
                walk(node['left'],left,depth+1);walk(node['right'],right,depth+1)
        walk(0,list(range(40)),0)
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
    parent=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json')
    assert summary['parent_by_role']==parent['by_role']
    checks['each_recipe_RGB_nonworse_saved_parent']=all(by[k]['output_RGB']<=parent['by_role'][k]['output_RGB']+1e-12 for k in by if k!='identity')
    checks['each_recipe_DE_nonworse_saved_parent']=all(by[k]['output_DE']<=parent['by_role'][k]['output_DE']+1e-12 for k in by if k!='identity')
    assert summary['checks']==checks and summary['development_checks_passed']==all(checks.values())
    np.testing.assert_allclose(summary['parameter_MAE'],np.mean([np.abs(np.array(p['controls'])-rows[p['case_id']]['nominal_controls']) for p in predictions],axis=0),rtol=1e-12,atol=1e-12)
    dest.write_text(json.dumps(dict(passed=True,trees=11,nodes_checked=nodes_checked,split_options_checked=split_options,held_routes_and_native_render_metric_checks=44,new_fits=0,original_photo_reads=0,holdout_reads=0,summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print(dest.read_text())

if __name__=='__main__':main()
