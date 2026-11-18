"""One cached106-input assessment of a fixed, nonlearned highlight safety cap."""
from pathlib import Path
import base64
import hashlib
import json
import sys

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.exposure_headroom import cap_exposure_headroom
from src.model_training.luminance_chroma_operator import render_rgb8, decode, W
from src.evaluation.luminance_chroma_scalar import replay

OUT=ROOT/'outputs/wb314_exposure_headroom_assessment_v1'
DELIVERY=ROOT/'output/wb314-headroom-repair-preview-2026-11-19'
PROTOCOL=ROOT/'docs/wb314-highlight-headroom-repair-protocol-2026-11-19.md'


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False)
def embed(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
def data(row):
    with np.load(row['input_path'],allow_pickle=False) as z:
        image,alpha,protected=[z[k].copy() for k in ['input','alpha','protected']]
    with np.load(row['old_output_path'],allow_pickle=False) as z:old=z['candidate'].copy()
    return image,alpha,protected,old
def overflow(image,alpha,protected,p):
    chosen=(alpha>0)&~protected;q,g,r,b,s=p
    lower=np.maximum(image[chosen].astype(float)-.5,0)/255.
    power=np.power((decode(lower)*[r,1,b])@W,q)
    return int(np.count_nonzero(g*power>1))


def main():
    if OUT.exists() or DELIVERY.exists():raise FileExistsError('No repeated cap assessment')
    qa=read(ROOT/'outputs/wb314_exposure_headroom_generated_QA_v1/verification.json');assert qa['passed']
    assert qa['module_sha256']==sha(ROOT/'src/model_training/exposure_headroom.py')
    assert qa['test_sha256']==sha(ROOT/'tests/test_exposure_headroom.py')
    bindings={str(p):sha(p) for p in [Path(__file__),PROTOCOL,ROOT/'src/model_training/exposure_headroom.py',
        ROOT/'src/model_training/luminance_chroma_operator.py',ROOT/'src/evaluation/luminance_chroma_scalar.py',
        ROOT/'outputs/wb314_final_training_v1/model.json',ROOT/'outputs/wb314_final_training_v1/verification.json',
        ROOT/'outputs/wb314_final_training_v1/render_comparison.json']}
    rows=[]
    final=ROOT/'outputs/wb314_final_training_v1'
    for i,r in enumerate(read(final/'render_comparison.json')['records']):
        path=ROOT/'outputs/wb_feature_direct_prediction_v1/evaluation'/(r['case_id']+'.npz')
        dest=final/'evaluation'/(r['case_id']+'.npz');assert sha(dest)==r['saved_sha256']
        rows.append(dict(group='final66',key=r['case_id'],controls=r['controls'],input_path=str(path),old_output_path=str(dest)))
    for group,folder in [('synthetic20','wb314_mste_development_packet_v2_area'),('normal20','wb314_normal_photo_preview_v1')]:
        parent=ROOT/'outputs'/folder;seal=parent/'predictions_sealed.json';bindings[str(seal)]=sha(seal)
        for r in read(seal)['records']:
            path=parent/'evaluation'/(r['pair_id']+'.npz');assert sha(path)==r['evaluation_sha256']
            box=r.get('face_box')
            if box is None:box=read(parent/'references'/r['candidate_id']/'parent_report.json')['face_box']
            rows.append(dict(group=group,key=r['pair_id'],MST=r['MST'],controls=r['controls'],
                input_path=str(path),old_output_path=str(path),face_box=box))
    assert len(rows)==106
    for r in rows:
        for k in ['input_path','old_output_path']:bindings[r[k]]=sha(Path(r[k]))
    OUT.mkdir();(OUT/'evaluation').mkdir();write(OUT/'bindings.json',bindings)
    write(OUT/'plan.json',dict(cases=106,fixed_rule='quantized_luminance_headroom_v1',
        new_model_calls=0,new_fits=0,source_JPEG_decodes=0,old86_exact_parity_required=True,
        no_threshold_or_formula_retry=True))
    write(OUT/'user_authorization.json',dict(reply='alright lets do that then',
        scope='Address demonstrated normal-photo unnecessary brightening using a bounded supported repair; no new training or source queue.'))
    controls=[]
    for r in rows:
        image,alpha,protected,old=data(r)
        controls.append(dict(r,guard=cap_exposure_headroom(image,alpha,protected,r['controls'])))
    write(OUT/'controls_sealed.json',dict(records=controls,sealed_before_candidate_renders=True,new_model_calls=0,new_fits=0))
    results=[];scalar_checks=0
    for i,r in enumerate(controls):
        image,alpha,protected,old=data(r);before=[a.tobytes() for a in [image,alpha,protected]]
        effective=r['guard']['effective_controls'];candidate=render_rgb8(image,alpha,protected,effective)
        if r['guard']['applied']:
            scalar,_=replay(image,image,alpha,protected,effective)
            assert np.array_equal(scalar,candidate);scalar_checks+=1
        assert before==[a.tobytes() for a in [image,alpha,protected]]
        assert np.array_equal(candidate[protected],image[protected]) and np.array_equal(candidate[alpha==0],image[alpha==0])
        p=OUT/'evaluation'/f'{i:03d}.npz';np.savez(p,candidate=candidate)
        results.append(dict(group=r['group'],key=r['key'],guard=r['guard'],output_path=str(p),output_sha256=sha(p),
            exact_previous_output=bool(np.array_equal(candidate,old)),old_exact_input=bool(np.array_equal(old,image)),
            new_exact_input=bool(np.array_equal(candidate,image)),raw_definite_overflow=overflow(image,alpha,protected,r['controls']),
            guarded_definite_overflow=overflow(image,alpha,protected,effective)))
    groups={g:[r for r in results if r['group']==g] for g in ['final66','synthetic20','normal20']}
    target=[r for r in groups['normal20'] if r['key'] in ['image_pair_01','image_pair_02']]
    gates=dict(final66_exact=all(r['exact_previous_output'] for r in groups['final66']),
        synthetic20_exact=all(r['exact_previous_output'] for r in groups['synthetic20']),
        original10_normal_identities_preserved=all(r['new_exact_input'] for r in groups['normal20'] if r['old_exact_input']),
        both_normal01_02_capped=len(target)==2 and all(r['guard']['applied'] for r in target),
        both_normal01_02_definite_overflow_removed=all(r['raw_definite_overflow']>0 and r['guarded_definite_overflow']==0 for r in target),
        normal_overflow_not_increased=all(r['guarded_definite_overflow']<=r['raw_definite_overflow'] for r in groups['normal20']))
    summary=dict(passed=all(gates.values()),gates=gates,cases=106,
        changed_outputs_by_group={g:sum(not r['exact_previous_output'] for r in rr) for g,rr in groups.items()},
        capped_controls_by_group={g:sum(r['guard']['applied'] for r in rr) for g,rr in groups.items()},
        new_model_calls=0,new_fits=0,scalar_changed_control_checks=scalar_checks,protected_outside_checks=106,
        raw_and_guarded_normal_target_overflow=[dict(key=r['key'],raw=r['raw_definite_overflow'],guarded=r['guarded_definite_overflow']) for r in target],
        auto_wrapper_integration_permitted=all(gates.values()),original_tree_unchanged=True,
        all_normal_correction_necessity_solved=False,new_human_ratings=0,scientific_or_final_adoption=False)
    write(OUT/'summary.json',summary);write(OUT/'results_PRIVATE.json',results)
    DELIVERY.mkdir();(DELIVERY/'triples').mkdir();sections=[]
    for r,result in zip(controls,results):
        if r['group']!='normal20':continue
        image,alpha,protected,old=data(r)
        with np.load(result['output_path'],allow_pickle=False) as z:guarded=z['candidate']
        x,y,w,h=r['face_box'];triple=np.concatenate([a[y:y+h,x:x+w] for a in [image,old,guarded]],axis=1)
        large=np.repeat(np.repeat(triple,4,axis=0),4,axis=1);path=DELIVERY/'triples'/(r['key']+'.png');Image.fromarray(large).save(path)
        sections.append(f'<section><h2>{r["key"]}</h2><p>Original normal input | Previous model result | Headroom-capped result</p>'
            f'<p>Cap applied: {r["guard"]["applied"]}; reason: {r["guard"]["reason"]}</p><div style="overflow-x:auto">'
            f'<img width="{w*12}" height="{h*4}" src="{embed(path)}" alt="Original, old correction, guarded correction"></div></section>')
    page=('<!doctype html><meta charset="utf-8"><title>Highlight-headroom repair assessment</title>'
        '<style>body{font:18px system-ui;max-width:1200px;margin:24px auto;padding:0 20px}section{border-top:1px solid #aaa;margin:28px 0}'
        'img{max-width:none;image-rendering:pixelated}</style><h1>Headroom-cap assessment</h1>'
        f'<p><strong>Required technical screen passed: {summary["passed"]}.</strong> '
        'This is a fixed mathematical safety-policy assessment, not proof of normal-photo quality or a finished model.</p>'
        '<p>The old model weights and features are unchanged. Existing outputs must pass the declared parity gates before wrapper integration. '
        'A brightness cap cannot decide whether every correction is needed. No new ratings or expert responses are assumed.</p>'+''.join(sections))
    (DELIVERY/'START_HERE.html').write_text(page,encoding='utf-8');write(DELIVERY/'SUMMARY.json',summary)
    for path,digest in bindings.items():assert sha(Path(path))==digest
    write(OUT/'verification.json',dict(completed=True,technical_checks_pass=True,screen_pass=summary['passed'],new_model_calls=0,new_fits=0,
        artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
