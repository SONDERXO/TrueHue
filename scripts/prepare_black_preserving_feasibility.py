"""Two exact saved three-control diagnostics; no correction rendering/fitting."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.model_training.reiqa_frozen_features import sha
from prepare_frozen_neighbour_identity_review import TEMPLATE
OLD=ROOT/'outputs/ffhq_directional_recoverability_v1'
PRIOR=ROOT/'outputs/frozen_neighbour_exposure_review_v1'
OUT=ROOT/'outputs/black_preserving_saved_feasibility_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
def main():
    if OUT.exists():raise FileExistsError(OUT)
    proof=read(OLD/'verification_PRIVATE.json');assert proof['passed'] and proof['scalar_case_replays']==66
    hashes={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    parent=read(PRIOR/'manifest_PRIVATE.json');chosen=[parent['cases'][0],parent['cases'][2]]
    assert [(r['source_id'],r['role']) for r in chosen]==[('29617','exposure_under'),('32685','exposure_over')]
    # All selected cached containers and displayed context hashes BEFORE decoding.
    for r in chosen:
        for ext in ['json','npz']:
            relative=f"cases/{r['source_id']}/{r['role']}.{ext}";assert sha(OLD/relative)==hashes[relative]
        for key in ['input','candidate','reference']:assert sha(PRIOR/r[key])==r[key+'_sha256']
    OUT.mkdir();(OUT/'images').mkdir();manifest=[]
    for i,r in enumerate(chosen,1):
        relative=f"cases/{r['source_id']}/{r['role']}.npz"
        with np.load(OLD/relative,allow_pickle=False) as pack:
            image=pack['input'].copy();output=pack['output'].copy()
        assert output.shape==image.shape==(256,256,3) and output.dtype==image.dtype==np.uint8
        np.testing.assert_array_equal(image,np.asarray(Image.open(PRIOR/r['input'])))
        assert np.all(output[np.all(image==0,axis=2)]==0)
        assert np.all(output[:,:,1][image[:,:,1]==255]==255)
        record=dict(review_id=f'feasibility_{i:02d}',source_id=r['source_id'],role=r['role'],
            cached_three_control_pack_sha256=hashes[relative],reference_aware=True,predictor_output=False,
            three_controls=read(OLD/f"cases/{r['source_id']}/{r['role']}.json")['target']['parameters'])
        for field,source in [('input','input'),('rejected','candidate'),('reference','reference')]:
            path=OUT/'images'/f'{i:02d}_{field}.png';shutil.copyfile(PRIOR/r[source],path)
            assert sha(path)==r[source+'_sha256'];record[field]=path.relative_to(OUT).as_posix();record[field+'_sha256']=sha(path)
        path=OUT/'images'/f'{i:02d}_black_preserving.png';Image.fromarray(output).save(path)
        np.testing.assert_array_equal(np.asarray(Image.open(path)),output)
        record['candidate']=path.relative_to(OUT).as_posix();record['candidate_sha256']=sha(path)
        record['clipped_black_pixels_preserved']=int(np.all(image==0,axis=2).sum())
        record['saturated_green_pixels_remain_255']=int((image[:,:,1]==255).sum())
        manifest.append(record)
        assert sha(OLD/relative)==hashes[relative]
    binding=dict(review_kind='reference_aware_black_preserving_feasibility',cases=manifest,
        old_verification_sha256=sha(OLD/'verification_PRIVATE.json'),prior_manifest_sha256=sha(PRIOR/'manifest_PRIVATE.json'),
        proposal_sha256=sha(ROOT/'docs/black-preserving-feasibility-next-step-2026-11-15.md'),
        optimizer_calls=0,new_predictor_outputs=0,new_correction_renders=0)
    write(OUT/'manifest_PRIVATE.json',binding)
    config=dict(manifest_sha256=sha(OUT/'manifest_PRIVATE.json'),qa_fixture=False,
        cases=[{k:r[k] for k in ['review_id','input','candidate','rejected','reference']} for r in manifest])
    html=TEMPLATE.replace('max-width:1000px','max-width:1200px')
    html=html.replace('Identity preservation review','Black-preserving method feasibility')
    html=html.replace('Check that acceptable photographs stay acceptable','Can the black-preserving method look natural?')
    html=html.replace('Compare the input and candidate. Does the candidate introduce an <strong>unwanted change</strong>? A slight difference can still be acceptable. Use your usual review display and settings.',
        'Compare the black-preserving diagnostic with the input, rejected result and photographic reference. Its controls were fitted with the reference available: it is <strong>not a model prediction</strong>. This checks visual plausibility before considering more model work. Use your usual viewing setup.')
    html=html.replace('<figcaption>Candidate</figcaption>','<figcaption>Black-preserving diagnostic</figcaption>')
    needle='</figure></div>'
    assert html.count(needle)==1
    html=html.replace(needle,'</figure><figure><figcaption>Rejected result</figcaption><img id="rejected" alt="Previously rejected result"></figure><figure><figcaption>Photographic reference</figcaption><img id="reference" alt="Photographic reference"></figure></div>')
    html=html.replace('Is the candidate acceptable for this already acceptable input?','Is the black-preserving result natural enough to justify further investigation?')
    html=html.replace('Acceptable, including a slight acceptable difference','Natural enough to investigate further').replace('Unwanted change</button>','Unacceptable appearance</button>')
    html=html.replace('All 11 cases checked.','Both cases checked.')
    html=html.replace('This check is about preserving acceptable appearance; correction usefulness is assessed separately.',
        'Only two existing diagnostic outputs are shown. This does not establish prediction quality, useful restoration or skin-tone fairness. If either is unacceptable or uncertain, stop and save.')
    html=html.replace("el('candidate').src=c.candidate;","el('candidate').src=c.candidate;el('rejected').src=c.rejected;el('reference').src=c.reference;")
    html=html.replace('truehue_identity_review_v1','truehue_black_preserving_feasibility_v1').replace('identity_no_unwanted_change','reference_aware_black_preserving_feasibility').replace('truehue_identity_','truehue_black_preserving_').replace('truehue-identity-review.json','truehue-black-preserving-feasibility-review.json')
    html=html.replace('__CONFIG__',json.dumps(config))
    (OUT/'index.html').write_text(html,encoding='utf-8');(OUT/'script_syntax.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    write(OUT/'preparation_PRIVATE.json',dict(cases=2,images=8,new_correction_renders=0,new_fits=0,ratings=0,
        black_preservation_exact=True,saturated_green_stays_255=True,manifest_sha256=config['manifest_sha256'],code_sha256=sha(Path(__file__)),html_sha256=sha(OUT/'index.html')))
    print('Prepared two saved reference-aware diagnostics; exact input/context joins; no new render or fit.')
if __name__=='__main__':main()
