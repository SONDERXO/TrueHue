"""Verify cached comparison without inference or fitting."""
import runpy,json
from pathlib import Path
g=runpy.run_path(str(Path(__file__).with_name('581_compare_current_parser_appearance.py')))
globals().update({k:v for k,v in g.items() if not k.startswith('__') and k!='main'})

def main():
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    prep=read(P/'results_PRIVATE.json')['records'];inf={r['image_id']:r for r in read(P/'inference.json')['records']}
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    actual=read(ROOT/'outputs/stellenbosch_reference_points_import_v1/actual_export_PRIVATE.json')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm'];checks=0;patch_totals=Counter();point_totals=Counter()
    for r in d['records']:
        if r['review_id']=='review_06':assert r['status']=='failed' and not r['points'];continue
        source=next(x for x in prep if x['case_id']==r['case_id']);folder=Path(source['scene_path']).parent;target=OUT/r['review_id']
        image=cv2.imread(str(folder/'input.png'));points=np.load(folder/'landmarks.npy',allow_pickle=False)
        assert np.array_equal(parser_input(image),cv2.imread(str(target/'parser_input.png')))
        cat=cv2.imread(str(target/'categories.png'),0)
        parent=build_semantic_face_coverage(image,points,cat).mask;parent[nostril_guard((256,256),points)]=0
        assert np.array_equal(parent,cv2.imread(str(target/'parent_mask.png'),0))
        assert compute_masked_lab_statistics(image,parent,1000)==r['parent_statistics']
        prediction=inf[r['case_id']];lp=P/prediction['logits_path'];assert sha(lp)==prediction['logits_sha256']
        result=evaluate_parent(SimpleNamespace(report=dict(status='success'),image=image,mask=parent),points,template,lambda _:np.load(lp,allow_pickle=False))
        assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')))
        assert result.report==r['measurement_report']
        assert np.array_equal(result.mask,cv2.imread(str(target/'measurement_mask.png'),0))
        native=native_projection(result.mask,source['input_bridge'])[0]>0
        assert np.array_equal(native,cv2.imread(str(target/'native_grid.png'),0)>0)
        old=cv2.imread(source['measurement_native_path'],0)>0;b=bindings[r['review_id']];x0,y0,x1,y1=b['native_bounds']
        patch=cv2.imread(str(ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(r['review_id']+'_patch.png')),0)>0
        for name,mask,status in [('baseline',old,source['status']=='available'),('candidate',native,result.report['status']=='success')]:
            count=int((mask[y0:y1,x0:x1]&patch).sum());assert count==r[name+'_diagnostic_patch']
            patch_totals[name+'_diagnostic']+=count;patch_totals[name+'_usable']+=count if status else 0
        user=next(q for q in actual['rows'] if q['review_id']==r['review_id'])
        for point,saved in zip(user['points'],r['points'],strict=True):
            x=x0+point['x'];y=y0+point['y'];assert saved['x']==x and saved['y']==y
            assert saved['label']==point['label'] and saved['baseline_diagnostic']==bool(old[y,x]) and saved['candidate_diagnostic']==bool(native[y,x])
            if point['label']=='uncertain':continue
            kind='skin' if point['label']=='skin' else 'unwanted'
            point_totals[kind+'_old']+=int(old[y,x]);point_totals[kind+'_new']+=int(native[y,x])
        checks+=1
    assert patch_totals=={'baseline_diagnostic':687,'candidate_diagnostic':848,'baseline_usable':653,'candidate_usable':843}
    assert point_totals=={'skin_old':39,'skin_new':46,'unwanted_old':3,'unwanted_new':4}
    receipt=dict(status='PASS',cases_replayed=checks,input_hashes=len(bound),patch_totals=dict(patch_totals),point_totals=dict(point_totals),new_forwards=0,new_fits=0,
        result_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        output_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='verification_PRIVATE.json'})
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print('PASS five preprocessing/parent/service/native replays, original-pixel statistics, patches, source-coordinate sparse points;',len(bound),'input hashes.')

if __name__=='__main__':main()
