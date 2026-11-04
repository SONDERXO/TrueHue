"""Fill only the appeal template's content slots; preserve other ZIP parts."""
from pathlib import Path
from xml.dom import minidom
import hashlib
import json
import zipfile
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/NYTHAN/Downloads/Appeal Letter template.docx')
OUT = ROOT / 'outputs/appeal_change_request_20261031_v1'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    global OUT
    simple = '--simple' in sys.argv
    if simple:
        OUT = ROOT / 'outputs/appeal_change_request_20261031_simple_v1'
        OUT.mkdir(exist_ok=True)
    target = OUT / 'TrueHue_Appeal_for_Methodology_Changes_Draft.docx'
    assert not target.exists()
    original = SOURCE.read_bytes()
    with zipfile.ZipFile(SOURCE) as z:
        parts = {x.filename: z.read(x.filename) for x in z.infolist()}
        infos = z.infolist()
    dom = minidom.parseString(parts['word/document.xml'])
    body = dom.getElementsByTagNameNS(W, 'body')[0]
    blocks = [x for x in body.childNodes if x.nodeType == x.ELEMENT_NODE]
    def text(node):
        return ''.join(t.firstChild.data if t.firstChild else '' for t in node.getElementsByTagNameNS(W, 't'))
    def fill(node, value):
        ts = node.getElementsByTagNameNS(W, 't')
        if not ts:
            run = dom.createElementNS(W, 'w:r')
            t = dom.createElementNS(W, 'w:t')
            run.appendChild(t); node.appendChild(run); ts = [t]
        for t in ts:
            while t.firstChild:
                t.removeChild(t.firstChild)
        ts[0].setAttribute('xml:space', 'preserve')
        ts[0].appendChild(dom.createTextNode(value))
    edits = {
        1: '31 October 2026',
        12: text(blocks[12]).replace('<Thesis Title>', '“Smartphone-Based Post-Capture Skin Tone Correction Using ITA Estimation and Machine Learning”'),
        13: 'During the implementation of our initial models, we encountered incomplete facial skin coverage, uneven correction and unwanted changes to acceptable photographs. After two source-held development comparisons, neither new candidate passed our safety criteria; their results are summarized below.',
        14: 'Because of this, we decided to request approval to improve facial masking and formally document the training, evaluation and deployment changes described below. We will retain ITA, calibrated MST, facial statistics and decision-tree gamma/red/blue correction. The challenges we encountered are specifically:',
        15: 'Correction quality: both new candidates increased mean CIEDE2000 error and changed more clean photographs. Lower error is better; clean photographs should remain unchanged. Compare methods within each cycle only.',
        16: 'Measurement quality: existing masks miss facial skin. The parser preview improves coverage but can include facial hair. MST calibration remains experimental and currently outputs categories 1–9. The tables show development results, not final validation.',
        17: 'Retained Research Reference Performance',
        20: 'New Candidate Performance — Neither Adopted',
        24: 'Scope and Limitations: Retain single-photo, on-device Android facial correction and the decision-tree model. Request the following amendments:',
        25: 'Use the existing face parser for skin selection, with reviewed exclusions and matching MST recalibration before adoption. Beard/mustache-specific models and neck correction are excluded from this request.',
        26: 'Document added clean training controls, gamma-only distortion pairs, six RGB endpoint statistics and the clean-control leaf safety policy. State the composite distortion and approximate target-fitting assumptions, including clipping limitations.',
        27: 'Document source-held development comparisons rather than five-fold development validation, with reserved evaluation roles and exposure disclosure. Clarify MST-E calibration/evaluation use, never correction-tree training. Report limited MST support; retain outstanding validation requirements.',
        28: 'Technical Background: Describe YuNet detection, landmark exclusions, the proposed parser, experimental monotone ITA-to-MST calibration, portable JSON tree evaluation instead of ONNX Runtime Mobile, and actual local Windows training. ITA, MST and decision-tree correction remain.',
        29: 'Methodology: Update diagrams and text for 256×256 measurements, the existing HSV AND YCrCb rules, morphology, direct-gamma research targets and legacy reciprocal-gamma conversion. Report duplicate/mask admission, clean-preservation gates and primary/stress results. FairFace-only development does not complete combined SCIN coverage, tone-dependent generation or MST fairness evaluation. Professional feedback, refinement and re-review remain planned after a good initial model. The desktop demo is interim; Android remains the deliverable. Distinguish failed experiments and pending work from adopted changes; this request does not claim model completion.',
    }
    if simple:
        edits.update({
            13: 'During implementation, we found that the system sometimes misses parts of the face, produces uneven color, and changes photographs that already look acceptable. We completed two rounds of model comparisons, but neither new version gave a safe overall improvement.',
            14: 'Because of this, we decided to request approval to improve how facial skin is selected and update the paper to match the actual implementation. We will keep the main approach: ITA skin-tone measurement, MST skin-tone mapping, and decision-tree correction. The challenges we encountered are specifically:',
            15: 'Correction quality: both new versions had larger average color errors and changed more acceptable photographs. The tables show these development results. Lower color error is better. Compare the old and new versions within the same round.',
            16: 'Skin selection: the current method leaves out some facial skin. A separate face-selection model gives better coverage, but still needs checks for hair and other unwanted areas. The skin-tone mapping also needs further checking before we can call it reliable.',
            17: 'Earlier Research Model Results',
            20: 'New Model Results — Neither Version Adopted',
            24: 'Scope and Limitations: Keep an Android app that corrects facial skin from one selected photo. We request the following changes:',
            25: 'Use the existing face-selection model to cover more facial skin. Check its exclusions and update the skin-tone mapping to match it before adoption. Additional beard/mustache models and neck correction are not part of this request.',
            26: 'Include unchanged photographs during training to teach the system when to leave a photo alone. Document the extra lightened and darkened training examples, added color measurements, and rule for preserving training examples that need no correction.',
            27: 'Update the development testing procedure so versions of the same source photo stay together. Keep reserved evaluation photos separate from model improvement. Explain which data were already examined and where skin-tone coverage remains limited.',
            28: 'Technical Background: Update the descriptions of the tools actually used to find faces, select skin, map skin tones, and run the decision tree on Android. This includes YuNet face detection and a saved tree file instead of the originally proposed ONNX tool. Record that training was done on a local Windows computer.',
            29: 'Methodology: Update the diagrams and explanations to match the actual image preparation, training examples, brightness/color settings, skin-tone mapping and tests. Explain that MST-E data support skin-tone mapping and evaluation, not correction-model training. Clearly separate unsuccessful trials from adopted changes. Testing across the intended datasets and skin-tone groups is still unfinished. After obtaining a good initial model, we will retain the planned professional review, refinement and review again. Android remains the final application; the desktop version is a development tool. These changes do not mean the correction model is finished.',
        })
    for i, value in edits.items():
        fill(blocks[i], value)
    # Keep the filled table caption with its table; no type/spacing changes.
    props = blocks[17].getElementsByTagNameNS(W, 'pPr')[0]
    props.appendChild(dom.createElementNS(W, 'w:keepNext'))
    tables = [blocks[18], blocks[21]]
    headers = ['Cycle', 'Cases', 'Sources', 'Mean error', 'Clean edits', 'Status', 'Role']
    if simple:
        headers = ['Round', 'Cases', 'Source photos', 'Color error', 'Clean edits', 'Status', 'Stage']
    rows = [
        [headers, ['Primary', '105', '26', '6.964', '1/26', 'Kept', 'Research'],
         ['Expansion', '121', '32', '6.613', '2/32', 'Kept', 'Research'], [''] * 7],
        [headers, ['Primary', '105', '26', '7.561', '3/26', 'Failed', 'Research'],
         ['Expansion', '121', '32', '7.956', '4/32', 'Failed', 'Research'], [''] * 7],
    ]
    if simple:
        for values in rows:
            values[1][0] = 'Round 1'
            values[2][0] = 'Round 2'
            values[1][6] = values[2][6] = 'Develop-ment'
    for table, values in zip(tables, rows):
        tr = table.getElementsByTagNameNS(W, 'tr')
        assert len(tr) == len(values)
        for row, cells in zip(tr, values):
            tc = row.getElementsByTagNameNS(W, 'tc')
            assert len(tc) == len(cells)
            for cell, value in zip(tc, cells):
                fill(cell.getElementsByTagNameNS(W, 'p')[0], value)
    edited = dom.toxml(encoding='UTF-8')
    with zipfile.ZipFile(target, 'w') as z:
        for info in infos:
            z.writestr(info, edited if info.filename == 'word/document.xml' else parts[info.filename])
    changed = []
    with zipfile.ZipFile(target) as z:
        for name, value in parts.items():
            if z.read(name) != value:
                changed.append(name)
    assert changed == ['word/document.xml']
    assert SOURCE.read_bytes() == original
    check = minidom.parseString(edited)
    finalblocks = [x for x in check.getElementsByTagNameNS(W, 'body')[0].childNodes if x.nodeType == x.ELEMENT_NODE]
    originaldom = minidom.parseString(parts['word/document.xml'])
    originalblocks = [x for x in originaldom.getElementsByTagNameNS(W, 'body')[0].childNodes if x.nodeType == x.ELEMENT_NODE]
    for i, (before, after) in enumerate(zip(originalblocks, finalblocks)):
        if i not in edits and i not in (18, 21):
            assert before.toxml() == after.toxml(), i
    verification = {'template': str(SOURCE), 'template_sha256': sha(original),
                    'output_sha256': sha(target.read_bytes()), 'changed_parts': changed,
                    'original_unchanged': True, 'untouched_body_blocks_preserved': True,
                    'name_placeholders_unchanged': True, 'draft_not_submitted': True}
    (OUT / 'verification.json').write_text(json.dumps(verification, indent=2), encoding='utf-8')
    (OUT / 'artifact.md').write_text(
        '# Template contract\n\nReference: ' + str(SOURCE) + '\nSHA256: ' + sha(original) +
        '\nLetter portrait 12240×15840 twips; all margins 1440; original header and drawing retained.\n'
        'Preserve every package part except word/document.xml; preserve all non-slot body blocks.\n'
        'Editable body slots: ' + str(sorted(edits)) + '; performance tables at 18 and 21.\n'
        'Preserve fonts, paragraph properties, list definitions, table geometry and signature/name sections.\n'
        'Replace template example models and scores with TrueHue content only. Empty third data rows intentional.\n'
        'Names remain user-owned. No approval or final model success is asserted.\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
