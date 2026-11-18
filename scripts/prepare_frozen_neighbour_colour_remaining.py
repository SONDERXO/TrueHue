"""Preserve case09 explanation and show ONLY the two originally unrated cases."""
from pathlib import Path
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.model_training.reiqa_frozen_features import sha
from prepare_frozen_neighbour_colour_review import template
OLD=ROOT/'outputs/frozen_neighbour_colour_review_v2'
RATINGS=ROOT/'outputs/frozen_neighbour_colour_ratings_v1'
EXPLAIN=ROOT/'outputs/frozen_neighbour_colour_case09_explanation_v1'
OUT=ROOT/'outputs/frozen_neighbour_colour_remaining_review_v1'
def write(p,v):Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
def main():
    if EXPLAIN.exists() or OUT.exists():raise FileExistsError('Preserve prior explanation/continuation')
    raw=RATINGS/'raw_user_review_PRIVATE.json';assert sha(raw)=='4b0778507b02fd5ba3d4b4bb6742251931a44b7f2271df575c9376854e8fa014'
    saved=json.loads(raw.read_text());assert saved['status']=='stopped_uncertain'
    assert saved['answers']['colour_09']==dict(preference='no_useful_difference',appearance='uncertain',note='')
    assert not any(i in saved['answers'] for i in ['colour_10','colour_11'])
    EXPLAIN.mkdir()
    write(EXPLAIN/'clarification_PRIVATE.json',dict(source='explicit_user_reply',source_id='53146',review_id='colour_09',
        question='For colour case 9 (source 53146), what made you choose Unsure about appearance: uncertainty about an unwanted change, or about whether the correction helped? The candidate is pixel-identical to the input. This is an explanation of your saved answer, not a replacement rating.',
        exact_user_answer='the input and candidate looks the same',original_user_review_sha256=sha(raw),
        meaning='No perceived input-candidate difference reported; no explicit replacement appearance rating or assertion of unwanted change.',
        original_rating_unchanged=True,automatic_visual_pass=False))
    manifest=json.loads((OLD/'manifest_PRIVATE.json').read_text())
    remaining=[r for r in manifest['cases'] if r['review_id'] in ['colour_10','colour_11']]
    assert [r['source_id'] for r in remaining]==['54632','59807']
    OUT.mkdir();(OUT/'images').mkdir()
    for r in remaining:
        for field in ['input','candidate','reference']:
            assert sha(OLD/r[field])==r[field+'_sha256']
            shutil.copyfile(OLD/r[field],OUT/r[field])
            assert sha(OUT/r[field])==r[field+'_sha256']
    binding={k:manifest[k] for k in ['review_kind','identity_assessment_sha256','run_verification_sha256','protocol_sha256']}
    binding.update(cases=remaining,continuation=True,parent_manifest_sha256=sha(OLD/'manifest_PRIVATE.json'),
        original_user_review_sha256=sha(raw),clarification_sha256=sha(EXPLAIN/'clarification_PRIVATE.json'),
        original_case09_appearance='uncertain_not_replaced')
    write(OUT/'manifest_PRIVATE.json',binding)
    config=dict(manifest_sha256=sha(OUT/'manifest_PRIVATE.json'),qa_fixture=False,
        cases=[{k:r[k] for k in ['review_id','input','candidate','reference']} for r in remaining])
    html=template().replace('All 11 cases recorded.','Both remaining cases recorded.')
    html=html.replace('This page contains 11 colour cases; exposure correction is assessed separately.',
        'Only the two remaining colour cases are shown. Earlier answers remain saved; exposure correction is assessed separately.')
    html=html.replace('truehue-colour-usefulness-review.json','truehue-colour-remaining-review.json')
    html=html.replace('__CONFIG__',json.dumps(config))
    (OUT/'index.html').write_text(html,encoding='utf-8')
    script=html.split('<script>',1)[1].split('</script>',1)[0]
    (OUT/'script_syntax.js').write_text(script,encoding='utf-8')
    write(OUT/'preparation_PRIVATE.json',dict(cases=2,images=6,new_ratings=0,prior_answers_modified=False,
        html_sha256=sha(OUT/'index.html'),manifest_sha256=config['manifest_sha256'],code_sha256=sha(Path(__file__))))
    assert sha(raw)==binding['original_user_review_sha256']
    print('Prepared ONLY original cases10/11; case09 explanation separately bound, no ratings replaced.')
if __name__=='__main__':main()
