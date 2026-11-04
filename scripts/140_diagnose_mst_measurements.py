"""Descriptive saved-measurement diagnosis without new fitting or image access."""
import csv
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/mst_measurement_diagnosis_v1'
    if out.exists():raise FileExistsError(out)
    source=ROOT/'outputs/mst_square256_measurement_v1/summary.json'
    original=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    calibration=ROOT/'outputs/mst_square256_calibration_v1/summary.json'
    tracked=[source,original,calibration,Path(__file__),ROOT/'docs/mst-measurement-diagnosis-protocol.md']
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    summary=json.loads(source.read_text());cal=json.loads(calibration.read_text())
    with original.open(encoding='utf-8-sig',newline='') as f:old={r['image_id']:r for r in csv.DictReader(f)}
    records=summary['records'];assert len(records)==len(old)==418
    success=[r for r in records if r['status']=='success']
    assert len(success)==396
    for r in success:
        f=r['features'];ita=round(math.degrees(math.atan((f['input_mean_l_star']-50)/f['input_mean_b_star'])),4)
        assert abs(ita-f['input_ita_degrees'])<1e-10
        assert int(old[r['image_id']]['source_mst_label'])==r['source_mst_label']
    def stats(values):
        values=np.asarray(values,float)
        return dict(zip(['min','q25','median','q75','max'],map(float,np.percentile(values,[0,25,50,75,100]))))
    subjects=[];lighting=[]
    for subject in sorted({r['subject_id'] for r in records}):
        attempted=[r for r in records if r['subject_id']==subject]
        available=[r for r in success if r['subject_id']==subject]
        labels={r['source_mst_label'] for r in attempted};assert len(labels)==1
        row=dict(subject_id=subject,mst=labels.pop(),attempted=len(attempted),available=len(available))
        if available:
            row.update(ita=stats([r['features']['input_ita_degrees'] for r in available]),
                mean_l=stats([r['features']['input_mean_l_star'] for r in available]),
                mean_b=stats([r['features']['input_mean_b_star'] for r in available]),
                nonpositive_b=sum(r['features']['input_mean_b_star']<=0 for r in available),
                crop_selected_fraction=stats([r['skin_pixels']/(r['face_box'][2]*r['face_box'][3]) for r in available]))
        subjects.append(row)
        for label in sorted({old[r['image_id']]['source_lighting'] for r in available}):
            group=[r for r in available if old[r['image_id']]['source_lighting']==label]
            lighting.append(dict(subject_id=subject,mst=row['mst'],lighting=label,images=len(group),
                ita=stats([r['features']['input_ita_degrees'] for r in group])))
    pairs=[]
    for a,b in itertools.combinations(subjects,2):
        if not a['available'] or not b['available']:continue
        light,dark=sorted([a,b],key=lambda r:(r['mst'],r['subject_id']))
        delta=light['ita']['median']-dark['ita']['median']
        kind='same_label' if light['mst']==dark['mst'] else 'ordered' if delta>0 else 'reversed' if delta<0 else 'tied'
        pairs.append(dict(subject_a=light['subject_id'],mst_a=light['mst'],subject_b=dark['subject_id'],mst_b=dark['mst'],ita_median_difference=delta,status=kind))
    support={i:sum(s['mst']==i and s['available']>0 for s in subjects) for i in range(1,11)}
    folds=Counter(f['calibration']['status'] for f in cal['folds'])
    report=dict(status='complete_descriptive_diagnosis',subjects=subjects,subject_lighting=lighting,
        subject_pairs=pairs,pair_order_counts=dict(Counter(p['status'] for p in pairs)),category_subject_support=support,
        singleton_categories=[k for k,v in support.items() if v==1],heldout_fold_failure_counts=dict(folds),
        arithmetic_ita_checks=len(success),nonpositive_b_images=sum(r['features']['input_mean_b_star']<=0 for r in success),
        largest_within_subject_ita_range=max(s['ita']['max']-s['ita']['min'] for s in subjects if s['available']),
        new_images_opened=0,new_model_fits=0,masks_changed=0,lookup_exported=False,input_sha256=hashes,
        limitations='Photo-level variation, lighting/pose, mask errors and subject support are confounded. No causal attribution, skin-material truth, new cutoff or final mapping accuracy established.')
    assert sum(folds.values())==15 and sum(support.values())==15
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    out.mkdir();(out/'summary.json').write_text(json.dumps(report,indent=2))
    with (out/'subject_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['subject_id','mst','attempted','available','ita_min','ita_median','ita_max','nonpositive_b'])
        for s in subjects:writer.writerow([s['subject_id'],s['mst'],s['attempted'],s['available'],s['ita']['min'],s['ita']['median'],s['ita']['max'],s['nonpositive_b']])
    print(json.dumps({k:v for k,v in report.items() if k not in ['subjects','subject_lighting','subject_pairs','input_sha256']},indent=2))


if __name__=='__main__':main()
