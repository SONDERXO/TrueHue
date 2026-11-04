"""Preserve proposal content; insert clearly marked findings and anchored comments."""
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from xml.dom import minidom as D
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('C:/Users/NYTHAN/Downloads/Copy of Thesis Proposal Document.docx')
OUT=ROOT/'outputs/thesis_integration_20261031_v1'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(node):return ''.join(n.firstChild.data for n in node.getElementsByTagNameNS(W,'t') if n.firstChild)
def direct(node,name):return [n for n in node.childNodes if n.nodeType==n.ELEMENT_NODE and n.namespaceURI==W and n.localName==name]


def main():
    if OUT.exists():raise FileExistsError(OUT)
    before=digest(SOURCE)
    with ZipFile(SOURCE) as source:parts={name:source.read(name) for name in source.namelist()}
    doc=D.parseString(parts['word/document.xml']);body=doc.getElementsByTagNameNS(W,'body')[0]
    original=direct(body,'p');original_text=[text(p) for p in original]
    assert original_text[436]=='BIBLIOGRAPHY' and original_text[281]=='CHAPTER 4'
    def element(name,attrs=None):
        n=doc.createElementNS(W,'w:'+name)
        for k,v in (attrs or {}).items():n.setAttributeNS(W,'w:'+k,str(v))
        return n
    def paragraph(value,style=None,page=False):
        p=element('p');pr=element('pPr')
        if style:pr.appendChild(element('pStyle',{'val':style}));pr.appendChild(element('keepNext'))
        if page:pr.appendChild(element('pageBreakBefore'))
        pr.appendChild(element('spacing',{'before':0 if not style else 180,'after':120,'line':360,'lineRule':'auto'}))
        pr.appendChild(element('jc',{'val':'both' if style is None else 'left'}))
        p.appendChild(pr);run=element('r');rp=element('rPr')
        rp.appendChild(element('rFonts',{'ascii':'Times New Roman','hAnsi':'Times New Roman'}))
        rp.appendChild(element('sz',{'val':24}));run.appendChild(rp)
        t=element('t');t.setAttribute('xml:space','preserve');t.appendChild(doc.createTextNode(value));run.appendChild(t);p.appendChild(run)
        return p
    comments=D.Document();cr=comments.createElementNS(W,'w:comments');cr.setAttribute('xmlns:w',W);comments.appendChild(cr)
    notes={
        28:'Draft status: the Android application and reliable correction are not complete. This proposal statement must not become a completed-result claim. See new Chapters 5–6; the desktop demo is an older failed-gate baseline.',
        130:'Data-role ambiguity: this passage says MST-E is evaluation-only, but Section 4.3.2 uses it to derive a lookup. Existing work discloses MST-E mapping development/evaluation, never correction-tree training. Confirm permitted role wording with the adviser; do not claim an untouched benchmark.',
        133:'Scope decision required: the proposal explicitly excludes neck correction, while a later user requirement requests visible neck coverage. Neck correction is unfinished; reconcile scope with the adviser rather than silently changing this paragraph.',
        287:'Implementation record: actual Python work runs locally in the Windows Python3.14 environment. Do not claim GX10/Colab training unless supporting run records exist. Android testing remains incomplete.',
        289:'Latest direction: photographer opinions come after model completion using the existing Google Form. No photographer scores have been collected. Do not use expert feedback as an assumed prerequisite for current model development.',
        299:'Preserve conflicting SCIN annotations and gradability metadata; attached labels do not automatically establish a clean facial reference or independent true skin color. Do not imply every selected source supplies validated MST training truth.',
        308:'The executed engineering recipes and supplemental gamma-only inputs are explicitly documented assumptions. The completed comparisons do not establish this full tone-dependent generation design or balanced ten-category coverage.',
        309:'The source file already acknowledges uncalibrated references in Section1.4. Here, known well-exposed reference is an assumption, not verified truth for every admitted image. Use photographic-reference wording consistent with that limitation.',
        316:'Actual research contract: square256 YuNet0.85, exactly one face, HSV AND YCrCb,5x5 morphology, component/anatomical exclusions and required landmarks. It is not the MediaPipe/Haar plus YCrCb-only recipe stated here. Parser changes remain a separate held proposal.',
        322:'The current monotone lookup is experimental, not final validated calibration. It emits MST1–9, never10, with weak exact accuracy and limited subject support. Do not present a schema/lookup file as proof of validated mapping.',
        324:'Reconcile with actual source-held development folds and the separately frozen600-source allocation. Neither current development comparison nor that allocation establishes validated MST stratification or verified distinct-person splits.',
        336:'The completed fixed comparisons use26/32 source-held folds, depth3/seed42/leaf1 and fitting-control protection, rather than a completed five-fold model-selection procedure. Do not describe the proposed procedure as performed.',
        339:'The stated10% fairness-disparity rule has not been established as a completed evaluation here. No supported ten-category fairness conclusion follows from pooled CIEDE2000 or the failed clean-safety gates.',
        419:'No expert ratings/refinement or final MOS results have been executed. Preserve this as a plan, with photographer opinions after model completion. Later development must not retune to final evaluation outcomes.',
        421:'Android on-device latency remains unmeasured/incomplete. Python timings and a successful APK build do not satisfy this proposed device evaluation.',
        433:'These are intended validation activities, not evidence of achieved fairness or realistic-use reliability. New Chapters5–6 distinguish implemented software from unmet scientific and mobile objectives.',
    }
    for cid,(index,note) in enumerate(notes.items()):
        p=original[index];start=element('commentRangeStart',{'id':cid});end=element('commentRangeEnd',{'id':cid})
        offset=1 if direct(p,'pPr') else 0;p.insertBefore(start,p.childNodes[offset] if len(p.childNodes)>offset else None)
        p.appendChild(end);r=element('r');r.appendChild(element('commentReference',{'id':cid}));p.appendChild(r)
        c=comments.createElementNS(W,'w:comment')
        for k,v in {'id':str(cid),'author':'TrueHue review','date':datetime.now(timezone.utc).isoformat()}.items():c.setAttributeNS(W,'w:'+k,v)
        cp=comments.createElementNS(W,'w:p');rr=comments.createElementNS(W,'w:r');tt=comments.createElementNS(W,'w:t')
        tt.appendChild(comments.createTextNode(note));rr.appendChild(tt);cp.appendChild(rr);c.appendChild(cp);cr.appendChild(c)
    anchor=original[436];inserted=[]
    def add(value,style=None,page=False):
        node=paragraph(value,style,page);body.insertBefore(node,anchor);inserted.append(node)
    add('4.11 Implemented Research Method and Status — Draft Update','Heading3')
    add('This implementation update and the following findings chapters were added on31 October2026 for thesis integration review. Chapters1–4 retain their original proposal wording with anchored review comments. Planned procedures must not be interpreted as completed work. The bibliography and appendices remain in their original order. Chapter numbering and the table of contents require confirmation before final submission.')
    add('4.11.1 Measurement and correction implementation','Heading4')
    add('The research pipeline retains face detection, facial skin masking, ITA, experimental calibrated MST and facial statistics, followed by decision-tree gamma/red/blue correction. The evaluated measurement uses whole-frame256x256 INTER_LINEAR resizing, YuNet confidence0.85, exactly one face, combined HSV/YCrCb selection,5x5 morphological processing, component selection, landmark-based anatomical exclusions and at least1000 selected pixels. This differs from the proposed detector/mask description and must be documented as an implementation choice.')
    add('Eleven input-only features enter the strongest retained research schema: masked mean L*,a*,b*, ITA, mapped MST index, and the masked fractions exactly0 and255 in each RGB channel. MST is estimated from the input ITA; no reference label or target statistic enters inference. The lookup is experimental and actually emits labels1–9. It is tied to the original measurement contract and cannot be reused silently with a different mask.')
    add('The fixed correction experiments use depth3, seed42, minimum leaf1, unweighted fitting and identity output in leaves containing fitting clean controls. All variants of each held source/known duplicate group are excluded together. For normalized encoded RGB, direct correction is clip([red_gain*R**gamma, G**gamma, blue_gain*B**gamma],0,1), rounded to8-bit and applied only inside the input mask. Legacy code uses reciprocal gamma and requires conversion; the desktop demo continues to run that older baseline separately.')
    add('4.11.2 Data provenance and evaluation','Heading4')
    add('The completed evidence is development-exposed. The original reviewed cohort contains26 controls and21 distorted stress cases. The primary cycle adds58 accepted primary masks; the broader cycle adds six original controls, six saved stress cases and four accepted primary variants from two new sources. Rejects, holds and exact review notes are retained. Mask approval does not validate correct illumination or intrinsic skin color.')
    add('The historical650-source partition is already exposed. A separate600-source allocation has420 training,90 development-validation and90 final-test selections; duplicate screening leaves418/89/90 candidates. Candidates are not automatically approved data or verified independent people. Earlier duplicate auditing decoded held-out pixels; reserved roles remain locked against fitting/tuning, not described as never opened. MST-E is retained for disclosed mapping development/evaluation only, not correction-tree training.')
    add('Evaluation reports source-mask CIEDE2000 on matched rows, no-correction baselines, case-weighted and source-equal means, processing holds and exact changed-pixel counts on clean controls. The original and expanded procedures are compared with frozen settings. Failed gates prohibit adoption or follow-up same-cohort parameter/source-exception searches. Photographer opinions remain after model completion; no MOS results are reported.')
    add('CHAPTER 5','Heading1',True);add('DEVELOPMENT RESULTS AND DISCUSSION — DRAFT','Heading1')
    add('5.1 Scope of the results','Heading2')
    add('These findings describe completed Python development comparisons, not independent final validation, a completed smartphone application or a demonstrated fairness improvement across all MST categories. Lower CIEDE2000 is better. Comparisons are valid within matched evaluation sets; totals across47,105 and121 cases must not be treated as isolated effects of changing one factor.')
    add('5.2 Experimental MST evidence','Heading2')
    add('The earlier strict center/threshold recipe produced zero available held-subject predictions. A separately frozen monotone recipe later produced396 predictions from418 attempts across15 measured subjects, retaining22 processing failures. Equal-subject ordinal MAE was2.306 versus3.000 for the same-row median baseline; exact accuracy was11.11% versus14.39%, and within-one accuracy was33.84% versus22.22%. The packaged lookup emits1–9 rather than a validated ten-category range.')
    add('Of the measured images,180 lacked another fitting subject from the held category. Categories4,5,7,9 and10 each had one measured subject. Ordinal development improvement and portable implementation parity do not establish final scientific validity. The previously user-reported adviser approval of limited MST evaluation scope is retained; it does not validate the lookup or every later method amendment.')
    add('5.3 Completed correction comparisons','Heading2')
    add('Endpoint fractions improved the earlier47-case comparison from8.013 for its matched five-feature comparator to5.300, leaving25/26 clean originals unchanged. The remaining clean failure prevented adoption. Two later predeclared data cycles were completed without tuning after outcomes.')
    add('In the105-case primary comparison, total CIEDE2000 was6.964 for the endpoint reference and7.561 for the primary candidate. Normal-primary error improved8.312 to6.629, but stress error worsened11.279 to18.000. Clean changes increased from1/26 to3/26. The candidate failed the declared safety requirement and was not adopted.')
    add('In the121-case comparison across32 source groups, no-correction error was8.765, endpoint reference A was6.613, prior-primary comparator B was7.751 and expanded candidate C was7.956. C changed4/32 clean originals, compared with2/32 for A and3/32 for B. C clean failures were62331,83205,29880 and68073; all four boards showed visible unwanted correction.')
    add('C pooled-primary error was6.787 versus8.066 without correction, but new-primary error was5.439 versus3.782 without correction. Pooled primary color error was5.076 versus3.828 without correction, and stress error was18.524 versus10.357 for A. Source-equal total error also favored A:6.552, compared with7.943 for B and8.116 for C. Exposure reconstruction gains therefore do not establish general color-correction or clean-preservation success.')
    add('Only four of fifteen new primary masks were accepted, from two added sources. Eleven were rejected, while13 additional clipped variants and two technical mask-screen holds remained outside the new primary fit and evaluation. All121 admitted cases produced all three outputs. These explicit preparation/review exclusions are not hidden processing failures.')
    add('5.4 Reproducibility and software verification','Heading2')
    add('The broader comparison fitted34 new trees and reused52 historical trees and210 historical predictions. Verification reconstructed121 feature vectors, checked34 tree memberships and protected/unprotected leaf means, and replayed153 new image/metric outputs without verification refits. A reporting interruption preserved29 already fitted trees and completed only five remaining fits; it did not restart a scientific trial. All saved metrics and stopping decisions remain available in the local evidence records.')
    add('The latest full Python suite passed836 tests in28.36seconds with caching disabled. Real Tk widget checks covered open, controlled result display, failed-run exports, save cancellation, save errors and retry. Controlled inference responses verify UI state handling, not model accuracy. Visual GUI layout and Android device evaluation were not established by those checks.')
    add('5.5 Interpretation and threats to validity','Heading2')
    add('A lower pooled error can coexist with unacceptable clean-image changes. Fitting-control leaf protection cannot guarantee that an unseen clean face reaches a protected leaf. Neither rejected successor should be described as a safe automatic correction upgrade. The endpoint reference also fails clean safety and remains research evidence, not an approved deployment model.')
    add('ITA and mapped MST derive from the same facial color statistics and do not independently observe illumination. Reference quality, weak mapping accuracy, limited source diversity, target approximation and mask support are plausible contributors to the failures. These comparisons do not identify one sole cause or prove that the retained method is mathematically impossible. Adding six controls without broad accepted distortion coverage cannot establish that more independent controlled data would fail.')
    add('Synthetic pairs share geometry and target lineage; real captures can differ in motion, shadows and camera processing. Reference-mask CIEDE2000 measures reconstruction disagreement, not intrinsic reflectance, aesthetic preference or identity preservation. Source groups do not prove distinct participants, and historically exposed evaluation cannot support an untouched final-generalization claim.')
    add('Positive gamma/gains cannot restore encoded zero channels, and green255 remains invariant under the unscaled green channel. Outside-mask pixels remain unchanged. The earlier RGB-MAE lower-bound audit is not a CIEDE2000 bound or a complete artifact explanation. Patchy masks, JPEG-dependent coverage, facial-hair exclusions and visible neck coverage remain unresolved.')
    add('CHAPTER 6','Heading1',True);add('CONCLUSION AND RECOMMENDATIONS — DRAFT','Heading1')
    add('6.1 Conclusion','Heading2')
    add('TrueHue has implemented a reproducible Python research pipeline, portable decision-tree inference, reviewed development data and traceable comparisons under the retained ITA/MST method. Endpoint information improved an early matched result, but both later frozen data cycles failed clean safety and comparative quality gates. Reliable automatic skin-tone correction, supported ten-category MST validation and the full smartphone deliverable have not been achieved.')
    add('No rejected candidate was adopted. The desktop demo still uses the older ten-source baseline5/fold1 rather than the stronger endpoint research reference or either successor. Its explicit experimental notice and hash-bound saved reports identify that distinction; they do not improve or validate its correction quality. New training and parser/beard changes remain on hold while the adviser decision is pending.')
    add('6.2 Recommendations and outstanding objectives','Heading2')
    add('The next substantial research decision should establish trustworthy photographic-reference evidence and an achievable evaluation claim before another fitting cycle. Controlled smartphone reference collection with a neutral/color target is a discussion draft only: participant access, institutional requirements, equipment, sample-size rationale, repeatability and person-level data roles must be agreed before collection. The target would support offline reference evidence, not introduce reference-guided runtime inputs or establish intrinsic skin reflectance by itself.')
    add('Retain ITA, calibrated MST and facial-statistics decision-tree correction unless explicitly amended. Future MST work needs matching masks, disclosed historical exposure, supported category scope and independent labeled-subject validation with criteria fixed beforehand. Do not manufacture MST10 output, relabel historical exposure as untouched evaluation, or treat correction success as independent mapping validation.')
    add('A learned-parser replacement requires a separate method decision and matching measurement/calibration evidence. Parser and beard/moustache work is currently held. Android integration and device timing, neck coverage, independent correction evaluation and photographer appraisal remain unfinished. The proposal excludes neck correction while a later user requirement requests it; this scope difference needs an explicit decision rather than a silent claim of completion.')
    add('Continue thesis writing and software usability work while awaiting the adviser response, but do not use documentation or passing tests as substitutes for scientific validation. Any future correction cycle should be substantive and predeclared, with preserved failures and no same-cohort mask, feature, depth, weight or source-specific adjustments after a gate failure.')
    # Keep bibliography on a new page after the inserted chapter draft.
    pp=direct(anchor,'pPr')
    if pp:pp=pp[0]
    else:pp=element('pPr');anchor.insertBefore(pp,anchor.firstChild)
    if not direct(pp,'pageBreakBefore'):pp.appendChild(element('pageBreakBefore'))
    rels=D.parseString(parts['word/_rels/document.xml.rels'])
    ids={n.getAttribute('Id') for n in rels.documentElement.childNodes if n.nodeType==n.ELEMENT_NODE}
    rid='rIdTrueHueReviewComments';assert rid not in ids
    rel=rels.createElementNS(REL,'Relationship');rel.setAttribute('Id',rid)
    rel.setAttribute('Type','http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments');rel.setAttribute('Target','comments.xml');rels.documentElement.appendChild(rel)
    types=D.parseString(parts['[Content_Types].xml']);override=types.createElementNS(CT,'Override')
    override.setAttribute('PartName','/word/comments.xml');override.setAttribute('ContentType','application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml');types.documentElement.appendChild(override)
    changes={'word/document.xml':doc.toxml(encoding='utf-8'),'word/comments.xml':comments.toxml(encoding='utf-8'),
        'word/_rels/document.xml.rels':rels.toxml(encoding='utf-8'),'[Content_Types].xml':types.toxml(encoding='utf-8')}
    OUT.mkdir();output=OUT/'TrueHue_Thesis_Integration_Review_Draft.docx'
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for name,raw in parts.items():z.writestr(name,changes.get(name,raw))
        z.writestr('word/comments.xml',changes['word/comments.xml'])
    assert digest(SOURCE)==before
    with ZipFile(output) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):D.parseString(z.read(name))
        saved=D.parseString(z.read('word/document.xml'));after=[text(p) for p in direct(saved.getElementsByTagNameNS(W,'body')[0],'p')]
        assert after[:436]==original_text[:436]
        assert after[-len(original_text[436:]):]==original_text[436:]
        assert len(after)==len(original_text)+len(inserted)
        for name,raw in parts.items():
            if name not in changes:assert z.read(name)==raw,name
        starts=saved.getElementsByTagNameNS(W,'commentRangeStart');ends=saved.getElementsByTagNameNS(W,'commentRangeEnd');refs=saved.getElementsByTagNameNS(W,'commentReference')
        assert len(starts)==len(ends)==len(refs)==len(notes)
    report=dict(status='structural_checks_pass_visual_render_unavailable',source_sha256=before,source_unchanged=True,
        original_direct_paragraphs=len(original),added_paragraphs=len(inserted),anchored_comments=len(notes),
        original_paragraph_text_preserved=True,unchanged_package_parts_verified=True,
        output_sha256=digest(output),new_chapters_draft_only=True,google_document_modified=False,
        table_of_contents_requires_update=True,visual_QA=False,visual_QA_reason='LibreOffice/soffice is not installed.',
        notes_by_original_paragraph=notes,producer_sha256=digest(Path(__file__)))
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','source_unchanged','original_direct_paragraphs','added_paragraphs','anchored_comments','visual_QA']},indent=2))


if __name__=='__main__':main()
