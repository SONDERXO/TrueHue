"""Private case-level source-followup assessment; no admission or fitting."""
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
VERIFY=ROOT/'outputs/stellenbosch_new_subject_verification_v1'
OUT=ROOT/'outputs/stellenbosch_new_subject_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NOTES={
1:('visually_usable','Broad apparent facial skin; missing right/central region and native contour limits remain, not obvious object inclusion.'),
2:('visually_usable','Broad apparent skin; eyes closed and small nose/mouth exclusions retained, fine borders unverified.'),
3:('visually_usable','Broad selected forehead/cheeks/chin appear facial skin; no dominant visible external object.'),
4:('uncertain','Glasses reflections, sparse temple/chin pieces and major face loss prevent confident material/comparability judgement.'),
5:('uncertain','Glasses/reflections and selected eye-adjacent patches remain ambiguous at native detail.'),
6:('uncertain','Fragmented facial perimeter around glasses; fine rims/reflections and sampling comparability unresolved.'),
7:('visually_usable','Connected lower-cheek/jaw/chin support appears facial skin, without obvious beard/object; major upper-face omission retained.'),
8:('visually_usable','Selected cheeks/chin appear skin despite central and forehead holes; fringe boundary remains uncertain.'),
9:('visually_usable','Broad lower-face/cheek skin; fringe-adjacent upper face omitted, fine hairline boundaries not certified.'),
10:('visually_usable','Broad apparent facial skin; outer hair/forehead and mouth borders still unverified.'),
11:('visually_usable','Broad face-skin support; nearby earring/garment outside main support, fine jaw-edge uncertainty retained.'),
12:('visually_usable','Selected forehead/cheek/chin pieces appear skin; central omission and nearby earring make complete coverage/precision unproven.'),
13:('uncertain','Possible selected upper-lip/chin stubble or facial hair cannot be separated confidently from skin at native resolution.'),
14:('uncertain','Upper-lip/chin facial-hair ambiguity remains alongside central skin loss; no beard-free measurement claim.'),
15:('uncertain','Broad skin-looking selection includes uncertain chin/upper-lip facial-hair material at native scale.'),
16:('visually_usable','Broad apparent facial skin; high hair and straps outside main mask, fine chin/mouth borders uncertain.'),
17:('visually_usable','Broad forehead/cheek/chin skin-looking selection; small forehead exclusion and native contour limits retained.'),
18:('visually_usable','Broad apparent facial skin, with ordinary fine feature/contour uncertainty and no obvious dominant object.'),
19:('uncertain','Very dim forehead-only pieces with incomplete facial context; not enough confidence in representativeness/material judgement.'),
20:('uncertain','Visible beard/side-face material may enter cheek/chin selection; central omission and native blur unresolved.'),
21:('uncertain','Broad lower-face selection overlaps visible/possible beard material; not established as skin-only.'),
22:('uncertain','Possible chin/jaw facial hair within broad mask cannot be confidently separated at native detail.'),
23:('uncertain','Possible selected jaw/chin stubble persists despite broad face support; fine material distinction unresolved.'),
24:('uncertain','Central gap and possible jaw/chin facial hair remain; no clean-skin judgement despite technical pass.'),
25:('uncertain','Very dim original and narrow forehead-only support; native material/context judgement uncertain.'),
26:('visually_usable','Warm-condition forehead/right-cheek/chin selection appears facial skin with visible context; asymmetric loss and native detail remain limitations.'),
27:('visually_usable','Warm-condition selected forehead/cheek/chin patches appear skin; large asymmetric central loss limits comparability, not obvious external-object selection.'),
28:('uncertain','Dim original; forehead-only strip near hairline has limited native context and cross-condition comparability.'),
30:('uncertain','Sparse forehead/side-face pieces in dim native image; material confidence and anatomical sampling remain uncertain.')}

def main():
    if OUT.exists():raise FileExistsError(OUT)
    plan=read(PARENT/'plan_PRIVATE.json');bound=read(PARENT/'inference_plan.json')['input_sha256']
    for root in [PARENT,VERIFY]:bound.update({str(root/p):h for p,h in read(root/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    result=read(PARENT/'results_PRIVATE.json');rows=[];groups=defaultdict(list);bands=defaultdict(Counter)
    old=read(ROOT/'outputs/stellenbosch_bounded_preparation_v1/plan_PRIVATE.json')['selection']
    oldhashes={sha(Path(r['source_path'])) for r in old};newhashes={r['source_sha256'] for r in result['records']}
    assert len(newhashes)==30 and not oldhashes&newhashes
    for r in result['records']:
        if r['status']=='success':disposition,note=NOTES[r['case_index']]
        else:
            assert r['case_index'] not in NOTES;disposition='failed';note=r.get('reason') or r.get('measurement_report',{}).get('reason')
        row=dict(case_id=r['case_id'],subject_key=r['subject_key'],condition=r['condition'],sampling_stratum=r['sampling_stratum'],
            source_mst_exact_decimal=r['source_mst_exact_decimal'],technical_status=r['status'],disposition=disposition,note=note,
            calibration_admitted=False,training_admitted=False,source_sha256=r['source_sha256'],
            mask_sha256=sha(PARENT/r['case_id']/'measurement_mask.png') if r['status']=='success' else None)
        rows.append(row);groups[r['subject_key']].append(row);bands[r['sampling_stratum']].update(attempts=1,**{disposition:1})
    counts=Counter(r['disposition'] for r in rows)
    assert counts==Counter(visually_usable=14,uncertain=15,failed=1) and len(groups)==10
    complete=sum(all(r['disposition']=='visually_usable' for r in group) for group in groups.values());assert complete==4
    summary=dict(attempts=30,new_publisher_keys=10,technical_passes=29,counts=dict(counts),complete_visually_plausible_subject_keys=complete,
        by_descriptive_stratum={k:dict(v) for k,v in bands.items()},
        highest_interval_visually_plausible_conditions=[r['condition'] for r in rows if r['sampling_stratum']=='[9,10]' and r['disposition']=='visually_usable'],
        all30boards_assistant_inspected=True,source_scores_hidden_on_boards=True,independent_or_blinded=False,
        raw_source_byte_hashes_disjoint_from_old30=True,publisher_keys_not_cross_dataset_identity_verification=True,
        decision='do_not_promote_visual_subset_to_cross_lighting_calibration_cohort',
        admissions=0,mapping_fits=0,tree_fits=0,new_forwards_for_assessment=0,
        no_untouched_highest_interval_keys_left_in_release=True,
        old_and_new_not_pooled_for_fitting=True,automatic_next_batch=False,
        script_sha256=sha(__file__),parent_manifest_sha256=sha(PARENT/'sha256.json'))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=rows),indent=2),encoding='utf-8')
    with (OUT/'cases_PRIVATE.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (OUT/'cases_PRIVATE.csv').open(newline='',encoding='utf-8') as stream:reloaded=list(csv.DictReader(stream))
    assert len(reloaded)==30 and all(a['source_mst_exact_decimal']==b['source_mst_exact_decimal'] and a['disposition']==b['disposition'] for a,b in zip(reloaded,rows))
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
