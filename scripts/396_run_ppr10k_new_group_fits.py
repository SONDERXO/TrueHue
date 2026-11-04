"""Run exactly two fixed operator fits on each retained new-group photograph."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image,ImageDraw,ImageOps
from scipy.optimize import least_squares
import tifffile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
from src.distortion_generation.generate_distortions import transform_rgb
OUT=ROOT/get_config().OUTPUTS_ROOT/'ppr10k_new_group_comparison_v1'


def load(number,name):
    spec=importlib.util.spec_from_file_location(name,next((ROOT/'scripts').glob(number+'_*py')))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    if (OUT/'results.json').exists(): raise FileExistsError('Completed results exist')
    plan=json.loads((OUT/'frozen_sample.json').read_text())
    regions=json.loads((OUT/'source_regions.json').read_text())
    assert set(regions)==set(plan['frames'])
    metric=load('392','metric').metrics;four=load('394','contrast').transform
    audit=json.loads((OUT/'image_audit.json').read_text())
    for r in audit:assert hashlib.sha256((OUT/r['file']).read_bytes()).hexdigest()==r['sha256']
    protocol=dict(plan_sha256=hashlib.sha256((OUT/'frozen_sample.json').read_bytes()).hexdigest(),
        regions_sha256=hashlib.sha256((OUT/'source_regions.json').read_bytes()).hexdigest(),
        three='shared transform_rgb: gain*x**(1/gamma);bounds[.25,4]each',
        four='script394 transform: contrast about.5 between gamma/gains;bounds gamma/red/blue[.25,4],contrast[.5,2]',
        solver='One identity start each; squared-sRGB fit residual,xtol/ftol/gtol1e-12,max_nfev2000',
        split='Same8px checker parity0 fit,parity1check',new_models=False,mst_fits=0,tree_fits=0)
    (OUT/'fit_protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    rows=[];cards=[]
    for frame in plan['frames']:
        region=regions[frame]
        if region.get('failure'):
            rows.append(dict(frame=frame,status='source_face_unusable',reason=region['failure']))
            cards.append(f'<h2>{frame}: retained failure</h2><img src="source_{frame}.png">')
            continue
        a=tifffile.imread(OUT/'originals/source'/f'{frame}.tif').astype(float)/65535
        b=tifffile.imread(OUT/'originals/target_a'/f'{frame}.tif').astype(float)/255
        assert a.shape==b.shape
        h,w=a.shape[:2];poly=region['polygon'];canvas=Image.new('1',(w,h));ImageDraw.Draw(canvas).polygon([tuple(p) for p in poly],fill=1)
        mask=np.array(canvas,dtype=bool);yy,xx=np.indices((h,w));fm=mask&((xx//8+yy//8)%2==0);cm=mask&~fm
        assert fm.any() and cm.any()
        x=a[fm].reshape(-1,1,3);y=b[fm].reshape(-1,1,3)
        outputs={};parameters={};solvers={};clip={};metrics={};fit_mse={}
        for name,op,low,high in [('three',transform_rgb,[.25]*3,[4.]*3),('four',four,[.25,.25,.25,.5],[4.,4.,4.,2.])]:
            fit=least_squares(lambda q:(op(x,*q)-y).ravel(),[1.]*len(low),bounds=(low,high),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=2000)
            solvers[name]=dict(success=bool(fit.success),nfev=fit.nfev,active_bounds=fit.active_mask.tolist(),message=fit.message)
            raw=op(a,*fit.x,clip=False);v=np.clip(raw,0,1);out=a.copy();out[mask]=v[mask]
            outputs[name]=out;parameters[name]=fit.x.tolist()
            metrics[name]={k:metric(v,b,m) for k,m in [('fit',fm),('check',cm),('all_face',mask)]}
            clip[name]=dict(samples=int(((raw[mask]<0)|(raw[mask]>1)).sum()),total=int(mask.sum()*3))
            fit_mse[name]=float(np.mean((v[fm]-b[fm])**2))
            Image.fromarray(np.rint(out*255).astype('uint8')).save(OUT/f'{name}_{frame}.png')
        np.savez_compressed(OUT/f'{frame}_replay.npz',source=a,target=b,mask=mask,fit_mask=fm,check_mask=cm,
            three_parameters=parameters['three'],four_parameters=parameters['four'],three_output=outputs['three'],four_output=outputs['four'])
        row=dict(frame=frame,status='completed' if all(s['success'] for s in solvers.values()) else 'solver_failure_retained',
            source_observation=region['note'],pixels=int(mask.sum()),fit_pixels=int(fm.sum()),check_pixels=int(cm.sum()),
            parameters=parameters,solvers=solvers,metrics=metrics,clipping=clip,fit_mse=fit_mse)
        rows.append(row)
        p=np.array(poly);box=(max(0,int(p[:,0].min())-12),max(0,int(p[:,1].min())-12),min(w,int(p[:,0].max())+13),min(h,int(p[:,1].max())+13))
        board=Image.new('RGB',(1440,430),'white');draw=ImageDraw.Draw(board)
        for i,(label,image) in enumerate([('Source',a),('Three controls',outputs['three']),('Four controls',outputs['four']),('Expert A',b)]):
            crop=Image.fromarray(np.rint(image*255).astype('uint8')).crop(box);board.paste(ImageOps.contain(crop,(350,380),Image.Resampling.NEAREST),(i*360,35));draw.text((i*360+5,8),label,fill='black')
        board.save(OUT/f'comparison_{frame}.png')
        outline=Image.fromarray(np.rint(a*255).astype('uint8'));ImageDraw.Draw(outline).line([tuple(p) for p in poly]+[tuple(poly[0])],fill='lime',width=1);outline.save(OUT/f'outline_{frame}.png')
        m=metrics;cards.append(f'<h2>{frame}</h2><p>{region["note"]}</p><p>Check mean relative ΔE00 {m["three"]["check"]["de00_mean"]:.3f} → {m["four"]["check"]["de00_mean"]:.3f}. Clipped face channel samples {clip["three"]["samples"]} → {clip["four"]["samples"]}.</p><img src="comparison_{frame}.png"><details><summary>Source face region</summary><img style="max-width:540px" src="outline_{frame}.png"></details>')
        print(frame,'DE',m['three']['check']['de00_mean'],m['four']['check']['de00_mean'],flush=True)
    successful=[r for r in rows if r['status']=='completed']
    summary=dict(attempts=len(rows),completed=len(successful),failures=len(rows)-len(successful),
        improved_check_de00=sum(r['metrics']['four']['check']['de00_mean']<r['metrics']['three']['check']['de00_mean'] for r in successful),
        mean_check_de00={k:float(np.mean([r['metrics'][k]['check']['de00_mean'] for r in successful])) for k in ['three','four']},
        increased_clipping=sum(r['clipping']['four']['samples']>r['clipping']['three']['samples'] for r in successful),
        oracle_fit_attempts=sum(2 for r in rows if 'solvers' in r),tree_fits=0,mst_fits=0,adopted=False)
    (OUT/'results.json').write_text(json.dumps(dict(summary=summary,results=rows),indent=2),encoding='utf8')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>New PPR10K groups: frozen comparison</title><style>body{font:18px system-ui;max-width:1460px;margin:30px auto;background:#eee}img{max-width:100%}</style><h1>Eight new groups: three vs four controls</h1><p>Each expert target was used to fit each image: these are not automatic predictions or new-person validation. Source-only approximate face regions include features/makeup, exclude neck; sharp boundaries are diagnostic only. Same-photo block checks; small faces enlarged without smoothing. All selected attempts retained. Group IDs do not establish different people or MST coverage.</p>'+''.join(cards),encoding='utf8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
