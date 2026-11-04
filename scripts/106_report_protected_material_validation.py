"""Package complete stage boards and a technical readiness decision."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/paint_protection_validation_v1';data=json.loads((out/'summary.json').read_text())
    manifest=json.loads((ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json').read_text())
    records={r['key']:r for r in data['records']};(out/'contacts').mkdir(exist_ok=True)
    failures=[];totals={a:dict(available=0,protected_selection_cases=0,interior_selection_cases=0,statistical_valid_cases=0,prospective_retention_assessable=0,prospective_retention_pass=0) for a in ['A','F','C','C2']}
    for r in records.values():
        if r['status']!='available':continue
        for a,t in totals.items():
            t['available']+=1
            v=r['stages']['correction'][a];protected=v['protected_regions']
            # This includes user features; names/labels are retained per row.
            selected=sum(x['selected'] for x in protected.values());interior=sum(x['interior_selected'] for x in protected.values())
            if protected:
                t['protected_selection_cases']+=int(selected>0);t['interior_selection_cases']+=int(interior>0)
                if selected:failures.append(dict(case=r['key'],arm=a,stage='correction',regions=protected))
            t['statistical_valid_cases']+=int(r['stages']['measurement'][a]['statistics']['valid'] and r['stages']['measurement'][a]['brightness']['valid'])
            retention=r['retention_prospective_generation']
            if retention and retention[a]:
                t['prospective_retention_assessable']+=1;t['prospective_retention_pass']+=int(retention[a]['screen_pass'])
    for f in manifest['frames']:
        rows=[];ident=f['frame_id'];h,w=f['height'],f['width']
        for variant in manifest['variants']:
            key=ident+'_'+variant;r=records[key];image=cv2.imread(str(out/'images'/(key+'.png')))
            for stage in (['generation','measurement','correction'] if variant=='clean' else ['measurement','correction']):
                panels=[]
                for title in ['source','A','F','C','C2']:
                    shown=image.copy()
                    if title!='source' and r['status']=='available':
                        mask=cv2.imread(str(out/'masks'/(key+'_'+stage+'_'+title+'.png')),0)>0
                        shown[mask]=np.rint(.55*shown[mask]+.45*np.array([0,220,0])).astype(np.uint8)
                    shown=cv2.copyMakeBorder(shown,32,0,0,0,cv2.BORDER_CONSTANT)
                    cv2.putText(shown,key+' '+stage,(2,11),cv2.FONT_HERSHEY_SIMPLEX,.25,(255,255,255),1)
                    text=title if r['status']=='available' else title+' UNAVAILABLE'
                    cv2.putText(shown,text,(2,25),cv2.FONT_HERSHEY_SIMPLEX,.30,(255,255,255),1);panels.append(shown)
                rows.append(np.hstack(panels))
        assert cv2.imwrite(str(out/'contacts'/(ident+'.png')),np.vstack(rows))
    readiness=dict(status='hold_mask_policy_failed_no_regeneration_no_training',frozen_manifest_sha256=data['frozen_manifest_sha256'],
        inventory_sources=114,source_frames=17,diagnostic_probes=51,available_probes=48,
        unavailable=[dict(case=r['key'],reason=r['reason']) for r in records.values() if r['status']!='available'],
        gates=dict(protected_material_zero_selection='FAIL',primary_user_paint_protection='FAIL',
            ordinary_skin_coverage_loss_resolved='FAIL_prior_user_reference_loss_unresolved',
            inference_availability='FAIL_3_probes_unavailable',new_material_ground_truth='PROVISIONAL_not_user_or_expert_verified',
            historical_failures_resolved='FAIL_prior_5_retention_failures_and_31154_hold_retained'),
        totals=totals,correction_protected_region_failures=failures,training_pairs_regenerated=0,models_fitted=0,
        previous_reviews_holds_and_folds_unchanged=True,
        interpretation='Selected development challenge set; neither sample count nor region passes establish population performance. Do not train around mask defects.')
    (out/'readiness.json').write_text(json.dumps(readiness,indent=2))
    page=['<!doctype html><meta charset="utf-8"><title>TrueHue protected-material validation</title><style>body{font:16px system-ui;max-width:1250px;margin:24px auto;background:#182028;color:#eee}a{color:#9cd9ff}img{max-width:100%;height:auto}section{margin:32px 0}summary{cursor:pointer}</style><h1>Protected-material development validation</h1>',
      '<p>114 known TRAIN sources inventoried; 17 frozen frames × 3 diagnostic probes. 48 available, 3 unavailable. Fixed A/F/C/C2; no retuning. Green: selected support. Red outlines on case boards: protected references. New Codex interiors are provisional, not user/expert truth. No training pairs regenerated or model fitted.</p>',
      '<p><b>HOLD:</b> painted/cosmetic/mark pixels remain selected; coverage and historical holds remain unresolved.</p><p><a href="summary.json">All results</a> · <a href="readiness.json">Readiness gates</a> · <a href="verification.json">Independent replay</a> · <a href="../../data/manifests/paint_protection_validation_v1/frozen_manifest.json">Frozen sources/labels</a></p>']
    for f in manifest['frames']:
        ident=f['frame_id'];page.append('<section><h2>'+ident+' — '+html.escape(f['role'])+'</h2>')
        if f['annotation'].get('regions'):page.append('<details><summary>Frozen provisional regions</summary><img loading="lazy" src="../paint_protection_inventory_v1/regions/'+ident+'_frozen.png"></details>')
        page.append('<details><summary>All stages and candidates (full resolution)</summary><a href="contacts/'+ident+'.png"><img loading="lazy" src="contacts/'+ident+'.png"></a></details>')
        for variant in manifest['variants']:page.append('<img loading="lazy" src="boards/'+ident+'_'+variant+'.png">')
        page.append('</section>')
    (out/'review.html').write_text('\n'.join(page),encoding='utf-8')
    print(json.dumps(dict(totals=totals,unavailable=readiness['unavailable'])))
if __name__=='__main__':main()
