"""Frozen 224 generated probes; no scientific image/model/fit access."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.histogram_gap_features import histogram_gap_features,NAMES
from src.distortion_generation.development_roles import core_exposure
from src.distortion_generation.core_colour_recipe import render_rgb
from src.distortion_generation.table2_composite import composite_rgb
OUT=ROOT/'outputs/histogram_gap_generated_robustness_v1'

def independent(image):
    result=[]
    for j in range(3):
        observed={int(v) for v in image[:,:,j].flat};lo=min(observed);hi=max(observed)
        for a,b in [(0,127),(128,255)]:
            eligible=set(range(max(a,lo),min(b,hi)+1))
            result.append(float(Fraction(len(eligible-observed),len(eligible))) if eligible else 0.)
    return result

def main():
    if OUT.exists():raise FileExistsError('Preserve fixed engineering attempt')
    x=np.tile(np.arange(256,dtype=np.uint8),(256,1));alpha=np.ones(x.shape,float)
    palettes=dict(full=x,sparse=(x//4*4).astype(np.uint8),dark=(16+x%64).astype(np.uint8),
        light=(176+x%64).astype(np.uint8),two_modes=np.where(x<128,40+x%32,180+x%32).astype(np.uint8),
        constant=np.full_like(x,128),already_edited=np.rint(255*(x/255.)**.7).astype(np.uint8))
    records=[]
    for source,palette in palettes.items():
        clean=np.repeat(palette[:,:,None],3,axis=2)
        images={'identity':(clean,dict(clipped_channel_samples=0)),
            'under':core_exposure(clean,alpha,'medium','under'),
            'over':core_exposure(clean,alpha,'medium','over'),
            'cool':render_rgb(clean,alpha,'medium','cool'),
            'warm':render_rgb(clean,alpha,'medium','warm'),
            'under_cool':render_rgb(clean,alpha,'medium','cool','under'),
            'over_warm':render_rgb(clean,alpha,'medium','warm','over'),
            'table2_clipping':composite_rgb(clean,'medium')}
        for role,(image,forward) in images.items():
            ok,jpeg=cv2.imencode('.jpg',image[:,:,::-1],[cv2.IMWRITE_JPEG_QUALITY,90]);assert ok
            processed=dict(native=image,jpeg90=cv2.imdecode(jpeg,cv2.IMREAD_COLOR)[:,:,::-1],
                resize128back=cv2.resize(cv2.resize(image,(128,128),interpolation=cv2.INTER_AREA),(256,256),interpolation=cv2.INTER_LINEAR),
                sample16=image[::16,::16])
            original=None
            for processing,data in processed.items():
                result=histogram_gap_features(data);values=[result['features'][n] for n in NAMES]
                assert result['valid'] and values==independent(data)
                if processing=='native':original=values
                records.append(dict(source=source,role=role,processing=processing,
                    features=result['features'],sample_pixels=result['sample_pixels'],channels=result['channels'],
                    exact_equal_to_native=values==original,L1_change_from_native=sum(abs(a-b) for a,b in zip(values,original)),
                    forward_clipped_channel_samples=forward['clipped_channel_samples'],generated_only=True))
    assert len(records)==224
    grouped=defaultdict(list)
    for row in records:grouped[(row['processing'],tuple(row['features'].values()))].append(dict(source=row['source'],role=row['role']))
    collisions=[dict(processing=k[0],features=list(k[1]),cases=cases) for k,cases in grouped.items() if len({c['role'] for c in cases})>1]
    example={r['role']:r['features'] for r in records if r['source']=='full' and r['processing']=='native'}
    changes={p:dict(cases=sum(r['processing']==p for r in records),changed=sum(r['processing']==p and not r['exact_equal_to_native'] for r in records),
        max_L1_change=max(r['L1_change_from_native'] for r in records if r['processing']==p)) for p in ['jpeg90','resize128back','sample16']}
    OUT.mkdir()
    for name,value in [('generated_records_ONLY.json',records),('feature_collisions_ONLY.json',collisions),
        ('summary_PRIVATE.json',dict(status='ENGINEERING_COMPLETE_ASSESSMENT_PENDING',records=224,independent_scalar_features=1344,
            full_palette_native=example,processing_changes=changes,collision_groups=len(collisions),
            discriminator_or_threshold_fitted=False,scientific_rows=0,photo_reads=0,tree_fits=0,predictions=0))]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    files=['docs/histogram-gap-generated-protocol-2026-11-12.md','src/model_training/histogram_gap_features.py',
        'tests/test_histogram_gap_features.py','scripts/859_check_histogram_gap_robustness.py',
        'src/distortion_generation/development_roles.py','src/distortion_generation/core_colour_recipe.py','src/distortion_generation/table2_composite.py']
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,independent_features_checked=1344,
        dataset_reads=0,generated_rows_excluded_from_science=True,
        input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
    print(json.dumps(dict(changes=changes,collision_groups=len(collisions),full_native=example),indent=2))

if __name__=='__main__':main()
