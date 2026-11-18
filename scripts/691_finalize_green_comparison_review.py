"""Exact unchanged-output review lineage and fixed family-stratified accounting."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/green_nonharm_comparison_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def family(recipe):
    if recipe=='clean':return 'clean'
    if recipe in ('colour_cool','colour_warm','stress_color_none'):return 'colour_only'
    if recipe.startswith(('exposure_','stress_exposure_')):return 'exposure_only'
    return 'combined'

def main():
    target=OUT/'review_receipt_PRIVATE.json';assert not target.exists()
    d=read(OUT/'results_PRIVATE.json');changes=read(OUT/'changes_PRIVATE.json');v=read(OUT/'verification_PRIVATE.json')
    parent_path=ROOT/'outputs/colour_nonharm_comparison_v1/results_PRIVATE.json';parent=read(parent_path)
    assert v['passed'] and v['result_sha256']==sha(OUT/'results_PRIVATE.json')
    assert changes['unchanged_outputs_and_metrics']==756 and not changes['changes'] and not changes['boards'] and not changes['sheets']
    assert all(a['case_id']==b['case_id'] and a['candidate']==b['candidate'] for a,b in zip(d['records'],parent['records'],strict=True))
    detail={}
    for co in ('development','later'):
        detail[co]={}
        for layer in ('clean','core','composite_stress_design'):
            detail[co][layer]={}
            for fam in ('clean','exposure_only','colour_only','combined'):
                rows=[r for r in d['records'] if r['cohort']==co and r['layer']==layer and family(r['recipe'])==fam]
                if not rows:continue
                scored=[r for r in rows if r['reference_available']];groups=sorted({r['subject_id'] for r in scored})
                entry=dict(attempts=len(rows),available=sum(r['mask_status']=='available' for r in rows),scored=len(scored),methods={})
                for method in ('parent','candidate'):
                    mm=dict(changed=sum(r[method]['changed_channels']>0 for r in rows))
                    for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                        values=[r[method]['region_metrics'][metric] for r in scored]
                        mm[metric]=dict(mean=sum(values)/len(values) if values else None,
                            harms=sum(r[method]['region_metrics'][metric]>r['input_region_metrics'][metric] for r in scored),
                            benefits=sum(r[method]['region_metrics'][metric]<r['input_region_metrics'][metric] for r in scored),
                            equal_publisher_group_mean=sum(sum(r[method]['region_metrics'][metric] for r in scored if r['subject_id']==g)/sum(r['subject_id']==g for r in scored) for g in groups)/len(groups) if groups else None)
                    entry['methods'][method]=mm
                detail[co][layer][fam]=entry
    (OUT/'family_summary_PRIVATE.json').write_text(json.dumps(detail,indent=2,allow_nan=False))
    receipt=dict(completed=True,selection=changes['selection'],changed_outputs=0,
        unchanged_output_pixels_and_metric_records=756,new_visual_boards_viewed=0,
        visual_review='No changed controls or outputs versus global nonharm. Script690 proved exact pixels and metric records for all756; prior global-nonharm review lineage reused. No fresh756-board visual review claimed.',
        parent_results_sha256=sha(parent_path),result_sha256=sha(OUT/'results_PRIVATE.json'),
        changes_sha256=sha(OUT/'changes_PRIVATE.json'),family_summary_sha256=sha(OUT/'family_summary_PRIVATE.json'),
        disposition='No evaluation behaviour improvement; preserve failed comparison and stop automatic follow-up.',
        production_adopted=False,holdout_image_reads=0)
    target.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
