"""Lossless existing outputs only; candidate-specific standalone colour review."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def literal(path,name):
    return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))

def main():
    run=ROOT/'outputs/wb_feature_direct_prediction_v1';out=ROOT/'outputs/wb_feature_colour_review_v1'
    if out.exists():raise FileExistsError(out)
    ident=ROOT/'outputs/wb_feature_identity_ratings_v1';assert read(ident/'assessment_PRIVATE.json')['status']=='complete_acceptable'
    assert read(ident/'independent_verification_PRIVATE.json')['passed']
    assert sha(ident/'raw_user_review_PRIVATE.json')==read(ident/'assessment_PRIVATE.json')['raw_file_sha256']
    proof=read(run/'verification.json');assert proof['passed'] and proof['candidate_numeric_eligible']
    hashes={p.replace('\\','/'):h for p,h in proof['artifacts'].items()}
    rows=sorted((r for r in read(run/'records.json') if r['role']=='colour_only'),key=lambda r:r['source_id'])
    assert len(rows)==len({r['source_id'] for r in rows})==11
    packs={r['case_id']:run/'evaluation'/(r['case_id']+'.npz') for r in rows}
    for p in packs.values():assert sha(p)==hashes[p.relative_to(run).as_posix()]
    old=ROOT/'scripts/prepare_frozen_neighbour_colour_review.py'
    ns={'IDENTITY_TEMPLATE':literal(ROOT/'scripts/prepare_frozen_neighbour_identity_review.py','TEMPLATE'),
        'SCRIPT':literal(old,'SCRIPT').replace('truehue-colour-usefulness-review.json','truehue-wb-feature-colour-review.json')}
    node=next(n for n in ast.parse(old.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='template')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(old),'exec'),ns)
    template=ns['template']()
    out.mkdir();(out/'images').mkdir();cases=[]
    for i,r in enumerate(rows,1):
        p=packs[r['case_id']]
        with np.load(p,allow_pickle=False) as pack:images={name:pack[key].copy() for name,key in [('input','input'),('candidate','314'),('reference','reference')]}
        entry=dict(review_id=f'wb_colour_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],cached_pack_sha256=sha(p),
                   pixel_identical=bool(np.array_equal(images['input'],images['candidate'])))
        for name,array in images.items():
            path=out/'images'/f'{i:02d}_{name}.png';Image.fromarray(array).save(path)
            assert np.array_equal(np.asarray(Image.open(path)),array)
            entry[name]=path.relative_to(out).as_posix();entry[name+'_sha256']=sha(path)
        cases.append(entry)
    protocol=ROOT/'docs/wb-feature-colour-usefulness-protocol-2026-11-16.md'
    manifest=dict(cases=cases,review_kind='colour_usefulness_and_appearance',candidate='camera_task_tree_314_WB_features',
                  identity_assessment_sha256=sha(ident/'assessment_PRIVATE.json'),identity_raw_sha256=sha(ident/'raw_user_review_PRIVATE.json'),
                  run_verification_sha256=sha(run/'verification.json'),protocol_sha256=sha(protocol))
    write(out/'manifest_PRIVATE.json',manifest);digest=sha(out/'manifest_PRIVATE.json')
    config=dict(manifest_sha256=digest,qa_fixture=False,cases=[{k:c[k] for k in ['review_id','input','candidate','reference']} for c in cases])
    html=template.replace('__CONFIG__',json.dumps(config));(out/'index.html').write_text(html,encoding='utf-8')
    for c in cases:
        for field in ['input','candidate','reference']:
            data=(out/c[field]).read_bytes();assert hashlib.sha256(data).hexdigest()==c[field+'_sha256']
            html=html.replace(json.dumps(c[field]),json.dumps('data:image/png;base64,'+base64.b64encode(data).decode('ascii')))
    (out/'standalone.html').write_text(html,encoding='utf-8')
    (out/'review.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    fixture=dict(manifest_sha256='generated_wb_colour_ui_only',qa_fixture=True,cases=[dict(review_id=f'qa_{i:02d}',input='fixture.png',candidate='fixture.png',reference='fixture.png') for i in range(1,12)])
    (out/'qa_review.js').write_text(ns['SCRIPT'].replace('__CONFIG__',json.dumps(fixture)),encoding='utf-8')
    for p in packs.values():assert sha(p)==hashes[p.relative_to(run).as_posix()]
    report=dict(cases=11,native_pngs_hash_verified=33,roundtrips_exact=33,ratings_generated=0,
                pixel_identical=sum(c['pixel_identical'] for c in cases),manifest_sha256=digest,
                standalone_sha256=sha(out/'standalone.html'),code_sha256=sha(Path(__file__)),interactive_browser_qa=False,
                sample_replacements=0,correction_renders=0)
    write(out/'preparation_PRIVATE.json',report);print(report)

if __name__=='__main__':main()
