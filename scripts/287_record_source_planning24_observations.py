"""Preserve assistant observations of the six sheets; no human decisions."""
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/source_planning24_triage_v1'

# Visual observations made from the original-size saved four-panel sheets.
OBSERVATIONS = {
    '50457': 'Soft, warm-looking reference. Reference support appears to include peripheral hair/background; input support extends toward image edges.',
    '16951': 'Strong warm illumination and highly asymmetric mask coverage; large cheek regions are omitted in both supports.',
    '61590': 'Dim reference with glasses and beard included in reference support; distorted processing failed.',
    '2434': 'Relatively clear frontal reference and broad facial support. Distorted support has nose/cheek holes and needs exact inspection; skin detail and lighting are not calibrated.',
    '76204': 'Soft reference with sideward pose and facial hair. Distorted support loses large eye, cheek and lower-face regions.',
    '10567': 'Reflective sunglasses occupy much of the face and are partly selected. Hat and peripheral non-face regions also need exclusion review.',
    '9572': 'Dark, low-detail reference; mask is only a small patch beside the eye. Distorted processing failed.',
    '76067': 'Broad facial support, but a dark forehead mark remains selected in the reference. Source suitability and exclusion of non-skin pigment need resolution.',
    '25517': 'Relatively clear frontal reference with broad matching face support. Check boundary hair/background inclusion and small forehead holes in distorted support.',
    '72939': 'Slanted image with beard and strong skin highlights. Both supports have holes around the nose; input adds forehead/cheek gaps.',
    '86255': 'Soft reference with bright facial highlights and visible cosmetic appearance. Input support has enlarged holes near eyes and nose; reference neutrality is unknown.',
    '47439': 'Strong blur and visible cosmetic appearance. Mask has major forehead/nose gaps; fine boundaries and reference color are unreliable to judge here.',
    '71785': 'Soft oblique reference; reference mask already has holes and facial-hair concerns. Distorted processing failed despite some displayed support.',
    '46277': 'Glasses and lens areas are included in reference support. Distorted support has additional eye and chin gaps.',
    '65420': 'Soft reference with uneven facial shading. Distorted mask omits large facial areas and appears to include nearby non-face regions.',
    '19067': 'Dim low-detail reference with a vertical obstruction across the face. Distorted support fragments into a small set of patches.',
    '72367': 'Heavy blur and oblique pose make reference detail and boundaries uncertain. Distorted processing failed.',
    '68317': 'Downward pose and reference softness. Distorted support loses sizable nose and lower-cheek regions.',
    '2025': 'Soft reference with glasses and a forehead mark; reference support includes these non-skin features. Input has additional eye/chin gaps.',
    '65641': 'Reference shows facial hair, shadow and bright highlights. Distorted support breaks into separated patches across the central face.',
    '75119': 'Warm-looking, soft reference; support includes facial hair/peripheral regions. Input develops substantial lower-face gaps.',
    '58767': 'Hair crosses the face and is selected in reference support; facial support is patchy. Distorted processing failed.',
    '11900': 'Flash-like highlights, facial hair and piercing need source/mask review. Distorted support retains only a fragmented central patch.',
    '39083': 'Relatively readable reference and broad corresponding facial support. Check peripheral hair, mouth exclusion and reference lighting before use.',
}
PRIORITY = {'2434', '25517', '39083'}


def main():
    target = OUT/'assistant_observations.json'
    if target.exists():
        raise FileExistsError(target)
    rows = json.loads((OUT/'triage.json').read_text())
    assert {r['source_id'] for r in rows} == set(OBSERVATIONS)
    summary = json.loads((OUT/'summary.json').read_text())
    for relative, sha in summary['input_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == sha
    for r in rows:
        r['assistant_visual_observation'] = OBSERVATIONS[r['source_id']]
        r['assistant_triage'] = ('existing_distorted_technical_hold' if r['original_processing_status']!='pending_review'
            else 'priority_for_missing_judgments' if r['source_id'] in PRIORITY else 'visible_concerns_need_resolution')
        r['human_decision'] = 'not_requested'
        assert not r['training_admitted']
    target.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    cards = []
    for r in sorted(rows, key=lambda r:(r['source_id'] not in PRIORITY, r['source_id'])):
        board = '../correction_training_preparation_v1/boards/'+r['source_id']+'.png'
        cards.append(f'<section><h2>{r["source_id"]}: {html.escape(r["assistant_triage"].replace("_", " "))}</h2>'
            f'<p>{html.escape(r["assistant_visual_observation"])}</p>'
            f'<p>Recorded status: {r["original_processing_status"]}; failure: {html.escape(str(r["distorted_failure"]))}; '
            f'experimental severity: {r["experimental_severity"]}; clipping fraction: {r["clipping_fraction"]}.</p>'
            f'<a href="{board}"><img loading="lazy" src="{board}" alt="{r["source_id"]} original saved four-panel board"></a></section>')
    (OUT/'triage.html').write_text('<!doctype html><meta charset="utf-8"><title>Additional-source quality triage</title>'
        '<style>body{font:17px system-ui;max-width:1250px;margin:30px auto;padding:20px;background:#15181e;color:#eee}'
        'section{border-top:1px solid #777;margin-top:30px}img{max-width:100%}</style>'
        '<h1>24-source quality triage</h1><p>Assistant observations only. No human approvals or training admission. '
        'First three cases are leads for missing judgments, not accepted data. Existing technical holds remain. '
        'Green indicates selected pixels, not mask accuracy. Click a board for full size.</p>'+''.join(cards), encoding='utf-8')
    result = dict(status='pass', observed_sources=24,
        assistant_triage_counts=dict(Counter(r['assistant_triage'] for r in rows)),
        reserved_role_access=0, new_human_decisions=0, training_admissions=0, model_fits=0,
        original_evidence_hashes_unchanged=True,
        evidence_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()})
    (OUT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},indent=2))


if __name__ == '__main__':
    main()
