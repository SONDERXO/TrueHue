"""Bind nine pending judgments to three exact saved training boards."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate
from src.utilities.config import get_config


def main():
    base=ROOT/get_config().OUTPUTS_ROOT
    out=base/'additional_source_reference_review3_v1'
    if out.exists():raise FileExistsError(out)
    inputs={}
    def read(path):
        raw=path.read_bytes();inputs[path.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    triage=base/'source_planning24_triage_v1'
    verification=read(triage/'verification.json')
    records=read(triage/'assistant_observations.json')
    assert inputs[(triage/'assistant_observations.json').relative_to(ROOT).as_posix()]==verification['evidence_sha256']['assistant_observations.json']
    manifest=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    sources=[]
    for r in records:
        if r['assistant_triage']!='priority_for_missing_judgments':continue
        training_candidate(r['image_id'],manifest,policy)
        board=ROOT/r['board_path'];sha=hashlib.sha256(board.read_bytes()).hexdigest()
        assert sha==r['board_sha256'] and not r['training_admitted']
        inputs[r['board_path']]=sha
        sources.append(dict(image_id=r['image_id'],source_id=r['source_id'],board_sha256=sha,
            board_url='../correction_training_preparation_v1/boards/'+r['source_id']+'.png',
            observation=r['assistant_visual_observation'],clipping_fraction=r['clipping_fraction']))
    assert {r['source_id'] for r in sources}=={'2434','25517','39083'}
    spec=dict(schema_version='truehue_source_reference_review_spec_v1',sources=sources,
        scopes=['reference_suitability','reference_mask','displayed_stress_mask'],
        automatic_admission=False,training_authorized=False,
        variant_scope='Existing displayed clipped stress input only; no future variant approval')
    spec['spec_sha256']=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    template=ROOT/'scripts/review_tools/source_reference_review.html'
    script=ROOT/'scripts/review_tools/source_reference_review.js'
    for p in [template,script,Path(__file__)]:inputs[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    out.mkdir()
    (out/'spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
    (out/'review.html').write_text(template.read_text(encoding='utf-8').replace('__SPEC__',json.dumps(spec).replace('<','\\u003c')),encoding='utf-8')
    (out/script.name).write_bytes(script.read_bytes())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in inputs.items())
    (out/'verification.json').write_text(json.dumps(dict(status='pass',source_count=3,distinct_judgments=9,
        defaults='all_not_reviewed',inputs_unchanged=True,input_sha256=inputs,
        output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()},
        raw_image_decodes=0,reserved_role_access=0,training_admissions=0,model_fits=0),indent=2),encoding='utf-8')
    print('Prepared 3 exact-board sources, 9 separate pending judgments; no data admitted or model fitted.')


if __name__=='__main__':main()
