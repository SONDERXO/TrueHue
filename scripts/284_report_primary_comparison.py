"""Preserve every result and enforce the recorded no-more-small-trials decision."""
import hashlib
import html
import json
import os
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'outputs/reviewed_primary_comparison_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(folder/'plan.json');rows={r['pair_id']:r for r in plan['rows']};records=read(folder/'predictions.json')
    summary=read(folder/'summary.json');assert not summary['gates']['primary_candidate']['passed']
    by_key={(r['pair_id'],r['method']):r for r in records};methods=plan['methods']
    pairs=sorted(rows,key=lambda p:(not any(by_key[(p,m)]['variant']=='identity' and by_key[(p,m)]['changed_input_pixels'] for m in methods),p))
    cards=[];boards=[]
    for pair in pairs:
        row=rows[pair];baseline=by_key[(pair,methods[0])];candidate=by_key[(pair,methods[1])]
        paths=[ROOT/row['reference_path'],ROOT/row['input_path'],
            folder/f'fold_{baseline["fold_id"]}'/(pair+'_'+methods[0]+'.png'),folder/f'fold_{candidate["fold_id"]}'/(pair+'_'+methods[1]+'.png')]
        assert sha(paths[2])==baseline['output_sha256'] and sha(paths[3])==candidate['output_sha256']
        failed_clean=row['variant']=='identity' and candidate['changed_input_pixels']>0
        cells=''.join('<figure><img loading="lazy" src="'+html.escape(os.path.relpath(path,folder).replace('\\','/'),quote=True)+'"><figcaption>'+label+'</figcaption></figure>' for path,label in zip(paths,['Reference','Input','Frozen endpoint baseline','Primary-data candidate']))
        note=row.get('exact_review_notes','')
        cards.append('<section><h2>'+html.escape(pair)+(' — candidate changed a clean photo' if failed_clean else '')+'</h2><p>Unchanged error '+f'{candidate["no_correction"]["ciede2000_source_mask"]:.3f}'+', baseline '+f'{baseline["metrics"]["ciede2000_source_mask"]:.3f}'+', candidate '+f'{candidate["metrics"]["ciede2000_source_mask"]:.3f}'+'</p>'+
            ('<p>Original review note: '+html.escape(note)+'</p>' if note else '')+'<div class="grid">'+cells+'</div></section>')
        if failed_clean:
            image=np.hstack([cv2.imread(str(p)) for p in paths]);header=np.full((32,image.shape[1],3),245,np.uint8)
            cv2.putText(header,pair+' | reference / input / baseline / candidate',(5,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,20,20),1)
            name='clean_failure_'+pair.split('__')[0]+'.png';assert cv2.imwrite(str(folder/name),np.vstack((header,image)));boards.append(name)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Primary data comparison</title><style>body{font:17px system-ui;max-width:1200px;margin:24px auto;padding:0 16px;background:#f4f6f8;color:#17202a}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}figure{margin:0}img{width:100%}section{background:white;padding:16px;margin:20px 0}h2{font-size:20px}@media(max-width:650px){.grid{grid-template-columns:repeat(2,1fr)}}</style><h1>Single planned comparison — candidate not adopted</h1><p>All 105 held-source cases are shown. Normal-case error improves, but three clean photos change and stress results worsen. No further labels are requested. This is exposed development, not final validation.</p>'+''.join(cards)+'</html>'
    (folder/'review.html').write_text(page,encoding='utf-8')
    (folder/'stopping_decision.json').write_text(json.dumps(dict(status='planned_comparison_complete_candidate_not_adopted',
        candidate_gate=summary['gates']['primary_candidate'],small_model_experiment_cycle_stopped=True,
        no_followup_feature_depth_weight_threshold_or_recipe_search=True,prior_endpoint_baseline_retained=True,
        user_reviews_and_prepared_data_preserved=True,active_demo_changed=False,
        next_action='A documented source-data or method decision before any new candidate; do not tune to these three clean failures.',
        summary_sha256=sha(folder/'summary.json')),indent=2),encoding='utf-8')
    (folder/'gallery_verification.json').write_text(json.dumps(dict(status='static_source_assets_verified',case_count=105,
        all_baseline_and_candidate_png_hashes_checked=True,live_browser_tested=False,
        html_sha256=sha(folder/'review.html'),producer_sha256=sha(Path(__file__)),
        clean_failure_board_sha256={name:sha(folder/name) for name in boards}),indent=2),encoding='utf-8')
    print('All 105 comparisons preserved; three clean failures shown; stopping rule recorded, no further trial launched.')


if __name__=='__main__':main()
