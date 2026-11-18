"""Independent input-feature arithmetic; no production feature extractor or learned fitting."""
import math
import struct
import cv2
import numpy as np


def f32(v):return struct.unpack('!f',struct.pack('!f',float(v)))[0]


def features(rgb,mask,mapping,names):
    assert rgb.shape==(256,256,3) and rgb.dtype==np.uint8
    selected=mask>0;assert int(selected.sum())>=1000
    lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB).astype(np.float32)
    converted=np.stack([lab[:,:,0]*(100/255),lab[:,:,1]-128,lab[:,:,2]-128],axis=2)
    values=converted[selected]
    means=[round(float(np.mean(values[:,c])),4) for c in range(3)]
    assert abs(means[2])>=1e-6
    ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
    out=dict(zip(['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees'],means+[ita]))
    xs,ys=mapping['ita_knots'],mapping['mst_score_knots']
    if ita<=xs[0]:mst=ys[0]
    elif ita>=xs[-1]:mst=ys[-1]
    else:
        i=next(i for i in range(len(xs)-1) if xs[i]<=ita<=xs[i+1])
        mst=ys[i]+(ys[i+1]-ys[i])*(ita-xs[i])/(xs[i+1]-xs[i])
    out['input_mst_score']=mst
    g=np.percentile(rgb[:,:,1][selected],[10,50,90],method='linear')
    out.update(zip(['input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast'],
                   [float(v) for v in g]+[math.log((g[2]+1)/(g[0]+1))]))
    channel_means=rgb.reshape(-1,3).mean(axis=0)
    out.update(scene_log_r_over_g=math.log((channel_means[0]+1)/(channel_means[1]+1)),
               scene_log_b_over_g=math.log((channel_means[2]+1)/(channel_means[1]+1)))
    l=np.percentile(lab[:,:,0]*(100/255),[10,50,90],method='linear')
    out.update(zip(['scene_l_p10','scene_l_p50','scene_l_p90'],map(float,l)))
    out['scene_any_zero_fraction']=int(np.any(rgb==0,axis=2).sum())/(256*256)
    out['scene_any_full_fraction']=int(np.any(rgb==255,axis=2).sum())/(256*256)
    for c,channel in enumerate(['red','green','blue']):
        observed={int(v) for v in rgb[:,:,c].flat};lo,hi=min(observed),max(observed)
        for band,left,right in [('low',0,127),('high',128,255)]:
            a,b=max(lo,left),min(hi,right);eligible=max(0,b-a+1)
            out[f'scene_{channel}_{band}_internal_gap_fraction']=sum(code not in observed for code in range(a,b+1))/eligible if eligible else 0.
    histogram=[0.]*256;positive=clipped=0
    for row in rgb.tolist():
        for r,g,b in row:
            if min(r,g,b)==0:continue
            positive+=1;u,v=math.log(r/g),math.log(b/g)
            clipped+=abs(u)>2 or abs(v)>2
            a,b=(min(2.,max(-2.,u))+2)*3.75,(min(2.,max(-2.,v))+2)*3.75
            i,j=math.floor(a),math.floor(b);wa,wb=a-i,b-j
            for ix,w1 in [(i,1-wa),(min(i+1,15),wa)]:
                for iy,w2 in [(j,1-wb),(min(j+1,15),wb)]:histogram[ix*16+iy]+=w1*w2
    out['joint_colour_available']=1. if positive else 0.
    out['joint_colour_positive_fraction']=positive/(256*256)
    out['joint_colour_clipped_fraction']=clipped/positive if positive else 0.
    for i in range(16):
        for j in range(16):out[f'joint_colour_u{i:02}_v{j:02}']=histogram[i*16+j]/positive if positive else 0.
    assert len(out)==281 and set(out)==set(names)
    return [f32(out[n]) for n in names]
