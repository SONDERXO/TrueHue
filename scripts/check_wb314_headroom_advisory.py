"""Verify non-replacing integration with cached106-case base-result replays.

The base stub returns the actual saved features/controls/outputs. No new trained
predictor/encoder forwards occur. Native construction is checked without calling
correction. The primary and candidate are verified separately.
"""
from pathlib import Path
import base64
import json
import sys

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from wb314_headroom_advisory import WB314WithHeadroomAdvisory
from assess_wb314_facial_headroom import measurement
from assess_wb314_exposure_headroom import data,read,sha,write

PARENT=ROOT/'outputs/wb314_facial_headroom_assessment_v1'
OUT=ROOT/'outputs/wb314_headroom_advisory_integration_v1'
DELIVERY=ROOT/'output/wb314-headroom-advisory-2026-11-19'


class CachedBase:
    def __init__(self,row,output,features,leaf):
        self.row=row;self.output=output;self.features=features;self.leaf=leaf;self.calls=0
    def correct(self,image,m,a,p):
        self.calls+=1
        return dict(output=self.output.copy(),controls=self.row['controls'].copy(),
            features=self.features.copy(),leaf=self.leaf,qualification_complete=False,
            model_sha256='7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f')


def main():
    if OUT.exists() or DELIVERY.exists():raise FileExistsError('Preserve previous integration receipt')
    approval=read(ROOT/'outputs/wb314_headroom_advisory_authorization_v1/scope.json')
    assert approval['primary_image_must_be_exact_previous_output'] and not approval['new_guard_variant']
    scoped=read(PARENT/'summary.json');assert scoped['passed'] is False
    rows=read(PARENT/'controls_sealed.json')['records'];outcomes=read(PARENT/'results_PRIVATE.json')
    assert len(rows)==len(outcomes)==106
    qa=read(ROOT/'outputs/wb314_headroom_advisory_authorization_v1/generated_QA.json');assert qa['passed']
    assert qa['wrapper_sha256']==sha(ROOT/'scripts/wb314_headroom_advisory.py')
    assert qa['test_sha256']==sha(ROOT/'tests/test_wb314_headroom_advisory.py')
    features={}
    wb=ROOT/'outputs/wb_feature_direct_prediction_v1'
    leaves={r['case_id']:r['leaf'] for r in read(ROOT/'outputs/wb314_final_training_v1/training_predictions.json')}
    for r in read(wb/'rows.json'):features[('final66',r['case_id'])]=(r['x314'],leaves[r['case_id']])
    for group,name in [('synthetic20','wb314_mste_development_packet_v2_area'),('normal20','wb314_normal_photo_preview_v1')]:
        for r in read(ROOT/'outputs'/name/'predictions_sealed.json')['records']:
            features[(group,r['pair_id'])]=(r['features'],r['leaf'])
    bindings={str(p):sha(p) for p in [Path(__file__),ROOT/'scripts/wb314_headroom_advisory.py',
        ROOT/'tests/test_wb314_headroom_advisory.py',ROOT/'src/model_training/facial_exposure_headroom.py',
        PARENT/'summary.json',PARENT/'controls_sealed.json',PARENT/'results_PRIVATE.json',
        ROOT/'outputs/wb314_headroom_advisory_authorization_v1/scope.json']}
    for p,h in read(PARENT/'bindings.json').items():assert sha(Path(p))==h
    OUT.mkdir();write(OUT/'bindings.json',bindings)
    DELIVERY.mkdir();(DELIVERY/'primary-pairs').mkdir();(DELIVERY/'candidate-pairs').mkdir()
    records=[];sections=[];cache={};candidate_differences=0
    for r,s in zip(rows,outcomes):
        assert (r['group'],r['key'])==(s['group'],s['key'])
        image,alpha,protected,old=data(r);m=measurement(r,cache)
        x,leaf=features[(r['group'],r['key'])]
        obj=WB314WithHeadroomAdvisory.__new__(WB314WithHeadroomAdvisory)
        obj.base=CachedBase(r,old,x,leaf)
        immutable=[a.tobytes() for a in [image,m,alpha,protected]]
        result=obj.correct(image,m,alpha,protected)
        assert obj.base.calls==1 and result['headroom_applied_to_primary'] is False
        assert np.array_equal(result['output'],old) and result['controls']==r['controls']
        assert result['features']==x and result['leaf']==leaf
        assert result['headroom_advisory']['available']
        assert result['headroom_candidate_controls']==r['facial_guard']['effective_controls']
        with np.load(s['output_path'],allow_pickle=False) as z:expected=z['candidate'].copy()
        assert np.array_equal(result['headroom_candidate'],expected)
        assert not np.shares_memory(result['output'],result['headroom_candidate'])
        assert immutable==[a.tobytes() for a in [image,m,alpha,protected]]
        differs=bool(np.any(old!=expected));candidate_differences+=differs
        records.append(dict(group=r['group'],key=r['key'],primary_exact=True,controls_and_features_exact=True,
            candidate_exact_existing_scoped=True,alternative_differs=differs))
        if r['group']!='normal20':continue
        xx,yy,w,h=r['face_box'];name=r['key']+'.png'
        primary=np.concatenate([a[yy:yy+h,xx:xx+w] for a in [image,result['output']]],axis=1)
        p=DELIVERY/'primary-pairs'/name
        Image.fromarray(np.repeat(np.repeat(primary,4,axis=0),4,axis=1)).save(p)
        title=f'Normal photo {int(r["key"].split("_")[-1]):02d}'
        section=f'<section><h2>{title}</h2><p><strong>Original input (left) | Main model result (right, unchanged)</strong></p>'
        section+=f'<img width="{w*8}" height="{h*4}" src="data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}" alt="Input and unchanged primary correction">'
        if differs:
            candidate=np.concatenate([a[yy:yy+h,xx:xx+w] for a in [image,expected]],axis=1)
            q=DELIVERY/'candidate-pairs'/name
            Image.fromarray(np.repeat(np.repeat(candidate,4,axis=0),4,axis=1)).save(q)
            section+='<details><summary>Separate highlight-headroom candidate — not applied to the main result</summary>'
            section+=f'<p>Original input left | Protected candidate right. This alternative can look dimmer.</p><img width="{w*8}" height="{h*4}" src="data:image/png;base64,{base64.b64encode(q.read_bytes()).decode()}" alt="Input and separate headroom candidate"></details>'
        else:section+='<p>The scoped check proposes no different result for this image.</p>'
        sections.append(section+'</section>')
    # Asset/configuration construction only: intentionally no correction call.
    native=WB314WithHeadroomAdvisory();assert native.base.model['dimensions']==314
    summary=dict(passed=True,cached_cases=106,primary_RGB8_exact_previous=106,
        primary_controls_features_exact=106,candidate_exact_existing_scoped_outputs=106,
        separate_candidate_differences=candidate_differences,input_immutability_checks=106,
        primary_and_candidate_arrays_independent=True,native_constructor_without_inference=True,
        cached_base_replay_calls=106,new_trained_model_or_encoder_inference=0,new_fits=0,
        new_guard_variant=False,headroom_applied_to_primary=False,automatic_highlight_repair=False,
        original_scoped_screen_pass=False,primary_policy='unchanged_frozen_tree',
        advisory_policy='facial_measurement_luminance_headroom_v1',
        model_sha256=scoped['model_sha256'],primary_pipeline_qualification_complete=False,
        Android_defaults_changed=False,expert_Form_changed=False,new_human_ratings=0)
    write(OUT/'summary.json',summary);write(OUT/'records_PRIVATE.json',records)
    page=('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Previous model edits retained, headroom advisory separate</title>'
        '<style>body{font:18px system-ui;max-width:1100px;margin:24px auto;padding:0 20px}img{max-width:100%;height:auto;image-rendering:pixelated}'
        'section{border-top:1px solid #aaa;margin:28px 0}details{margin:16px 0}summary{cursor:pointer}.note{padding:16px;background:#edf3f7}</style>'
        '<h1>Previous edits retained</h1><div class="note"><p><strong>The main result remains exactly the previous model output.</strong></p>'
        '<p>The facial headroom check is integrated as a separate advisory/candidate. It is not automatically applied to the main image. '
        'Open a candidate only where one differs. No new model training or guard rule was introduced.</p></div>'
        '<p>This preserves the previous look, including its existing highlight behaviour. It does not claim that automatic overcorrection is solved. '
        'The existing scoped cap screen still failed one exact normal expectation; no old result is retroactively marked passed. '
        'Images remain256px analysis with4xviewing copies, not new HD detail.</p>'+''.join(sections))
    (DELIVERY/'START_HERE.html').write_text(page,encoding='utf-8')
    (DELIVERY/'README.txt').write_text('Research integration: primary edits unchanged; headroom candidate separate.\n\n'
        'Use scripts/wb314_headroom_advisory.py: WB314WithHeadroomAdvisory.correct(...). '
        'output and controls remain the frozen model result. headroom_candidate and headroom_candidate_controls '
        'contain the separate scoped proposal. headroom_advisory reports availability and its reason; '
        'headroom_applied_to_primary is always false. Do not call this automatic highlight protection or mix '
        'per-image alternatives into an undeclared automatic evaluation policy.\n\n'
        'No Android/app default, expert Form or final qualification change has occurred.\n',encoding='utf-8')
    write(DELIVERY/'SUMMARY.json',summary)
    for p,h in bindings.items():assert sha(Path(p))==h
    write(OUT/'verification.json',dict(passed=True,artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()},
        source_sha256=sha(Path(__file__)),wrapper_sha256=sha(ROOT/'scripts/wb314_headroom_advisory.py')))
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
