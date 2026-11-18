"""Read-only join of displayed assets to saved controls/output; no rerender."""
import base64
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out=ROOT/'outputs/wb_feature_exposure_display_diagnosis_v1'
    if out.exists():raise FileExistsError(out)
    review=ROOT/'outputs/wb_feature_exposure_review_v1';run=ROOT/'outputs/wb_feature_direct_prediction_v1'
    m=read(review/'manifest_PRIVATE.json');prep=read(review/'preparation_PRIVATE.json');proof=read(run/'verification.json')
    assert sha(review/'manifest_PRIVATE.json')==prep['manifest_sha256']
    assert sha(run/'verification.json')==m['source_verification_sha256']
    hashes={k.replace('\\','/'):v for k,v in proof['artifacts'].items()}
    assert sha(run/'held_controls_sealed.json')==hashes['held_controls_sealed.json']
    held={r['case_id']:r for r in read(run/'held_controls_sealed.json')}
    assert sha(review/'standalone.html')==prep['standalone_sha256']
    html=(review/'standalone.html').read_text(encoding='utf-8')
    config=json.loads(html.split('const CONFIG=',1)[1].split(';\nconst key=',1)[0])
    assert len(m['cases'])==len(config['cases'])==8 and config['manifest_sha256']==prep['manifest_sha256']
    for c in m['cases']:
        p=run/'evaluation'/(c['case_id']+'.npz');assert sha(p)==c['cached_pack_sha256']==hashes[p.relative_to(run).as_posix()]
        for f in ['input','candidate','reference']:assert sha(review/c[f])==c[f+'_sha256']
    rows=[]
    for c,display in zip(m['cases'],config['cases']):
        assert c['review_id']==display['review_id']
        p=run/'evaluation'/(c['case_id']+'.npz')
        with np.load(p,allow_pickle=False) as pack:inp=pack['input'].copy();candidate=pack['314'].copy();alpha=pack['alpha'].copy()
        for f,array in [('input',inp),('candidate',candidate)]:
            assert np.array_equal(np.asarray(Image.open(review/c[f])),array)
            embedded=base64.b64decode(display[f].split(',',1)[1],validate=True)
            assert hashlib.sha256(embedded).hexdigest()==c[f+'_sha256']
        controls=held[c['case_id']]['controls314'];diff=np.abs(candidate.astype(float)-inp);mask=alpha>0
        rows.append(dict(review_id=c['review_id'],case_id=c['case_id'],role=c['role'],controls=controls,
                         pixel_identical=bool(np.array_equal(inp,candidate)),neutral_controls=controls==[1.,1.,1.,1.,1.],
                         changed_pixels=int(np.any(inp!=candidate,axis=2).sum()),primary_pixels=int(mask.sum()),
                         primary_mean_RGB_change=float(diff[mask].mean()),whole_mean_RGB_change=float(diff.mean()),
                         primary_mean_signed_RGB_change=(candidate.astype(float)-inp)[mask].mean(axis=0).tolist(),
                         displayed_matches_saved_output=True))
    for c in m['cases']:assert sha(run/'evaluation'/(c['case_id']+'.npz'))==c['cached_pack_sha256']
    assert sha(review/'standalone.html')==prep['standalone_sha256']
    out.mkdir()
    user='All of the candidates looked like the input version. I don\'t think exposure correction was applied to the candidates as they look similar to the input.'
    (out/'user_observation_PRIVATE.json').write_text(json.dumps(dict(date='2026-11-16',exact_user_message=user,
        reported_context='exposure review',page_confirmation='pending',review_manifest_sha256=prep['manifest_sha256'],
        per_case_ratings_fabricated=False),indent=2),encoding='utf-8')
    result=dict(passed=True,cases=rows,identical_cases=sum(r['pixel_identical'] for r in rows),
                changed_cases=sum(not r['pixel_identical'] for r in rows),asset_mapping_exact=True,
                native_input_candidate_pngs_verified=16,embedded_input_candidate_pngs_verified=16,
                new_fits=0,new_renders=0,reference_array_reads=0,raw_original_reads=0,
                limitation='No live browser observation; numeric change does not establish user-visible usefulness.')
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
