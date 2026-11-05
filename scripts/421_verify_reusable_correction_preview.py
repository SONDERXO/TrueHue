"""All12 saved-input regression plus remaining-issue ledger; no inference."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.skin_masking.correction_preview import render_preview

api=importlib.import_module('419_preview_object_protected_face')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=ROOT/'outputs/reusable_correction_preview_v1'
OLD=ROOT/'outputs/ffhq_clear_lens_correction_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    previous=read(OLD/'results.json');hashes=read(OLD/'plan.json')['input_sha256']
    for p,h in read(OLD/'sha256.json').items():hashes[str(OLD/p)]=h
    for p in [Path(__file__),ROOT/'scripts/419_preview_object_protected_face.py',ROOT/'scripts/420_run_preview_faceocc.py',
        ROOT/'src/skin_masking/correction_preview.py',ROOT/'tests/test_correction_preview.py',
        ROOT/'docs/reusable-correction-preview-protocol-2026-11-05.md',
        ROOT/'outputs/ffhq_mask_support_assessment_v1/assessment.json']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    OUT.mkdir();api.write(OUT/'plan.json',dict(input_sha256=hashes,new_inference=0,
        status='frozen_before_saved_replay',glasses_choice_source='prior_assistant_visual_designations_not_user_answers_or_classifier'))
    issues={r['id']:r for r in read(ROOT/'outputs/ffhq_mask_support_assessment_v1/assessment.json')['records']}
    records=[];cards=[];mode_checks=[]
    for old in previous['records']:
        sid=old['id'];data=api.load_saved_case(sid);image,facial,categories,points,visible,metadata=data
        mode='clear' if old['transparent_glasses'] else 'uncertain'
        result=render_preview(image,facial,categories,points,visible,glasses=mode)
        assert np.array_equal(result.support.correction_mask,cv2.imread(str(OLD/sid/'correction_mask.png'),0))
        assert np.array_equal(result.alpha,np.load(OLD/sid/'alpha.npy',allow_pickle=False))
        assert np.array_equal(result.output,cv2.imread(str(OLD/sid/'operator_demo.png')))
        assert not result.alpha[result.protected].any()
        assert np.array_equal(result.output[result.protected],image[result.protected])
        api.write_preview(OUT/sid,image,result,dict(metadata,glasses_choice_provenance='prior_assistant_designation'))
        if categories.max()>=6 and (categories==6).any():
            uncertain=render_preview(image,facial,categories,points,visible)
            opaque=render_preview(image,facial,categories,points,visible,glasses='opaque')
            assert uncertain.report['requires_glasses_choice']
            assert np.array_equal(uncertain.alpha,opaque.alpha)
            mode_checks.append(dict(id=sid,uncertainty_visible=True,uncertain_equals_opaque=True))
            api.write_preview(OUT/(sid+'_uncertain'),image,uncertain,dict(metadata,glasses_choice_provenance='uncertainty_software_check'))
        rec=dict(id=sid,status='saved_parity_verified',glasses_choice=mode,
            requires_glasses_choice=result.report['requires_glasses_choice'],training_admitted=False,
            measurement_concern=issues[sid]['measurement_observation'],source_limitation=issues[sid]['source_limitation'],
            remaining_support_concern=issues[sid]['correction_observation'],
            issue_scope='retained_prior_observations_not_new_annotations_or_admission')
        records.append(rec)
        cards.append('<h2>'+sid+'</h2><p>Choice: '+mode+'; exact saved mask/alpha/output parity.</p>'+ 
                     '<img src="'+sid+'/board.png">')
    assert all(sha(p)==h for p,h in hashes.items())
    result=dict(records=records,saved_cases=12,exact_mask_alpha_RGB8_parities=12,
        glasses_uncertainty_checks=mode_checks,new_inference=0,MST_fits=0,target_fits=0,tree_fits=0,
        admissions=0,automatic_glasses_classifier=False,prior_packages_and_pinned_inputs_unchanged=True)
    api.write(OUT/'results.json',result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Reusable correction preview checks</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Reusable preview: all12 saved regressions</h1><p>No new inference/training. Explicit clear/opaque/uncertain choice; '+
        'uncertain keeps glasses protected and flags a required choice. Choices here reuse prior assistant designations, '+
        'not user answers or automatic classification. Panels: input; correction; baseline measurement; lens/rim detail; fixed illustration.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Source attribution</a> · '+
        '<a href="results.json">Remaining beard/hair/neck/reference issues</a></p>'+''.join(cards),encoding='utf-8')
    api.write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':main()
