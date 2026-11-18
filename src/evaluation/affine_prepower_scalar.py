"""Independent scalar five-control rendering/objective, with no optimizer imports."""
import math
import numpy as np


def replay(image,reference,alpha,controls):
    q,r,b,a,d=controls
    output=np.empty(image.shape,float)
    squared=[];floored=0;overflowed=0
    for y,x,c in np.ndindex(image.shape):
        v=float(image[y,x,c]);pre=a*v+d
        raw=math.pow(max(0.,pre),q)*(r,1.,b)[c]
        output[y,x,c]=(1-float(alpha[y,x]))*v+float(alpha[y,x])*min(1.,max(0.,raw))
        if alpha[y,x]>0:
            squared.append((output[y,x,c]-float(reference[y,x,c]))**2)
            floored+=pre<0;overflowed+=raw>1
    return output,dict(float_mse=math.fsum(squared)/len(squared),
        float_rmse=math.sqrt(math.fsum(squared)/len(squared)),
        prepower_floor_channel_samples=floored,output_overflow_channel_samples=overflowed)


def verify(image,reference,alpha,protected,result,*,rgb8):
    if result['parameters'] is None:
        assert result['status'].startswith('unavailable_')
        return True
    im=image.astype(float)/255 if rgb8 else image
    ref=reference.astype(float)/255 if rgb8 else reference
    output,metrics=replay(im,ref,alpha,result['parameters'])
    for key in ['float_rmse','float_mse']:
        assert math.isclose(metrics[key],result[key],abs_tol=1e-12,rel_tol=1e-12)
    for key in ['prepower_floor_channel_samples','output_overflow_channel_samples']:
        if key in result: assert metrics[key]==result[key]
    assert np.array_equal(output[alpha==0],im[alpha==0])
    assert np.array_equal(output[protected],im[protected])
    if rgb8:
        actual=np.empty(image.shape,np.uint8)
        for position in np.ndindex(image.shape): actual[position]=round(255*float(output[position]))
        actual[alpha==0]=image[alpha==0]
        expected=math.fsum(abs(int(a)-int(b)) for a,b in zip(actual[alpha>0].flat,reference[alpha>0].flat))/(3*int((alpha>0).sum()))
        assert math.isclose(result['rgb8_mae_codes'],expected,abs_tol=1e-12)
    return True
