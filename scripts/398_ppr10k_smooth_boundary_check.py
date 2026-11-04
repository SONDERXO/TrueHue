"""One frozen smooth boundary experiment on saved parameters; no refitting."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
BASE=ROOT/get_config().OUTPUTS_ROOT
OUT=BASE/'ppr10k_detail_repair_v1'


def soft_boundary(raw):
    """Fixed .02 normalized-RGB softplus difference, evaluated symmetrically."""
    raw=np.asarray(raw,dtype=float)
    if not np.isfinite(raw).all():raise ValueError('Finite values required')
    reflected=np.minimum(raw,1-raw)
    low=.02*(np.logaddexp(0,reflected/.02)-np.logaddexp(0,(reflected-1)/.02))
    return np.where(raw<=.5,low,1-low)


def endpoint_detail(image,source,target,mask):
    codes=np.rint(image*255).astype(int);result=dict(endpoint_samples=int(((codes[mask]==0)|(codes[mask]==255)).sum()))
    collapsed=0
    for axis in [0,1]:
        first=[slice(None)]*3;second=[slice(None)]*3;first[axis]=slice(None,-1);second[axis]=slice(1,None);first,second=tuple(first),tuple(second)
        inside=(mask[first[:2]]&mask[second[:2]])[...,None]
        same=(codes[first]==codes[second])&((codes[first]==0)|(codes[first]==255))
        vary=(np.abs(source[first]-source[second])>=1/255)&(np.abs(target[first]-target[second])>=1/255-1e-12)
        collapsed+=int((inside&same&vary).sum())
    result['adjacent_source_and_target_variation_flattened_at_endpoint']=collapsed
    return result


def main():
    if (OUT/'results.json').exists():raise FileExistsError('Frozen results exist')
    protocol=json.loads((OUT/'protocol.json').read_text())
    spec=importlib.util.spec_from_file_location('metrics',ROOT/'scripts/392_ppr10k_operator_diagnostic.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    parents=[BASE/'ppr10k_contrast_diagnostic_v1',BASE/'ppr10k_new_group_comparison_v1'];rows=[];cards=[]
    for folder in parents:
        for name,sha in json.loads((folder/'sha256.json').read_text()).items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==sha
        for record in json.loads((folder/'results.json').read_text())['results']:
            frame=record['frame'];old=folder.name=='ppr10k_contrast_diagnostic_v1'
            z=np.load((BASE/'ppr10k_operator_diagnostic_v1' if old else folder)/f'{frame}_replay.npz');new=np.load(folder/f'{frame}_replay.npz')
            a,b,original=z['source'],z['target'],z['mask'];mask=original.copy()
            if frame in protocol['region_changes']:
                h,w=mask.shape;can=Image.new('1',(w,h));ImageDraw.Draw(can).polygon([tuple(p) for p in protocol['region_changes'][frame]],fill=1);mask=np.array(can,dtype=bool)
            p3=z['parameters'] if old else z['three_parameters'];p4=new['parameters'] if old else z['four_parameters']
            raw3=a**(1/p3[0])*np.array([p3[1],1,p3[2]])
            raw4=(.5+p4[3]*(a**(1/p4[0])-.5))*np.array([p4[1],1,p4[2]])
            variants=dict(three_hard=np.clip(raw3,0,1),four_hard=np.clip(raw4,0,1),four_soft=soft_boundary(raw4))
            assert all(np.isfinite(x).all() and x.min()>=0 and x.max()<=1 for x in variants.values())
            yy,xx=np.indices(mask.shape);check=mask&((xx//8+yy//8)%2==1)
            metrics={kind:dict(all_region=mod.metrics(image,b,mask),check_pattern=mod.metrics(image,b,check),detail=endpoint_detail(image,a,b,mask)) for kind,image in variants.items()}
            outputs={}
            for kind,image in variants.items():
                out=a.copy();out[mask]=image[mask];outputs[kind]=out;assert np.array_equal(out[~mask],a[~mask])
            row=dict(frame=frame,region_changed=frame in protocol['region_changes'],old_pixels=int(original.sum()),new_pixels=int(mask.sum()),metrics=metrics,
                raw_four_out_of_range_channels=int(((raw4[mask]<0)|(raw4[mask]>1)).sum()),
                warning='No refit: parameters originally fitted on old approximate support. Revised checkpattern is not clean heldout evidence.')
            rows.append(row)
            np.savez_compressed(OUT/f'{frame}_replay.npz',mask=mask,four_soft=outputs['four_soft'])
            yy,xx=np.where(mask);box=(max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(mask.shape[1],int(xx.max())+13),min(mask.shape[0],int(yy.max())+13))
            board=Image.new('RGB',(1750,410),'white');draw=ImageDraw.Draw(board)
            for i,(label,image) in enumerate([('Source',a),('Three hard',outputs['three_hard']),('Four hard',outputs['four_hard']),('Four smooth',outputs['four_soft']),('Expert A',b)]):
                crop=Image.fromarray(np.rint(image*255).astype('uint8')).crop(box);board.paste(ImageOps.contain(crop,(340,360),Image.Resampling.NEAREST),(i*350,35));draw.text((i*350+4,8),label,fill='black')
            board.save(OUT/f'comparison_{frame}.png')
            if row['region_changed']:
                outline=Image.fromarray(np.rint(a*255).astype('uint8'));ImageDraw.Draw(outline).line([tuple(p) for p in protocol['region_changes'][frame]]+[tuple(protocol['region_changes'][frame][0])],fill='lime',width=1);outline.save(OUT/f'revised_outline_{frame}.png')
            hard=metrics['four_hard'];soft=metrics['four_soft'];cards.append(f'<h2>{frame}{" — revised region" if row["region_changed"] else ""}</h2><p>All-region relative ΔE00 hard {hard["all_region"]["de00_mean"]:.3f} → smooth {soft["all_region"]["de00_mean"]:.3f}; RGB8 endpoint samples {hard["detail"]["endpoint_samples"]} → {soft["detail"]["endpoint_samples"]}.</p><img src="comparison_{frame}.png">')
    summary=dict(images=14,new_fits=0,new_inference=0,changed_regions=2,
        mean_allregion_de00={k:float(np.mean([r['metrics'][k]['all_region']['de00_mean'] for r in rows])) for k in variants},
        soft_improves_allregion_de00=sum(r['metrics']['four_soft']['all_region']['de00_mean']<r['metrics']['four_hard']['all_region']['de00_mean'] for r in rows),
        endpoint_samples={k:sum(r['metrics'][k]['detail']['endpoint_samples'] for r in rows) for k in variants},
        collapsed_adjacent_variation={k:sum(r['metrics'][k]['detail']['adjacent_source_and_target_variation_flattened_at_endpoint'] for r in rows) for k in variants})
    (OUT/'results.json').write_text(json.dumps(dict(summary=summary,results=rows),indent=2),encoding='utf8')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Fixed smooth boundary comparison</title><style>body{font:18px system-ui;max-width:1770px;margin:30px auto;background:#eee}img{width:100%}</style><h1>One smooth clipping candidate, no refitting</h1><p>Same saved parameters. Only904/1188approximate regions revised to remove identified shirt/background; old results preserved. All comparisons within each revised region use identical support. No automatic predictions, skin truth, independent validation or runtime adoption. Hard polygon edges remain diagnostic. Fewer endpoint values do not prove recovered texture or guaranteed detail preservation.</p>'+''.join(cards),encoding='utf8')
    print(json.dumps(summary,indent=2))
    for r in rows:print(r['frame'],r['old_pixels'],r['new_pixels'],r['metrics']['four_hard']['all_region']['de00_mean'],r['metrics']['four_soft']['all_region']['de00_mean'],r['metrics']['four_hard']['detail'],r['metrics']['four_soft']['detail'])


if __name__=='__main__':main()
