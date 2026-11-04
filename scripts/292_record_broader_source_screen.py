"""Record new saved-board observations, preserving prior triage and user scope."""
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/broader_source_screen61_v1'
NOTES={
 '55653':'Warm/yellow reference with forehead markings and nearby fabric. Distorted support collapses to a tiny cheek patch.',
 '77745':'Bright soft reference; reference support includes hair/background and omits large cheek regions. Existing distorted processing failure remains.',
 '58800':'Relatively readable reference with broad matching facial support. Check sideburn/ear boundaries, peripheral non-face inclusion and mouth exclusion.',
 '66237':'Soft reference with highly incomplete forehead/eye coverage. Distorted support reduces to a narrow cheek strip.',
 '22765':'Strong directional light and downward pose; large highlighted/shadowed regions and a nearby hand complicate reference suitability. Inspect nose and side-face coverage.',
 '46551':'Side profile, cap and another visible face/person nearby. Reference support is broad rectangular selection; distorted support is fragmented.',
 '5025':'Strongly oblique reference with a nose highlight. Distorted support loses large eye, forehead and cheek regions.',
 '63509':'Relatively readable reference with broad consistent facial support. Check hair/temple, ear and clothing boundary inclusion before approval.',
 '26935':'Strong orange-looking reference; support covers only a small eye/edge region. Saved target is unavailable despite successful measurement.',
 '75287':'Facial hair and shiny highlights. Distorted support splits into separated cheek/forehead patches; reference suitability remains unresolved.',
 '67512':'Downward pose and directional shadow. Distorted support has broad eye and lower-face omissions; boundary detail needs review.',
 '36658':'Soft dim reference with facial hair. Distorted mask has major central-face and forehead gaps.',
 '21962':'Glasses, warm lighting and bright highlights. Both supports have large cheek/forehead holes and peripheral selection.',
 '42965':'Relatively readable reference and broad corresponding face support. Check outer hair/background edge and mouth boundary; recorded color is not calibrated truth.',
 '47127':'Soft reference with bright cheek highlights. Reference support omits substantial eye/cheek regions; distorted processing failed.',
 '5589':'Low-detail reference. Reference mask reaches hair/peripheral regions; distorted support has enlarged eye-region holes.',
 '54566':'Reference shows strong shadow/highlight contrast. Distorted support loses much of the upper and right-side face.',
 '65608':'Dim reference with strongly lit background. Input support is a small upper-face patch and saved recovery target is unavailable.',
 '77150':'Glasses included in reference support, with forehead/cheek holes. Distorted support loses large portions of the face.',
 '48569':'Oblique pose, soft detail and large missing cheek regions. Distorted support contains additional holes around eyes and mouth.',
 '39934':'Dark sunglasses obscure the eyes; input support loses forehead and nose coverage. Source suitability remains unresolved.',
 '26828':'Soft reference with directional shading and bright nose highlight. Distorted support is highly fragmented.',
 '23693':'Reference has cosmetic appearance and a bright cheek highlight. Supports are comparatively broad, but cosmetic/reference suitability and hair boundary need explicit judgment.',
 '64733':'Heavy blur and reflective glasses prevent precise boundary/detail judgment. Both supports have holes; distorted support adds lower-face omissions.',
 '53979':'Dim warm-looking reference. Distorted processing failed; displayed input has no usable support.',
 '17031':'Soft yellow/green-looking reference with cosmetic appearance. Mask omits forehead and has multiple cheek/chin holes.',
 '67821':'Glasses and hair cover much of the face; reference/input support excludes nearly all upper face and may include peripheral hair.',
 '56020':'Relatively readable reference but a hand is near the chin. Input support has large central-face gaps and possible peripheral inclusion.',
 '40243':'Strong directional sunlight/highlights. Reference mask omits large nose/cheek regions and input adds a large lower-face gap.',
 '77351':'Relatively clear reference, but the mask omits a large strip of the right cheek and reaches toward the shoulder; source and boundary suitability remain unresolved.',
 '67510':'Glasses and dim reference. Reference mask is a sparse one-sided set of patches; saved target is unavailable.',
 '81108':'Soft reference with glasses, lens reflections and facial hair included in support. Input adds large eye/chin gaps.',
 '77101':'Relatively readable reference with broad corresponding facial support. Check chin/side boundaries, mouth exclusion and a nose hole in the input mask.',
 '9654':'Heavy facial hair and large gaps around eyes/nose. Input support reduces to a small lower-face patch; saved target is unavailable.',
 '35000':'Soft downward-facing reference with uneven lighting. Input support adds broad lower-face gaps.',
 '67397':'Strong highlights and shadow; support appears to include peripheral non-face material. Input mask splits into patches.',
 '70911':'Dark-proxy estimate comes from a tiny patch near hair/eye, not broad facial coverage. Existing distorted failure and 100% generation-support clipping remain. This is not evidence of usable dark-tone coverage.',
}
PRIORITY={'58800','63509','42965','77101'}


