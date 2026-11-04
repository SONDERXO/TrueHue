"""One authorised fourth-control comparison; saved baseline remains immutable."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy.optimize import least_squares
from skimage.color import rgb2lab

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.utilities.config import get_config

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/get_config().OUTPUTS_ROOT
OLD=BASE/'ppr10k_operator_diagnostic_v1'
OUT=BASE/'ppr10k_contrast_diagnostic_v1'


def transform(image,gamma,red,blue,contrast,*,clip=True):
    image=np.asarray(image,dtype=float)
    parameters=np.array([gamma,red,blue,contrast],dtype=float)
    if not np.isfinite(parameters).all() or (parameters<=0).any():
        raise ValueError('Finite positive parameters required')
    if not np.isfinite(image).all() or image.min()<0 or image.max()>1:
        raise ValueError('Finite normalized image required')
    raw=(.5+contrast*(image**(1/gamma)-.5))*np.array([red,1.,blue])
    return np.clip(raw,0,1) if clip else raw


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    OUT.mkdir(exist_ok=True)
    if (OUT/'protocol.json').exists(): raise FileExistsError('Protocol frozen')
    manifest=json.loads((OLD/'sha256.json').read_text())
    for name,sha in manifest.items(): assert digest(OLD/name)==sha
    protocol=dict(authorisation='User: okay lets do those; single proposed contrast-control comparison.',
        formula='clip((0.5+contrast*(source**(1/gamma)-0.5))*[red,1,blue],0,1)',
        parameters=['gamma','red_gain','blue_gain','contrast'],bounds=[[.25,.25,.25,.5],[4.,4.,4.,2.]],
        initial=[1.,1.,1.,1.],solver='least_squares; single identity start; squared encoded-sRGB fit-block residual; xtol/ftol/gtol1e-12;max_nfev2000',
        frames=[r['frame'] for r in json.loads((OLD/'results.json').read_text())['results']],
        baseline_manifest=manifest,baseline_protocol_sha256=digest(OLD/'protocol.json'),
        support='Exact saved float sources/targets, selected-face polygons and fit/check masks. No neck, new masks, registration, inference or replacements.',
        metrics='Same RGB MAE,relativeDE00 mean/median/p95 on fit/check/all; signed Lab intensity-quartile residuals; clipping.',
        decision='Descriptive six-photo comparison, no validated success threshold; preserve regressions. No sweep,tree/MST fit,adoption or runtime change.',
        limitations='Target-aware fits on related development-exposed photos; approximate masks contain eyes/lips/hair/makeup. Same-photo check blocks not independent validation.',
        script_sha256=digest(Path(__file__)))
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    print('Frozen protocol',digest(OUT/'protocol.json'))


def residuals(image,target,source,check):
    delta=(rgb2lab(image)-rgb2lab(target))[check]
    g=source[...,1][check];cuts=np.quantile(g,[0,.25,.5,.75,1]);bins=[]
    for i in range(4):
        selected=(g>=cuts[i]) & ((g<cuts[i+1]) if i<3 else (g<=cuts[i+1]))
        bins.append(dict(quartile=i+1,pixels=int(selected.sum()),mean_signed_Lab=delta[selected].mean(axis=0).tolist()))
    return dict(mean_signed_Lab=delta.mean(axis=0).tolist(),quartiles=bins)


def run():
    if (OUT/'results.json').exists(): raise FileExistsError('Results frozen')
    protocol=json.loads((OUT/'protocol.json').read_text())
    assert digest(Path(__file__))==protocol['script_sha256']
    for name,sha in protocol['baseline_manifest'].items(): assert digest(OLD/name)==sha
    spec=importlib.util.spec_from_file_location('baseline',ROOT/'scripts/392_ppr10k_operator_diagnostic.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    oldreport=json.loads((OLD/'results.json').read_text());rows=[]
    polygons=json.loads((OLD/'protocol.json').read_text())['polygons']
    for frame in protocol['frames']:
        z=np.load(OLD/f'{frame}_replay.npz');a,b,mask,fitmask,check=z['source'],z['target'],z['mask'],z['fit_mask'],z['check_mask']
        x=a[fitmask].reshape(-1,1,3);y=b[fitmask].reshape(-1,1,3)
        fit=least_squares(lambda p:(transform(x,*p)-y).ravel(),protocol['initial'],bounds=protocol['bounds'],xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=2000)
        if not fit.success: raise RuntimeError(f'Keep failed attempt {frame}: {fit.message}')
        raw=transform(a,*fit.x,clip=False);v=np.clip(raw,0,1);out=a.copy();out[mask]=v[mask]
        np.savez_compressed(OUT/f'{frame}_replay.npz',parameters=fit.x,output=out)
        oldparameters=z['parameters'];oldraw=a**(1/oldparameters[0])*np.array([oldparameters[1],1,oldparameters[2]])
        oldv=np.clip(oldraw,0,1)
        assert np.array_equal(z['output'][mask],oldv[mask]) and np.array_equal(out[~mask],a[~mask])
        record=dict(frame=frame,parameters=dict(zip(protocol['parameters'],map(float,fit.x))),
            solver=dict(success=bool(fit.success),nfev=fit.nfev,active_bounds=fit.active_mask.tolist(),optimality=float(fit.optimality)),
            metrics={name:dict(three=module.metrics(oldv,b,m),four=module.metrics(v,b,m)) for name,m in [('fit',fitmask),('check',check),('all_face',mask)]},
            residuals=dict(three=residuals(oldv,b,a,check),four=residuals(v,b,a,check)),
            clipping={name:dict(three=int(((oldraw[m]<0)|(oldraw[m]>1)).sum()),four=int(((raw[m]<0)|(raw[m]>1)).sum()),channel_samples=int(m.sum()*3)) for name,m in [('check',check),('all_face',mask)]})
        record['fit_mse']={k:float(np.mean((image[fitmask]-b[fitmask])**2)) for k,image in [('three',oldv),('four',v)]}
        rows.append(record)
        Image.fromarray(np.rint(out*255).astype('uint8')).save(OUT/f'oracle_{frame}.png')
        h,w=a.shape[:2];poly=np.array(polygons[frame]);box=(max(0,int(poly[:,0].min())-12),max(0,int(poly[:,1].min())-12),min(w,int(poly[:,0].max())+13),min(h,int(poly[:,1].max())+13))
        board=Image.new('RGB',(1440,430),'white');draw=ImageDraw.Draw(board)
        for i,(label,image) in enumerate([('Source',a),('Three controls',z['output']),('Four: added contrast',out),('Expert A',b)]):
            crop=Image.fromarray(np.rint(image*255).astype('uint8')).crop(box)
            board.paste(ImageOps.contain(crop,(350,380),Image.Resampling.NEAREST),(i*360,35));draw.text((i*360+5,8),label,fill='black')
        board.save(OUT/f'comparison_{frame}.png')
    summary=dict(three_mean_check_de00=float(np.mean([r['metrics']['check']['three']['de00_mean'] for r in rows])),
        four_mean_check_de00=float(np.mean([r['metrics']['check']['four']['de00_mean'] for r in rows])),
        improved_check_de00=sum(r['metrics']['check']['four']['de00_mean']<r['metrics']['check']['three']['de00_mean'] for r in rows),
        oracle_fits=6,tree_fits=0,mst_fits=0,runtime_adopted=False)
    (OUT/'results.json').write_text(json.dumps(dict(protocol_sha256=digest(OUT/'protocol.json'),summary=summary,results=rows),indent=2),encoding='utf8')
    cards=''.join(f'<h2>{r["frame"]}</h2><p>Check-block mean relative ΔE00 {r["metrics"]["check"]["three"]["de00_mean"]:.2f} → {r["metrics"]["check"]["four"]["de00_mean"]:.2f}; contrast {r["parameters"]["contrast"]:.3f}. Clipped face channel samples {r["clipping"]["all_face"]["three"]} → {r["clipping"]["all_face"]["four"]}.</p><img src="comparison_{r["frame"]}.png">' for r in rows)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>One contrast-control comparison</title><style>body{font:18px system-ui;max-width:1460px;margin:30px auto;background:#eee}img{width:100%}</style><h1>Does adding contrast improve these six approximations?</h1><p>Source / saved three-control fit / four-control candidate / expert A. These use each expert target to fit adjustments: not automatic predictions. Same six development-exposed photographs, same approximate face-only polygons and checkerboard split. Small faces enlarged without smoothing. Sharp polygon edges and unchanged neck/background are diagnostic limitations, not adopted production rendering. No reliable-MST, skin-truth, new-photo validation or method-adoption claim.</p>'+cards,encoding='utf8')
    print(json.dumps(summary,indent=2))
    for r in rows: print(r['frame'],r['parameters'],'bounds',r['solver']['active_bounds'],'clip',r['clipping']['all_face'])


if __name__=='__main__': {'freeze':freeze,'run':run}[sys.argv[1]]()
