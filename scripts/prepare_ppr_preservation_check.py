"""One new identity-change gate, saved pixels only; no inference/rating transfer."""
from pathlib import Path
import sys, html, hashlib
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from wb_feature_direct_workflow import read,write,sha


def main():
    run=ROOT/'outputs/ppr_parameter_correction_prediction_v1'
    out=ROOT/'outputs/ppr_parameter_preservation_check_v1'
    if out.exists():raise FileExistsError(out)
    audit=read(run/'independent_audit.json');assert audit['passed'] and audit['numerical_eligible']
    records=read(run/'records.json');proof=read(run/'verification.json')
    parent=ROOT/'outputs/wb_feature_direct_prediction_v1'
    old={r['case_id']:r for r in read(parent/'held_controls_sealed.json')}
    candidates=sorted([r for r in records if r['role']=='identity' and r['changed_pixels']>0 and
                       r['controls']!=old[r['case_id']]['controls314']],key=lambda r:r['case_id'])
    assert len(candidates)==1;r=candidates[0]
    path=run/'evaluation'/(r['case_id']+'.npz')
    assert sha(path)==proof['artifact_sha256'][path.relative_to(run).as_posix()]
    with np.load(path,allow_pickle=False) as p:arrays={k:p[k].copy() for k in ['input','reference','joint']}
    assert np.array_equal(arrays['input'],arrays['reference'])
    out.mkdir();pixels={}
    for label,key in [('input','input'),('candidate','joint')]:
        Image.fromarray(arrays[key]).save(out/(label+'.png'))
        assert np.array_equal(np.asarray(Image.open(out/(label+'.png'))),arrays[key])
        pixels[label]=dict(file_sha256=sha(out/(label+'.png')),rgb_sha256=hashlib.sha256(arrays[key].tobytes()).hexdigest())
    board=Image.new('RGB',(536,302),'white');draw=ImageDraw.Draw(board)
    draw.text((8,8),'Input / acceptable original',fill='black');draw.text((276,8),'PPR319 candidate',fill='black')
    board.paste(Image.fromarray(arrays['input']),(8,34));board.paste(Image.fromarray(arrays['joint']),(276,34))
    board.save(out/'comparison.png')
    page='''<!doctype html><meta charset="utf-8"><title>TrueHue: one preservation check</title>
<style>body{font:18px system-ui;max-width:800px;margin:28px auto;padding:0 16px;background:#f5f5f5;color:#111}.pair{display:flex;gap:24px;flex-wrap:wrap}figure{margin:0}img{width:256px;height:256px}figcaption{margin:8px 0}p{line-height:1.5}</style>
<h1>One preservation check</h1><p>This input is already the reference photograph. It needs no synthetic exposure or colour repair. The new candidate brightens it. Judge whether that change is acceptable, unwanted, or uncertain. Reply in our conversation; there is no save file.</p>
<div class="pair"><figure><figcaption>Input / acceptable original</figcaption><img src="input.png" alt="Original input"></figure><figure><figcaption>PPR319 candidate</figcaption><img src="candidate.png" alt="New candidate"></figure></div>
<p>This is a check of preservation, not expert MOS or final model adoption. If the change is unwanted or uncertain, stop this candidate's review. Earlier ratings stay preserved and have not been assigned to this candidate.</p>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    write(out/'manifest.json',dict(case_id=r['case_id'],source_id=r['source_id'],role='identity',
          selection='only newly changed identity controls relative toWB314, before pixel inspection',
          source_pack_sha256=sha(path),source_audit_sha256=sha(run/'independent_audit.json'),
          controls=r['controls'],pixels=pixels,ratings_collected=0,old_ratings_transferred=False,
          native_png_roundtrip_passed=True,interactive_browser_qa=False,
          page_sha256=sha(out/'index.html'),comparison_sha256=sha(out/'comparison.png')))
    print('One new preservation-risk pair ready; zero inference/renders/ratings.')


if __name__=='__main__':main()
