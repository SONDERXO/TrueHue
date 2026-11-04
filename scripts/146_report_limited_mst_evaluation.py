"""Report fixed existing mapping evidence under the proposed limited scope."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation.mst_validation import evaluate_mst


def main():
    out=ROOT/'outputs/mst_limited_evaluation_v1'
    if out.exists():raise FileExistsError(out)
    paths=[ROOT/'outputs/mst_square256_measurement_v1/summary.json',
        ROOT/'outputs/mst_square256_calibration_v1/summary.json',
        ROOT/'outputs/mst_evaluation_design_v1/fold_plan.json',
        ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv',
        ROOT/'src/evaluation/mst_validation.py',Path(__file__),ROOT/'docs/adviser-mst-limited-scope-proposal.md']
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    measurements=json.loads(paths[0].read_text());cal=json.loads(paths[1].read_text());plan=json.loads(paths[2].read_text())
    with paths[3].open(encoding='utf-8-sig',newline='') as f:metadata={r['image_id']:r for r in csv.DictReader(f)}
    attempts=[dict(image_id=r['image_id'],subject_id=r['subject_id'],mst=r['source_mst_label'],
        lighting=metadata[r['image_id']]['source_lighting'],measured=r['status']=='success') for r in measurements['records']]
    labels={r['subject_id']:r['source_mst_label'] for r in measurements['records']}
    folds=[dict(held_subject=f['held_subject'],fit_subject_labels={s:labels[s] for s in f['fit_subject_ids']}) for f in plan['folds']]
    predictions=[dict(image_id=r['image_id'],prediction=r['prediction'],baseline=r['baseline']) for r in cal['predictions']]
    report=evaluate_mst(attempts,predictions,folds)
    assert report['overall']['attempts']==418 and report['overall']['measured']==396
    assert report['overall']['processing_failures']==22 and report['overall']['available_predictions']==0
    assert report['overall']['candidate'] is None and report['overall']['paired_baseline'] is None
    result=dict(status='development_reporting_only_scope_awaiting_adviser_review',metrics=report,
        new_fits=0,mapping_exported=False,adviser_approval_received=False,
        data_role='Previously exposed MST-E mapping development, never correction training or untouched final test',
        input_sha256=hashes)
    out.mkdir();(out/'summary.json').write_text(json.dumps(result,indent=2))
    rows=[]
    for scope,groups in [('overall',{'all':report['overall']}),('mst',report['by_mst']),('lighting',report['by_lighting']),('subject',report['by_subject'])]:
        for name,r in groups.items():
            rows.append(dict(scope=scope,group=name,**{k:v for k,v in r.items() if not isinstance(v,dict) and k not in ['candidate','paired_baseline','supported_candidate','supported_paired_baseline','all_measured_baseline']}))
    with (out/'availability.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    table=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in ['group','attempts','measured','processing_failures','available_predictions','unavailable_predictions','measured_without_held_category_support'])+'</tr>' for r in rows if r['scope']=='mst')
    page='<!doctype html><meta charset="utf-8"><title>MST limited evaluation</title><style>body{font:17px system-ui;max-width:1100px;margin:30px auto}table{border-collapse:collapse}td,th{padding:9px;border:1px solid #bbb}</style><h1>MST development evaluation</h1><p>Proposed limited scope; adviser review pending. Previously exposed mapping-development images.</p><p>418attempts;396measured;22processing failures. Zero mapping predictions: accuracy and paired candidate-baseline comparison are unavailable, not zero.</p><table><tr><th>MST</th><th>Attempts</th><th>Measured</th><th>Processing failures</th><th>Available predictions</th><th>Unavailable predictions</th><th>Measured without held-category support</th></tr>'+table+'</table><p>No lookup fitted/exported or correction model changed. Baseline-only statistics remain separate in JSON.</p><p><a href="summary.json">All metrics/provenance</a> · <a href="availability.csv">Category, lighting and subject denominators</a></p>'
    (out/'review.html').write_text(page,encoding='utf-8')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    print(json.dumps(dict(status=result['status'],overall=report['overall']),indent=2))


if __name__=='__main__':main()
