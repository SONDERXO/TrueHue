"""Whole-document augmentation evidence index; no training or PDF changes."""
import hashlib
import json
import re
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'outputs/pdf_augmentation_audit_runtime_v1'))
from pypdf import PdfReader


def main():
    out=ROOT/'outputs/proposal_full_scan_v1'
    target=out/'summary.json'
    if target.exists():raise FileExistsError(target)
    pdf=Path('C:/Users/NYTHAN/Downloads/Thesis Proposal Document.pdf')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before=digest(pdf);reader=PdfReader(pdf)
    terms=['gamma','midtone','distortion','synthetic','brightness','contrast','cyan','yellow',
        'equation','clipping','photoshop','lightroom','gimp','pillow','script','appendix','programmatically']
    pages=[];texts={}
    for index,page in enumerate(reader.pages,1):
        raw=page.extract_text() or '';normalized=re.sub(r'\s+',' ',raw).strip()
        texts[index]=normalized
        pages.append(dict(pdf_page=index,extracted_characters=len(normalized),
            text_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            matched_terms={term:len(re.findall(r'\b'+re.escape(term)+r'\b',normalized,re.I)) for term in terms
                if re.search(r'\b'+re.escape(term)+r'\b',normalized,re.I)}))
    assert len(pages)==111
    assert 'Values of gamma less than 1 brighten darker regions' in texts[38]
    assert 'three synthetic distorted versions' in texts[59]
    assert 'Gamma/ Midtone' in texts[62] or 'Gamma/' in texts[62]
    assert list(reader.attachments.keys())==[]
    # Retain method evidence only, not personal CV/contact details on final pages.
    excerpts={str(n):texts[n] for n in [28,38,39,59,60,61,62,63,64,65,71,72,75]}
    (out/'all_page_search_index.json').write_text(json.dumps(pages,indent=2),encoding='utf-8')
    (out/'method_evidence.json').write_text(json.dumps(excerpts,indent=2),encoding='utf-8')
    summary=dict(status='full_document_scan_complete',pages_scanned=111,pdf_sha256=before,
        attachment_count=0,explicit_gamma_convention=dict(pdf_page=38,printed_page=31,
            behavior='numeric gamma below1 brightens; above1 darkens',current_reciprocal_parameterization='opposite behavior for same numeric gamma'),
        three_distorted_versions_per_source_pdf_page=59,
        table2_pdf_page=62,table3_pdf_page=64,
        complete_augmentation_equations_found=False,generation_script_or_editor_preset_found=False,
        unresolved=['operation order','brightness/contrast units and transfer functions','channel-shift semantics',
            'intermediate clipping','gamma/midtone table versus correction-definition convention','definition of the three distorted variants'],
        appendix_content='App screen mockups and evaluation questionnaire; no augmentation source code',
        rendered_inspected_pdf_pages=[17,38,42,61,64,69,71,72,73,77,80,85,86,97,98,100,101,102,103,105,106,107],
        code_or_dataset_changes=0,models_fitted=0,
        correction_to_previous_audit='Gamma convention is stated in definition section; previous method-page-only audit missed it. Full composite remains underdetermined.')
    target.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    assert digest(pdf)==before
    (out/'verification.json').write_text(json.dumps(dict(status='pass',all111_pages_indexed=True,pdf_unchanged=True,
        explicit_definition_and_three_variant_text_verified=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
