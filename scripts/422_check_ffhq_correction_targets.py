"""One fixed14-case/photo oracle diagnostic; no tree or MST training."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
import scipy
import skimage
from src.model_training.photographic_target_diagnostic import case_matrix,distort,metrics,PRESET
from src.model_training.blended_recovery_targets import fit_target,render_rgb8
from src.correction.seamless_blend import apply_blended

OUT=ROOT/'outputs/ffhq_correction_targets_v1'
PARENT=ROOT/'outputs/ffhq_clear_lens_correction_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,value):p.write_text(json.dumps(value,indent=2),encoding='utf-8')
def save(p,rgb):
    if not cv2.imwrite(str(p),cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)):raise IOError(str(p))
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    history=ROOT/'outputs/reusable_correction_preview_v1'
    hashes=read(history/'plan.json')['input_sha256']
    for p,h in read(history/'sha256.json').items():hashes[str(history/p)]=h
    for p in [Path(__file__),ROOT/'src/model_training/photographic_target_diagnostic.py',
        ROOT/'tests/test_photographic_target_diagnostic.py',ROOT/'docs/ffhq-correction-target-protocol-2026-11-05.md']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    parents=read(PARENT/'results.json')['records'];cases=case_matrix()
    assert len(parents)==12 and len(cases)==14
    OUT.mkdir()
    write(OUT/'plan.json',dict(input_sha256=hashes,cases=cases,sources=[r['id'] for r in parents],
        status='frozen_before_variants_and_target_fits',severity_preset=PRESET,
        severity_provenance='same_engineering_preset_for_all_NOT_MST_or_skin_group',
        fixed_source_alpha=True,input_support_recomputed=False,
        scoring='all_positive_source_correction_alpha',training_admitted=False,
        versions=dict(numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__,opencv=cv2.__version__)))
    records=[];cards=[];visual={k:[] for k in ['combined_cool_under','stress_combined_under']}
    for parent in parents:
        sid=parent['id'];folder=OUT/sid;folder.mkdir()
        reference=rgb(PARENT/sid/'input.png');alpha=np.load(PARENT/sid/'alpha.npy',allow_pickle=False)
        mask=alpha>0
        save(folder/'reference.png',reference)
        # Width is unchanged from the existing renderer contract.
        baseline=cv2.imread(str(ROOT/'outputs/ffhq_mask_support_v1'/sid/'baseline_mask.png'),0)
        _,xx=np.nonzero(baseline);width=int(xx.max()-xx.min()+1)
        correction=cv2.imread(str(PARENT/sid/'correction_mask.png'),0)
        veto=cv2.imread(str(PARENT/sid/'protected_mask.png'),0)>0
        neutral,checked,_=apply_blended(cv2.cvtColor(reference,cv2.COLOR_RGB2BGR),correction,[1.,1.,1.],face_width=width,protected=veto)
        assert np.array_equal(checked,alpha) and np.array_equal(neutral,cv2.cvtColor(reference,cv2.COLOR_RGB2BGR))
        sections=[]
        for case in cases:
            target=folder/case['id'];target.mkdir()
            rec=dict(source_id=sid,case=case,training_admitted=False,MST=None,
                source_alpha_path=str(PARENT/sid/'alpha.npy'),source_alpha_sha256=sha(PARENT/sid/'alpha.npy'),
                scoring_pixels=int(mask.sum()),status='failed')
            try:
                image,recipe,role=distort(reference,alpha,case)
                assert np.array_equal(image[~mask],reference[~mask])
                save(target/'distorted.png',image)
                rec.update(recipe=recipe,technical_role=role,input_metrics=metrics(image,reference,mask))
                fit=fit_target(image,reference,alpha,mask);rec['fit']=fit
                parameters=fit.get('parameters')
                if parameters is not None:
                    output=render_rgb8(image,alpha,parameters)
                    actual,actual_alpha,_=apply_blended(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),correction,
                        parameters,face_width=width,protected=veto)
                    assert np.array_equal(actual_alpha,alpha)
                    assert np.array_equal(output,cv2.cvtColor(actual,cv2.COLOR_BGR2RGB))
                    assert np.array_equal(output[~mask],reference[~mask])
                    assert np.array_equal(output[veto],reference[veto])
                    save(target/'recovery.png',output)
                    rec.update(status='target_available_not_admitted',output_metrics=metrics(output,reference,mask),
                        renderer_parity=True,outside_and_protected_unchanged=True)
                    board=np.hstack([reference,image,output]);save(target/'board.png',board)
                    if case['id'] in visual:
                        label=np.full((26,board.shape[1],3),255,np.uint8)
                        cv2.putText(label,sid+' '+case['id'],(6,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
                        visual[case['id']].append(np.vstack([label,cv2.cvtColor(board,cv2.COLOR_RGB2BGR)]))
                else:rec.update(status='target_unavailable',failure_reason=fit['status'])
            except (ValueError,RuntimeError,cv2.error) as error:rec['failure_reason']=str(error)
            rec['file_sha256']={p.name:sha(p) for p in target.iterdir() if p.is_file()}
            write(target/'record.json',rec)
            with (OUT/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(rec)+'\n')
            records.append(rec)
            sections.append('<h3>'+case['id']+'</h3><p>'+rec['status']+'</p><img src="'+sid+'/'+case['id']+'/board.png">')
            print(sid+' '+case['id']+' '+rec['status'],flush=True)
        cards.append('<section><h2>'+sid+' — retained diagnostic source, not admitted</h2>'+''.join(sections)+'</section>')
    for name,boards in visual.items():
        for i in range(0,len(boards),3):
            if not cv2.imwrite(str(OUT/(name+'_contact_'+str(i//3+1)+'.png')),np.vstack(boards[i:i+3])):raise IOError('Contact save failed')
    assert len(records)==168 and all(sha(p)==h for p,h in hashes.items())
    layers={}
    for layer in ['clean','core','composite_stress_design']:
        rows=[r for r in records if r['case']['layer']==layer];available=[r for r in rows if r['status']=='target_available_not_admitted']
        layers[layer]=dict(attempts=len(rows),available=len(available),unavailable=len(rows)-len(available),
            mean_scope='available_cases_only_with_failure_denominator_above',
            input_mae=float(np.mean([r['input_metrics']['rgb8_mae_codes'] for r in available])) if available else None,
            output_mae=float(np.mean([r['output_metrics']['rgb8_mae_codes'] for r in available])) if available else None,
            input_deltaE00=float(np.mean([r['input_metrics']['relative_deltaE00_mean'] for r in available])) if available else None,
            output_deltaE00=float(np.mean([r['output_metrics']['relative_deltaE00_mean'] for r in available])) if available else None,
            rgb8_mae_regressions=sum(r['output_metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in available),
            deltaE00_regressions=sum(r['output_metrics']['relative_deltaE00_mean']>r['input_metrics']['relative_deltaE00_mean'] for r in available),
            max_output_mae=max([r['output_metrics']['rgb8_mae_codes'] for r in available],default=None),
            clipped_cases=sum(r.get('recipe',{}).get('clipped_channel_samples',0)>0 for r in rows))
    result=dict(records=records,layers=layers,attempts=168,source_photos=12,verified_person_count=None,
        target_fit_attempts=sum(r['case']['layer']!='clean' for r in records),clean_shortcuts=12,
        new_model_inference=0,tree_fits=0,MST_fits=0,training_admissions=0,
        frozen_inputs_unchanged=True,automatic_predictions=False,input_support_recomputed=False)
    write(OUT/'results.json',result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Photographic correction targets</title>'+
        '<style>body{font:18px system-ui;max-width:1200px;margin:auto;padding:20px}img{width:100%}section{border-top:2px solid #aaa}</style>'+
        '<h1>Fixed photographic recovery diagnostic</h1><p>Original; synthetic distortion; target-aware fitted recovery. '+
        'These are oracle target fits, NOT learned predictions. Same12 unadmitted sources,14cases each. '+
        'Same engineering severity for every source, NOT an MST category. Synthesis/recovery share saved source alpha; '+
        'input-derived masking/measurement was not re-run. Skin/neck/reference/grouping issues remain.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Attribution and source limitations</a></p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


def verify():
    plan=read(OUT/'plan.json');result=read(OUT/'results.json')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    assert all(sha(OUT/p)==h for p,h in read(OUT/'sha256.json').items())
    checked=0
    for row in result['records']:
        folder=OUT/row['source_id']/row['case']['id']
        reference=rgb(folder.parent/'reference.png');image=rgb(folder/'distorted.png')
        alpha=np.load(row['source_alpha_path'],allow_pickle=False);mask=alpha>0
        assert metrics(image,reference,mask)==row['input_metrics']
        if row['status']=='target_available_not_admitted':
            output=rgb(folder/'recovery.png')
            assert np.array_equal(render_rgb8(image,alpha,row['fit']['parameters']),output)
            assert metrics(output,reference,mask)==row['output_metrics']
            assert np.array_equal(output[~mask],reference[~mask])
            if row['case']['layer']=='clean':assert np.array_equal(output,reference)
            checked+=1
    report=dict(attempts=len(result['records']),saved_recovery_and_metric_checks=checked,
        refits=0,artifact_and_frozen_input_hashes_unchanged=True)
    # Verification is separate from the frozen experiment package.
    destination=ROOT/'outputs/ffhq_correction_targets_verification_v1'
    destination.mkdir()
    write(destination/'verification.json',dict(report,parent_manifest_sha256=sha(OUT/'sha256.json')))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true')
    verify() if parser.parse_args().verify else prepare()
