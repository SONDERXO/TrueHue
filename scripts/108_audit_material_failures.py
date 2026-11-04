"""Explain cached protected-material failures without proposing a new mask."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    a=cv2.imread(str(p),0);assert a is not None and set(np.unique(a))<={0,255};return a>0
def quantiles(values):
    return dict(zip(['p10','p50','p90'],map(float,np.percentile(values,[10,50,90])))) if values.size else None
def main():
    out=ROOT/'outputs/material_failure_attribution_v1'
    if out.exists():raise FileExistsError(out)
    parent=ROOT/'outputs/paint_protection_validation_v1';sp=parent/'summary.json'
    previous=json.loads(sp.read_text());final=json.loads((parent/'final_verification.json').read_text())
    verification=json.loads((parent/'verification.json').read_text())
    hashes=dict(previous['input_sha256'])
    for table in [verification['artifact_sha256'],final['artifact_sha256']]:hashes.update(table)
    tracked=[Path(__file__),sp,parent/'final_verification.json',parent/'verification.json',ROOT/'docs/material-failure-attribution-protocol.md']
    hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    manifest=json.loads((ROOT/'data/manifests/paint_protection_validation_v1/frozen_manifest.json').read_text())
    frames={f['frame_id']:f for f in manifest['frames']}
    scoring=importlib.import_module('90_score_face_boundary_references');regions={}
    export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text())
    for f in manifest['frames']:
        ident=f['frame_id'];w,h=f['width'],f['height'];values={}
        if f['annotation']['kind']=='unchanged_user_reference':
            labels=cv2.imread(str(ROOT/f['annotation']['labels_path']),0);values['user_skin']=(labels==1)
            if ident=='16798':
                spec=next(r for r in export['images'] if Path(r['image_id']).stem==ident);paint=np.zeros((h,w),bool)
                for p in spec['polygons'][:6]:paint|=scoring.polygon_pixels(p['points'],w,h)
                values['user_paint']=paint&(labels==3);values['user_features']=(labels==3)&~paint
            else:values['user_features']=labels==3
        for r in f['annotation'].get('regions',[]):values[r['region_id']]=scoring.polygon_pixels(r['points'],w,h)
        regions[ident]=values
    out.mkdir();(out/'boards').mkdir();records=[];flat=[];witnesses=[]
    for case in previous['records']:
        key=case['key'];ident=case['frame_id'];record=dict(key=key,frame_id=ident,status=case['status'],regions={})
        if case['status']!='available':
            record['reason']=case['reason'];records.append(record);continue
        ing=parent/'ingredients';image=cv2.imread(str(parent/'images'/(key+'.png')))
        dense=cv2.imread(str(ing/(key+'_parser.png')),0);coarse=cv2.imread(str(ing/(key+'_semantic.png')),0)
        excluded=load(ing/(key+'_excluded.png'));seeds=load(ing/(key+'_seeds.png'))
        x,y,w,h=case['face_box'];pad=case['material']['pad'];bounds=np.zeros(excluded.shape,bool)
        bounds[max(0,y-pad):min(image.shape[0],y+h+pad),max(0,x-pad):min(image.shape[1],x+w+pad)]=True
        d=np.isin(dense,[1,10]);s=d&(coarse==3);e=s&~excluded;a=e&bounds
        arms={name:load(parent/'masks'/(key+'_correction_'+name+'.png')) for name in ['A','F','C','C2']};assert np.array_equal(a,arms['A'])
        lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
        z=(lab-np.asarray(case['material']['median']))/np.asarray(case['material']['scale'])
        full=np.sqrt((z*z).sum(axis=2));chroma=np.sqrt((z[:,:,1:]**2).sum(axis=2))
        for name,region in regions[ident].items():
            protected=name!='user_skin';n=int(region.sum());inside=region&a
            removed=dict(dense_reject=int((region&~d).sum()),coarse_reject=int((region&d&~s).sum()),
                anatomy_reject=int((region&s&~e).sum()),bounds_reject=int((region&e&~a).sum()),survive_A=int(inside.sum()))
            assert sum(removed.values())==n
            item=dict(reference_type='unchanged_user' if name.startswith('user_') else 'provisional_codex',
                role='protected' if protected else 'ordinary_skin',pixels=n,funnel=removed,
                seed_selected=int((region&seeds).sum()),seed_total=int(seeds.sum()),
                dense_categories=np.bincount(dense[region],minlength=19).tolist(),
                coarse_categories=np.bincount(coarse[region],minlength=6).tolist(),
                full_distance_in_A=quantiles(full[inside]),chroma_distance_in_A=quantiles(chroma[inside]),
                stages={stage:{arm:int((region&load(parent/'masks'/(key+'_'+stage+'_'+arm+'.png'))).sum()) for arm in entries} for stage,entries in case['stages'].items()})
            assert item['stages']['correction']['A']==removed['survive_A']
            if protected:
                for stage,entries in case['stages'].items():
                    for arm,v in entries.items():assert item['stages'][stage][arm]==v['protected_regions'][name]['selected']
            else:
                for stage,entries in case['stages'].items():
                    for arm,v in entries.items():assert item['stages'][stage][arm]==v['user_reference']['selected_skin_pixels']
            record['regions'][name]=item
            flat.append(dict(case=key,region=name,reference_type=item['reference_type'],role=item['role'],pixels=n,
                **removed,seed_selected=item['seed_selected'],seed_total=item['seed_total'],
                F=int((region&arms['F']).sum()),C=int((region&arms['C']).sum()),C2=int((region&arms['C2']).sum())))
        if ident=='16798':
            paint=regions[ident]['user_paint']&a;skin=regions[ident]['user_skin']&a
            if paint.any() and skin.any():
                py,px=np.argwhere(paint)[np.argmin(chroma[paint])];sy,sx=np.argwhere(skin)[np.argmax(chroma[skin])]
                witness=dict(case=key,paint_xy=[int(px),int(py)],paint_chroma_distance=float(chroma[py,px]),
                    skin_xy=[int(sx),int(sy)],skin_chroma_distance=float(chroma[sy,sx]),
                    incompatible_order=bool(chroma[py,px]<chroma[sy,sx]),scope='Frozen C scalar distance only; not a candidate mask or general impossibility claim')
                witnesses.append(witness)
        if regions[ident]:
            protected=np.zeros(a.shape,bool)
            for name,region in regions[ident].items():
                if name!='user_skin':protected|=region
            panels=[]
            for title,mask in [('Source',None),('Protected in seeds',protected&seeds),('Protected in A',protected&a),('Protected in C2',protected&arms['C2'])]:
                shown=image.copy()
                if mask is not None:shown[mask]=[0,0,255]
                shown=cv2.copyMakeBorder(shown,24,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(shown,title,(2,15),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(shown)
            assert cv2.imwrite(str(out/'boards'/(key+'.png')),np.hstack(panels))
        records.append(record)
    with (out/'region_funnels.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    result=dict(status='complete_cached_diagnostic_only',records=records,chroma_order_witnesses=witnesses,input_sha256=hashes,
        new_inference=0,new_masks=0,new_models=0,training_pairs_regenerated=0,models_fitted=0,
        limitations='Provisional labels are not user/expert truth. Sequential funnel is accounting, not causal attribution. No labels enter inference or seed fitting.')
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(cases=len(records),region_rows=len(flat),witnesses=witnesses)))
if __name__=='__main__':main()
