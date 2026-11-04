"""Combined-region candidate pairs for6anchors; never fitting admission."""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.ita_estimation.semantic_measurement import measure,contract
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.face_neck_support import build_face_neck_support
from src.skin_masking.correction_facial_features import include_brows_lips
from src.utilities.config import get_config
from src.model_training.recovery_targets import fit_recovery_target
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters,transform_rgb
from src.evaluation.mask_support_quality import support_retention


def main(parent=None,out=None,peribrow=False):
    parent=parent or ROOT/'outputs/preferred_support_cohort_v1';out=out or ROOT/'outputs/preferred_support_pairs_v1'
    if out.exists():raise FileExistsError(out)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    refs=[r for r in read(parent/'records.json') if r['kind']=='anchor'];assert len(refs)==6
    oldplan=read(ROOT/'outputs/semantic_paired_preparation_v1/plan.json')
    groups={r['source_image_id']:r['severity'] for r in oldplan['sources']}
    identity=contract(ROOT)[1];lookup=DevelopmentMonotoneLookup(read(parent/'development_lookup.json'),identity)
    generation=importlib.import_module('333_prepare_semantic_pairs').generate
    files=[Path(__file__),ROOT/'scripts/333_prepare_semantic_pairs.py',parent/'records.json',parent/'development_lookup.json',
           ROOT/'docs/preferred-support-development-cycle-protocol.md']
    if peribrow:files.append(ROOT/'src/skin_masking/peribrow_correction.py')
    hashes={str(p):digest(p) for p in files}
    for ref in refs:
        hashes[str(ROOT/ref['input_path'])]=digest(ROOT/ref['input_path'])
        for name,path in ref['mask_paths'].items():
            assert digest(ROOT/path)==ref['mask_sha256'][name]
            hashes[str(ROOT/path)]=digest(ROOT/path)
    out.mkdir();(out/'images').mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='fixed_before_generation',anchor_ids=[r['image_id'] for r in refs],
        variants=oldplan['variants'],generation_region='face_neck_brows_lips_union',input_sha256=hashes,
        measurement_contract_sha256=identity,lookup_sha256=digest(parent/'development_lookup.json'),
        correction_mask_review='pending_do_not_fit',correction_tree_fits=0),indent=2),encoding='utf-8')
    prepare=importlib.import_module('11_prepare_training_manifests');config=get_config()
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def landmarks(im,box):
        pts,_,_=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        return None if pts is None else pts+np.array(box[:2])
    class Parser:
        def __init__(self):self.net=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx');self.last=None
        def categories_bgr(self,im):self.last=self.net.categories_bgr(im);return self.last
    parser=Parser();records=[];controls=[];replays=0
    for ref in refs:
        reference=cv2.imread(str(ROOT/ref['input_path']));rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB)
        genmask=cv2.imread(str(ROOT/ref['mask_paths']['combined']),0)>0
        controls.append(dict(source_image_id=ref['image_id'],input_path=ref['input_path'],
            reference_region_masks=ref['mask_paths'],features=ref['features'],target=[1.,1.,1.],
            correction_support_decision='pending',training_admitted=False))
        for variant in oldplan['variants']:
            generated,clipping,inverse=generation(rgb,genmask,groups[ref['image_id']],variant)
            bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR);measurement=measure(bgr,detector,landmarks,parser)
            stem=Path(ref['image_id']).stem+'_'+variant;ip=out/'images'/(stem+'.png')
            assert cv2.imwrite(str(ip),bgr)
            row=dict(case_id=stem,source_image_id=ref['image_id'],variant=variant,
                input_path=ip.relative_to(ROOT).as_posix(),input_sha256=digest(ip),
                reference_path=ref['input_path'],reference_region_masks=ref['mask_paths'],
                clipping=clipping,measurement=measurement.report,target=inverse,
                lane='processing_hold',training_admitted=False,mask_review='pending',
                reference_combined_mask_review='pending')
            if measurement.report['status']=='success':
                base=build_face_neck_support(bgr,measurement.mask,parser.last,face_count=1)
                if peribrow:
                    from src.skin_masking.peribrow_correction import include_features_and_peribrow
                    support=include_features_and_peribrow(base,parser.last)
                else:support=include_brows_lips(base,parser.last)
                mp=out/'images'/(stem+'_measurement_mask.png');cp=out/'images'/(stem+'_correction_mask.png')
                assert cv2.imwrite(str(mp),measurement.mask) and cv2.imwrite(str(cp),support.correction_mask)
                features=dict(measurement.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
                screen=support_retention(genmask,measurement.mask>0,support.correction_mask>0)
                # Measurement is intentionally FACE ONLY: do not apply the old
                # whole-generation facial-estimation retention gate to neck/lips.
                facegen=cv2.imread(str(ROOT/ref['mask_paths']['face']),0)>0
                facialscreen=support_retention(facegen,measurement.mask>0,support.correction_mask>0)
                correction_ok=all(not v['evaluated'] or v['correction_retention']>=.8 for v in screen['regions'].values())
                row.update(features=features,measurement_mask_path=mp.relative_to(ROOT).as_posix(),
                    correction_mask_path=cp.relative_to(ROOT).as_posix(),
                    measurement_mask_sha256=digest(mp),correction_mask_sha256=digest(cp),
                    facial_support_screen=facialscreen,combined_support_diagnostics=screen)
                if inverse is None:
                    fit=fit_recovery_target(generated,rgb,support.correction_mask>0,genmask);row['target_fit']=fit
                    if fit['parameters'] is not None:
                        p=legacy_to_paper_parameters(*fit['parameters']);row['target']=[p[k] for k in ['gamma','red_gain','blue_gain']]
                row['lane']='target_hold'
                if row['target'] is not None:
                    row['lane']=('support_hold' if not facialscreen['screen_pass'] or not correction_ok else
                        'clipped_stress_unreviewed' if clipping['clipped_channel_samples'] else 'primary_unreviewed')
                corrected=transform_rgb(generated.astype(float)/255,*row['target']) if row['target'] is not None else None
                if corrected is not None:
                    selected=genmask&(support.correction_mask>0)
                    row['target_reconstruction_rgb_mae']=float(np.abs(np.rint(corrected[selected]*255)-rgb[selected]).mean()/255)
            expected,_,_=generation(rgb,genmask,groups[ref['image_id']],variant)
            actual=cv2.cvtColor(cv2.imread(str(ip)),cv2.COLOR_BGR2RGB)
            assert np.array_equal(actual,expected) and np.array_equal(actual[~genmask],rgb[~genmask]);replays+=1
            records.append(row);print(stem,row['lane'],flush=True)
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    (out/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    summary=dict(status='candidate_pairs_prepared_not_admitted',sources=6,controls=6,variants=len(records),
        lanes=dict(Counter(r['lane'] for r in records)),generation_replays=replays,
        generation_and_scoring_regions='face_neck_brows_lips_separate_saved_regions',
        features_region='facial_skin_only',reference_combined_mask_approvals=0,input_mask_approvals=0,
        correction_tree_fits=0,reserved_pixel_access=0,demo_changed=False)
    (out/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
