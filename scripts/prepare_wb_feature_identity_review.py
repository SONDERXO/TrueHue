"""Candidate-specific review assets after independently verified numeric gate."""
import ast
import json
from pathlib import Path
import numpy as np
from PIL import Image
from wb_feature_direct_workflow import ROOT,read,write,sha

def main():
    run=ROOT/'outputs/wb_feature_direct_prediction_v1';out=ROOT/'outputs/wb_feature_identity_review_v1'
    if out.exists():raise FileExistsError(out)
    proof=read(run/'verification.json');summary=read(run/'summary.json')
    hashes={k.replace('\\','/'):v for k,v in proof['artifacts'].items()}
    assert proof['passed'] and proof['candidate_numeric_eligible'] and summary['candidate_numeric_eligible']
    template_source=ROOT/'scripts/prepare_frozen_neighbour_identity_review.py'
    template=next(ast.literal_eval(n.value) for n in ast.parse(template_source.read_text(encoding='utf-8')).body
                  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TEMPLATE' for t in n.targets))
    template=template.replace('truehue-identity-review.json','truehue-wb-feature-identity-review.json')
    records=[r for r in read(run/'records.json') if r['role']=='identity'];assert len(records)==11
    records.sort(key=lambda r:(r['identity_changed_pixels']['314']==0,r['source_id']))
    out.mkdir();(out/'images').mkdir();cases=[]
    for i,r in enumerate(records,1):
        path=run/'evaluation'/(r['case_id']+'.npz');relative=path.relative_to(run).as_posix()
        assert sha(path)==hashes[relative]
        with np.load(path,allow_pickle=False) as pack:arrays={name:pack[key].copy() for name,key in [('input','input'),('candidate','314')]}
        entry=dict(review_id=f'wb_identity_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],cached_pack_sha256=sha(path))
        for name,a in arrays.items():
            p=out/'images'/f'{i:02d}_{name}.png';Image.fromarray(a).save(p)
            assert np.array_equal(np.asarray(Image.open(p)),a)
            entry[name]=p.relative_to(out).as_posix();entry[name+'_sha256']=sha(p)
        entry['pixel_identical']=bool(np.array_equal(arrays['input'],arrays['candidate']));cases.append(entry)
    body=dict(review_kind='identity_no_unwanted_change',cases=cases,source_verification_sha256=sha(run/'verification.json'),
              candidate='camera_task_tree_314_WB_features',policy='all11; slightacceptable allowed; stopunwanted/uncertain; no carried ratings')
    write(out/'manifest_PRIVATE.json',body);digest=sha(out/'manifest_PRIVATE.json')
    config=dict(manifest_sha256=digest,qa_fixture=False,cases=[{k:r[k] for k in ['review_id','input','candidate']} for r in cases])
    html=template.replace('__CONFIG__',json.dumps(config));(out/'index.html').write_text(html,encoding='utf-8')
    (out/'review.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    qa=out/'qa';qa.mkdir();Image.fromarray(np.full((256,256,3),128,np.uint8)).save(qa/'fixture.png')
    fixture=dict(manifest_sha256='wb_feature_synthetic_ui_only',qa_fixture=True,cases=[dict(review_id=f'qa_{i:02d}',input='fixture.png',candidate='fixture.png') for i in range(1,12)])
    (qa/'index.html').write_text(template.replace('__CONFIG__',json.dumps(fixture)),encoding='utf-8')
    report=dict(cases=11,pixel_identical=sum(r['pixel_identical'] for r in cases),manifest_sha256=digest,ratings_collected=0,
                script_sha256=sha(Path(__file__)),template_sha256=sha(template_source),index_sha256=sha(out/'index.html'),interactive_browser_qa=False)
    write(out/'preparation_PRIVATE.json',report);print(report)

if __name__=='__main__':main()
