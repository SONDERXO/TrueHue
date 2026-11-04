"""Frozen six-photo oracle operator diagnostic; no predictive model training."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageCms
from scipy.optimize import least_squares
from skimage.color import rgb2lab, deltaE_ciede2000
import tifffile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utilities.config import get_config
from src.distortion_generation.generate_distortions import transform_rgb

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / get_config().OUTPUTS_ROOT
SOURCE = BASE / 'ppr10k_inspection_v1'
OUT = BASE / 'ppr10k_operator_diagnostic_v1'
POLYGONS = {
    '1398_0': [[340,106],[357,97],[380,101],[396,116],[391,148],[380,170],[363,180],[346,169],[336,146],[335,124]],
    '1398_1': [[268,91],[281,80],[302,86],[320,103],[334,131],[328,147],[309,161],[293,155],[277,137],[269,116]],
    '1398_2': [[317,91],[336,80],[357,86],[374,101],[375,128],[365,150],[348,164],[330,158],[316,140],[312,117]],
    '1487_0': [[168,134],[177,129],[187,131],[192,141],[189,151],[181,160],[173,158],[166,150],[165,142]],
    '1487_1': [[154,267],[164,262],[177,263],[188,272],[186,286],[179,297],[168,302],[156,295],[151,281]],
    '1487_2': [[367,73],[378,67],[391,73],[402,85],[411,97],[408,106],[398,114],[388,109],[378,98],[370,87]],
}


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    OUT.mkdir(exist_ok=True)
    path = OUT / 'protocol.json'
    if path.exists(): raise FileExistsError(path)
    previous = json.loads((SOURCE / 'image_audit.json').read_text())
    for row in previous: assert digest(SOURCE / row['file']) == row['sha256']
    protocol = dict(frames=list(POLYGONS), polygons=POLYGONS,
        selection='Woman in group1398; single prominent face in group1487; source-only assistant approximate face polygons, not skin truth.',
        support='Whole polygon including eyes/lips/makeup, excluding neck. Diagnostic approximation only; not adopted production face+neck support.',
        fit='8x8 checkerboard blocks parity0 within polygon; parity1 reserved spatial check; all pixels in each block retained.',
        operator='src.distortion_generation.generate_distortions.transform_rgb; clipped gain*x**(1/gamma); fixed green gain1',
        bounds=[[0.25,0.25,0.25],[4.,4.,4.]], initial=[1.,1.,1.],
        objective='Unweighted encoded-sRGB squared RGB residuals on fit blocks, originals float64 source/65535 and target/255.',
        solver='scipy least_squares single identity start; xtol/ftol/gtol1e-12; max_nfev2000; no model/feature/threshold sweep',
        metrics='RGB MAE in 8bit-equivalent units and relative CIEDE2000 mean/median/p95; source vs target and fitted vs target, fit/check/all regions.',
        criterion='Descriptive approximation only; no validated acceptability threshold, clinical/skin accuracy or cohort admission.',
        rendering='Three equal enlarged face crops source/oracle/target; full-frame polygon-only oracle image with hard diagnostic boundary. No production-mask/blending validation.',
        registration='Same publisher frame/stem/dimensions; visual correspondence only; no warp/search or certified pixelwise registration. Residual may include misregistration.',
        limits='Target-aware per-photo oracle, not model predictions. Six related, development-exposed publisher-validation photos; block checks not independent generalization.',
        input_hashes={r['file']:r['sha256'] for r in previous},
        operator_sha256=digest(ROOT/'src/distortion_generation/generate_distortions.py'),
        no_replacements=True, tree_training=False, mst_calibration=False, runtime_change=False)
    path.write_text(json.dumps(protocol,indent=2),encoding='utf8')
    print('Protocol frozen before fitting:',digest(path))
    # Source-only outline boards are available to audit approximate support.
    for frame, polygon in POLYGONS.items():
        im=Image.open(SOURCE/f'source_{frame}.png').copy()
        ImageDraw.Draw(im).line([tuple(p) for p in polygon]+[tuple(polygon[0])],fill='lime',width=1)
        im.save(OUT/f'outline_{frame}.png')


def metrics(a,b,mask):
    rgb=float(np.abs(a-b)[mask].mean()*255)
    de=deltaE_ciede2000(rgb2lab(a),rgb2lab(b))[mask]
    return dict(rgb_mae_255=rgb,de00_mean=float(de.mean()),de00_median=float(np.median(de)),de00_p95=float(np.percentile(de,95)))


def run():
    protocol=json.loads((OUT/'protocol.json').read_text())
    if (OUT/'results.json').exists(): raise FileExistsError('Results already frozen')
    for name,sha in protocol['input_hashes'].items(): assert digest(SOURCE/name)==sha
    assert digest(ROOT/'src/distortion_generation/generate_distortions.py')==protocol['operator_sha256']
    rows=[]
    for frame in protocol['frames']:
        a=tifffile.imread(SOURCE/'originals/source'/f'{frame}.tif').astype(float)/65535
        b=tifffile.imread(SOURCE/'originals/target_a'/f'{frame}.tif').astype(float)/255
        assert a.shape==b.shape
        h,w=a.shape[:2]; region=Image.new('1',(w,h));polygon=protocol['polygons'][frame]
        ImageDraw.Draw(region).polygon([tuple(p) for p in polygon],fill=1)
        mask=np.array(region,dtype=bool); yy,xx=np.indices((h,w));fitmask=mask & ((xx//8+yy//8)%2==0);check=mask & ~fitmask
        x=a[fitmask].reshape(-1,1,3);y=b[fitmask].reshape(-1,1,3)
        fit=least_squares(lambda p:(transform_rgb(x,*p)-y).ravel(), protocol['initial'],
            bounds=protocol['bounds'],xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=2000)
        transformed=transform_rgb(a,*fit.x)
        assert fit.success and np.isfinite(fit.x).all()
        identity=metrics(a,b,fitmask);fitted=metrics(transformed,b,fitmask)
        assert fitted['rgb_mae_255']>=0
        assert np.mean((transformed[fitmask]-b[fitmask])**2)<=np.mean((a[fitmask]-b[fitmask])**2)+1e-12
        out=a.copy();out[mask]=transformed[mask]
        assert np.array_equal(out[~mask],a[~mask])
        np.savez_compressed(OUT/f'{frame}_replay.npz',source=a,target=b,mask=mask,fit_mask=fitmask,check_mask=check,parameters=fit.x,output=out)
        replay=transform_rgb(a,*fit.x);assert np.array_equal(replay,transformed)
        image=Image.fromarray(np.rint(out*255).astype('uint8'));image.save(OUT/f'oracle_{frame}.png')
        px=np.array(polygon);left=max(0,int(px[:,0].min())-12);right=min(w,int(px[:,0].max())+13);top=max(0,int(px[:,1].min())-12);bottom=min(h,int(px[:,1].max())+13)
        board=Image.new('RGB',(1080,430),'white');draw=ImageDraw.Draw(board)
        for i,(label,arr) in enumerate([('Source',a),('Oracle: target-aware fit',out),('Expert A',b)]):
            crop=Image.fromarray(np.rint(arr*255).astype('uint8')).crop((left,top,right,bottom))
            crop=ImageOps.contain(crop,(350,380),Image.Resampling.NEAREST)
            board.paste(crop,(i*360,35));draw.text((i*360+5,8),label,fill='black')
        board.save(OUT/f'comparison_{frame}.png')
        row=dict(frame=frame,parameters=dict(zip(['gamma','red_gain','blue_gain'],map(float,fit.x))),
            pixels=int(mask.sum()),fit_pixels=int(fitmask.sum()),check_pixels=int(check.sum()),
            solver=dict(success=bool(fit.success),nfev=fit.nfev,optimality=float(fit.optimality),active_bounds=fit.active_mask.tolist()),
            metrics={name:dict(source=metrics(a,b,m),oracle=metrics(transformed,b,m)) for name,m in [('fit',fitmask),('check',check),('all_face',mask)]},
            replay_exact=True,outside_polygon_preserved=True)
        rows.append(row)
    report=dict(protocol_sha256=digest(OUT/'protocol.json'),results=rows,oracle_fits=6,calibration_fits=0,tree_fits=0,training_admitted=False)
    (OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    cards=''.join(f'<h2>{r["frame"]}</h2><p>gamma {r["parameters"]["gamma"]:.3f}; red {r["parameters"]["red_gain"]:.3f}; blue {r["parameters"]["blue_gain"]:.3f}. Check-block mean relative ΔE00: {r["metrics"]["check"]["source"]["de00_mean"]:.2f} → {r["metrics"]["check"]["oracle"]["de00_mean"]:.2f}.</p><img src="comparison_{r["frame"]}.png"><details><summary>Source-only approximate outline</summary><img class="small" src="outline_{r["frame"]}.png"></details>' for r in rows)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>PPR10K operator diagnostic</title><style>body{font:18px system-ui;max-width:1100px;margin:30px auto;background:#eee}img{max-width:100%}.small{max-width:540px}</style><h1>Can three controls approximate the expert faces?</h1><p>Six fixed target-aware fits. These are oracle approximations, not automatic predictions. Approximate face outlines include eyes/lips/makeup, exclude neck; no skin measurement or production rendering evaluation. Enlarged crops use nearest-neighbour display; small faces have limited detail. Source and target registration is not certified. Same-photo block checks do not measure new-photo performance.</p>'+cards,encoding='utf8')
    print(json.dumps([dict(frame=r['frame'],parameters=r['parameters'],check=r['metrics']['check']) for r in rows],indent=2))


if __name__=='__main__': {'freeze':freeze,'run':run}[sys.argv[1]]()
