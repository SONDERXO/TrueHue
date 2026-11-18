"""Strict user patch import and native-grid reference rasterization."""
import cv2
import numpy as np


def valid_polygon(points, width, height):
    if not isinstance(points, list) or not 3 <= len(points) <= 200:
        return False
    if any(not isinstance(p, list) or len(p) != 2 or any(type(v) is not int for v in p)
           or not 0 <= p[0] < width or not 0 <= p[1] < height for p in points):
        return False
    if len({tuple(p) for p in points}) != len(points):
        return False
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on(a,b,c):return cross(a,b,c)==0 and min(a[0],b[0])<=c[0]<=max(a[0],b[0]) and min(a[1],b[1])<=c[1]<=max(a[1],b[1])
    n=len(points)
    for i in range(n):
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):continue
            a,b,c,d=points[i],points[(i+1)%n],points[j],points[(j+1)%n]
            if (cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0) or on(a,b,c) or on(a,b,d) or on(c,d,a) or on(c,d,b):return False
    return sum(a[0]*points[(i+1)%n][1]-a[1]*points[(i+1)%n][0] for i,a in enumerate(points))!=0


def validate_export(value, manifest, identity):
    if not isinstance(value,dict) or set(value)!={'schema_version','manifest_sha256','reviewer','draft','rows'} or value.get('schema_version')!='truehue_skin_patch_review_v1' or value.get('manifest_sha256')!=identity or value.get('draft') is not False:
        raise ValueError('Completed exact-bound patch export required')
    if not isinstance(value['reviewer'],str) or not value['reviewer'].strip():raise ValueError('Reviewer required')
    expected={r['review_id']:r for r in manifest['rows']};seen=set()
    if not isinstance(value['rows'],list) or len(value['rows'])!=len(expected):raise ValueError('All fixed cases required')
    for r in value['rows']:
        if not isinstance(r,dict) or set(r)!={'review_id','image_sha256','status','notes','polygons'} or not isinstance(r['review_id'],str) or r['review_id'] not in expected or r['review_id'] in seen:raise ValueError('Invalid case membership/schema')
        b=expected[r['review_id']];seen.add(r['review_id'])
        if r['image_sha256']!=b['image_sha256'] or not isinstance(r['notes'],str) or not isinstance(r['polygons'],list):raise ValueError('Image binding or annotation types invalid')
        if r['status']=='marked':
            if not r['polygons']:raise ValueError('Marked case needs patches')
        elif r['status']=='unavailable':
            if r['polygons'] or not r['notes'].strip():raise ValueError('Unavailable needs reason and no patches')
        else:raise ValueError('Explicit outcome required')
        if any(not valid_polygon(p,b['width'],b['height']) for p in r['polygons']):raise ValueError('Invalid native polygon')
    return value['rows']


def rasterize(polygons, width, height):
    """Union native integer polygons using OpenCV filled pixels including boundary."""
    mask=np.zeros((height,width),np.uint8)
    for p in polygons:
        if not valid_polygon(p,width,height):raise ValueError('Invalid polygon')
        cv2.fillPoly(mask,[np.array(p,np.int32)],255)
    return mask
