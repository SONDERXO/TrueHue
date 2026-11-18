"""Generated-only discrete edit-signal feasibility, not a feature extractor."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.distortion_generation.development_roles import core_exposure
from src.distortion_generation.core_colour_recipe import render_rgb
OUT=ROOT/'outputs/quantized_edit_signal_feasibility_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve check')
    codes=np.arange(256,dtype=np.uint8).reshape(16,16)
    # RGB uniform ramp. A second palette has only every fourth code populated.
    references=[('all_codes',codes),('sparse_palette',(codes//4*4).astype(np.uint8))]
    records=[]
    for name,ramp in references:
        clean=np.repeat(ramp[:,:,None],3,axis=2);alpha=np.ones((16,16),float)
        images={'identity':clean,'under':core_exposure(clean,alpha,'medium','under')[0],
            'over':core_exposure(clean,alpha,'medium','over')[0],
            'cool':render_rgb(clean,alpha,'medium','cool','none')[0]}
        for role,image in images.items():
            support=[np.flatnonzero(np.bincount(image[:,:,j].ravel(),minlength=256)).tolist() for j in range(3)]
            records.append(dict(reference=name,role=role,occupied_bins=[len(s) for s in support],
                occupied_code_locations=support,generated_only=True))
        # An acceptable original may already have exactly the same quantization
        # pattern. This limits certainty; it does not demand universal identifiability.
        assert np.array_equal(images['under'],core_exposure(clean,alpha,'medium','under')[0])
    full={r['role']:r for r in records if r['reference']=='all_codes'}
    assert full['identity']['occupied_bins']==[256]*3
    assert all(n<256 for n in full['under']['occupied_bins']+full['over']['occupied_bins'])
    assert full['cool']['occupied_bins'][1:]==[256,256] and full['cool']['occupied_bins'][0]<256
    assert full['under']['occupied_code_locations'][1]!=full['over']['occupied_code_locations'][1]
    # A benign integer offset changes brightness but does not create internal
    # occupancy gaps for a fully populated input ramp (clipping is reported).
    offset=np.clip(codes.astype(int)+20,0,255).astype(np.uint8)
    present=np.flatnonzero(np.bincount(offset.ravel(),minlength=256));internal_gaps=len(set(range(int(present.min()),int(present.max())+1))-set(present))
    assert internal_gaps==0
    OUT.mkdir()
    (OUT/'generated_records_ONLY.json').write_text(json.dumps(records,indent=2)+'\n')
    files=['scripts/858_check_quantized_edit_signal.py','src/distortion_generation/development_roles.py',
        'src/distortion_generation/core_colour_recipe.py','src/distortion_generation/table2_composite.py',
        'outputs/proposal_scope_validation_20261103_v1/pages.json']
    result=dict(passed=True,status='DISTINCT_SIGNAL_FOUND_ENGINEERING_SPEC_NEEDED_NOT_VALIDATED',generated_records=8,
        full_ramp_occupied_bins={k:v['occupied_bins'] for k,v in full.items()},benign_offset_internal_gaps=internal_gaps,
        sparse_palette_confound_explicit=True,already_edited_acceptable_original_confound_explicit=True,
        post_edit_JPEG_or_resize_robustness='Not tested; must be fixed prospectively before claiming practical benefit',
        author_algorithm_reproduced=False,feature_vector_selected=False,tree_fits=0,photos_read=0,scientific_rows=0,
        input_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files})
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
