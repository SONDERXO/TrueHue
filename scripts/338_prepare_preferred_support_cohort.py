"""Freeze12additional sources, package development MST, prepare18region records."""
from collections import Counter,defaultdict
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.ita_estimation.semantic_measurement import contract,measure
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.face_neck_support import build_face_neck_support
from src.skin_masking.correction_facial_features import include_brows_lips


def main():
    out=ROOT/'outputs/preferred_support_cohort_v1'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    hashes={}
    def read(rel):
        p=ROOT/rel;hashes[rel]=digest(p);return json.loads(p.read_text(encoding='utf-8'))
    allocation=read('outputs/correction_data_redesign_v1/selection.json')
    policy=read('outputs/correction_data_redesign_v1/access_policy.json')
    inv=read('outputs/independent_source_inventory_v1/fairface_inventory.json')
    oldgroups={r['source_image_id'] for r in read('outputs/reviewed_source_evidence32_v1/registry.json')['rows']}
    dispositions={r['image_id']:r for r in read('outputs/correction_duplicate_audit_v1/candidate_dispositions.json')}
    pool=[r for r in inv if r['image_id'] not in oldgroups and not r['scoped_review_evidence']
          and r['reference_status']=='success' and r['duplicate_status']=='screen_clear_unreviewed']
    bins={}
    for group in ['light','medium','dark']:
        bins[group]=sorted([r for r in pool if r['experimental_severity']==group],
            key=lambda r:hashlib.sha256(('preferred-support-v1/'+r['image_id']).encode()).hexdigest())
    selected=[]
    while len(selected)<12 and any(bins.values()):
        for group in bins:
            if bins[group] and len(selected)<12:selected.append(bins[group].pop(0))
    assert len(selected)==12
    for row in selected:
        training_candidate(row['image_id'],allocation,policy)
        assert dispositions[row['image_id']]['status']=='screen_clear_unreviewed'
    anchors=read('outputs/semantic_reference_readiness_v1/manifest.json')['rows']
    imported=read('outputs/semantic_reference_mask_import_v1/decisions.json')
    assert all(r['mask_decision']=='accept' for r in imported)
    identity=contract(ROOT)[1]
    for p in [Path(__file__),ROOT/'docs/preferred-support-development-cycle-protocol.md',
        ROOT/'src/skin_masking/face_neck_support.py',ROOT/'src/skin_masking/correction_facial_features.py']:
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
    correction_id=hashlib.sha256(json.dumps({p:h for p,h in hashes.items() if p.startswith('src/skin_masking/')},sort_keys=True).encode()).hexdigest()
    out.mkdir();(out/'references').mkdir()
    plan=dict(status='frozen_before_new_pixels_and_mapping_packaging',selected=selected,
        pool_size=len(pool),anchors=[r['source_image_id'] for r in anchors],
        measurement_contract_sha256=identity,correction_support_sha256=correction_id,
        input_sha256=hashes,comparison_protocol='docs/preferred-support-development-cycle-protocol.md',
        training_admitted=False,reserved_roles_locked=True)
    (out/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    # One explicitly experimental all-row fit, not correction-tree training.
    mapping=read('outputs/semantic_mst_measurement_v1/summary.json')
    evaluation=read('outputs/semantic_mst_calibration_v1/summary.json')
    rows=[r for r in mapping['records'] if r['status']=='success'];assert len(rows)==393
    assert mapping['measurement_contract_sha256']==evaluation['measurement_contract_sha256']==identity
    counts=Counter(r['subject_id'] for r in rows)
    model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
    model.fit([r['features']['input_ita_degrees'] for r in rows],[r['source_mst_label'] for r in rows],
              sample_weight=[1/counts[r['subject_id']] for r in rows])
    payload=dict(schema_version='truehue_development_monotone_mst_v1',status='experimental_not_final_validated',
        measurement_contract_sha256=identity,ita_knots=model.X_thresholds_.tolist(),mst_knots=model.y_thresholds_.tolist(),
        rounding='floor_plus_half',outside_range='clip',quality=evaluation['metrics']['overall'],
        calibration_subjects=sorted(counts),calibration_images=len(rows),calibration_masks='unreviewed',
        allowed_use='declared_preferred_support_development_cycle_only_not_deployment',
        evaluation_summary_sha256=digest(ROOT/'outputs/semantic_mst_calibration_v1/summary.json'))
    lookup=DevelopmentMonotoneLookup(payload,identity)
    vectors=[r['features']['input_ita_degrees'] for r in rows]+[-90.,90.]
    assert np.allclose([lookup.continuous(x) for x in vectors],model.predict(vectors),rtol=0,atol=1e-12)
    payload['fitted_label_range']=[lookup.label(90),lookup.label(-90)]
    (out/'development_lookup.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    prepare=importlib.import_module('11_prepare_training_manifests');config=get_config()
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def landmarks(im,box):
        points,_,_=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        return None if points is None else points+np.array(box[:2])
    class Parser:
        def __init__(self):self.net=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx');self.last=None
        def categories_bgr(self,im):self.last=self.net.categories_bgr(im);return self.last
    parser=Parser();records=[]
    cases=[dict(image_id=r['source_image_id'],path=r['source_path'],kind='anchor',
                original_source_decision=r['prior_source_decision'],approved_face_mask=r['mask_path']) for r in anchors]
    cases += [dict(image_id=r['image_id'],path=training_candidate(r['image_id'],allocation,policy)['relative_image_path'],
                   kind='new_candidate',original_source_decision=None,approved_face_mask=None) for r in selected]
    for case in cases:
        path=ROOT/case['path'];rawhash=digest(path)
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(
            image_id=case['image_id'],role='train',phase='preferred_support_reference_preparation',source_sha256=rawhash))+'\n')
        measured=measure(cv2.imread(str(path)),detector,landmarks,parser)
        rec=dict(case,source_sha256=rawhash,measurement=measured.report,training_admitted=False,
                 person_independence='not_verified',previous_pixel_exposure='development_exposed')
        if measured.report['status']=='success':
            face=measured.mask
            if case['approved_face_mask']:
                assert np.array_equal(face,cv2.imread(str(ROOT/case['approved_face_mask']),0))
            base=build_face_neck_support(measured.image,face,parser.last,face_count=1)
            support=include_brows_lips(base,parser.last)
            masks={'face':face,'neck':support.neck_mask,
                   'brows':((support.correction_mask>0)&(base.correction_mask==0)&np.isin(parser.last,[2,3])).astype(np.uint8)*255,
                   'lips':((support.correction_mask>0)&(base.correction_mask==0)&np.isin(parser.last,[12,13])).astype(np.uint8)*255,
                   'combined':support.correction_mask}
            folder=out/'references'/Path(case['image_id']).stem;folder.mkdir()
            assert cv2.imwrite(str(folder/'input.png'),measured.image)
            for name,array in masks.items():assert cv2.imwrite(str(folder/(name+'.png')),array)
            assert cv2.imwrite(str(folder/'categories.png'),parser.last)
            features=dict(measured.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
            overlay=measured.image.copy()
            for name,color in [('face',[0,255,0]),('neck',[255,255,0]),('brows',[255,0,255]),('lips',[255,0,255])]:
                chosen=masks[name]>0;overlay[chosen]=np.rint(.5*overlay[chosen]+.5*np.array(color)).astype(np.uint8)
            board=folder/'board.png';assert cv2.imwrite(str(board),np.hstack((measured.image,overlay,cv2.cvtColor(face,cv2.COLOR_GRAY2BGR),cv2.cvtColor(masks['combined'],cv2.COLOR_GRAY2BGR))))
            rec.update(features=features,board_path=board.relative_to(out).as_posix(),
                input_path=(folder/'input.png').relative_to(ROOT).as_posix(),
                mask_paths={k:(folder/(k+'.png')).relative_to(ROOT).as_posix() for k in masks},
                region_pixels={k:int((v>0).sum()) for k,v in masks.items()},
                mask_sha256={k:digest(folder/(k+'.png')) for k in masks},
                source_decision='retained_accept' if case['kind']=='anchor' else 'pending',
                measurement_mask_decision='retained_accept' if case['kind']=='anchor' else 'pending',
                correction_mask_decision='pending')
        records.append(rec);print(case['image_id'],measured.report['status'],flush=True)
    assert contract(ROOT)[1]==identity
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    summary=dict(status='reference_candidates_prepared_not_approved',anchors=6,new_candidates=12,
        available=sum(r['measurement']['status']=='success' for r in records),failures=sum(r['measurement']['status']!='success' for r in records),
        engineering_severity=dict(Counter(r['experimental_severity'] for r in selected)),
        new_allrow_mapping_fits=1,correction_tree_fits=0,reserved_pixel_access=0,new_approvals=0,
        lookup_sha256=digest(out/'development_lookup.json'),lookup_final_validated=False,demo_changed=False,
        input_sha256=hashes)
    (out/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
