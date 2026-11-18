"""Native projection and pixel-exact costs for the shared masking candidate."""
import cv2
import numpy as np

def project_alpha(alpha,protected,bridge):
    alpha=np.asarray(alpha);protected=np.asarray(protected)
    if (alpha.shape!=(256,256) or not np.issubdtype(alpha.dtype,np.floating)
            or not np.isfinite(alpha).all() or (alpha<0).any() or (alpha>1).any()
            or protected.shape!=alpha.shape or protected.dtype!=bool):
        raise ValueError('Floating256 alpha and bool protection required')
    left,top,right,bottom=bridge['native_bounds'];height,width=bridge['source_shape'][:2]
    if not (0<=left<right<=width and 0<=top<bottom<=height):raise ValueError('Invalid native bounds')
    shape=(right-left,bottom-top)
    local=cv2.resize(alpha,shape,interpolation=cv2.INTER_LINEAR)
    veto=cv2.resize(protected.astype(np.float32),shape,interpolation=cv2.INTER_AREA)>0
    local[veto]=0
    result=np.zeros((height,width),float);guard=np.zeros((height,width),bool)
    result[top:bottom,left:right]=local;guard[top:bottom,left:right]=veto
    assert not result[guard].any()
    return result,guard

def blended_action_costs(image,reference,alpha,scoring,actions):
    if (image.dtype!=np.uint8 or reference.dtype!=np.uint8 or image.shape!=reference.shape
            or image.ndim!=3 or image.shape[2]!=3 or alpha.shape!=image.shape[:2]
            or not np.issubdtype(alpha.dtype,np.floating) or not np.isfinite(alpha).all()
            or (alpha<0).any() or (alpha>1).any() or scoring.shape!=alpha.shape
            or scoring.dtype!=bool or not scoring.any()):raise ValueError('Aligned RGB8, alpha and nonempty scoring mask required')
    x=image[scoring].astype(float)/255.;target=reference[scoring].astype(float);a=alpha[scoring,None]
    losses=[]
    for gamma,red,blue in actions:
        if not np.isfinite([gamma,red,blue]).all() or min(gamma,red,blue)<=0:raise ValueError('Positive finite controls required')
        corrected=np.clip(x**gamma*[red,1.,blue],0,1)
        out=np.rint((x*(1-a)+corrected*a)*255)
        losses.append(float(np.abs(out-target).mean()))
    return losses
