"""Generated selector/cue audit only; no real photographs or learned model."""
from pathlib import Path
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from tests.test_sclera_context import fixture
from src.model_training.sclera_context import extract_sclera_context
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
from src.distortion_generation.core_colour_recipe import render_rgb
from src.distortion_generation.development_roles import core_exposure
OUT=ROOT/'outputs/sclera_context_generated_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve engineering evidence')
    image,cat,points,truth,iris=fixture();alpha=np.ones((256,256),float)
    probes=[('baseline',image,cat,points,truth),
        ('cool',render_rgb(image,alpha,'medium','cool')[0],cat,points,truth),
        ('warm',render_rgb(image,alpha,'medium','warm')[0],cat,points,truth),
        ('under',core_exposure(image,alpha,'medium','under')[0],cat,points,truth)]
    varied=image.copy();varied[truth]=[180,155,130];probes.append(('natural_colour',varied,cat,points,truth))
    probes.append(('missing_iris',image,cat,points[:468],truth))
    glasses=cat.copy();glasses[np.isin(glasses,[4,5])]=6;probes.append(('sunglasses',image,glasses,points,truth))
    one=cat.copy();one[one==4]=6;probes.append(('one_covered',image,one,points,truth))
    closed=points.copy();closed[FEATURE_INDICES['left_eye']]=[176,100];probes.append(('closed',image,cat,closed,truth))
    off=points.copy();off[473]=[1,1];probes.append(('off_center',image,cat,off,truth))
    patch=np.zeros_like(truth);patch[96:99,165:168]=True
    contaminated=image.copy();contaminated[patch]=[170,90,65];correct=cat.copy();correct[patch]=1
    wrong=cat.copy();wrong[patch]=4;changed_truth=truth&~patch
    probes.extend([('skin_correctly_labelled',contaminated,correct,points,changed_truth),('skin_mislabelled_as_eye',contaminated,wrong,points,changed_truth)])
    records=[]
    for name,rgb,categories,landmarks,actual in probes:
        result=extract_sclera_context(rgb,categories,landmarks);mask=result['mask']
        entry=dict(name=name,valid=result['valid'],reason=result['reason'],features=result['features'],eyes=result['eyes'],
            selected_pixels=int(mask.sum()),non_sclera_selected=int((mask&~actual).sum()),iris_selected=int((mask&iris).sum()),generated_only=True)
        if result['valid']:
            pixels=rgb[mask].tolist();means=[math.fsum(row[j] for row in pixels)/len(pixels) for j in range(3)]
            expected=[1.,math.log((means[0]+1)/(means[1]+1)),math.log((means[2]+1)/(means[1]+1))]
            assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(result['features'].values(),expected))
        else:assert not mask.any() and list(result['features'].values())==[0.,0.,0.]
        records.append(entry)
    lookup={r['name']:r for r in records}
    assert all(not lookup[n]['valid'] for n in ['missing_iris','sunglasses','one_covered','closed','off_center'])
    assert lookup['cool']['features']['sclera_context_log_r_over_g']<lookup['baseline']['features']['sclera_context_log_r_over_g']
    assert lookup['warm']['features']['sclera_context_log_b_over_g']<lookup['baseline']['features']['sclera_context_log_b_over_g']
    assert lookup['skin_correctly_labelled']['non_sclera_selected']==0
    assert lookup['skin_mislabelled_as_eye']['non_sclera_selected']>0
    OUT.mkdir()
    (OUT/'generated_records_ONLY.json').write_text(json.dumps(records,indent=2)+'\n')
    files=['docs/sclera-context-generated-protocol-2026-11-13.md','src/model_training/sclera_context.py',
        'tests/test_sclera_context.py','scripts/872_check_generated_sclera_context.py','src/skin_masking/landmark_exclusion.py']
    summary=dict(passed=True,status='GEOMETRIC_ENGINEERING_PASS_REAL_SELECTION_QUALITY_UNTESTED',generated_probes=12,
        available=sum(r['valid'] for r in records),explicitly_unavailable=sum(not r['valid'] for r in records),
        deliberate_mislabel_contamination=lookup['skin_mislabelled_as_eye']['non_sclera_selected'],
        canonical_colour_used=False,source_transfer_demonstrated=False,photo_reads=0,fits=0,predictions=0,
        input_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files})
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
