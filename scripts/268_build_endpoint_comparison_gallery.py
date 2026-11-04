"""Display all source-held results including the candidate's clean failure."""
import hashlib
import html
import json
import os
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/endpoint_feature_tree_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def relative(p):return html.escape(os.path.relpath(p,out).replace('\\','/'),quote=True)
    plan=read(out/'plan.json');rows={r['pair_id']:r for r in plan['rows']}
    records=read(out/'predictions.json');candidate=[r for r in records if r['method']=='paired_endpoint11']
    base={r['pair_id']:r for r in records if r['method']=='clean_augmented_baseline'}
    cards=[];selected=[]
    # Show clean failures first; retain every other pair, not a favorable subset.
    candidate.sort(key=lambda r:(not(r['variant']=='identity' and r['changed_input_pixels']>0),r['pair_id']))
    for r in candidate:
        row=rows[r['pair_id']];old=base[r['pair_id']]
        paths=[ROOT/row['reference_path'],ROOT/row['input_path'],
            ROOT/'outputs/six_reviewed_pair_comparison_v1'/f'fold_{r["fold_id"]}'/(r['pair_id']+'_clean_augmented_baseline.png'),
            out/f'fold_{r["fold_id"]}'/(r['pair_id']+'.png')]
        assert sha(paths[-1])==r['output_sha256'] and sha(paths[2])==old['output_sha256']
        cells=''.join('<figure><img loading="lazy" src="'+relative(p)+'"><figcaption>'+label+'</figcaption></figure>' for p,label in zip(paths,['Reference','Input','Earlier model','Endpoint candidate']))
        failure=r['variant']=='identity' and r['changed_input_pixels']>0
        cards.append('<section><h2>'+html.escape(r['pair_id'])+(' — clean photo changed' if failure else '')+'</h2><p>Error: unchanged '+f'{r["no_correction"]["ciede2000_source_mask"]:.3f}'+', earlier '+f'{old["metrics"]["ciede2000_source_mask"]:.3f}'+', candidate '+f'{r["metrics"]["ciede2000_source_mask"]:.3f}'+'</p><div class="grid">'+cells+'</div></section>')
        if failure:
            selected.append(('clean_failure',paths,r['pair_id']))
    distorted=[r for r in candidate if r['variant']!='identity']
    best=max(distorted,key=lambda r:base[r['pair_id']]['metrics']['ciede2000_source_mask']-r['metrics']['ciede2000_source_mask'])
    row=rows[best['pair_id']]
    selected.append(('largest_distorted_gain',[ROOT/row['reference_path'],ROOT/row['input_path'],
        ROOT/'outputs/six_reviewed_pair_comparison_v1'/f'fold_{best["fold_id"]}'/(best['pair_id']+'_clean_augmented_baseline.png'),
        out/f'fold_{best["fold_id"]}'/(best['pair_id']+'.png')],best['pair_id']))
    for label,paths,pair in selected:
        images=[cv2.imread(str(p)) for p in paths];board=np.hstack(images)
        header=np.full((32,board.shape[1],3),245,np.uint8)
        cv2.putText(header,pair+' | reference / input / earlier / candidate',(5,23),cv2.FONT_HERSHEY_SIMPLEX,.55,(20,20,20),1)
        assert cv2.imwrite(str(out/(label+'.png')),np.vstack((header,board)))
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Endpoint feature comparison</title><style>body{font:17px system-ui;max-width:1200px;margin:24px auto;padding:0 16px;background:#f4f6f8;color:#17202a}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}figure{margin:0}img{width:100%}section{background:white;padding:16px;margin:20px 0}h2{font-size:20px}@media(max-width:650px){.grid{grid-template-columns:repeat(2,1fr)}}</style><h1>Correction candidate: all 47 held-source results</h1><p>Research comparison only. Each input was excluded from its own fitted model. The candidate still changes one clean photo, shown first. All results are included; no review decisions are requested.</p><p>Lower error is better. These synthetic development cases do not prove real-photo accuracy. The working demo is unchanged.</p>'+''.join(cards)+'</html>'
    (out/'review.html').write_text(page,encoding='utf-8')
    (out/'gallery_verification.json').write_text(json.dumps(dict(status='static_assets_verified',items=47,
        all_candidate_and_baseline_image_hashes_verified=True,clean_failure_shown_first=True,
        browser_interaction_tested=False,selected_boards=[dict(selection=a,pair_id=c) for a,b,c in selected],
        gallery_sha256=sha(out/'review.html'),producer_sha256=sha(Path(__file__))),indent=2),encoding='utf-8')
    print('Saved all 47 comparisons; clean failure first, largest distorted gain explicitly labeled.')


if __name__=='__main__':main()
