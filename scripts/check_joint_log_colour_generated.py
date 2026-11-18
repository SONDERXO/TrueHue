"""Fixed96generated probes and independent scalar descriptor replay; no dataset IO."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.joint_log_colour import extract,NAMES
OUT=ROOT/'outputs/joint_log_colour_generated_v1'

def scalar(image):
    hist=[0.]*256;count=clipped=0
    for row in image.tolist():
        for r,g,b in row:
            if min(r,g,b)==0:continue
            u=math.log(r/g);v=math.log(b/g);count+=1
            clipped+=int(abs(u)>2 or abs(v)>2)
            x=(min(2,max(-2,u))+2)*3.75;y=(min(2,max(-2,v))+2)*3.75
            i,j=math.floor(x),math.floor(y);a,b=x-i,y-j
            for ix,wx in [(i,1-a),(min(i+1,15),a)]:
                for iy,wy in [(j,1-b),(min(j+1,15),b)]:hist[ix*16+iy]+=wx*wy
    return [1.,count/(image.shape[0]*image.shape[1]),clipped/count]+[v/count for v in hist] if count else [0.]*259

def scenes():
    y,x=np.indices((64,64));ramp=(16+x*3).astype('uint8');neutral=np.stack([ramp]*3,axis=2)
    correlated=np.array([[160,100,160],[64,100,64]],np.uint8)[x%2]
    anti=np.array([[160,100,64],[64,100,160]],np.uint8)[x%2]
    shade=.15+.7*x/63;material=np.rint(shade[:,:,None]*np.array([220,150,110])).astype('uint8')
    mixed=material.copy();mixed[:,:32]=[35,90,170]
    zeros=np.array([[0,0,0],[0,40,80],[40,0,80],[40,80,0],[64,80,96]],np.uint8)[x%5]
    saturated=np.array([[255,180,120],[120,255,180],[180,120,255],[255,255,255]],np.uint8)[x%4]
    prior=material.copy();prior[:,:,0]=np.rint(prior[:,:,0].astype(float)*245/255).astype('uint8')
    return dict(neutral=neutral,correlated=correlated,anticorrelated=anti,material=material,mixed=mixed,zeros=zeros,saturated=saturated,prior_edited=prior)

def main():
    OUT.mkdir()
    bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
        'docs/joint-log-colour-generated-protocol-2026-11-13.md','src/model_training/joint_log_colour.py','scripts/check_joint_log_colour_generated.py']}
    (OUT/'execution_plan_PRIVATE.json').write_text(json.dumps(dict(input_sha256=bindings,generated_only=True,records=96),indent=2)+'\n')
    # Algebra before quantization: independent direct ratios versus transformed coordinates.
    algebra=[]
    for rgb in [(30.,60.,90.),(180.,110.,80.),(125.,125.,125.)]:
        for gamma in [1/.7,.7]:
            a=[v**gamma for v in rgb]
            assert all(math.isclose(math.log(a[c]/a[1]),gamma*math.log(rgb[c]/rgb[1]),abs_tol=1e-12) for c in [0,2])
        shifted=(rgb[0]*245/255,rgb[1],rgb[2])
        assert math.isclose(math.log(shifted[0]/shifted[1]),math.log(rgb[0]/rgb[1])+math.log(245/255),abs_tol=1e-12)
        algebra.append(True)
    records=[];stored={};fixtures=scenes();maximum=0.
    for name,base in fixtures.items():
        for role in ['identity','under','over','cool']:
            f=base.astype(float)/255;gamma={'identity':1,'under':1/.7,'over':.7,'cool':1}[role]
            f=f**gamma
            if role=='cool':f[:,:,0]*=245/255
            raw=np.rint(f*255).astype('uint8')
            ok,encoded=cv2.imencode('.jpg',raw[:,:,::-1],[cv2.IMWRITE_JPEG_QUALITY,90]);assert ok
            variants=dict(native=raw,jpeg90=cv2.imdecode(encoded,cv2.IMREAD_COLOR)[:,:,::-1].copy(),
                          resize=cv2.resize(cv2.resize(raw,(32,32),interpolation=cv2.INTER_LINEAR),(64,64),interpolation=cv2.INTER_LINEAR))
            for processing,image in variants.items():
                before=image.copy();result=extract(image);actual=list(result['features'].values());expected=scalar(image)
                error=max(abs(a-b) for a,b in zip(actual,expected));maximum=max(maximum,error)
                assert error<=1e-12 and np.array_equal(image,before)
                assert all(v>=0 for v in actual[3:]) and (not result['available'] or abs(sum(actual[3:])-1)<1e-12)
                key=f'{name}:{role}:{processing}';stored[key]=actual
                records.append(dict(generated_fixture=True,scene=name,role=role,processing=processing,
                    available=result['available'],features=actual,independent_max_abs_error=error))
    a,b=fixtures['correlated'],fixtures['anticorrelated']
    assert all(np.array_equal(np.sort(a[:,:,c].ravel()),np.sort(b[:,:,c].ravel())) for c in range(3))
    assert stored['correlated:identity:native']!=stored['anticorrelated:identity:native']
    assert np.allclose(extract(np.tile(a,(2,2,1)))['features'].values() if False else list(extract(np.tile(a,(2,2,1)))['features'].values()),list(extract(a)['features'].values()),atol=1e-12,rtol=0)
    assert list(extract(np.zeros((2,2,3),np.uint8))['features'].values())==[0.]*259
    h=np.array(list(extract(a)['features'].values())[3:]).reshape(16,16)
    swapped=a[:,:,[2,1,0]].copy();hs=np.array(list(extract(swapped)['features'].values())[3:]).reshape(16,16)
    assert np.allclose(h.T,hs,atol=1e-12,rtol=0)
    assert stored['prior_edited:identity:native']==stored['material:cool:native']
    assert len(records)==96
    result=dict(passed=True,generated_only=True,records=96,scalar_values_verified=96*259,maximum_scalar_error=maximum,
        algebra_checks=algebra,same_marginal_different_joint=True,prior_edited_collision=True,
        new_training_qualified=False,actual_photo_reads=0,fits=0,input_sha256=bindings)
    (OUT/'records_PRIVATE.json').write_text(json.dumps(records,indent=2)+'\n')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
