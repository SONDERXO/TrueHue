"""Archive qualitative source screen separately from user decisions/admission."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/table2_source_expansion24_v1'
NOTES={
 '74448':('hold','Fragmented reference support and strong existing illumination; distorted detection failed.'),
 '52483':('hold','Reference selects mainly lower face; distorted mask shifts to forehead. Target intersection insufficient.'),
 '86027':('hold','Reference captures only a small lower-face region; distorted support below pixel minimum.'),
 '30507':('hold','Soft detail, strong hat shadow/illumination difference, fragmented distorted support.'),
 '56690':('hold','Glasses and nearby hair/surroundings selected; substantial distorted support loss.'),
 '37705':('hold','Soft facial detail and major distorted support fragmentation.'),
 '26179':('hold','Soft reference detail; large distorted facial region missing.'),
 '17337':('hold','Downward pose and hat shadow with pronounced distorted-region gaps.'),
 '51803':('provisional_user_review','Broad support; soft reference detail and lower-face/neck or nearby edge selection need explicit review.'),
 '29247':('hold','Glasses included in reference support and large upper-face loss after distortion.'),
 '19225':('hold','Low detail/soft reference and pre-existing uneven facial illumination; mouth-edge support concerns.'),
 '85960':('hold','Dark/soft reference with sparse support; distorted landmarks unavailable.'),
 '34301':('hold','Eyewear/eye selection and beard/side-face boundaries uncertain; soft reference.'),
 '85946':('hold','Strong warm cast, low detail, hair/background edge selection and severe clipping.'),
 '25565':('hold','Strong highlights/illumination and patchy reference support; facial-hair boundary concerns.'),
 '4889':('hold','Strong warm cast and glasses selected; soft detail and surroundings/neck spill.'),
 '71139':('hold','Large holes in reference and distorted support; pose and background selection concerns.'),
 '61165':('hold','Hair selected across upper face and substantial reference support gaps.'),
 '53109':('provisional_user_review','Broad reference/input facial support; verify side-face/ear and clothing boundaries and photographic reference suitability.'),
 '713':('provisional_user_review','Broad facial support; hand/neck boundary selection and possible cosmetic/styled-lighting reference concerns require review; cosmetics not established by preview.'),
 '40849':('hold','Low facial detail and outer support spill; large distorted cheek/forehead loss.'),
 '65424':('hold','Eyewear/eye and hair/outer-edge selection; soft facial detail and fragmented distorted support.'),
 '81493':('hold','Strong uneven colored illumination/marks and upper-face support gaps; reference suitability uncertain.'),
 '14470':('hold','Glasses/eyes and strong uneven illumination; distorted landmarks unavailable.'),
}


def main():
    target=OUT/'codex_source_screen.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    data=json.loads((OUT/'summary.json').read_text(encoding='utf-8'))
    verification=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
    assert digest(OUT/'summary.json')==verification['summary_sha256']
    assert set(NOTES)=={r['source_id'] for r in data['records']}
    records=[dict(source_id=r['source_id'],screen_status=NOTES[r['source_id']][0],reason=NOTES[r['source_id']][1],
        numerical_status=r['status'],user_decision='pending',training_eligible=False,
        board_sha256=digest(OUT/'boards'/(r['source_id']+'.png'))) for r in data['records']]
    shortlisted=[r for r in records if r['screen_status']=='provisional_user_review']
    assert len(shortlisted)==3 and all(r['numerical_status']=='pending_review' for r in shortlisted)
    target.write_text(json.dumps(dict(reviewer='Codex visual source/reference suitability screen; not human or expert approval',
        scope='All24boards inspected. No model predictions, source replacement or original decision edits.',
        summary_sha256=digest(OUT/'summary.json'),original_review_sha256=digest(OUT/'review.html'),
        records=records,provisional_sources=[r['source_id'] for r in shortlisted],held_sources=21,
        limitations='Small selected development yield, not representative acceptance rate. Reference photos are not calibrated truth.'),indent=2),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Expansion shortlist review</title><style>body{font:17px system-ui;max-width:1250px;margin:25px auto;padding:12px}img{max-width:100%}section{margin:30px 0;border-top:1px solid #aaa}</style><h1>Three provisional sources for your review</h1><p>24 fixed attempts completed; 21 held on numerical or source-quality concerns. These three are provisional, not approved. Review each reference and distorted input for suitability, unwanted selected regions and major missed skin. Green means selected support. An acceptance covers the displayed identity/reference and selected Table2 input, with concerns retained. Reply accept / reject / uncertain per source. No fitting has occurred.</p><p><a href="review.html">All 24 attempts, including held cases</a></p>'
    for r in shortlisted:
        html+=f'<section><h2>{r["source_id"]}</h2><p>{r["reason"]}</p><img src="boards/{r["source_id"]}.png"></section>'
    (OUT/'shortlist_review.html').write_text(html,encoding='utf-8')
    (OUT/'screen_verification.json').write_text(json.dumps(dict(status='pass',all_24_boards_accounted_for=True,
        held=21,provisional=3,no_training_admissions=True,source_screen_sha256=digest(target),
        shortlist_review_sha256=digest(OUT/'shortlist_review.html'),original_summary_unchanged=digest(OUT/'summary.json')==verification['summary_sha256'],
        original_review_unchanged=digest(OUT/'review.html')==verification['review_sha256']),indent=2),encoding='utf-8')
    print('3 provisional sources: '+', '.join(r['source_id'] for r in shortlisted)+'; 21 held; 0 admitted')


if __name__=='__main__':main()
