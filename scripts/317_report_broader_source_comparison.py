"""Preserve all121 matched cases and the predeclared stopping decision."""
import hashlib
import html
import json
import os
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/broader_source_comparison_v1'


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    if (OUT/'stopping_decision.json').exists():raise FileExistsError('Report already saved')
    verification=read(OUT/'verification.json');assert verification['status']=='pass'
    for p,digest in verification['evidence_sha256'].items():assert sha(OUT/p)==digest,p
    plan=read(OUT/'plan.json');summary=read(OUT/'summary.json');records=read(OUT/'predictions.json')
    rows={r['pair_id']:r for r in plan['rows']};by_key={(r['pair_id'],r['method']):r for r in records}
    # Independently check aggregates and conservative decision without refitting.
    for scope,include in [('all',lambda p:True),('clean',lambda p:rows[p]['stratum']=='original_control'),
        ('primary_all',lambda p:rows[p]['stratum']=='primary'),('stress_all',lambda p:rows[p]['stratum']=='clipped_stress')]:
        for method in ['A','B','C']:
            part=[r for r in records if r['method']==method and include(r['pair_id'])]
            saved=next(a for a in summary['aggregates'] if a['method']==method and a['scope']==scope)
            assert saved['cases']==len(part)
            assert saved['case_weighted']==float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part]))
    failures=[r['pair_id'] for r in records if r['method']=='C' and rows[r['pair_id']]['stratum']=='original_control' and r['changed_input_pixels']]
    assert failures==summary['clean_failures']['C'] and len(failures)==4
    assert not summary['passed'] and not summary['gates']['all_clean_originals_unchanged']
    # Preserve interrupted fits and ensure the resume did not refit them.
    recovery=read(OUT/'interruption_recovery.json')
    assert recovery['interrupted_fits_preserved']==29
    for p,digest in recovery['tree_sha256'].items():assert sha(OUT/p)==digest
    gallery=[];boards={}
    order=sorted(rows,key=lambda p:(p not in failures,p))
    for pair in order:
        row=rows[pair];paths=[ROOT/row['reference_path'],ROOT/row['input_path']]+[ROOT/by_key[(pair,m)]['output_path'] for m in ['A','B','C']]
        labels=['Reference','Input','A: endpoint','B: prior primary','C: expanded primary']
        images=''.join('<figure><img loading="lazy" src="'+html.escape(os.path.relpath(p,OUT).replace('\\','/'),quote=True)+'"><figcaption>'+label+'</figcaption></figure>' for p,label in zip(paths,labels))
        metric='; '.join(m+': '+format(by_key[(pair,m)]['metrics']['ciede2000_source_mask'],'.3f') for m in ['A','B','C'])
        note=row.get('exact_review_notes','')
        gallery.append('<section><h2>'+html.escape(pair)+(' — C changed a clean original' if pair in failures else '')+'</h2><p>'+metric+'</p>'+('<p>Exact review note: '+html.escape(note)+'</p>' if note else '')+'<div class="grid">'+images+'</div></section>')
        if pair in failures:
            panel=np.hstack([cv2.imread(str(p)) for p in paths]);header=np.full((32,panel.shape[1],3),245,np.uint8)
            cv2.putText(header,pair+' | reference / input / A / B / C',(6,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,20,20),1)
            name='clean_failure_'+pair.split('__')[0]+'.png';assert cv2.imwrite(str(OUT/name),np.vstack([header,panel]));boards[name]=sha(OUT/name)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Broader-source comparison</title><style>body{font:17px system-ui;background:#f4f6f8;color:#17202a;max-width:1400px;margin:24px auto;padding:0 16px}.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}figure{margin:0}img{width:100%}section{background:white;padding:16px;margin:20px 0}h2{font-size:20px}@media(max-width:700px){.grid{grid-template-columns:repeat(2,1fr)}}</style><h1>Source-expansion comparison — candidate not adopted</h1><p>All121 held-source cases. Four clean originals change; overall error and new-primary results fail the predeclared gates. Exposed development only. No new review requested; no model tuning follows.</p>'+''.join(gallery)+'</html>'
    (OUT/'review.html').write_text(page,encoding='utf-8')
    preparation=read(ROOT/'outputs/additional_six_source_pairs_v1/summary.json')
    holds=dict(rejected_primary_masks=11,new_clipped_variants_not_admitted=13,technical_mask_screen_holds=2,
        new_preparation_attempts=preparation['generated_attempts'],new_admitted_primary=4,
        note='These26 excluded new variants are preparation/review holds, not silently dropped model failures; all121 admitted cases processed successfully.')
    (OUT/'holds.json').write_text(json.dumps(holds,indent=2),encoding='utf-8')
    decision=dict(status='single_predeclared_comparison_complete_candidate_not_adopted',
        candidate_gate_passed=False,failed_gates=[k for k,v in summary['gates'].items() if not v],
        clean_failure_ids=failures,endpoint_research_reference_retained=True,active_demo_changed=False,
        no_followup_feature_mask_depth_weight_recipe_or_source_exception_search=True,
        parser_and_beard_work_on_hold=True,summary_sha256=sha(OUT/'summary.json'),verification_sha256=sha(OUT/'verification.json'),
        next_action='Document evidence and unresolved reference/illumination/MST requirements; adviser method discussion before any new correction cycle. No same-cohort tuning.')
    (OUT/'stopping_decision.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
    report=dict(status='pass',case_count=121,clean_failure_boards=boards,live_browser_tested=False,
        interrupted_tree_hashes_preserved=29,producer_sha256=sha(Path(__file__)),
        evidence_sha256={name:sha(OUT/name) for name in ['review.html','holds.json','stopping_decision.json']})
    (OUT/'report_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('All121 cases preserved;4 clean failures; nonadoption and stopping rule saved.')


if __name__=='__main__':main()
