"""Saved JSON/source diagnosis only. No arrays, learners or prediction calls."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/oblique_support_brightness_diagnosis_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve diagnosis')
    bound={}
    def read(relative):
        p=Path(relative)
        if not p.is_absolute():p=ROOT/p
        assert p.suffix=='.json' and p.resolve().is_relative_to(ROOT.resolve())
        bound[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text(encoding='utf-8'))
    prep='outputs/reviewed_ffhq_restoration_preparation_v1/'
    base='outputs/oblique_source_held_comparison_v1/'
    rows=read(prep+'rows_PRIVATE.json');preds=read(base+'predictions_PRIVATE.json')
    assessment=read(base+'assessment_45516d2751fd453580dae63f41d809bd.json')
    assert len(rows)==len(preds)==len(assessment['outcomes'])==44
    support=[]
    for r in rows:
        if r['experimental_role']!='identity':continue
        p=Path(r['annotation']);report=read(p/'report.json');manifest=read(p/'manifest.json')
        digest=hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest()
        assert digest==r['annotation_manifest_sha256']
        assert report['generated_fixture'] is False and report['correction_review']=='user_reviewed'
        support.append(dict(case_id=r['case_id'],annotation=r['annotation'],manifest_sha256=digest,
            strokes=len(report['strokes']),changed_pixels=report['changed_pixels'],
            face_width=report['face_width'],inward_edge_width=max(2,math.ceil(.03*report['face_width'])),
            inherited_whole_frame_256=True,pixel_manifest_entries=len(manifest['files'])))
    grouped=defaultdict(dict)
    for p in preds:grouped[p['source']][p['role']]=p
    equal=[s for s,r in grouped.items() if r['identity']['controls']==r['colour_cool']['controls']]
    collapsed=[s for s,r in grouped.items() if len({tuple(p['controls']) for p in r.values()})==1]
    mapping={p['case_id']:p for p in preds}
    noticeable=[mapping[r['case_id']] for r in assessment['outcomes'] if r['outcome']=='noticeable_change']
    result=dict(status='SAVED_EVIDENCE_DIAGNOSIS_COMPLETE_NO_REPAIR_SELECTED',support_metadata=support,
        manual_correction_changed_sources=sum(x['changed_pixels']['correction']>0 for x in support),
        manual_measurement_changed_sources=sum(x['changed_pixels']['measurement']>0 for x in support),
        identity_cool_exact_same_controls_sources=equal,all_four_same_controls_sources=collapsed,
        interpretation='Equal controls do not prove a shared leaf; different leaves may have identical constants.',
        noticeable_identity_brightening=sum(p['controls'][0]<1-1e-12 for p in noticeable),
        noticeable_identity_darkening=sum(p['controls'][0]>1+1e-12 for p in noticeable),
        per_source_gap_locations='Not established without separately scoped existing-pixel inspection',
        actual_tone_groups='Not independently established; no lighter-skin threshold inferred',
        fits=0,predictions=0,pixel_reads=0,holdout_reads=0,runtime_changes=False)
    sources=['scripts/414_check_ffhq_mask_support.py','scripts/803_prepare_reviewed_ffhq_support.py',
        'src/demo/photographic_support.py','src/demo/manual_brush.py','scripts/808_prepare_reviewed_ffhq_restoration.py',
        'src/skin_masking/full_face_support.py','src/skin_masking/continuous_correction.py',
        'src/correction/seamless_blend.py','scripts/848_run_oblique_source_held_comparison.py',
        'scripts/853_diagnose_saved_support_and_brightness.py']
    for name in sources:bound[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    OUT.mkdir()
    (OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in bound.items())
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,source_hashes_unchanged=True,
        input_sha256=bound,scientific_rows=44,distinct_support_exports=11,pixel_reads=0,fits=0,predictions=0),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='support_metadata'},indent=2))

if __name__=='__main__':main()
