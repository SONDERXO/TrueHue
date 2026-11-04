"""Replay saved generation/targets/features, never rerun detection or fitting."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/additional_six_source_pairs_v1'
    if (out/'verification.json').exists():raise FileExistsError('Verification already recorded')
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');rows=read(out/'attempts.json')
    assert read(out/'run_status.json')['status']=='complete'
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    manifest=read(ROOT/'outputs/correction_data_redesign_v1/selection.json');policy=read(ROOT/'outputs/correction_data_redesign_v1/access_policy.json')
    lookup_path=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(lookup_path)==plan['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(lookup_path),plan['measurement_contract_sha256'])
    prior_sources={r['source_image_id'] for r in read(ROOT/'outputs/reviewed_primary_comparison_v1/plan.json')['rows']}
    sources={r['source_image_id']:r for r in plan['sources']}
    assert len(sources)==6 and not set(sources)&prior_sources
    assert len(rows)==30 and Counter(r['variant'] for r in rows)=={v:6 for v in plan['variants']}
    assert len({r['pair_id'] for r in rows})==30
    checked_features=0;checked_targets=0
    for source in sources.values():
        training_candidate(source['source_image_id'],manifest,policy)
        rgb=cv2.cvtColor(cv2.imread(str(ROOT/source['reference_path'])),cv2.COLOR_BGR2RGB)
        ref_mask=cv2.imread(str(ROOT/source['reference_mask_path']),0)>0
        for r in [r for r in rows if r['source_image_id']==source['source_image_id']]:
            settings=source['settings'];variant=r['variant'];g=settings['gamma']
            raw=rgb.astype(float)/255
            if variant in ['gamma_lighten','gamma_darken']:
                exponent=g if variant=='gamma_lighten' else 1/g
                raw=np.power(raw,exponent)
            else:
                if variant in ['exposure','combined']:
                    raw=np.power(raw,g)
                    raw=(raw-.5)*(1+settings['contrast']/100)+.5+settings['brightness']/255
                if variant in ['color','combined']:
                    raw+=np.array([settings['cyan_red'],0,settings['yellow_blue']])/255
            clipped=((raw<0)|(raw>1))[ref_mask]
            assert int(clipped.any(axis=1).sum())==r['clipping']['clipped_pixels']
            assert int(clipped.sum())==r['clipping']['clipped_channel_samples']
            generated=rgb.copy();generated[ref_mask]=np.rint(np.clip(raw[ref_mask],0,1)*255).astype(np.uint8)
            ip,mp=ROOT/r['input_path'],ROOT/r['input_mask_path']
            assert digest(ip)==r['input_sha256'] and digest(mp)==r['input_mask_sha256']
            image=cv2.imread(str(ip));mask=cv2.imread(str(mp),0)>0
            assert np.array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),generated)
            assert np.array_equal(generated[~ref_mask],rgb[~ref_mask])
            assert int(((generated==0)&(rgb>0))[ref_mask].sum())==r['newly_zero_channel_samples']
            if r['measurement']['status']=='success':
                stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
                f={name:float(stats[key]) for name,key in zip(FEATURES,FEATURE_KEYS)}
                f['input_mst_index']=lookup.label(f['input_ita_degrees'])-1
                selected=generated[mask]
                for channel,name in enumerate(['red','green','blue']):
                    f[f'input_{name}_zero_fraction']=float((selected[:,channel]==0).mean())
                    f[f'input_{name}_full_fraction']=float((selected[:,channel]==255).mean())
                assert f==r['features'];checked_features+=1
                screen=support_retention(ref_mask,mask,mask);assert screen==r['support_screen']
            if 'paper_target' in r:
                gamma,red,blue=r['paper_target']
                if variant in ['gamma_lighten','gamma_darken']:
                    assert r['paper_target']==[1/exponent,1.,1.]
                    restored=np.rint(np.power(generated.astype(float)/255,gamma)*255).astype(np.uint8)
                    error=float(np.abs(restored.astype(float)-rgb)[ref_mask].mean()/255)
                    assert error==r['inverse_rgb_mae_on_generation_support']
                else:
                    assert r['paper_target']==[1/r['target_fit']['parameters'][0],*r['target_fit']['parameters'][1:]]
                    support=ref_mask&mask;x=generated[support].astype(float)/255
                    corrected=np.clip(np.power(x,gamma)*[red,1.,blue],0,1)
                    error=float(np.abs(np.rint(corrected*255)-rgb[support].astype(float)).mean()/255)
                    assert abs(error-r['target_fit']['quantized_rgb_mae'])<1e-12
                checked_targets+=1
            expected=('input_failure_hold' if r['measurement']['status']!='success' else
                'target_unavailable_hold' if 'paper_target' not in r else
                'clipped_stress_pending_exact_mask_review' if r['clipping']['clipped_pixels'] else
                'unclipped_mask_screen_hold' if not r['support_screen']['screen_pass'] else 'primary_pending_exact_mask_review')
            assert r['lane']==expected and r['training_eligible'] is False and r['exact_input_mask_review']=='pending'
    assert read(out/'primary_review_queue.json')==[r for r in rows if r['lane']=='primary_pending_exact_mask_review']
    result=dict(status='pass',generated_image_replays=30,clipping_replays=30,input_feature_vectors=checked_features,
        direct_targets_verified=checked_targets,old26_sources_regenerated=0,correction_tree_fits=0,
        target_optimizer_refits=0,new_mask_approvals=0,new_fitting_admissions=0,reserved_pixel_access=0,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        verifier_sha256=digest(Path(__file__)))
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},indent=2))


if __name__=='__main__':main()