def main():
    if (OUT/'assistant_observations.json').exists():raise FileExistsError('Observations already recorded')
    rows=json.loads((OUT/'sources.json').read_text())
    summary=json.loads((OUT/'summary.json').read_text())
    for p,sha in summary['input_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha
    new={r['source_id'] for r in rows if r['previous_assistant_observation'] is None}
    assert new==set(NOTES)
    for r in rows:
        sid=r['source_id']
        r['assistant_observation']=r['previous_assistant_observation'] if sid not in NOTES else NOTES[sid]
        r['observation_reused']=sid not in NOTES
        r['readiness']=('exact_user_judgments_recorded_not_admitted' if r['exact_user_judgments'] else
            'existing_distorted_technical_hold' if r['processing_status']!='pending_review' else
            'additional_priority_lead_not_approved' if sid in PRIORITY else 'visible_concerns_need_resolution')
        r['training_admitted']=False
    def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('assistant_observations.json',rows)
    result=dict(status='bounded_screen_complete_no_fitting',sources=61,prior_observations_reused=24,
        additional_observed_sources=37,readiness=dict(Counter(r['readiness'] for r in rows)),
        new_priority_leads=sorted(PRIORITY),no_new_user_review_requested=True,
        dark_proxy_source70911='inadequate_facial_support_not_validated_dark_tone',
        dark_proxy_source59484='prior_original_mask_rejection_No_coverage_retained_not_rereviewed',
        mask_changes=0,distortions_generated=0,model_fits=0,training_admissions=0,
        reserved_pixel_access=0,raw_source_decodes=0)
    write('completion.json',result)
    cards=[]
    for r in sorted(rows,key=lambda r:(r['source_id'] not in PRIORITY,r['source_id'])):
        url='../correction_training_preparation_v1/boards/'+r['source_id']+'.png'
        notes=''
        if r['exact_user_judgments']:
            notes='<ul>'+''.join('<li>'+html.escape(scope)+': '+html.escape(j['decision'])+' — '+html.escape(j['notes'])+'</li>' for scope,j in r['exact_user_judgments'].items())+'</ul>'
        cards.append(f'<section><h2>{r["source_id"]} · {html.escape(r["readiness"].replace("_"," "))}</h2>'
            f'<p>{html.escape(r["assistant_observation"])}</p>{notes}'
            f'<p>Original technical status: {r["processing_status"]}. Experimental severity: {r["experimental_severity"]}. '
            f'Prior observation reused: {r["observation_reused"]}.</p><a href="{url}"><img loading="lazy" src="{url}" alt="Saved board {r["source_id"]}"></a></section>')
    (OUT/'screen.html').write_text('<!doctype html><meta charset="utf-8"><title>Bounded 61-source screen</title>'
        '<style>body{font:17px system-ui;background:#151923;color:#eee;max-width:1250px;margin:30px auto;padding:20px}img{max-width:100%}section{border-top:1px solid #888;padding-top:10px;margin-top:30px}</style>'
        '<h1>Bounded source screen complete</h1><p>61 sources: reuse 24 previous observations and inspect 37 additional saved boards. '
        'User judgments remain separate from assistant observations. No training admission, new variant generation or review request.</p>'
        '<p>The four first cases are unapproved leads. Original failures are retained without replacements. '
        'The dark-proxy source70911 has inadequate facial support; no dark-tone coverage is claimed.</p>'+''.join(cards),encoding='utf-8')
    write('verification.json',dict(status='pass',unique_sources=len({r['image_id'] for r in rows}),
        new_observation_membership_exact=True,prior24_reused=True,user3_decisions_preserved=True,
        original_input_hashes_unchanged=True,
        evidence_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
