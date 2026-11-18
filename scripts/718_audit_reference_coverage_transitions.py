"""Saved human-reference coverage, transitions and stage trace; no model calls."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import hashlib,json
import cv2
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/native_existing_skin_reference_audit_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    dest=OUT/'coverage_and_transitions_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve completed audit')
    bound={}
    def read(p):bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    refs=read(OUT/'results_PRIVATE.json')
    new=read(ROOT/'outputs/native_mst_measurement_readiness_v1/results_PRIVATE.json')
    old=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')
    provenance=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    current={r['source_case']:r for r in new['records']}
    previous={r['source_case']:r for r in old['records'] if r['cohort']=='development' and r['recipe']=='clean'}
    joined={}
    for p in refs['points']:
        key=(p['review_id'],p['x'],p['y'],p['label']);entry=joined.setdefault(key,{})
        assert p['model'] not in entry;entry[p['model']]=p
    assert len(joined)==238 and all(set(v)=={'old','native'} for v in joined.values())
    gained=[];lost=[]
    for key,v in joined.items():
        if not all(v[m]['usable_measurement'] for m in v):continue
        if v['native']['selected'] and not v['old']['selected']:gained.append(v['native'])
        if v['old']['selected'] and not v['native']['selected']:lost.append(v['native'])
    traces=[]
    for p in gained:
        if p['label']=='skin':continue
        rid=p['review_id'];cid=provenance[rid]['case_id'];trace=dict(point=p,stages={})
        for name,r,folder in [('old',previous[cid],ROOT/'outputs/aligned_correction_preparation_v1/cases'/(cid+'__clean')),
                              ('native',current[cid],ROOT/'outputs/native_mst_measurement_readiness_v1'/cid)]:
            b=r['input_bridge'];l,t,rr,bb=b['native_bounds'];side=rr-l
            x=(p['full_x']-l)*256//side;y=(p['full_y']-t)*256//side
            assert 0<=x<256 and 0<=y<256
            stage=dict(normalized_mask_sample=[x,y],native_bounds=b['native_bounds'])
            for filename,field in [('parent_mask.png','parent_selected'),('measurement_mask.png','final_selected'),('categories.png','parser_class')]:
                path=folder/filename;assert path.is_file();bound[str(path)]=sha(path)
                value=int(cv2.imread(str(path),0)[y,x]);stage[field]=value if field=='parser_class' else value>0
            trace['stages'][name]=stage
        traces.append(trace)
    referenced={r['source_case'] for r in refs['records']}
    groups_with_refs={current[c]['subject_id'] for c in referenced}
    def interval(value):
        v=Decimal(value)
        return '[1,3)' if v<3 else '[3,5)' if v<5 else '[5,7)' if v<7 else '[7,9)' if v<9 else '[9,10]'
    strata={}
    for key in ['[1,3)','[3,5)','[5,7)','[7,9)','[9,10]']:
        rows=[r for r in new['records'] if interval(r['source_mst_exact_decimal'])==key]
        annotated=[r for r in rows if r['source_case'] in referenced]
        strata[key]=dict(attempts=len(rows),source_score_labelled=len(rows),
            reference_photos=len(annotated),reference_subjects=len({r['subject_id'] for r in annotated}),
            technically_available_with_reference=sum(r['status']=='available' for r in annotated))
    result=dict(passed=True,source_score_labelled_photos=30,source_score_labelled_subjects=10,
        human_reference_photos=len(referenced),human_reference_subjects=len(groups_with_refs),
        photos_without_human_references=30-len(referenced),subjects_without_human_references=10-len(groups_with_refs),
        technical_passes_with_reference=sum(current[c]['status']=='available' for c in referenced),
        score_interval_reference_coverage=strata,gained_points=gained,lost_points=lost,
        new_unwanted_points=[p for p in gained if p['label']!='skin'],new_unwanted_stage_traces=traces,
        skin_gains=sum(p['label']=='skin' for p in gained),skin_losses=sum(p['label']=='skin' for p in lost),
        unwanted_gains=sum(p['label']!='skin' for p in gained),unwanted_losses=sum(p['label']!='skin' for p in lost),
        independent_point_key_join=True,new_forwards=0,new_fits=0,holdout_reads=0,
        input_sha256=bound,verifier_sha256=sha(Path(__file__)),
        disposition='No native measurement improvement/admission established; existing references reused, no annotation task or new model test.')
    assert all(sha(p)==h for p,h in bound.items())
    dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS:238paired point keys; gain/loss skin',result['skin_gains'],result['skin_losses'],'unwanted',result['unwanted_gains'],result['unwanted_losses'])
    print('Coverage',json.dumps(strata));print('New unwanted trace',json.dumps(traces))
if __name__=='__main__':main()
