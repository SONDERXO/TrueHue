"""Read-only aggregation of actual-input mask/recovery evidence; never refits."""
import csv
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/ffhq_distorted_input_support_v1'
OUT=ROOT/'outputs/ffhq_distorted_input_support_assessment_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
NOTES={
 '54632':'Core close visually; stress extends support near head-covering/face edge and keeps magenta/beard artifacts.',
 '39568':'Core hairline/chin/neck support changes; stress recovery still has dark eye/mouth remnants and bright surrounding regions.',
 '29617':'Core keeps sunglasses protected on board with hand/jaw edge changes; stress has glasses/forehead boundary loss and magenta lower-face artifacts.',
 '29863':'Core largely close; stress mask clearly admits white head covering, and recovery visibly changes it while red/black face artifacts remain.',
 '16061':'Core retains clear-lens correction but trims fringe/temple; stress misses forehead/hairline skin and leaves an untreated dark edge.',
 '52445':'Core trims hairline/chin; stress boundaries shift and mouth/eye artifacts remain; no complete neck result.',
 '32685':'Core support extends onto right collar area; stress loses fringe/jaw support and keeps mouth/eye artifacts.',
 '53146':'Core cap/side/chin boundaries move; stress recovery still has dark eye/mouth and washed bright regions.',
 '48879':'Core shows face/hair/jaw changes; stress chin/neck changes and eye/mouth artifacts remain. Separate stress-over case fails nasal geometry.',
 '49131':'Core shows a visible jaw/neck transition compared with fixed-alpha recovery; stress has strong jaw/eye patches.',
 '59807':'Core glasses/fringe/neck boundaries shift; stress clear-lens/rim areas and neck shift, with posterisation and bright forehead patches.',
 '46795':'Core shifts forehead/jaw edges; stress loses more forehead support and retains magenta/black face artifacts.'}


def main():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=read(PARENT/'sha256.json');inputs=read(PARENT/'inference_plan.json')['input_sha256']
    assert all(sha(PARENT/p)==h for p,h in manifest.items()) and all(sha(p)==h for p,h in inputs.items())
    result=read(PARENT/'results.json');rows=[];layers={}
    for r in result['records']:
        c=r.get('correction_comparison',{});m=r.get('measurement_comparison',{});f=r.get('fit',{})
        features=r.get('measurement_report',{}).get('features') or {}
        rows.append(dict(source_id=r['source_id'],case_id=r['case']['id'],layer=r['case']['layer'],status=r['status'],
            correction_iou=c.get('consistency_iou'),measurement_iou=m.get('consistency_iou'),
            correction_lost_pixels=c.get('lost_pixels'),correction_added_pixels=c.get('added_pixels'),
            fit_intersection_pixels=f.get('fit_intersection_pixels'),missed_score_pixels=f.get('missed_original_scoring_pixels'),
            input_MAE=r['input_metrics']['rgb8_mae_codes'],fixed_alpha_MAE=r['fixed_alpha_metrics']['rgb8_mae_codes'],
            current_alpha_MAE=r['output_metrics_original_score']['rgb8_mae_codes'],
            current_alpha_deltaE00=r['output_metrics_original_score']['relative_deltaE00_mean'],
            changed_prior_protected_pixels=r['outside_source_changes']['changed_source_protected_pixels'],
            changed_pixels_outside_source=r['outside_source_changes']['changed_pixels_outside_source'],
            outside_source_MAE=r['outside_source_changes']['outside_source_MAE'],
            input_measured_ITA=features.get('input_ita_degrees'),MST=None,training_admitted=False))
    for layer in ['clean','core','composite_stress_design']:
        current=[r for r in rows if r['layer']==layer];available=[r for r in current if r['correction_iou'] is not None]
        measured=[r['measurement_iou'] for r in current if r['measurement_iou'] is not None]
        layers[layer]=dict(result['layers'][layer],measurement_consistency_iou_mean=statistics.mean(measured),
            measurement_comparison_denominator=len(measured),
            min_lost_correction_pixels=min(r['correction_lost_pixels'] for r in available),
            max_lost_correction_pixels=max(r['correction_lost_pixels'] for r in available),
            changed_prior_protected_pixels_median=statistics.median(r['changed_prior_protected_pixels'] for r in current),
            changed_prior_protected_pixels_max=max(r['changed_prior_protected_pixels'] for r in current),
            outside_source_MAE_all_attempts=statistics.mean(r['outside_source_MAE'] for r in current))
    OUT.mkdir()
    with (OUT/'cases.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (OUT/'cases.csv').open(newline='',encoding='utf-8') as stream:saved=list(csv.DictReader(stream))
    assert len(saved)==168
    assert all(float(a['current_alpha_MAE'])==b['current_alpha_MAE'] and a['source_id']==b['source_id'] for a,b in zip(saved,rows))
    assessment=dict(layers=layers,observer='assistant',inspected_boards=24,
        inspection_scope='predeclared_combined_cool_under_and_stress_combined_under_all12_at256px_not_all168',
        observations=NOTES,failures=[dict(id=r['image_id'],reason=r.get('reason')) for r in result['records'] if not r['recovery_available']],
        original_protection_is_ground_truth=False,parent_manifest_sha256=sha(PARENT/'sha256.json'),
        source_script_sha256=sha(Path(__file__)),csv_JSON_parity=True,new_inference=0,new_fits=0,admissions=0)
    (OUT/'assessment.json').write_text(json.dumps(assessment,indent=2),encoding='utf-8')
    assert all(sha(PARENT/p)==h for p,h in manifest.items()) and all(sha(p)==h for p,h in inputs.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2))
    print(json.dumps(dict(cases=len(rows),inspected_boards=24,failures=assessment['failures'],new_fits=0),indent=2))


if __name__=='__main__':main()
