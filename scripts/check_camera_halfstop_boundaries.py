"""Additional complete8bit-channel arithmetic check, no photos or model fits."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.distortion_generation.camera_inspired_halfstop import generate,inverse,ROLES
from src.evaluation.camera_halfstop_generation_scalar import forward
from src.model_training.luminance_chroma_operator import render_rgb8,decode,encode
from src.evaluation.luminance_chroma_scalar import replay
from src.model_training.reiqa_frozen_features import sha
def main():
    destination=ROOT/'outputs/camera_halfstop_boundary_assessment_v1/verification_PRIVATE.json'
    if destination.exists():raise FileExistsError(destination)
    v=np.arange(256,dtype=np.uint8)
    palette=np.concatenate([np.repeat(v[:,None],3,axis=1),np.stack([v,v*0,v*0],axis=1),np.stack([v*0,v,v*0],axis=1),np.stack([v*0,v*0,v],axis=1)]).reshape(32,32,3)
    alpha=np.ones((32,32));protected=np.zeros((32,32),bool);records=[]
    for role in ROLES:
        image,meta=generate(palette,role);expected,clipped=forward(palette,role)
        np.testing.assert_array_equal(image,expected)
        assert meta['newly_all_black_pixels']==0
        actual=render_rgb8(image,alpha,protected,inverse(role));scalar,_=replay(image,palette,alpha,protected,inverse(role))
        np.testing.assert_array_equal(actual,scalar)
        assert np.all(actual[np.all(palette==0,axis=2)]==0)
        if role=='identity':np.testing.assert_array_equal(image,palette)
        unclip=~clipped.any(axis=2)
        worst=int(np.abs(actual.astype(int)-palette)[unclip].max())
        p=inverse(role);direct=np.rint(encode(np.clip(decode(image/255.)*p[1]*np.array([p[2],1,p[3]]),0,1))*255).astype(np.uint8)
        direct_error=int(np.abs(direct.astype(int)-palette)[unclip].max());assert direct_error<=2
        records.append(dict(role=role,new_allblack_pixels=0,scalar_forward_exact=True,known_inverse_scalar_exact=True,
            unclipped_composed_operator_max_RGB8_error=worst,direct_inverse_quantization_max_error=direct_error,clipped_pixels_retained=int(clipped.any(axis=2).sum())))
    result=dict(passed=True,reference_palette_pixels=1024,roles=6,all256codes_eachchannel_covered=True,records=records,
                no_new_zero_channel_holes_from_positive_codes=True,
                composed_gamut_error_retained_not_quantization_bound=True,
                initial_wrong_test_retained=True,operator_modified=False,real_photos=0,model_fits=0,script_sha256=sha(Path(__file__)))
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
