"""Freeze qualitative dispositions for all60attempts, preserving numerical failures."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/table2_source_expansion60_v1'
PROVISIONAL={
 '1398':'Broad reference support; distorted cheek/jaw losses and face-box edge need review.',
 '68453':'Broad support; retained cheek holes and hairline/outer-face boundaries need review.',
 '12222':'Broad side-face support; verify eye/hair and lower/jaw boundaries in the posed view.',
 '59944':'Broad support; verify upper-eye/hairline selection and photographic illumination suitability.',
 '66156':'Broad support at light severity; check lower rectangular support near neck/clothing and reference softness.',
 '63087':'Broad facial support; verify side/ear/neck edges and photographic reference suitability.',
 '60381':'Broad light-severity support; flash/highlight spots and hand/hair/background boundaries need review.',
}
HOLDS={
 '80771':'Eyewear selected; distorted support collapses to narrow facial strips.',
 '62256':'Hat/upper-border selection and fragmented distorted facial support.',
 '22008':'Strong uneven shadow/illumination and large unsupported facial region.',
 '38352':'Soft detail and severe distorted support fragmentation.',
 '35583':'Pacifier/occlusion and large distorted facial support loss.',
 '55522':'Low detail/uneven illumination and missing half-face after distortion.',
 '79397':'Facial hair/outer-edge contamination and missing lower support.',
 '6876':'Warm reference/cast and severe distorted lower-face holes.',
 '37995':'Warm/dim reference with major distorted face-region gaps.',
 '79973':'Low detail, hair/edge concerns and severe distorted support loss.',
 '13783':'Strong side shadow; large distorted side-face loss.',
 '80465':'Beard/hair and foreground cup/hand near selected region; major support loss.',
 '1656':'Soft reference detail and sparse distorted mid-face support.',
 '58519':'Hair selected extensively in reference and distorted support.',
 '20499':'Soft reference and distorted support limited mainly to upper face.',
 '22500':'Large reference/input support holes, including nose and cheeks.',
 '61509':'Extensive distorted facial holes and hair/outer-face edge uncertainty.',
 '56164':'Large pale facial regions not selected; reference support is limited mainly to lower face.',
 '71274':'Facial-hair inclusion and distorted cheek/mouth support gaps.',
 '37301':'Sunglasses selected inside nominal skin region.',
 '5263':'Very soft detail/strong highlights and surrounding edge spill.',
 '31065':'Strong warm/greenish cast and makeup/eye/edge uncertainty; no cosmetics claim established.',
 '19260':'Strong warm illumination and extensive reference/input holes.',
 '80729':'Glasses included; reference/input selection fragmented.',
 '19177':'Reference and distorted support contain large scattered facial holes.',
 '45982':'Dim/uneven reference and severe distorted nose/cheek holes.',
 '3109':'Another person near face-box boundary and soft detail; scene/support isolation uncertain.',
 '33518':'Large reference and distorted facial gaps and collar/edge spill.',
 '57887':'Visible facial white marks/foreign material, with possible inclusion; material suitability unresolved.',
 '21056':'Strong facial highlights; forehead/nose gaps and microphone/jaw-edge uncertainty.',
 '31645':'Eyewear/eye selection and lower neck/clothing spill.',
 '7030':'Soft bright reference with hair/outer-region inclusion and gaps.',
 '10392':'Bright reference, facial holes and hair/outer-edge inclusion.',
 '82108':'Soft detail, eye-rim selection and large lower/right border spill.',
 '55528':'Strong highlights/uneven reference and large facial selection gaps.',
 '22334':'Large unselected cheek regions and foreground/shadow strip geometry.',
 '16376':'Eyewear/eye selection and soft reference; side boundary uncertain.',
 '2394':'Large reference/input gaps and selected clothing/outer-edge regions.',
 '64202':'Bright/soft reference, glasses/eyes selected and neck/clothing spill.',
 '86704':'Pose/hair occlusion and uncertain selected eye/outer-face boundaries.',
 '5942':'Sunglasses and hair selected as skin.',
}


def main():
    target=OUT/'codex_source_screen.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    data=json.loads((OUT/'summary.json').read_text(encoding='utf-8'));v=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
    assert digest(OUT/'summary.json')==v['summary_sha256']
    records=[]
    for s in data['records']:
        name=s['source_id'];status=s['status']
        if status!='pending_review':
            reason='Numerical hold: '+status+'; '+str(s.get('input_measurement',s['reference_measurement']).get('reason','target support unavailable'))
            disposition='hold_numerical'
        elif name in PROVISIONAL:reason=PROVISIONAL[name];disposition='provisional_user_review'
        else:reason=HOLDS[name];disposition='hold_source_or_processing_suitability'
        records.append(dict(source_id=name,numerical_status=status,screen_status=disposition,reason=reason,
            board_sha256=digest(OUT/'boards'/(name+'.png')),user_decision='pending',training_eligible=False))
    assert len(records)==60 and sum(r['screen_status']=='provisional_user_review' for r in records)==7
    assert {s['source_id'] for s in data['records'] if s['status']=='pending_review'}==set(PROVISIONAL)|set(HOLDS)
    target.write_text(json.dumps(dict(reviewer='Codex qualitative source/pair screen,not human approval or photographer opinion',
        records=records,provisional_sources=list(PROVISIONAL),held_sources=53,inspected_boards=60,
        summary_sha256=digest(OUT/'summary.json'),no_model_predictions_used=True,training_admitted=0),indent=2),encoding='utf-8')
    sections=[]
    for name,reason in PROVISIONAL.items():
        s=next(s for s in data['records'] if s['source_id']==name)
        sections.append(f'<section><h2>{name}: {s["assigned_severity"]} distortion</h2><p>{reason}</p><img src="boards/{name}.png"></section>')
    (OUT/'shortlist_review.html').write_text('<!doctype html><meta charset="utf-8"><title>Seven provisional source pairs</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}section{margin:30px 0;border-top:1px solid #999}</style><h1>Seven provisional sources from the fixed60batch</h1><p>User source/pair review before training, not photographer evaluation. Green is selected support, not correctness. Each source has reference/control and its displayed MST-conditioned distortion. Assess reference usability, missed skin, hair/eye/clothing/background or other-person inclusion. Reply accept/reject/uncertain per source and retain concerns. No model fitting occurred. The other53holds and all failures are preserved.</p><p><a href="review.html">All60attempts</a></p>'+''.join(sections),encoding='utf-8')
    (OUT/'screen_verification.json').write_text(json.dumps(dict(status='pass',all_60_accounted_for=True,provisional=7,held=53,
        source_screen_sha256=digest(target),shortlist_review_sha256=digest(OUT/'shortlist_review.html'),
        summary_unchanged=digest(OUT/'summary.json')==v['summary_sha256'],original_review_unchanged=digest(OUT/'review.html')==v['review_sha256']),indent=2),encoding='utf-8')
    print('7provisional sources;53holds;0admissions/fits')


if __name__=='__main__':main()
