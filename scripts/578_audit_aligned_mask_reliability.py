"""Saved-mask diagnosis against existing patches; no inference or fitting."""
from pathlib import Path
from collections import Counter
import hashlib,json
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/aligned_mask_reliability_audit_v3'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed audit')
    bound={}
    def load(p):
        p=Path(p);bound[str(p)]=sha(p);return read(p)
    def mask(p):
        p=Path(p);bound[str(p)]=sha(p)
        a=cv2.imread(str(p),0)
        assert a is not None
        return a>0
    prep=load(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']
    bindings=load(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    previous=load(ROOT/'outputs/stellenbosch_skin_patch_import_v2/results_PRIVATE.json')
    evaluation=load(ROOT/'outputs/aligned_action_tree_comparison_v1/results_PRIVATE.json')['records']
    bound[str(Path(__file__))]=sha(Path(__file__))
    failure=lambda r: ('insufficient_skin_pixels' if 'insufficient skin pixels' in r.get('reason','') else r.get('reason',r['stage']))
    failures=Counter(failure(r) for r in prep if r['status']!='available')
    patches=[];boards=[]
    for key,b in bindings.items():
        patch=mask(ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(key+'_patch.png'))
        full=np.zeros((224,224),bool);x0,y0,x1,y1=b['native_bounds']
        assert patch.shape==(y1-y0,x1-x0)
        full[y0:y1,x0:x1]=patch
        matches=[r for r in prep if r['source_sha256']==b['source_sha256']]
        assert len(matches)==14
        conditions=[]
        for r in matches:
            selected=mask(r['measurement_native_path']) if r.get('measurement_native_path') else np.zeros_like(full)
            assert selected.shape==full.shape
            overlap=int((selected&full).sum())
            parent_path=Path(r['scene_path']).parent/'parent_mask.png'
            parent_overlap=None
            if parent_path.exists():
                pm=mask(parent_path)
                bx0,by0,bx1,by1=r['input_bridge']['native_bounds']
                projected=np.zeros_like(full)
                projected[by0:by1,bx0:bx1]=cv2.resize(pm.astype(np.uint8),(bx1-bx0,by1-by0),interpolation=cv2.INTER_NEAREST)>0
                parent_overlap=int((projected&full).sum())
            applied=np.zeros_like(full)
            if r['status']=='available':
                p=Path(r['alpha_path']);bound[str(p)]=sha(p);applied=np.load(p,allow_pickle=False)>0
            conditions.append(dict(case_id=r['case_id'],recipe=r['recipe'],status=r['status'],stage=r['stage'],
                reason=r.get('reason'),saved_diagnostic_measurement=bool(r.get('measurement_native_path')),
                diagnostic_measurement_patch_pixels=overlap,
                parent_diagnostic_patch_pixels=parent_overlap,
                usable_measurement_patch_pixels=overlap if r['status']=='available' else 0,
                applied_support_patch_pixels=int((applied&full).sum()),
                selected_native_pixels=int(selected.sum())))
        old=next(r for r in previous['records'] if r['review_id']==key)
        assert int(patch.sum())==old['native_patch_pixels']
        origin=next(r for r in matches if r['recipe']=='clean')
        image=cv2.imread(origin['scene_path']);assert image is not None
        bound[origin['scene_path']]=sha(origin['scene_path'])
        selected=mask(origin['measurement_native_path']) if origin.get('measurement_native_path') else np.zeros_like(full)
        panels=[]
        for support in (None,full,selected):
            panel=image.copy()
            if support is not None:panel[support]=(panel[support]*.4+np.array([0,220,0])*.6).astype(np.uint8)
            panels.append(cv2.resize(panel,(336,336),interpolation=cv2.INTER_NEAREST))
        title=np.full((32,1008,3),255,np.uint8)
        cv2.putText(title,key+' '+origin['source_case']+' | original | existing patches | saved measurement',(5,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([title,np.hstack(panels)]))
        patches.append(dict(review_id=key,source_case=matches[0]['source_case'],patch_pixels=int(patch.sum()),
            previous_baseline_patch_selected=old['models']['baseline']['patch_selected'],conditions=conditions))
    clean=[next(c for c in p['conditions'] if c['recipe']=='clean') for p in patches]
    denominator=sum(p['patch_pixels'] for p in patches)
    changed=[]
    index={r['case_id']:r for r in prep}
    for r in evaluation:
        if r['recipe']!='clean' or not r['paths']['aligned_tree']['changed_channels']:continue
        p=index[r['case_id']]
        changed.append(dict(case_id=r['case_id'],region_mae=r['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes'],
            measurement_native_pixels=int(mask(p['measurement_native_path']).sum()),
            correction_native_pixels=p['correction_native_pixels'],
            patch_review_ids=[q['review_id'] for q in patches if q['source_case']==p['source_case']],
            normalized_measurement_pixels=p['measurement_report'].get('candidate_pixels')))
    result=dict(attempts=len(prep),available=sum(r['status']=='available' for r in prep),
        failure_reasons=dict(failures),failure_stages=dict(Counter(r['stage'] for r in prep if r['status']!='available')),
        clean_failures=[dict(case_id=r['case_id'],stage=r['stage'],reason=r.get('reason')) for r in prep if r['recipe']=='clean' and r['status']!='available'],
        patch_totals=dict(photos=len(patches),pixels=denominator,
            clean_usable_measurement_selected=sum(c['usable_measurement_patch_pixels'] for c in clean),
            clean_diagnostic_measurement_selected=sum(c['diagnostic_measurement_patch_pixels'] for c in clean),
            clean_applied_support_selected=sum(c['applied_support_patch_pixels'] for c in clean)),
        patches=patches,changed_clean=changed,new_fits=0,new_inference=0,
        limitations=['Existing selected patches include neck; not full facial ground truth.',
          'Patch overlap measures selected-patch coverage, not precision or contamination.',
          'Diagnostic masks on failed rows are not usable measurements or applied correction.',
          'Repeated conditions/pixels are not independent photos or people.'])
    assert len(patches)==6 and denominator==3156
    assert sum(failures.values())+result['available']==756
    assert len(changed)==4
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir()
    assert cv2.imwrite(str(OUT/'six_patch_boards_PRIVATE.png'),np.vstack(boards))
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('attempts','available','failure_reasons','failure_stages','patch_totals','changed_clean')},indent=2))
    for p in patches:
        c=next(c for c in p['conditions'] if c['recipe']=='clean')
        print(p['review_id'],p['source_case'],p['patch_pixels'],p['previous_baseline_patch_selected'],json.dumps(c))

if __name__=='__main__':main()
