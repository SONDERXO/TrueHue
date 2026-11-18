"""Independent scalar 256-code LUTs for the NEW camera-inspired condition family."""
import math
import numpy as np
def condition(role):
    if role not in ['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']:raise ValueError(role)
    ev={'exposure_under':-.5,'combined_under':-.5,'exposure_over':.5,'combined_over':.5}.get(role,0.)
    cast=role in ['colour_only','combined_under','combined_over']
    return ev,[.85,1.,1.15] if cast else [1.,1.,1.]
def controls(role):
    ev,wb=condition(role)
    return [1.,2.**(-ev),1/wb[0],1/wb[2],1.]
def forward(reference,role):
    ev,wb=condition(role);gain=2.**ev;tables=[];overflow=[]
    for c in range(3):
        table=[];clips=[]
        for code in range(256):
            v=code/255.;linear=v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
            raw=(linear*gain)*wb[c];clips.append(raw>1)
            linear=min(1.,raw)
            encoded=12.92*linear if linear<=.0031308 else 1.055*linear**(1/2.4)-.055
            table.append(round(encoded*255))
        tables.append(np.array(table,np.uint8));overflow.append(np.array(clips,bool))
    image=np.stack([tables[c][reference[:,:,c]] for c in range(3)],axis=2)
    clipping=np.stack([overflow[c][reference[:,:,c]] for c in range(3)],axis=2)
    return image,clipping
