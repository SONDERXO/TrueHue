"""Saved-output highlight/shadow audit; no fits, inference or mask changes."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
BASE=ROOT/get_config().OUTPUTS_ROOT
OUT=BASE/'ppr10k_clipping_detail_check_v1'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def analyse(source,target,mask,raw):
    """Count actual clipping separately from code-endpoint/detail diagnostics."""
    low=(raw<0)&mask[...,None];high=(raw>1)&mask[...,None];clipped=low|high
    output=np.clip(raw,0,1)
    # Existing targets are RGB8. Two code values from an endpoint is descriptive,
    # not an acceptability threshold or proof of unwanted clipping.
    target_codes=np.rint(target*255).astype(int)
    disagreement=(low&(target_codes>=2))|(high&(target_codes<=253))
    new_source=((low&(source>0))|(high&(source<1)))
    pairs={}
    for axis,label in [(0,'vertical'),(1,'horizontal')]:
        first=[slice(None)]*3;second=[slice(None)]*3
        first[axis]=slice(None,-1);second[axis]=slice(1,None)
        first,second=tuple(first),tuple(second)
        valid=(mask[tuple(first[:2])]&mask[tuple(second[:2])])[...,None]
        saturated_same=((low[first]&low[second])|(high[first]&high[second]))&valid
        srcdiff=np.abs(source[first]-source[second])>=1/255
        tgtdiff=np.abs(target[first]-target[second])>=1/255-1e-12
        pairs[label]=dict(same_endpoint_pairs=int(saturated_same.sum()),
            source_variation_collapsed=int((saturated_same&srcdiff).sum()),
            target_variation_not_reproduced=int((saturated_same&tgtdiff).sum()),
            source_and_target_variation=int((saturated_same&srcdiff&tgtdiff).sum()))
    return dict(low_channel_samples=int(low.sum()),high_channel_samples=int(high.sum()),
        clipped_channel_samples=int(clipped.sum()),clipped_pixels=int(clipped.any(axis=2).sum()),
        region_pixels=int(mask.sum()),region_channel_samples=int(mask.sum()*3),
        low_by_RGB=low.sum(axis=(0,1)).tolist(),high_by_RGB=high.sum(axis=(0,1)).tolist(),
        newly_endpoint_from_nonendpoint_source=int(new_source.sum()),
        target_two_codes_away_samples=int(disagreement.sum()),
        all_RGB_black_pixels=int((low.all(axis=2)&mask).sum()),
        all_RGB_white_pixels=int((high.all(axis=2)&mask).sum()),
        adjacent_pairs=pairs),low,high,output


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'results.json').exists(): raise FileExistsError('Audit already frozen')
    parents=[BASE/'ppr10k_contrast_diagnostic_v1',BASE/'ppr10k_new_group_comparison_v1']
    manifest={}
    for folder in parents:
        for name,value in json.loads((folder/'sha256.json').read_text()).items():
            assert sha(folder/name)==value
        manifest[folder.name]=sha(folder/'results.json')
    protocol=dict(parents=manifest,scope='All14saved comparisons; focus six new photos with increased clipping; no new fits/photos/inference/masks.',
        clipping='Raw<0 or>1 before finalclip, within original saved face polygons; low/high and RGB distinguished.',
        target_comparison='Clipped samples whose target is at least2RGB8codes away from clipped endpoint; descriptive,not pass/fail.',
        detail='Horizontal/vertical same-channel adjacent pairs both raw-clipped to same endpoint: source/target code differences>=1. Counts overlap, not independent features.',
        limitations='Approximate mixed-feature facial polygons, makeup/hair/glasses and uncertified pixel registration; endpoint/pair counts not groundtruth skin detail. Small images cannot prove fine texture preservation.',
        visual='All14same crops source/three/four/expert plus clipping overlay; blue shadow,magenta highlight,yellow both across channels. No new user review.',
        conclusion='No automatic adoption, tuning or training follows.')
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    rows=[];cards=[]
    for folder in parents:
        records=json.loads((folder/'results.json').read_text())['results']
        for record in records:
            frame=record['frame'];old=folder.name=='ppr10k_contrast_diagnostic_v1'
            z=np.load((BASE/'ppr10k_operator_diagnostic_v1' if old else folder)/f'{frame}_replay.npz')
            fourz=np.load(folder/f'{frame}_replay.npz')
            source,target,mask=z['source'],z['target'],z['mask']
            threep=z['parameters'] if old else z['three_parameters']
            fourp=fourz['parameters'] if old else z['four_parameters']
            raws=dict(three=source**(1/threep[0])*np.array([threep[1],1,threep[2]]),
                four=(.5+fourp[3]*(source**(1/fourp[0])-.5))*np.array([fourp[1],1,fourp[2]]))
            measured={};images={};lows={};highs={}
            for kind,raw in raws.items():
                measured[kind],lows[kind],highs[kind],full=analyse(source,target,mask,raw)
                image=source.copy();image[mask]=full[mask];images[kind]=image
                saved=(z['output'] if kind=='three' else fourz['output']) if old else z[kind+'_output']
                assert np.array_equal(saved,image)
                expected=record['clipping']['all_face'][kind] if old else record['clipping'][kind]['samples']
                assert measured[kind]['clipped_channel_samples']==expected
            overlay=np.rint(images['four']*255).astype('uint8')
            lo=lows['four'].any(axis=2);hi=highs['four'].any(axis=2)
            overlay[lo]=[0,100,255];overlay[hi]=[255,0,180];overlay[lo&hi]=[255,220,0]
            yy,xx=np.where(mask);h,w=mask.shape
            box=(max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(w,int(xx.max())+13),min(h,int(yy.max())+13))
            board=Image.new('RGB',(1750,410),'white');draw=ImageDraw.Draw(board)
            for i,(label,image) in enumerate([('Source',source),('Three controls',images['three']),('Four controls',images['four']),('Expert A',target),('Four: clipped locations',overlay)]):
                data=image if image.dtype==np.uint8 else np.rint(image*255).astype('uint8')
                crop=ImageOps.contain(Image.fromarray(data).crop(box),(340,360),Image.Resampling.NEAREST)
                board.paste(crop,(i*350,35));draw.text((i*350+5,8),label,fill='black')
            board.save(OUT/f'detail_{frame}.png')
            focus=folder.name.endswith('new_group_comparison_v1') and measured['four']['clipped_channel_samples']>measured['three']['clipped_channel_samples']
            rows.append(dict(frame=frame,parent=folder.name,focus_new_increased=focus,measures=measured))
            m=measured['four'];cards.append(f'<h2>{frame}{" — focus" if focus else ""}</h2><p>Four-control raw clipping: {m["low_channel_samples"]} low, {m["high_channel_samples"]} high channel samples; {m["target_two_codes_away_samples"]} clipped samples have targets ≥2codes away from endpoint.</p><img src="detail_{frame}.png">')
    (OUT/'results.json').write_text(json.dumps(dict(protocol_sha256=sha(OUT/'protocol.json'),results=rows,new_fits=0),indent=2),encoding='utf8')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Saved clipping and detail check</title><style>body{font:18px system-ui;max-width:1770px;margin:30px auto;background:#eee}img{width:100%}</style><h1>Highlight and shadow detail: saved outputs</h1><p>Blue: raw shadow clipping; magenta: raw highlight clipping; yellow: both in different channels. These markings do not mean every RGB channel is black/white. All14saved comparisons retained; six new increased-clipping cases flagged. Approximate face-only masks, hard cutoffs, low resolution, makeup/features and uncertain pixelwise correspondence limit interpretation. No new fits or automatic predictions.</p>'+''.join(cards),encoding='utf8')
    for r in rows:
        a,b=r['measures']['three'],r['measures']['four']
        print(r['frame'],'FOCUS' if r['focus_new_increased'] else '', 'low/high',b['low_channel_samples'],b['high_channel_samples'],'RGB',b['low_by_RGB'],b['high_by_RGB'],'target-away',b['target_two_codes_away_samples'],'collapsed-source',sum(v['source_variation_collapsed'] for v in b['adjacent_pairs'].values()),'target-detail',sum(v['target_variation_not_reproduced'] for v in b['adjacent_pairs'].values()))


if __name__=='__main__': main()
