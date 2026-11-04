"""Package an auditable paired report from frozen evidence, without inference."""
import csv
import hashlib
import html
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def main():
    out=ROOT/'outputs/faceocc_comparison_evidence_v1'
    if out.exists():raise FileExistsError(out)
    parent=ROOT/'outputs/additional_mst_eligibility_v1'
    candidate=ROOT/'outputs/faceocc_diagnostic_v1'
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    old=read(parent/'summary.json');new=read(candidate/'summary.json');plan=read(candidate/'plan.json')
    verification=read(candidate/'verification.json')
    assert verification['mask_feature_replays']==17
    assert all(digest(Path(p))==h for p,h in plan['input_sha256'].items())
    assert [r['image_id'] for r in old['records']]==[r['image_id'] for r in new['records']]
    rows=[];cards=[];marks=[];hashes={str(p):digest(p) for p in
        [parent/'summary.json',candidate/'summary.json',candidate/'verification.json',candidate/'plan.json',Path(__file__)]}
    out.mkdir();(out/'cases').mkdir()
    for index,(before,after) in enumerate(zip(old['records'],new['records']),1):
        row=dict(case_index=index,image_id=before['image_id'],subject_id=before['subject_id'],
            official_mst=before['official_mst'],lighting=before['lighting'],recorded_mask=before['recorded_mask'],
            previous_status=before['status'],candidate_status=after['status'],
            failure_reason=before.get('reason','') if before['status']!='success' else after.get('reason',''),
            previous_pixels=None,candidate_pixels=None,removed_pixels=None,retained_fraction=None,
            previous_ita=None,candidate_ita=None,ita_change=None,adopted=False)
        if before['status']=='success':
            folder=parent/Path(before['board_path']).parent
            image=cv2.imread(str(folder/'input.png'));baseline=cv2.imread(str(folder/'mask.png'),0)
            cp=candidate/('case_'+str(index))/'candidate_mask.png'
            assert digest(cp)==after['candidate_sha256']
            mask=cv2.imread(str(cp),0);assert not mask[baseline==0].any()
            for p in [folder/'input.png',folder/'mask.png',cp]:hashes[str(p)]=digest(p)
            before_stats=compute_masked_lab_statistics(image,baseline,1000)
            after_stats=compute_masked_lab_statistics(image,mask,1000)
            assert before_stats==before['statistics'] and after_stats==after['statistics']
            assert int(np.count_nonzero(baseline))==after['parent_pixels']
            row.update(previous_pixels=after['parent_pixels'],candidate_pixels=after['candidate_pixels'],
                removed_pixels=after['removed_pixels'],retained_fraction=after['retained_fraction'],
                previous_ita=before_stats.get('ita_degrees'),candidate_ita=after_stats.get('ita_degrees'))
            if row['candidate_ita'] is not None:row['ita_change']=row['candidate_ita']-row['previous_ita']
            panels=[]
            for selected in [baseline>0,mask>0]:
                shown=image.copy();shown[selected]=np.rint(.5*shown[selected]+.5*np.array([0,255,0])).astype(np.uint8)
                panels.append(shown)
            board=np.hstack((image,*panels))
            path=out/'cases'/('case_'+str(index)+'.png');assert cv2.imwrite(str(path),board)
            cards.append('<section><h2>Case '+str(index)+' — '+html.escape(row['image_id'])+'</h2><p>'+str(row['previous_pixels'])+' → '+str(row['candidate_pixels'])+' selected pixels; '+str(round(100*row['retained_fraction'],2))+'% parent selection retained.</p><img src="cases/'+path.name+'"><p>ITA '+str(row['previous_ita'])+' → '+str(row['candidate_ita'])+' degrees. A changed measurement is not evidence of greater colour accuracy.</p></section>')
        else:
            cards.append('<section><h2>Case '+str(index)+' — '+html.escape(row['image_id'])+'</h2><p>Original failure retained: '+html.escape(row['failure_reason'])+'. No new FaceOcc attempt or replacement.</p></section>')
        for category,points in after.get('sparse_mark_results',{}).items():
            for p in points:marks.append(dict(case_index=index,image_id=row['image_id'],category=category,**p))
        rows.append(row)
    success=[r for r in rows if r['previous_status']=='success']
    non_skin=[p for p in marks if p['category']=='non_skin'];skin=[p for p in marks if p['category']=='skin']
    subject_rows=[]
    for subject in sorted({r['subject_id'] for r in rows}):
        group=[r for r in rows if r['subject_id']==subject];available=[r for r in group if r['retained_fraction'] is not None]
        subject_rows.append(dict(subject_id=subject,attempts=len(group),
            previous_available=len(available),candidate_available=sum(r['candidate_status']=='success' for r in group),
            original_failures=sum(r['previous_status']!='success' for r in group),
            median_parent_retention=statistics.median(r['retained_fraction'] for r in available)))
    summary=dict(comparison='preferred_parser_anatomy_nostril_measurement_vs_same_plus_FaceOcc_veto',
        model_replacement=False,additional_component=True,attempts=len(rows),
        previous_available=old['successes'],candidate_available=new['candidate_successes'],
        retained_original_failures=8,paired_outputs=len(success),
        previous_known_non_skin_selected=sum(p['parent_selected'] for p in non_skin),
        candidate_known_non_skin_selected=sum(p['candidate_selected'] for p in non_skin),
        marked_skin_total=len(skin),previous_marked_skin_selected=sum(p['parent_selected'] for p in skin),
        candidate_marked_skin_selected=sum(p['candidate_selected'] for p in skin),
        median_parent_retention=statistics.median(r['retained_fraction'] for r in success),
        previous_selected_pixels=sum(r['previous_pixels'] for r in success),
        candidate_selected_pixels=sum(r['candidate_pixels'] for r in success),
        removed_pixels=sum(r['removed_pixels'] for r in success),subjects=subject_rows,
        previous_measurement_contract=old['measurement_contract_sha256'],
        candidate_contract=new['candidate_contract_sha256'],
        no_new_inference=True,no_fits=True,adopted=False,
        limitations=['25 exposed attempts/four subjects; no independent subject validation.',
            'Four non-skin and two skin marks are sparse assistant diagnostics, not full mask accuracy.',
            'Residual beard contamination; glasses improvement not tested.',
            'No paired MST accuracy, true-colour accuracy, correction quality or Android cost measured.',
            'Added runtime/model complexity; alignment adaptation not upstream equivalence.'])
    assert len(rows)==25 and len(success)==17 and len(non_skin)==4 and len(skin)==2
    for filename,data in [('paired_results.csv',rows),('diagnostic_marks.csv',marks),('subject_results.csv',subject_rows)]:
        with (out/filename).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    (out/'comparison.json').write_text(json.dumps(summary,indent=2))
    evidence=dict(input_sha256=hashes,output_sha256={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()})
    metrics='<table><tr><th>Same evidence</th><th>Previous measurement</th><th>Previous + FaceOcc</th></tr><tr><td>Technical availability, all25attempts</td><td>17/25</td><td>17/25</td></tr><tr><td>Known non-skin marks still selected</td><td>4/4</td><td>1/4</td></tr><tr><td>Known skin marks retained</td><td>2/2</td><td>2/2</td></tr></table>'
    intro='''<h1>Previous measurement versus FaceOcc-assisted measurement</h1><p><strong>Promising diagnostic improvement, not an adopted replacement.</strong> FaceOcc is an additional removal-only component; the existing parser and anatomical/nostril exclusions remain. This is not a correction-model comparison or a comparison with the original paper’s HSV/YCrCb implementation.</p>
<p>Each image: original; previous measurement overlay; combined FaceOcc-assisted measurement overlay. All25original attempts are listed, including eight failures. No new inference, source selection or model fitting was performed to prepare this report.</p>'''
    conclusion='''<h2>What supports investigating a change</h2><p>The fixed veto removed the premarked neck/clothing and worn-covering contamination while retaining two marked skin points. Most prior facial support remains. These observations justify further evaluation of an occlusion-veto component.</p><h2>What does not follow</h2><p>One marked beard pixel remains. Sparse points do not establish overall accuracy; removed pixels are not automatically non-skin. There is no glasses-specific result, paired MST accuracy, true-colour or correction improvement, independent subject validation, or Android timing/memory evidence. Added model/alignment cost remains. No adoption or calibration is implied.</p><p><a href="paired_results.csv">All25paired rows (CSV)</a> · <a href="diagnostic_marks.csv">Exact diagnostic marks</a> · <a href="subject_results.csv">Subject denominators</a> · <a href="comparison.json">Machine-readable comparison</a></p>'''
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrueHue paired masking evidence</title><style>body{font:18px/1.5 system-ui;max-width:1200px;margin:auto;padding:24px}section{border-top:1px solid #aaa;margin-top:24px}img{width:100%}table{border-collapse:collapse}td,th{padding:12px;border:1px solid #aaa}</style>'+intro+metrics+conclusion+''.join(cards)+'</html>'
    (out/'comparison.html').write_text(page,encoding='utf-8')
    assert all(digest(Path(p))==h for p,h in hashes.items())
    evidence['output_sha256']['comparison.html']=digest(out/'comparison.html')
    (out/'evidence_hashes.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
