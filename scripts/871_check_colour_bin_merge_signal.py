"""Generated scalar bin-density signal only; no image file or model access."""
from pathlib import Path
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.distortion_generation.core_colour_recipe import render_rgb
from src.distortion_generation.development_roles import core_exposure
OUT=ROOT/'outputs/colour_bin_merge_signal_v1'

def spectrum(codes):
    hist=np.bincount(codes,minlength=256);occupied=np.flatnonzero(hist)
    values=hist[occupied[0]:occupied[-1]+1].astype(float)
    transformed=np.fft.rfft(values-values.mean())
    if len(transformed)<2 or not np.any(values-values.mean()):return dict(peak=0.,index=None,span=len(values),occupied=len(occupied))
    index=int(np.argmax(np.abs(transformed[1:]))+1)
    scalar=complex(math.fsum(float(v)*math.cos(-2*math.pi*index*j/len(values)) for j,v in enumerate(values-values.mean())),
        math.fsum(float(v)*math.sin(-2*math.pi*index*j/len(values)) for j,v in enumerate(values-values.mean())))
    assert math.isclose(abs(scalar),abs(transformed[index]),rel_tol=1e-12,abs_tol=1e-10)
    return dict(peak=float(abs(transformed[index])/hist.sum()),index=index,span=len(values),occupied=len(occupied))

def main():
    if OUT.exists():raise FileExistsError('Preserve signal check')
    full=np.arange(256,dtype=np.uint8)
    palettes=dict(uniform=full,smooth_counts=np.repeat(full,1+full.astype(int)//32),sparse=full[::4])
    edited=np.repeat(full[None,:,None],3,axis=2);edited,_=render_rgb(edited,np.ones((1,256)),'medium','cool')
    records=[]
    for name,codes in list(palettes.items())+[('already_edited',None)]:
        clean=edited.copy() if codes is None else np.repeat(codes[None,:,None],3,axis=2)
        alpha=np.ones(clean.shape[:2]);images=dict(identity=clean,cool=render_rgb(clean,alpha,'medium','cool')[0],
            warm=render_rgb(clean,alpha,'medium','warm')[0],under=core_exposure(clean,alpha,'medium','under')[0])
        for role,image in images.items():records.append(dict(source=name,role=role,channels=[spectrum(image[:,:,j].ravel()) for j in range(3)],generated_only=True))
    # Independently map the exact existing medium attenuation factor.
    mapping=[round(k*245/255) for k in range(256)];multiplicity={k:mapping.count(k) for k in set(mapping)}
    merged=[k for k,v in sorted(multiplicity.items()) if v==2]
    assert len(multiplicity)==246 and len(merged)==10 and set(multiplicity.values())=={1,2}
    assert set(multiplicity)==set(range(246)) # No internal holes, despite merges.
    base=next(r for r in records if r['source']=='uniform' and r['role']=='identity')
    cool=next(r for r in records if r['source']=='uniform' and r['role']=='cool')
    prior=next(r for r in records if r['source']=='already_edited' and r['role']=='identity')
    assert cool['channels'][0]['peak']>0 and base['channels'][0]['peak']==0
    assert cool['channels'][1:]==base['channels'][1:] and cool['channels']==prior['channels']
    OUT.mkdir()
    (OUT/'generated_records_ONLY.json').write_text(json.dumps(records,indent=2)+'\n')
    files=['docs/colour-bin-merge-signal-protocol-2026-11-13.md','scripts/871_check_colour_bin_merge_signal.py',
        'src/distortion_generation/core_colour_recipe.py','src/distortion_generation/development_roles.py']
    result=dict(passed=True,status='DISTINCT_DENSITY_SIGNAL_PRESENT_NOT_PHOTO_VALIDATED',generated_records=16,
        merged_output_codes=merged,gain_output_support=246,internal_gaps=0,uniform_cool_red_peak=cool['channels'][0],
        uniform_clean_red_peak=base['channels'][0],prior_edit_identity_equals_new_cool=True,
        spectral_descriptor_selected=False,JPEG_resize_robustness_tested=False,photo_reads=0,real_fits=0,predictions=0,
        input_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files})
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    for r in records:print(r['source'],r['role'],[round(c['peak'],6) for c in r['channels']])

if __name__=='__main__':main()
