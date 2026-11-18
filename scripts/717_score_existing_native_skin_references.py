"""Score cached old/native masks on existing six human reviews; no forwards."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
OUT=ROOT/'outputs/native_existing_skin_reference_audit_v1'
NEW=ROOT/'outputs/native_mst_measurement_readiness_v1'
OLD=ROOT/'outputs/aligned_correction_preparation_v1'
REF=ROOT/'outputs/stellenbosch_reference_points_v1'
PATCH=ROOT/'outputs/stellenbosch_skin_patch_import_v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Preserve existing audit')
    bound={}
    def read(p):bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    manifest=read(REF/'manifest.json');bindings=read(REF/'prediction_bindings_PRIVATE.json')
    pointpath=ROOT/'outputs/stellenbosch_reference_points_import_v1/actual_export_PRIVATE.json'
    points=read(pointpath);patches=read(PATCH/'actual_export_PRIVATE.json')
    pm={r['review_id']:r for r in points['rows']};pp={r['review_id']:r for r in patches['rows']}
    rows=read(NEW/'results_PRIVATE.json');verified=read(NEW/'verification_PRIVATE.json')
    assert verified['passed'] and verified['results_sha256']==sha(NEW/'results_PRIVATE.json')
    newer={r['source_sha256']:r for r in rows['records']}
    older={r['source_sha256']:r for r in read(OLD/'results_PRIVATE.json')['records'] if r['cohort']=='development' and r['recipe']=='clean'}
    previous=read(PATCH/'results_PRIVATE.json');patchmanifest=read(PATCH/'sha256.json')
    assert sha(PATCH/'actual_export_PRIVATE.json')==previous['actual_export_sha256']==patchmanifest['actual_export_PRIVATE.json']
    assert sha(pointpath)=='99d477c3e080e6e7bb6845b1e594f4bf2aed7df97d1743b1670f2d31cce76c55'
    for p in [Path(__file__),ROOT/'docs/native-mask-existing-reference-protocol-2026-11-09.md']:
        bound[str(p)]=sha(p)
    aggregates={name:Counter() for name in ['old','native']};records=[];allpoints=[];boards=[]
    for item in manifest['rows']:
        rid=item['review_id'];b=bindings[rid];h=b['source_sha256']
        assert h in newer and h in older
        assert sha(b['source_path'])==h;bound[b['source_path']]=h
        original=cv2.imread(b['source_path']);l,t,rr,bb=b['native_bounds']
        refpath=REF/item['image_path'];assert sha(refpath)==item['image_sha256'];bound[str(refpath)]=sha(refpath)
        ref=cv2.imread(str(refpath));np.testing.assert_array_equal(ref,original[t:bb,l:rr])
        assert pp[rid]['image_sha256']==pm[rid]['image_sha256']==item['image_sha256']
        patch=np.zeros(ref.shape[:2],np.uint8)
        for poly in pp[rid]['polygons']:cv2.fillPoly(patch,[np.array(poly,np.int32)],255)
        saved=PATCH/(rid+'_patch.png');assert sha(saved)==patchmanifest[saved.name]
        bound[str(saved)]=sha(saved);np.testing.assert_array_equal(patch,cv2.imread(str(saved),0))
        record=dict(review_id=rid,source_case=newer[h]['source_case'],source_sha256=h,
            native_bounds=b['native_bounds'],patch_pixels=int((patch>0).sum()),models={})
        panels=[ref.copy(),ref.copy()];panels[1][patch>0]=np.rint(.6*ref[patch>0]+.4*np.array([0,255,0])).astype(np.uint8)
        for name,row in [('old',older[h]),('native',newer[h])]:
            path=Path(row['measurement_native_path']) if name=='old' and row.get('measurement_native_path') else (NEW/row['source_case']/'measurement_native.png' if name=='native' else None)
            exists=path is not None and path.is_file();usable=row['status']=='available' and exists
            full=None if not exists else cv2.imread(str(path),0)
            assert full is None or full.shape==original.shape[:2]
            if exists:bound[str(path)]=sha(path)
            totals=aggregates[name];totals['attempts']+=1;totals['usable_cases']+=int(usable);totals['diagnostic_masks']+=int(exists)
            per=Counter();selections=[]
            for p in pm[rid]['points']:
                x,y=p['x'],p['y'];label='skin' if p['label']=='skin' else 'unwanted'
                assert 0<=x<ref.shape[1] and 0<=y<ref.shape[0]
                selected=None if full is None else bool(full[t+y,l+x]>0)
                if full is not None:assert selected==bool(full[t:bb,l:rr][y,x]>0)
                totals[label+'_all']+=1;per[label+'_all']+=1
                for mode,available in [('diagnostic',exists),('usable',usable)]:
                    if available:
                        totals[mode+'_'+label+'_denominator']+=1;totals[mode+'_'+label+'_selected']+=int(selected)
                        per[mode+'_'+label+'_denominator']+=1;per[mode+'_'+label+'_selected']+=int(selected)
                    else:totals[mode+'_'+label+'_unavailable']+=1
                selections.append(selected)
                allpoints.append(dict(review_id=rid,model=name,x=x,y=y,full_x=l+x,full_y=t+y,
                    label=p['label'],selected=selected,usable_measurement=usable,inside_user_patch=bool(patch[y,x])))
            selectedpatch=None
            if exists:
                local=full[t:bb,l:rr]>0;selectedpatch=int((local&(patch>0)).sum())
                fullpatch=np.zeros(original.shape[:2],bool);fullpatch[t:bb,l:rr]=patch>0
                assert selectedpatch==int(((full>0)&fullpatch).sum())
                for mode,available in [('diagnostic',exists),('usable',usable)]:
                    if available:
                        totals[mode+'_patch_denominator']+=record['patch_pixels'];totals[mode+'_patch_selected']+=selectedpatch
                panel=ref.copy();panel[local]=np.rint(.6*ref[local]+.4*np.array([255,180,0])).astype(np.uint8)
            else:panel=np.full_like(ref,35)
            panels.append(panel);record['models'][name]=dict(status=row['status'],usable=usable,diagnostic_mask=exists,
                selected_patch_pixels=selectedpatch,point_counts=dict(per),point_selections=selections)
        records.append(record)
        board=np.hstack([cv2.resize(x,(220,220),interpolation=cv2.INTER_NEAREST) for x in panels])
        title=np.full((30,880,3),255,np.uint8);cv2.putText(title,rid+' original | actual patches | old | native',(5,21),cv2.FONT_HERSHEY_SIMPLEX,.48,(0,0,0),1)
        boards.append((rid,np.vstack([title,board])))
    assert len(records)==6 and len(allpoints)==476
    assert sum(r['patch_pixels'] for r in records)==3156
    assert all(sha(p)==h for p,h in bound.items())
    paired=[r for r in records if all(v['usable'] for v in r['models'].values())]
    paired_totals={name:dict(cases=len(paired),patch_denominator=sum(r['patch_pixels'] for r in paired),
        patch_selected=sum(r['models'][name]['selected_patch_pixels'] for r in paired),
        skin_denominator=sum(r['models'][name]['point_counts'].get('usable_skin_denominator',0) for r in paired),
        skin_selected=sum(r['models'][name]['point_counts'].get('usable_skin_selected',0) for r in paired),
        unwanted_denominator=sum(r['models'][name]['point_counts'].get('usable_unwanted_denominator',0) for r in paired),
        unwanted_selected=sum(r['models'][name]['point_counts'].get('usable_unwanted_selected',0) for r in paired)) for name in aggregates}
    result=dict(passed=True,records=records,points=allpoints,aggregate={k:dict(v) for k,v in aggregates.items()},
        paired_usable=paired_totals,source_joins=6,original_points=238,original_polygons=36,patch_union_pixels=3156,
        independent_coordinate_and_patch_replay=True,input_sha256=bound,new_forwards=0,new_fits=0,holdout_reads=0,
        calibration_admitted=False,limitation='Six exposed deliberately selected references; patch includes neck. Not dense accuracy, calibration qualification or population coverage.')
    OUT.mkdir()
    for rid,board in boards:assert cv2.imwrite(str(OUT/(rid+'_board.png')),board)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS:6exact source/crop joins,238unchanged points,36polygons/3156pixels; independent coordinate/patch scoring.')
    print('Aggregates',json.dumps(result['aggregate']));print('Paired usable',json.dumps(paired_totals))
if __name__=='__main__':main()
