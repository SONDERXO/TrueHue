"""Bind actual assistant per-case visual decisions; no calibration admission."""
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_usability_screen_v1'
SOURCE=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_usability_decisions_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NOTES={
1:('visually_usable','Broad apparent cheek/forehead/chin skin; hair lock mostly excluded. Fine hairline/native contour remains uncertain, not calibrated truth.'),
2:('visually_usable','Broad apparent facial skin under warm cast, no obvious selected object. Hairline/mouth-border precision remains limited.'),
3:('visually_usable','Broad apparent facial skin, hair lock excluded; small feature/contour uncertainties remain.'),
4:('visually_usable','Selected forehead/cheeks/chin appear facial skin; central holes are missing-skin concerns rather than clear object inclusion.'),
5:('visually_usable','Broad facial-skin selection; forehead/nasal holes retained as coverage concerns, no obvious dominant selected object.'),
6:('visually_usable','Facial cheek/forehead/chin regions remain visually plausible despite central gap; no complete-skin-coverage claim.'),
7:('visually_usable','Connected forehead/upper-cheek selection appears skin. Missing lower face is a comparability concern, not automatically contamination.'),
8:('visually_usable','Broad cheek/forehead/chin support appears facial skin; fine outer edge and feature boundaries unverified.'),
9:('visually_usable','Broad facial skin including restored chin; native contour precision and condition mismatch remain.'),
10:('visually_usable','Broad apparent facial skin with no obvious selected external object; fine hairline and nasal edge uncertain.'),
11:('visually_usable','Broad apparent facial skin; upper forehead contour uncertain at native resolution.'),
12:('visually_usable','Broad apparent face-skin selection; small nasal exclusions and mouth edge retained, no perfect-mask claim.'),
13:('visually_usable','Broad apparent facial skin, high hair outside mask; chin/mouth-edge uncertainty remains.'),
14:('visually_usable','Broad apparent cheek/chin/forehead skin restored; jaw/forehead boundary unverified.'),
15:('visually_usable','Broad apparent facial skin; right eye-side and chin-edge limitations remain.'),
17:('uncertain','Glasses/reflections and native blur prevent confident judgement of selected eye-adjacent material despite broader cheek/forehead support.'),
18:('uncertain','Sparse forehead/outer-cheek/chin pieces around glasses; reflected/fine rim material and anatomical comparability unresolved.'),
20:('uncertain','Very dim original; limited forehead/side-face strip. Cannot confidently judge material and representative facial support from native detail.'),
21:('uncertain','Dim fragmented forehead/cheek/chin pieces; local context/native detail insufficient for confident visual usability.'),
22:('visually_usable','Selected forehead/cheeks/chin appear facial skin; central hole is retained as missing-skin concern; hair-side boundaries remain uncertain.'),
23:('visually_usable','Selected forehead/cheek/chin pieces visibly follow facial skin; large central gap limits representativeness, not obvious object contamination.'),
24:('visually_usable','Remaining facial selection appears skin despite asymmetric central omission; fine sideburn/jaw boundaries remain unverified.'),
25:('uncertain','Very dim native face; narrow forehead-only selection. Material confidence and cross-condition sampling adequacy unresolved.'),
26:('uncertain','Dim original and forehead-only strip; small holes and native blur prevent confident usable-skin judgement.'),
27:('uncertain','Dim and fragmented forehead/cheek/chin selection; native detail and differing sampled region remain ambiguous.')}

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json')
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    evidence={r['case_id']:r for r in read(PARENT/'cases_PRIVATE.json')}
    rows=[];bygroup=defaultdict(list);coverage=defaultdict(Counter)
    for r in read(SOURCE/'results_PRIVATE.json')['records']:
        index=r['case_index'];e=evidence[r['case_id']]
        assert e['source_sha256']==sha(Path(r['source_path']))
        if r['status']=='success':
            disposition,reason=NOTES[index]
            assert e['measurement_mask_sha256']==sha(SOURCE/r['case_id']/'measurement_mask.png')
        else:
            assert index not in NOTES
            disposition='failed';reason=r.get('reason') or r['parent_report'].get('reason')
        row=dict(case_id=r['case_id'],subject_key=r['subject_key'],condition=r['condition'],
            source_mst_exact_decimal=r['source_mst_exact_decimal'],source_mst_raw_type=r['source_mst_raw_type'],
            sampling_stratum=r['sampling_stratum'],technical_status=r['status'],disposition=disposition,reason=reason,
            observer='assistant',independent_or_blinded_review=False,calibration_admitted=False,training_admitted=False,
            source_sha256=e['source_sha256'],mask_sha256=e['measurement_mask_sha256'])
        rows.append(row);bygroup[r['subject_key']].append(row)
        coverage[r['sampling_stratum']].update(attempts=1,**{disposition:1})
    assert len(rows)==30 and len(bygroup)==10 and len(NOTES)==25
    counts=Counter(r['disposition'] for r in rows)
    assert counts==Counter(visually_usable=18,uncertain=7,failed=5)
    complete=sum(len(g)==3 and all(r['disposition']=='visually_usable' for r in g) for g in bygroup.values())
    assert complete==6 and coverage['[9,10]']['visually_usable']==0
    summary=dict(attempts=30,subject_keys=10,counts=dict(counts),complete_visually_usable_subject_keys=complete,
        by_preexisting_descriptive_stratum={k:dict(v) for k,v in coverage.items()},
        by_condition={c:dict(Counter(r['disposition'] for r in rows if r['condition']==c)) for c in sorted({r['condition'] for r in rows})},
        all30_native_and_selected_boards_assistant_inspected=True,source_scores_hidden_on_boards=True,
        visually_usable_means_development_visual_plausibility_only=True,independent_validation=False,
        decision='no_defensible_cross_score_cross_lighting_calibration_cohort_established_by_this_screen',
        calibration_admissions=0,mapping_fits=0,tree_fits=0,new_forwards=0,
        repeat_same30_review_or_enhancement_not_activated=True,
        next_substantive_option='One separately specified source-first cohort with frozen candidate and support review; no processing activated.',
        parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir()
    (OUT/'decisions_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=rows),indent=2),encoding='utf-8')
    with (OUT/'decisions_PRIVATE.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (OUT/'decisions_PRIVATE.csv').open(newline='',encoding='utf-8') as stream:reloaded=list(csv.DictReader(stream))
    assert len(reloaded)==30 and all(a['source_mst_exact_decimal']==b['source_mst_exact_decimal'] and a['disposition']==b['disposition'] and a['mask_sha256']==(b['mask_sha256'] or '') for a,b in zip(reloaded,rows))
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
