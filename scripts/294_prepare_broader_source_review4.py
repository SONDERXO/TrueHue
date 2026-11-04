"""Reuse the scoped-review UI for only the four new bounded-screen leads."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate


def main():
    base=ROOT/get_config().OUTPUTS_ROOT
    out=base/'broader_source_reference_review4_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(p):
        raw=p.read_bytes();hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    parent=base/'broader_source_screen61_v1'
    assert read(parent/'independent_verification.json')['status']=='pass'
    rows=read(parent/'assistant_observations.json')
    manifest=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    previous=read(base/'additional_source_reference_review3_import_v1/reconciled_reviews.json')
    previous_ids={r['image_id'] for r in previous}
    sources=[]
    for r in rows:
        if r['readiness']!='additional_priority_lead_not_approved':continue
        training_candidate(r['image_id'],manifest,policy)
        assert r['image_id'] not in previous_ids and r['exact_user_judgments'] is None
        assert r['processing_status']=='pending_review' and r['clipping_fraction']>0
        path=ROOT/r['board_path'];sha=hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha==r['board_sha256'];hashes[r['board_path']]=sha
        sources.append(dict(image_id=r['image_id'],source_id=r['source_id'],board_sha256=sha,
            board_url='../correction_training_preparation_v1/boards/'+r['source_id']+'.png',
            observation=r['assistant_observation'],clipping_fraction=r['clipping_fraction']))
    assert {r['source_id'] for r in sources}=={'58800','63509','42965','77101'}
    spec=dict(schema_version='truehue_source_reference_review_spec_v1',sources=sources,
        scopes=['reference_suitability','reference_mask','displayed_stress_mask'],automatic_admission=False,
        training_authorized=False,variant_scope='Existing displayed clipped stress input only; no future variant approval')
    spec['spec_sha256']=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    template=ROOT/'scripts/review_tools/source_reference_review.html'
    js=ROOT/'scripts/review_tools/source_reference_review.js'
    page=template.read_text(encoding='utf-8').replace('three additional source leads','four additional source leads').replace('Three additional source leads','Four additional source leads').replace('All three displayed distortions','All four displayed distortions').replace('Export the nine judgments','Export the twelve judgments')
    script=js.read_text(encoding='utf-8').replace('${n} / 9 judgments recorded.','${n} / 12 judgments recorded.').replace('truehue_additional_source3_judgments.json','truehue_additional_source4_judgments.json')
    assert '/ 9 judgments' not in script and 'nine judgments' not in page
    for p in [template,js,Path(__file__)]:hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    out.mkdir()
    (out/'spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
    (out/'review.html').write_text(page.replace('__SPEC__',json.dumps(spec).replace('<','\\u003c')),encoding='utf-8')
    (out/'source_reference_review.js').write_text(script,encoding='utf-8')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
    (out/'verification.json').write_text(json.dumps(dict(status='pass',sources=4,distinct_pending_judgments=12,
        overlap_with_completed_review3=0,default_approvals=0,training_admissions=0,model_fits=0,
        input_sha256=hashes,output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}),indent=2),encoding='utf-8')
    print('Prepared four new sources, twelve separate pending judgments, zero repeated completed reviews.')


if __name__=='__main__':main()
