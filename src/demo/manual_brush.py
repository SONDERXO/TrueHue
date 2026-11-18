"""Standard-library brush geometry shared by Tk and the image worker."""
import math


def refine_masks(correction, measurement, protected, width, height, strokes):
    size=width*height
    if min(width,height)<1 or any(len(a)!=size for a in (correction,measurement,protected)):
        raise ValueError('Matching mask dimensions required')
    if any(v not in (0,255) for a in (correction,measurement,protected) for v in a):
        raise ValueError('Binary mask bytes required')
    if not isinstance(strokes,list) or len(strokes)>1000:raise ValueError('At most1000strokes allowed')
    c,m,p=map(bytearray,(correction,measurement,protected))
    for stroke in strokes:
        if not isinstance(stroke,dict):raise ValueError('Brush stroke required')
        target=stroke.get('target');mode=stroke.get('mode');radius=stroke.get('radius');points=stroke.get('points')
        if target not in ('correction','measurement','both') or mode not in ('add','remove','restore'):
            raise ValueError('Known target and brush mode required')
        if type(radius) is not int or not 1<=radius<=32:raise ValueError('Brush radius1–32required')
        if type(stroke.get('unlock',False)) is not bool:raise ValueError('Explicit boolean unlock required')
        if not isinstance(points,list) or not 1<=len(points)<=10000:raise ValueError('Bounded brush points required')
        for point in points:
            if (not isinstance(point,list) or len(point)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in point)
                    or not 0<=point[0]<width or not 0<=point[1]<height):
                raise ValueError('Brush point outside image')
        centres=[]
        for i,point in enumerate(points):
            a=points[i-1] if i else point;steps=max(1,math.ceil(max(abs(point[0]-a[0]),abs(point[1]-a[1]))))
            for j in range(steps+1):centres.append((round(a[0]+(point[0]-a[0])*j/steps),round(a[1]+(point[1]-a[1])*j/steps)))
        for x,y in centres:
            for yy in range(max(0,y-radius),min(height,y+radius+1)):
                for xx in range(max(0,x-radius),min(width,x+radius+1)):
                    if (xx-x)**2+(yy-y)**2>radius**2:continue
                    k=yy*width+xx
                    if mode=='add' and protected[k] and not stroke.get('unlock',False):continue
                    if target in ('correction','both'):
                        c[k]=0 if mode=='remove' else (correction[k] if mode=='restore' else 255)
                        p[k]=255 if mode=='remove' else (protected[k] if mode=='restore' else 0)
                    if target in ('measurement','both'):
                        m[k]=0 if mode=='remove' else (measurement[k] if mode=='restore' else 255)
    return bytes(c),bytes(m),bytes(p)
