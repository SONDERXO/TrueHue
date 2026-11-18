"""Record complete review provenance and one-source saved-mask diagnosis; no fits/edits."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,d):
    with Path(p).open('x',encoding='utf-8') as stream:json.dump(d,stream,indent=2,allow_nan=False);stream.write('\n')

def main():
    out=ROOT/'outputs/source_bagged_support_diagnosis_v1'
    if (out/'diagnosis_PRIVATE.json').exists():raise FileExistsError('Preserve prior diagnosis')
    comparison=ROOT/'outputs/source_bagged_source_held_v1'
    download=Path(r'C:\Users\NYTHAN\Downloads\correction-review-ratings (3).json')
    received=read(download);assert received['complete'] and len(received['ratings'])==44
    matches=[p for p in (comparison/'ratings').glob('*.json') if read(p)==received]
    assert len(matches)==3
    selected=comparison/'ratings/d52f3107e93c4886bc02198133e1d9a0.json';assert selected in matches
    assessment=read(comparison/'assessment_d52f3107e93c4886bc02198133e1d9a0.json')
    predictions=read(comparison/'predictions_PRIVATE.json');public=read(comparison/'review_public.json')
    assert received['protocol_id']==public['protocol_id'] and set(received['ratings'])=={c['id'] for c in public['cases']}
    counts={};independent_outcomes={}
    for p in predictions:
        r=received['ratings'][p['review_id']]
        if p['role']=='identity':outcome=r['identity']
        else:
            choice=r['preference']
            outcome=('output_preferred' if choice==p['output_panel'] else 'input_preferred') if choice in ['A','B'] else choice
        counts.setdefault(p['role'],Counter())[outcome]+=1;independent_outcomes[p['review_id']]=outcome
    assert independent_outcomes=={r['review_id']:r['outcome'] for r in assessment['outcomes']}
    assert assessment['development_status']=='NOTREADY' and assessment['numeric_families_pass']
    copy=out/'download_received_COMPLETE.json'
    with copy.open('xb') as stream:stream.write(download.read_bytes())
    plan=read(ROOT/'outputs/histogram_gap_source_held_design_v1/plan_PRIVATE.json')
    entry=next(s for s in plan['support_sources'] if s['source']=='ffhq_source_59807')
    annotation=Path(entry['annotation']);manifest=read(annotation/'manifest.json')
    inventory=read(ROOT/'outputs/ffhq_mask_support_v1/sha256.json')
    cached=ROOT/'outputs/ffhq_mask_support_v1/59807'
    support=ROOT/'outputs/histogram_gap_source_held_comparison_v1/supports/59807'
    receipt=read(support/'manifest_PRIVATE.json');bindings={}
    for name in ['input.png','categories.png']:
        path=cached/name;assert sha(path)==inventory['59807/'+name];bindings[str(path.relative_to(ROOT))]=sha(path)
    for name,h in receipt['files'].items():
        assert sha(support/name)==h;bindings[str((support/name).relative_to(ROOT))]=h
    for name in ['correction_mask.png','automatic_correction_mask.png','measurement_mask.png','protected_mask.png']:
        assert sha(annotation/name)==manifest['files'][name]['sha256']
        bindings[str((annotation/name).relative_to(ROOT))]=sha(annotation/name)
    mask=cv2.imread(str(support/'correction_mask.png'),0)>0
    cat=cv2.imread(str(cached/'categories.png'),0)
    alpha=np.load(support/'alpha.npy',allow_pickle=False)
    protection=cv2.imread(str(support/'protected_mask.png'),0)>0
    old=cv2.imread(str(annotation/'correction_mask.png'),0)>0
    automatic=cv2.imread(str(annotation/'automatic_correction_mask.png'),0)>0
    removed=automatic&~old
    classcounts=[]
    for k in sorted(set(cat.ravel().tolist())):
        # Independent scalar counts compared with vectorized diagnostics.
        total=sum(int(c)==k for c in cat.ravel().tolist())
        outside=sum(int(c)==k and not bool(m) for c,m in zip(cat.ravel().tolist(),mask.ravel().tolist()))
        assert total==int((cat==k).sum()) and outside==int(((cat==k)&~mask).sum())
        classcounts.append(dict(parser_class=k,total=total,outside_support=outside))
    width=max(2,math.ceil(entry['face_width']*.03))
    distance=cv2.distanceTransform(mask.astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
    t=np.clip(distance/width,0,1).astype(float)
    expected=t*t*(3-2*t);expected[~mask]=0
    assert np.array_equal(alpha,expected)
    outside_changes={}
    rows={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    for role in ['exposure_under','exposure_over']:
        r=rows['ffhq_59807__'+role];path=Path(r['pixels_file'])
        assert path.resolve()==(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'/r['case_id']/'paired_pixels.npz').resolve()
        assert sha(path)==r['pixels_sha256'];bindings[str(path.relative_to(ROOT))]=sha(path)
        with np.load(path,allow_pickle=False) as pack:
            changed=np.any(pack['input_rgb8']!=pack['reference_rgb8'],axis=2)
            outside_changes[role]=int((changed&~mask).sum())
    write_new(out/'review_provenance_PRIVATE.json',dict(complete=True,ratings=44,download_sha256=sha(download),
        downloaded_json_semantically_equal_to_saved=True,download_byte_equal_to_saved=download.read_bytes()==selected.read_bytes(),
        selected_revision=selected.name,selected_sha256=sha(selected),equivalent_saved_revisions=[p.name for p in matches],
        independent_AB_mapping_passed=True,outcomes={k:dict(v) for k,v in counts.items()},raw_comments_rewritten=False))
    write_new(out/'diagnosis_PRIVATE.json',dict(source='59807',screenshot_cases=['case-42','case-43'],
        scope='saved_arrays_and_codepath_diagnosis_not_mask_repair',
        bindings_checked_again_after_prior_visual_inspection=True,prospective_experiment_claimed=False,input_sha256=bindings,
        mask_pixels=int(mask.sum()),protected_pixels=int(protection.sum()),manual_removed_pixels=int(removed.sum()),
        automatic_equals_reviewed=bool(np.array_equal(old,automatic)),ear_added_pixels=int((mask&~old).sum()),
        alpha_band_width=width,feather_pixels=int(((alpha>0)&(alpha<1)).sum()),
        parser_class_counts=classcounts,outside_support_distorted_pixels=outside_changes,
        agent_viewed=['source_reference_contact.png','59807_support_board.png','59807_forehead_detail.png',
                      '59807_right_edge_detail.png','59807_neck_detail.png','59807_saved_review_pairs.png'],
        findings=['Upper forehead/hairline support ends below visible skin patches; adjacent parser hair labels prevent a simple add-all-skin fix.',
                  'All 9970 parser-skin pixels already included; 128 parser-neck pixels outside support, not independently validated anatomy.',
                  'Four-pixel inward alpha cannot expand missing coverage.',
                  'Whole-face support includes part of microphone and glasses; saved explicit protection is empty.',
                  'No manual brush removals explain this source; no prior edits discarded.'],
        mask_or_measurement_edits=0,new_model_fits=0,new_model_predictions=0,raw_original_reads=0,locked_reads=0))
    write_new(comparison/'final_development_assessment_PRIVATE.json',dict(development_status='FAIL_CLOSED_NOT_ADOPTED',
        selected_saved_revision=selected.name,selected_saved_sha256=sha(selected),assessment_file='assessment_'+selected.name,
        numeric_families_pass=True,visual_useful_colour=False,noticeable_identity_cases=7,
        visual_counts={k:dict(v) for k,v in counts.items()},
        support_feedback_separate=True,old_results_reclassified=False,new_fits_selected=False,model_adopted=False))
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    write_new(out/'verification_PRIVATE.json',dict(passed=True,download_semantic_match=True,independent_rating_mapping=True,
        scalar_class_counts=True,independent_alpha_replay=True,input_hashes_unchanged=True,
        new_fits=0,new_model_predictions=0,mask_edits=0,raw_original_or_locked_reads=0,
        artifact_sha256={p.name:sha(p) for p in out.iterdir() if p.is_file()}))
    print('PASS complete44review/independentmapping/59807mask+alpha+class diagnosis; ensemble FAIL/CLOSED/NOTADOPTED')

if __name__=='__main__':main()
