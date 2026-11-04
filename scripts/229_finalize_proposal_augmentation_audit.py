"""Verify PDF example placement and compare the current formula without adoption."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'outputs/pdf_augmentation_audit_runtime_v1')]
import cv2
import numpy as np
from pypdf import PdfReader
from pypdf.generic import ContentStream
from src.distortion_generation.table2_composite import composite_rgb,SETTINGS


def main():
    out=ROOT/'outputs/proposal_augmentation_audit_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    original=json.loads((out/'comparison.json').read_text(encoding='utf-8'))
    pdf=Path('C:/Users/NYTHAN/Downloads/Thesis Proposal Document.pdf')
    assert digest(pdf)==original['pdf_sha256']
    reader=PdfReader(pdf);page=reader.pages[63]
    operations=ContentStream(page['/Contents'],reader).operations
    draws=[]
    for index,(args,op) in enumerate(operations):
        if op!=b'Do':continue
        previous=[a for a,b in operations[:index] if b==b'cm'][-1]
        draws.append(dict(name=str(args[0]),x=float(previous[4]),y=float(previous[5])))
    expected=['/X139','/X140','/X139','/X141','/X142','/X141','/X143','/X144','/X143']
    assert [r['name'] for r in draws]==expected
    for index in range(0,9,3):
        row=draws[index:index+3];assert row[0]['x']<row[1]['x']<row[2]['x']
        assert len({r['y'] for r in row})==1
    records=[]
    def save(p,image):
        if not cv2.imwrite(str(p),image):raise OSError(p)
    def panel(rgb,label):
        bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        bgr=cv2.copyMakeBorder(bgr,28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(bgr,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
        return bgr
    for prior in original['records']:
        group=prior['group'];ref=out/'images'/f'{group}_reference.jpg';biased=out/'images'/f'{group}_paper_bias.png'
        x=cv2.cvtColor(cv2.imread(str(ref)),cv2.COLOR_BGR2RGB)
        y=cv2.cvtColor(cv2.imread(str(biased)),cv2.COLOR_BGR2RGB)
        current,clipping=composite_rgb(x,group)
        mae=float(np.abs(current.astype(float)-y).mean())
        # JPEG decoder differences are possible; require agreement within .05 DN.
        assert abs(mae-prior['current_error']['rgb_mae'])<.05
        save(out/'images'/f'{group}_current_formula.png',cv2.cvtColor(current,cv2.COLOR_RGB2BGR))
        save(out/f'{group}_comparison.png',np.hstack([panel(x,'Paper reference'),panel(y,'Paper simulated input'),panel(current,'Current formula diagnostic')]))
        records.append(dict(group=group,current_formula_rgb_mae_0_255=mae,
            paper_zero_channel_fraction=float((y==0).mean()),current_zero_channel_fraction=float((current==0).mean()),
            formula_clipping=clipping,reference_sha256=digest(ref),paper_bias_sha256=digest(biased)))
    report=dict(status='augmentation_specification_unresolved',pdf_sha256=digest(pdf),pdf_page=64,
        table3_placement_and_reused_target_images_verified=True,pdf_visually_rendered_and_inspected=True,
        current_formula='x**(1/gamma), contrast around0.5, brightness/255, additive red/blue offsets/255, final clipping',
        missing_paper_details=['gamma equation/convention','operation order','brightness/contrast units and transfer functions','channel adjustment semantics','clipping stages','global versus facial compositing'],
        comparison_scope='Native224 PDF examples; full-image pointwise formula diagnostic, not deployed masked256 pipeline or skin-truth evaluation',
        records=records,replacement_formula_established=False,training_images_changed=0,models_fitted=0,
        limitation='Embedded JPEG references, PNG bias assets and illustrative examples cannot determine an exact augmentation equation alone.')
    (out/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (out/'pdf_image_placement.json').write_text(json.dumps(draws,indent=2),encoding='utf-8')
    sections=''.join(f'<section><h2>{r["group"]}</h2><p>Formula versus paper input RGB MAE: {r["current_formula_rgb_mae_0_255"]:.2f}/255. This is reproduction error, not correction-model performance.</p><img src="{r["group"]}_comparison.png"></section>' for r in records)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Proposal augmentation specification audit</title><style>body{font:17px system-ui;background:#171923;color:#eee;max-width:1100px;margin:28px auto;padding:16px}img{max-width:100%}section{border-top:1px solid #777;margin:24px 0}a{color:#9cf}</style><h1>Paper examples versus the current distortion formula</h1><p>Source formula unresolved. No alternative has been approved or activated. Native224 full-image formula comparison; not a masked256 training-pipeline reproduction.</p><p><a href="table3_page64.png">Rendered proposal Table3, PDFpage64</a></p>'+sections,encoding='utf-8')
    assert digest(pdf)==original['pdf_sha256']
    target.write_text(json.dumps(dict(status='pass',pdf_unchanged=True,table3_image_order_and_reused_targets_verified=True,
        current_formula_reproduced=True,scientific_formula_validation='unresolved',
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],rows_verified=3,replacement_formula_established=False),indent=2))


if __name__=='__main__':main()
