"""Independently verify cached failure accounting and package diagnostic boards."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    a=cv2.imread(str(p),0);assert a is not None and set(np.unique(a))<={0,255};return a>0
def polygon(points,w,h):
    contour=np.asarray(points,np.float32)
    return np.array([[cv2.pointPolygonTest(contour,(float(x),float(y)),False)>=0 for x in range(w)] for y in range(h)])
def main():
    out=ROOT/'outputs/material_failure_attribution_v1';summary=json.loads((out/'summary.json').read_text())
    parent=ROOT/'outputs/paint_protection_validation_v1';old=json.loads((parent/'summary.json').read_text())
    cases={r['key']:r for r in old['records']};manifest=json.loads((ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json').read_text())
    frames={f['frame_id']:f for f in manifest['frames']};regions={};export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text())
    for ident,f in frames.items():
        w,h=f['width'],f['height'];rr={}
        if f['annotation']['kind']=='unchanged_user_reference':
            labels=cv2.imread(str(ROOT/f['annotation']['labels_path']),0);rr['user_skin']=labels==1
            if ident=='16798':
                spec=next(r for r in export['images'] if Path(r['image_id']).stem==ident);paint=np.zeros((h,w),bool)
                for p in spec['polygons'][:6]:paint|=polygon(p['points'],w,h)
                rr['user_paint']=paint&(labels==3);rr['user_features']=(labels==3)&~paint
            else:rr['user_features']=labels==3
        for r in f['annotation'].get('regions',[]):rr[r['region_id']]=polygon(r['points'],w,h)
        regions[ident]=rr
    rows=stages=0;contacts={};witnesses={w['case']:w for w in summary['chroma_order_witnesses']}
    for row in summary['records']:
        key=row['key'];case=cases[key];ident=row['frame_id']
        assert row['status']==case['status']
        if row['status']!='available':assert row['regions']=={} and row['reason']==case['reason'];continue
        ing=parent/'ingredients';dc=cv2.imread(str(ing/(key+'_parser.png')),0);sc=cv2.imread(str(ing/(key+'_semantic.png')),0)
        excluded=read(ing/(key+'_excluded.png'));seeds=read(ing/(key+'_seeds.png'));x,y,w,h=case['face_box'];pad=case['material']['pad']
        yy,xx=np.indices(dc.shape);bounds=(xx>=max(0,x-pad))&(xx<min(dc.shape[1],x+w+pad))&(yy>=max(0,y-pad))&(yy<min(dc.shape[0],y+h+pad))
        dense=np.isin(dc,[1,10]);semantic=sc==3
        # First failed condition expressed as mutually exclusive category codes.
        code=np.select([~dense,~semantic,excluded,~bounds],[0,1,2,3],default=4)
        image=cv2.imread(str(parent/'images'/(key+'.png')));lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
        normalized=(lab-np.array(case['material']['median']))/np.array(case['material']['scale'])
        fd=np.linalg.norm(normalized,axis=2);cd=np.linalg.norm(normalized[:,:,1:],axis=2)
        for name,item in row['regions'].items():
            region=regions[ident][name];hist=np.bincount(code[region],minlength=5)
            assert list(item['funnel'].values())==hist.tolist() and item['pixels']==int(region.sum())
            assert item['seed_selected']==int(seeds[region].sum()) and item['seed_total']==int(seeds.sum())
            assert item['dense_categories']==np.bincount(dc[region],minlength=19).tolist()
            assert item['coarse_categories']==np.bincount(sc[region],minlength=6).tolist()
            inside=region&(code==4)
            for field,dist in [('full_distance_in_A',fd),('chroma_distance_in_A',cd)]:
                if inside.any():np.testing.assert_allclose(list(item[field].values()),np.percentile(dist[inside],[10,50,90]),rtol=0,atol=1e-10)
                else:assert item[field] is None
            for stage,arms in item['stages'].items():
                for arm,count in arms.items():assert count==int(read(parent/'masks'/(key+'_'+stage+'_'+arm+'.png'))[region].sum());stages+=1
            rows+=1
        if key in witnesses:
            witness=witnesses[key];px,py=witness['paint_xy'];sx,sy=witness['skin_xy']
            assert regions[ident]['user_paint'][py,px] and regions[ident]['user_skin'][sy,sx] and code[py,px]==code[sy,sx]==4
            np.testing.assert_allclose([cd[py,px],cd[sy,sx]],[witness['paint_chroma_distance'],witness['skin_chroma_distance']],rtol=0,atol=1e-10)
            assert witness['incompatible_order'] and cd[py,px]<cd[sy,sx]
            shown=cv2.resize(image,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
            for label,xp,yp,color in [('paint-label',px,py,(0,0,255)),('skin-label',sx,sy,(0,255,0))]:
                cv2.circle(shown,(xp*3,yp*3),7,color,1);cv2.putText(shown,label,(max(1,xp*3-70),max(15,yp*3-9)),cv2.FONT_HERSHEY_SIMPLEX,.4,color,1)
            assert cv2.imwrite(str(out/'boards'/(key+'_witness.png')),shown)
        board_path=out/'boards'/(key+'.png')
        if board_path.exists():contacts.setdefault(ident,[]).append(cv2.imread(str(board_path)))
    with (out/'region_funnels.csv').open(newline='') as stream:assert len(list(csv.DictReader(stream)))==rows
    (out/'contacts').mkdir(exist_ok=True)
    for ident,boards in contacts.items():assert cv2.imwrite(str(out/'contacts'/(ident+'.png')),np.vstack(boards))
    assert all(digest(ROOT/p)==h for p,h in summary['input_sha256'].items())
    visual=dict(status='Eight contact boards and three chroma witness images inspected by Codex',
        original_labels_unchanged=True,adjudication_required=True,
        findings='Seed/reference overlaps confirmed as accounting. Chroma witnesses have mixed paint-edge/material ambiguities: clean/color skin-label at222,106 appears in painted cheek edge; dark skin-label97,103 is near visible nose color. Paint-label179,158/176,149 lies near blended skin/paint boundaries. These are label-order witnesses, not verified physical-material pairs.',
        inspected_frames=list(contacts),inspected_witnesses=list(witnesses),user_or_expert_adjudicated=False,
        decisions='Do not relabel automatically, use these points as training targets, or claim physical paint/skin inseparability. Preserve original failure metrics with reference-quality caveat.')
    (out/'visual_qa.json').write_text(json.dumps(visual,indent=2))
    links=['<!doctype html><meta charset="utf-8"><title>Material failure attribution</title><style>body{font:16px system-ui;max-width:1250px;margin:24px auto;background:#182028;color:#eee}img{max-width:100%;height:auto}a{color:#9cd9ff}</style><h1>Cached material failure attribution</h1><p>Red pixels show existing protected references inside seeds, A and C2. Five new region sets are provisional Codex labels; the original user labels remain unchanged. Rows: clean, dark, color. No new mask, inference, fitting or threshold selection.</p><p><b>Reference-quality flag:</b> visual inspection found mixed paint-boundary/material ambiguities at the scalar-order witness points. Saved label membership is verified; physical paint versus ordinary-skin membership is not adjudicated. These pairs do not prove physical-material inseparability.</p><p><a href="summary.json">Detailed accounting</a> · <a href="region_funnels.csv">Counts CSV</a> · <a href="verification.json">Replay</a> · <a href="visual_qa.json">Visual caveats</a></p>']
    for ident in contacts:links.append('<h2>'+ident+'</h2><img src="contacts/'+ident+'.png">')
    for key in witnesses:links.append('<h2>'+key+' frozen chroma-order witness</h2><img src="boards/'+key+'_witness.png">')
    (out/'review.html').write_text('\n'.join(links),encoding='utf-8')
    result=dict(status='pass',region_funnels_verified=rows,stage_region_counts_verified=stages,chroma_witnesses_verified=len(witnesses),
        unavailable_cases_retained=3,input_hashes_unchanged=True,summary_sha256=digest(out/'summary.json'),verifier_sha256=digest(Path(__file__)),
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in [out/'visual_qa.json']+list(out.glob('*.csv'))+list(out.glob('*.html'))+list((out/'boards').glob('*.png'))+list((out/'contacts').glob('*.png'))})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
