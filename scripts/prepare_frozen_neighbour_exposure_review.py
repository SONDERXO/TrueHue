"""Prospective risk-plus-deterministic eight-case exposure review."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.model_training.reiqa_frozen_features import sha
from prepare_frozen_neighbour_colour_review import template
RUN=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
OUT=ROOT/'outputs/frozen_neighbour_exposure_review_v1'
ROLES=['exposure_under','exposure_over','combined_under','combined_over']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
def main():
    if OUT.exists():raise FileExistsError(OUT)
    colour=ROOT/'outputs/frozen_neighbour_colour_ratings_v2/assessment_PRIVATE.json'
    saved=read(colour)
    assert saved['status']=='complete_recorded' and saved['appearance_counts']==dict(acceptable=11,unwanted=0,uncertain=0)
    proof=read(RUN/'verification_PRIVATE.json');assert proof['passed'] and proof['numeric_status']=='NUMERIC_PREDICTION_ELIGIBLE_ONLY'
    hashes={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    rows=read(RUN/'models/held_controls_sealed.json');selected=[];roster=[]
    # Frozen risk-first + metric-independent second selection; no image inspection.
    for role in ROLES:
        own=[r for r in rows if r['role']==role];assert len(own)==11
        def residual(r):
            relative='evaluation/'+r['case_id']+'.json';assert sha(RUN/relative)==hashes[relative]
            return read(RUN/relative)['regions']['primary']['tree']['RGB']
        worst=min(own,key=lambda r:(-residual(r),r['case_id']))
        others=[r for r in own if r['source_id']!=worst['source_id']]
        second=min(others,key=lambda r:(hashlib.sha256(('truehue_exposure_screen_20261115|'+r['case_id']).encode()).hexdigest(),r['case_id']))
        for label,r in [('largest_primary_RGB_residual',worst),('fixed_hash_other_source',second)]:
            selected.append(r);roster.append(dict(case_id=r['case_id'],source_id=r['source_id'],role=role,selection=label,primary_RGB=residual(r)))
    assert len(selected)==len({r['case_id'] for r in selected})==8
    OUT.mkdir();(OUT/'images').mkdir();manifest=[]
    write(OUT/'selection_PRIVATE.json',roster)
    for i,r in enumerate(selected,1):
        relative='evaluation/'+r['case_id']+'.npz';assert sha(RUN/relative)==hashes[relative]
        with np.load(RUN/relative,allow_pickle=False) as pack:images={k:pack[k].copy() for k in ['input','tree','reference']}
        record=dict(review_id=f'exposure_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],role=r['role'],cached_pack_sha256=hashes[relative])
        for field,arraykey in [('input','input'),('candidate','tree'),('reference','reference')]:
            p=OUT/'images'/f'{i:02d}_{field}.png';Image.fromarray(images[arraykey]).save(p)
            np.testing.assert_array_equal(np.asarray(Image.open(p)),images[arraykey]);record[field]=p.relative_to(OUT).as_posix();record[field+'_sha256']=sha(p)
        manifest.append(record)
    binding=dict(cases=manifest,review_kind='exposure_usefulness_and_appearance',
        identity_assessment_sha256=sha(ROOT/'outputs/frozen_neighbour_identity_ratings_v1/assessment_PRIVATE.json'),
        colour_assessment_sha256=sha(colour),run_verification_sha256=sha(RUN/'verification_PRIVATE.json'),
        protocol_sha256=sha(ROOT/'docs/frozen-neighbour-exposure-usefulness-protocol-2026-11-15.md'),
        selection_sha256=sha(OUT/'selection_PRIVATE.json'),unreviewed_exposure_cases=36)
    write(OUT/'manifest_PRIVATE.json',binding)
    config=dict(manifest_sha256=sha(OUT/'manifest_PRIVATE.json'),qa_fixture=False,
        cases=[{k:r[k] for k in ['review_id','input','candidate','reference']} for r in manifest])
    html=template().replace('Colour correction usefulness','Exposure correction usefulness').replace('Colour correction: is the improvement useful?','Exposure correction: is the improvement useful?')
    html=html.replace("skin's colour and overall appearance","skin's exposure, colour and overall appearance")
    html=html.replace('All 11 cases recorded.','All 8 cases recorded.').replace('This page contains 11 colour cases; exposure correction is assessed separately.','This page contains 8 exposure and combined-correction cases. Earlier reviews remain saved.')
    html=html.replace('truehue_colour_usefulness_review_v1','truehue_exposure_usefulness_review_v1').replace('colour_usefulness_and_appearance','exposure_usefulness_and_appearance').replace('truehue_colour_','truehue_exposure_').replace('truehue-colour-usefulness-review.json','truehue-exposure-usefulness-review.json')
    html=html.replace('__CONFIG__',json.dumps(config))
    (OUT/'index.html').write_text(html,encoding='utf-8');(OUT/'script_syntax.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    write(OUT/'preparation_PRIVATE.json',dict(cases=8,images=24,new_ratings=0,new_correction_renders=0,manifest_sha256=config['manifest_sha256'],html_sha256=sha(OUT/'index.html'),code_sha256=sha(Path(__file__))))
    print(json.dumps(roster,indent=2))
if __name__=='__main__':main()
