"""Validate prediction-hidden patch evidence; no model inference or adoption."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np

LABELS={'skin','facial_hair','object','outside','uncertain'}


def polygon_mask(points):
    if not isinstance(points,list) or not 3<=len(points)<=500:
        raise ValueError('Polygon requires3–500points')
    if any(not isinstance(p,list) or len(p)!=2 or any(type(v)!=int or not 0<=v<=255 for v in p) for p in points):
        raise ValueError('Integer square256 polygon coordinates required')
    if len({tuple(p) for p in points})!=len(points):raise ValueError('Repeated polygon vertices')
    contour=np.array(points,np.float32)
    if abs(cv2.contourArea(contour))<1:raise ValueError('Degenerate polygon')
    def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on(a,b,c):return min(a[0],b[0])<=c[0]<=max(a[0],b[0]) and min(a[1],b[1])<=c[1]<=max(a[1],b[1])
    def intersect(a,b,c,d):
        x,y,z,w=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
        return (x*y<0 and z*w<0) or (x==0 and on(a,b,c)) or (y==0 and on(a,b,d)) or (z==0 and on(c,d,a)) or (w==0 and on(c,d,b))
    n=len(points)
    for i in range(n):
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):continue
            if intersect(points[i],points[(i+1)%n],points[j],points[(j+1)%n]):raise ValueError('Self-intersecting polygon')
    mask=np.zeros((256,256),bool)
    x0,y0=contour.min(axis=0).astype(int);x1,y1=contour.max(axis=0).astype(int)
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            mask[y,x]=cv2.pointPolygonTest(contour,(x+.5,y+.5),False)>=0
    if not mask.any():raise ValueError('No pixel centres inside polygon')
    return mask


def validate(manifest,export,identity):
    if export.get('schema_version')!='truehue_faceocc_broader_patch_decisions_v1' or export.get('manifest_sha256')!=identity:
        raise ValueError('Wrong schema or manifest binding')
    if not isinstance(export.get('annotator'),str) or not export['annotator'].strip():raise ValueError('Annotator required')
    if export.get('technical_failures')!=manifest['technical_failures']:raise ValueError('Technical failure records changed')
    expected={r['image_id']:r for r in manifest['rows']};rows=export['rows']
    if len(rows)!=len(expected) or {r['image_id'] for r in rows}!=set(expected):raise ValueError('Missing/duplicate/extra images')
    output=[]
    for r in rows:
        if r.get('image_sha256')!=expected[r['image_id']]['image_sha256']:raise ValueError('Image hash mismatch')
        if r.get('status') not in {'gradable','ungradable'} or not isinstance(r.get('notes'),str):raise ValueError('Missing status/notes')
        if r['status']=='ungradable' and not r['notes'].strip():raise ValueError('Ungradable reason required')
        tag_values={'glasses':{'present','absent','unknown'},'covering':{'present','absent','unknown'},
            'facial_hair':{'present','absent','unknown'},'lighting':{'even','uneven_or_cast','dark','unknown'}}
        if set(r.get('tags',{}))!=set(tag_values) or any(r['tags'][k] not in vs for k,vs in tag_values.items()):raise ValueError('Invalid scene tags')
        masks={k:np.zeros((256,256),bool) for k in LABELS};patches=[]
        for p in r.get('polygons',[]):
            if p.get('label') not in LABELS:raise ValueError('Invalid polygon label')
            mask=polygon_mask(p['points']);label=p['label']
            if any((mask&m).any() for k,m in masks.items() if k!=label):raise ValueError('Conflicting overlapping patch labels')
            masks[label]|=mask;patches.append(dict(label=label,pixel_centres=int(mask.sum())))
        counts={k:int(v.sum()) for k,v in masks.items()}
        if r['status']=='gradable' and (counts['skin']==0 or sum(counts[k] for k in ['facial_hair','object','outside'])==0):
            raise ValueError('Gradable image needs clear skin and relevant unwanted-region patches')
        output.append(dict(**r,class_pixel_counts=counts,patch_pixel_counts=patches,admitted=False))
    return output


def main():
    parser=argparse.ArgumentParser();parser.add_argument('decisions',type=Path);args=parser.parse_args()
    folder=ROOT/'outputs/faceocc_broader_annotation_v1';out=ROOT/'outputs/faceocc_broader_annotation_import_v1'
    if out.exists():raise FileExistsError(out)
    raw=(folder/'manifest.json').read_bytes();manifest=json.loads(raw)
    for r in manifest['rows']:
        if hashlib.sha256((folder/r['image_path']).read_bytes()).hexdigest()!=r['image_sha256']:raise ValueError('Prepared image changed')
    decisions=args.decisions.read_bytes();export=json.loads(decisions)
    rows=validate(manifest,export,hashlib.sha256(raw).hexdigest())
    out.mkdir();(out/'original_export.json').write_bytes(decisions)
    (out/'annotations.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(dict(status='annotations_frozen_no_inference',
        annotator=export['annotator'],manifest_sha256=hashlib.sha256(raw).hexdigest(),
        export_sha256=hashlib.sha256(decisions).hexdigest(),attempts=24,
        gradable=sum(r['status']=='gradable' for r in rows),ungradable=sum(r['status']=='ungradable' for r in rows),
        technical_failures=manifest['technical_failures'],adopted=False),indent=2))
    print('Annotations bound and frozen. No model inference or adoption.')


if __name__=='__main__':main()
