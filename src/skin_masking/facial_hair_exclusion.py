"""Removal-only facial-hair suggestions and explicit user-painted exclusions.

EasyPortrait's background is not a dedicated beard label. Its lower-face
disagreement with the preferred mask is a suggestion requiring inspection.
There is deliberately no darkness threshold and no automatic default removal.
"""
import cv2
import numpy as np

MODEL_SHA256='f649f30a4f000ea3d8c5f4593b01c140b3c50659388c6d2997a6f546a451c434'
MEAN=np.array([143.55267075,132.96705975,126.94924335],np.float32)
STD=np.array([60.2625333,60.32740275,59.30988645],np.float32)


def preprocess_auxiliary(image,*,size=384):
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8 BGR image required')
    if size not in (384,512):raise ValueError('Declared auxiliary input size required')
    resized=cv2.resize(image,(size,size),interpolation=cv2.INTER_LINEAR).astype(np.float32)
    return np.ascontiguousarray(((resized-MEAN)/STD).transpose(2,0,1)[None])


class FacialHairAuxiliary:
    def __init__(self,path,*,profile='mobilenet384',backend='opencv'):
        import hashlib
        from pathlib import Path
        profiles={'mobilenet384':(384,MODEL_SHA256),
            'fpn512':(512,'cc5e9ce11c8e51b00b2975ba24c560b82d298d428b8c4ee4d15e9d005d567d15')}
        if profile not in profiles:raise ValueError('Unknown auxiliary profile')
        self.size,expected=profiles[profile]
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:
            raise ValueError('Auxiliary model hash mismatch')
        self.backend=backend
        if backend=='onnxruntime':
            import sys
            runtime=Path(path).parent.parent/'facial_hair_auxiliary_v1/runtime'
            if runtime.is_dir() and str(runtime) not in sys.path:sys.path.insert(0,str(runtime))
            import onnxruntime as ort
            self.session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
        elif backend=='opencv':
            self.net=cv2.dnn.readNetFromONNX(str(path))
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        else:raise ValueError('Unknown auxiliary inference backend')

    def categories_bgr(self,image):
        tensor=preprocess_auxiliary(image,size=self.size)
        if self.backend=='onnxruntime':logits=self.session.run(['logits'],{'image':tensor})[0]
        else:self.net.setInput(tensor);logits=self.net.forward('logits')
        if logits.shape!=(1,8,self.size,self.size) or not np.isfinite(logits).all():
            raise ValueError('Expected finite eight-class auxiliary logits')
        labels=np.argmax(logits[0],axis=0).astype(np.uint8)
        return cv2.resize(labels,(image.shape[1],image.shape[0]),interpolation=cv2.INTER_NEAREST)


def lower_face_suggestion(base_mask,primary_categories,auxiliary_categories):
    masks=[np.asarray(m) for m in [base_mask,primary_categories,auxiliary_categories]]
    if any(m.dtype!=np.uint8 or m.ndim!=2 or not m.size or m.shape!=masks[0].shape for m in masks):
        raise ValueError('Matching uint8 mask and category maps required')
    base,primary,auxiliary=masks
    if not set(np.unique(base))<={0,255} or (primary>18).any() or (auxiliary>7).any():
        raise ValueError('Invalid binary mask or category labels')
    nose=(primary==10)&(base>0)
    if not nose.any():raise ValueError('No selected nose region; no automatic lower-face boundary')
    nose_bottom=int(np.nonzero(nose)[0].max())
    lower=np.indices(base.shape)[0]>nose_bottom
    veto=(base>0)&(primary==1)&lower&(auxiliary==0)
    return veto,dict(method='lower_face_auxiliary_background_disagreement_v1',
        nose_bottom_row=nose_bottom,suggested_pixels=int(veto.sum()),
        interpretation='Possible facial hair/non-skin, not a dedicated beard prediction',
        automatically_applied=False,requires_inspection=True)


def paint_exclusions(shape,strokes,*,initial=None):
    """Rasterize image-coordinate brush strokes; restore only clears the veto."""
    if len(shape)!=2 or min(shape)<=0:raise ValueError('Positive image shape required')
    h,w=shape
    if initial is None:veto=np.zeros(shape,bool)
    else:
        initial=np.asarray(initial)
        if initial.shape!=shape or initial.dtype!=bool:raise ValueError('Matching boolean initial veto required')
        veto=initial.copy()
    for stroke in strokes:
        mode=stroke.get('mode');radius=stroke.get('radius');points=np.asarray(stroke.get('points'),dtype=float)
        if mode not in {'exclude','restore'} or isinstance(radius,bool) or not isinstance(radius,(int,float)) or not np.isfinite(radius) or not 1<=radius<=max(shape):
            raise ValueError('Valid brush mode and pixel radius required')
        if points.ndim!=2 or points.shape[1]!=2 or not len(points) or not np.isfinite(points).all():
            raise ValueError('Finite brush points required')
        if ((points[:,0]<0)|(points[:,0]>=w)|(points[:,1]<0)|(points[:,1]>=h)).any():
            raise ValueError('Brush points outside image')
        xy=np.rint(points).astype(np.int32);xy[:,0]=np.clip(xy[:,0],0,w-1);xy[:,1]=np.clip(xy[:,1],0,h-1)
        footprint=np.zeros(shape,np.uint8);r=int(round(radius))
        for point in xy:cv2.circle(footprint,tuple(point),r,255,-1)
        for start,end in zip(xy,xy[1:]):cv2.line(footprint,tuple(start),tuple(end),255,2*r+1)
        if mode=='exclude':veto|=footprint>0
        else:veto&=~(footprint>0)
    return veto


def apply_exclusions(base_mask,veto):
    base=np.asarray(base_mask);veto=np.asarray(veto)
    if base.dtype!=np.uint8 or base.ndim!=2 or not base.size or not set(np.unique(base))<={0,255}:
        raise ValueError('Binary uint8 base mask required')
    if veto.dtype!=bool or veto.shape!=base.shape:raise ValueError('Matching boolean veto required')
    mask=base.copy();mask[veto]=0
    alpha=cv2.GaussianBlur(mask,(3,3),0);alpha[mask==0]=0
    assert not (mask[base==0]).any() and not mask[veto].any() and not alpha[veto].any()
    return mask,alpha
