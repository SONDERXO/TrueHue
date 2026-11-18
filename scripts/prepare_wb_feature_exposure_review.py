"""Fixed risk-plus-hash screen, existing verified outputs only."""
import ast
import base64
import json
from pathlib import Path
import numpy as np
from PIL import Image
from prepare_wb_feature_colour_review import ROOT,read,write,sha,literal

def main():
    run=ROOT/'outputs/wb_feature_direct_prediction_v1';out=ROOT/'outputs/wb_feature_exposure_review_v1'
    if out.exists():raise FileExistsError(out)
    identity=ROOT/'outputs/wb_feature_identity_ratings_v1/assessment_PRIVATE.json'
    corrected=ROOT/'outputs/wb_feature_colour_user_correction_v1'
    assert read(identity)['status']=='complete_acceptable'
    assert read(corrected/'verification_PRIVATE.json')['passed']
    assert read(corrected/'assessment_PRIVATE.json')['preference_counts']['candidate']==11
    raw=ROOT/'outputs/wb_feature_colour_ratings_v1/raw_user_review_PRIVATE.json'
    assert sha(raw)==read(corrected/'assessment_PRIVATE.json')['parent_raw_sha256']
    proof_path=run/'verification.json';proof=read(proof_path);assert proof['passed'] and proof['candidate_numeric_eligible']
    hashes={p.replace('\\','/'):h for p,h in proof['artifacts'].items()}
    assert sha(run/'records.json')==hashes['records.json']
    rows=read(run/'records.json');selected=[]
    for role in ['exposure_under','exposure_over','combined_under','combined_over']:
        own=[r for r in rows if r['role']==role];assert len(own)==11
        worst=min(own,key=lambda r:(-r['regions']['primary']['314']['RGB'],r['case_id']))
        others=[r for r in own if r['source_id']!=worst['source_id']]
        import hashlib
        other=min(others,key=lambda r:(hashlib.sha256(('truehue_wb314_exposure_screen_20261116|'+r['case_id']).encode()).hexdigest(),r['case_id']))
        for reason,r in [('largest_primary_RGB_residual',worst),('fixed_hash_other_source',other)]:
            selected.append(dict(case_id=r['case_id'],source_id=r['source_id'],role=role,selection=reason,primary_RGB=r['regions']['primary']['314']['RGB']))
    assert len({r['case_id'] for r in selected})==8
    packs={r['case_id']:run/'evaluation'/(r['case_id']+'.npz') for r in selected}
    for p in packs.values():assert sha(p)==hashes[p.relative_to(run).as_posix()]
    old=ROOT/'scripts/prepare_frozen_neighbour_colour_review.py'
    js=literal(old,'SCRIPT')
    ns={'IDENTITY_TEMPLATE':literal(ROOT/'scripts/prepare_frozen_neighbour_identity_review.py','TEMPLATE'),'SCRIPT':js}
    function=next(n for n in ast.parse(old.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='template')
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(old),'exec'),ns)
    template=ns['template']()
    for a,b in [('Colour correction usefulness','Exposure correction usefulness'),('Colour correction: is the improvement useful?','Exposure correction: is the improvement useful?'),
                ("skin's colour and overall appearance","skin's exposure, colour and overall appearance"),('All 11 cases recorded.','All 8 cases recorded.'),
                ('This page contains 11 colour cases; exposure correction is assessed separately.','This page contains 8 exposure and combined-correction cases.'),
                ('truehue_colour_usefulness_review_v1','truehue_exposure_usefulness_review_v1'),('colour_usefulness_and_appearance','exposure_usefulness_and_appearance'),
                ('truehue_colour_','truehue_wb_exposure_'),('truehue-colour-usefulness-review.json','truehue-wb-feature-exposure-review.json'),
                ('colour-review-QA.json','exposure-review-QA.json')]:template=template.replace(a,b)
    template=template.replace('<label>Optional explanation','<p id="selection" aria-live="polite"></p><label>Optional explanation')
    statement="el('note').value=a?.note||'';"
    confirmation="el('selection').textContent='Your selections — Usefulness: '+({candidate:'Candidate: visible, useful improvement',input:'Input is preferable',no_useful_difference:'No useful difference',uncertain:'Unsure'}[a?.preference]||'not answered')+'; Appearance: '+({acceptable:'Acceptable',unwanted:'Unwanted change',uncertain:'Unsure'}[a?.appearance]||'not answered');"
    assert statement in template
    template=template.replace(statement,statement+confirmation)
    out.mkdir();(out/'images').mkdir();write(out/'selection_PRIVATE.json',selected);cases=[]
    for i,r in enumerate(selected,1):
        p=packs[r['case_id']]
        with np.load(p,allow_pickle=False) as pack:arrays={name:pack[key].copy() for name,key in [('input','input'),('candidate','314'),('reference','reference')]}
        entry=dict(review_id=f'wb_exposure_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],role=r['role'],cached_pack_sha256=sha(p))
        for field,a in arrays.items():
            path=out/'images'/f'{i:02d}_{field}.png';Image.fromarray(a).save(path)
            assert np.array_equal(np.asarray(Image.open(path)),a)
            entry[field]=path.relative_to(out).as_posix();entry[field+'_sha256']=sha(path)
        entry['pixel_identical']=bool(np.array_equal(arrays['input'],arrays['candidate']));cases.append(entry)
    protocol=ROOT/'docs/wb-feature-exposure-usefulness-protocol-2026-11-16.md'
    manifest=dict(cases=cases,review_kind='exposure_usefulness_and_appearance',unreviewed_cases=36,
                  identity_assessment_sha256=sha(identity),colour_raw_sha256=sha(raw),
                  colour_user_correction_sha256=sha(corrected/'user_correction_PRIVATE.json'),colour_corrected_assessment_sha256=sha(corrected/'assessment_PRIVATE.json'),
                  source_verification_sha256=sha(proof_path),protocol_sha256=sha(protocol),selection_sha256=sha(out/'selection_PRIVATE.json'))
    write(out/'manifest_PRIVATE.json',manifest);digest=sha(out/'manifest_PRIVATE.json')
    config=dict(manifest_sha256=digest,qa_fixture=False,cases=[{k:c[k] for k in ['review_id','input','candidate','reference']} for c in cases])
    html=template.replace('__CONFIG__',json.dumps(config));(out/'index.html').write_text(html,encoding='utf-8')
    for c in cases:
        for field in ['input','candidate','reference']:
            data=(out/c[field]).read_bytes();assert sha(out/c[field])==c[field+'_sha256']
            html=html.replace(json.dumps(c[field]),json.dumps('data:image/png;base64,'+base64.b64encode(data).decode('ascii')))
    (out/'standalone.html').write_text(html,encoding='utf-8');(out/'review.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    fixture=dict(manifest_sha256='generated_wb_exposure_ui_only',qa_fixture=True,cases=[dict(review_id=f'qa_{i:02d}',input='fixture.png',candidate='fixture.png',reference='fixture.png') for i in range(1,9)])
    (out/'qa_review.js').write_text(template.replace('__CONFIG__',json.dumps(fixture)).split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    for p in packs.values():assert sha(p)==hashes[p.relative_to(run).as_posix()]
    write(out/'preparation_PRIVATE.json',dict(cases=8,native_png_hashes=24,roundtrips_exact=24,manifest_sha256=digest,
          standalone_sha256=sha(out/'standalone.html'),ratings_generated=0,correction_renders=0,interactive_browser_qa=False))
    print(json.dumps(selected,indent=2))

if __name__=='__main__':main()
