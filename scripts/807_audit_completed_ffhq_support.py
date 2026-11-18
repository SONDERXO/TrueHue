"""Audit actual immutable dual-mask reviews and native accounting, without fits."""
from pathlib import Path
from collections import defaultdict,Counter
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.manual_refinement import verify_export,digest
from src.demo.manual_brush import refine_masks
from src.demo.labelled_measurement import write
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.seamless_blend import apply_blended
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.model_training.aligned_correction_support import project_alpha

TASKS=ROOT/'outputs/reviewed_ffhq_support_tasks_v1'
OUT=ROOT/'outputs/reviewed_ffhq_support_audit_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial support audit')
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    bound={}
    def bind(p):bound[str(p)]=digest(p);return bound[str(p)]
    initial=read(TASKS/'verification_PRIVATE.json');assert initial['passed']
    for p,h in initial['input_sha256'].items():assert digest(p)==h;bound[p]=h
    queue=read(TASKS/'queue.json');index={};roots={};allfolders={}
    def bundle(folder):
        manifest=verify_export(folder);identity=bind(folder/'manifest.json');allfolders[identity]=folder
        for name in manifest['files']:bind(folder/name)
        return identity
    for row in queue['tasks']:
        folder=TASKS/row['folder'];identity=bundle(folder);assert identity==row['manifest_sha256']
        roots[identity]=(row,folder,read(folder/'report.json'))
    paths=sorted((ROOT/'outputs/reviewed_ffhq_support_annotations_v1').glob('support_*/report.json'))
    for p in paths:bundle(p.parent)
    revisions=[];by_task=defaultdict(list)
    for path in paths:
        folder=path.parent;r=read(path);payload=read(folder/'edits.json')
        assert r['schema_version']=='truehue_photographic_support_annotation_v1' and not r['generated_fixture']
        row,original,task=roots[r['task_manifest_sha256']];parent=allfolders[r['base_manifest_sha256']]
        assert r['case_id']==task['case_id'] and r['frame']==task['frame'] and r['role']==task['role']
        assert r['method_sha256']==task['method_sha256'] and r['input_bridge']==task['input_bridge']
        assert r['reference_preference']==task['reference_preference'] and r['reference_preference']['reference_appearance_decision']=='acceptable'
        assert payload['base_manifest_sha256']==r['base_manifest_sha256']
        assert payload['strokes']==r['strokes'] and payload['review']==r['review']
        assert digest(parent/'report.json')==digest(folder/'before_support_report.json')
        for name in ['photo_used.png','measurement_mask.png','correction_mask.png','protected_mask.png','correction_alpha.npy','report.json']:
            assert digest(original/name)==digest(folder/('automatic_'+name))
        assert digest(parent/'photo_used.png')==digest(folder/'photo_used.png')
        load=lambda f,n:cv2.imread(str(f/n),0)
        old=[load(parent,n) for n in ['correction_mask.png','measurement_mask.png','protected_mask.png']]
        actual=[load(folder,n) for n in ['correction_mask.png','measurement_mask.png','protected_mask.png']]
        replay=refine_masks(*(a.tobytes() for a in old),256,256,payload['strokes'])
        assert all(a.tobytes()==b for a,b in zip(actual,replay))
        c,m,p=actual;image=cv2.imread(str(folder/'photo_used.png'))
        assert not np.any((c>0)&(p>0))
        stats=compute_masked_lab_statistics(image,m,1000);assert stats==r['measurement_statistics']
        assert r['changed_pixels']=={k:int(np.count_nonzero(a!=b)) for k,a,b in zip(['correction','measurement','protection'],actual,old)}
        output,alpha,_=apply_blended(image,c,(1.,1.,1.),face_width=r['face_width'],protected=p>0)
        assert np.array_equal(output,image) and np.array_equal(alpha,np.load(folder/'correction_alpha.npy',allow_pickle=False))
        assert not any(r[k] for k in ['training_admitted','calibration_admitted','mst_recomputed','registration_verified'])
        assert r['identity_render_only'] and r['model_calls']==0
        if r['review']=='reviewed_selection':
            assert payload['measurement_reviewed'] is True and payload['correction_reviewed'] is True
            assert r['measurement_review']==r['correction_review']=='user_reviewed'
        expected='reviewed_support_pending_admission' if r['review']=='reviewed_selection' and stats['valid'] and c.any() else 'unavailable'
        assert r['status']==expected
        entry=dict(case_id=r['case_id'],frame=r['frame'],role=r['role'],task_manifest_sha256=r['task_manifest_sha256'],
            annotation=str(folder),manifest_sha256=digest(folder/'manifest.json'),saved_utc=r['saved_utc'],status=r['status'],
            review=r['review'],statistics=stats,changed_pixels=r['changed_pixels'],stroke_count=len(payload['strokes']))
        revisions.append(entry);by_task[r['task_manifest_sha256']].append(entry)
    latest={k:max(v,key=lambda r:r['saved_utc']) for k,v in by_task.items()}
    jobs=[]
    for path in sorted((ROOT/'outputs/reviewed_ffhq_support_jobs_v1').glob('*/edits.json')):
        bind(path);result=path.with_suffix('.result.json')
        if result.exists():
            bind(result);folder=Path(read(result)['export']);assert read(path)==read(folder/'edits.json')
            assert any(Path(r['annotation'])==folder for r in revisions)
        jobs.append(dict(payload=str(path),saved=result.exists()))
    drafts=[]
    for path in sorted((ROOT/'outputs/reviewed_ffhq_support_drafts_v1').glob('*/draft_*.json')):
        bind(path);d=read(path);assert d['review_approved'] is False
        assert d['base_manifest_sha256'] in allfolders
        if d['status']=='saved':
            assert Path(d['annotation']) in [Path(r['annotation']) for r in revisions]
            assert d['strokes']==read(Path(d['annotation'])/'edits.json')['strokes']
        drafts.append(dict(path=str(path),status=d['status'],base_manifest_sha256=d['base_manifest_sha256']))
    OUT.mkdir();rows=[]
    for key,(taskrow,original,task) in roots.items():
        entry=latest.get(key)
        if entry is None:rows.append(dict(case_id=task['case_id'],status='no_saved_review'));continue
        folder=Path(entry['annotation']);image=cv2.imread(str(folder/'photo_used.png'))
        m=load(folder,'measurement_mask.png');c=load(folder,'correction_mask.png');p=load(folder,'protected_mask.png')
        alpha=np.load(folder/'correction_alpha.npy',allow_pickle=False)
        panels=[image]
        for mask in [m,c,p]:
            shown=image.copy();sel=mask>0;colour=np.array([255,0,255]) if mask is p else np.array([0,255,0])
            shown[sel]=np.rint(.65*shown[sel]+.35*colour).astype(np.uint8);panels.append(shown)
        header=np.full((32,1024,3),255,np.uint8)
        cv2.putText(header,task['case_id']+' | photo / measurement / correction / retained protection',(5,22),cv2.FONT_HERSHEY_SIMPLEX,.48,(0,0,0),1)
        assert cv2.imwrite(str(OUT/(task['case_id']+'_board.png')),np.vstack([header,np.hstack(panels)]))
        rows.append(dict(entry,measurement_working_pixels=int(np.count_nonzero(m)),
            correction_working_pixels=int(np.count_nonzero(c)),alpha_working_pixels=int(np.count_nonzero(alpha)),
            native_adequacy_established=False,input_bridge=task['input_bridge'],face_width=task['face_width'],
            training_admitted=False,calibration_admitted=False))
    pairs=[]
    for p in [Path(__file__),TASKS/'queue.json',TASKS/'method.json',TASKS/'verification_PRIVATE.json']:
        bind(p)
    assert all(digest(p)==h for p,h in bound.items())
    summary=dict(saved_revisions=len(revisions),distinct_saved_roles=len(latest),editable_roles=len(roots),
        missing_roles=[row['case_id'] for key,(row,_,_) in roots.items() if key not in latest],
        valid_latest=sum(r['status']=='reviewed_support_pending_admission' for r in rows),
        failed_jobs=sum(not r['saved'] for r in jobs),jobs=len(jobs),draft_statuses=dict(Counter(r['status'] for r in drafts)),
        blocked_roles=queue['blocked'],complete_pairs=len(pairs),calibration_fits=0,target_fits=0,tree_fits=0,
        image_model_calls=0,original_TIFF_reads=0,holdout_bytes_read=0)
    write(OUT/'audit_PRIVATE.json',dict(passed=True,summary=summary,latest=rows,pairs=pairs,revisions=revisions,jobs=jobs,drafts=drafts,input_sha256=bound))
    write(OUT/'artifact_sha256_PRIVATE.json',{p.name:digest(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps(summary,indent=2));print('Working256 counts:',[(r['case_id'],r.get('measurement_working_pixels'),r.get('alpha_working_pixels')) for r in rows])


if __name__=='__main__':main()
