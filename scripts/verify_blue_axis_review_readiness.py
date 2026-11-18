"""Independent reuse/image checks and read-only HTTP readiness; no new ratings."""
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
import json,sys,threading,subprocess,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blue_axis_preparation import read,write,sha
from src.demo.blue_axis_review import handler,page

def main():
    out=ROOT/'outputs/blue_axis_review_v1';dest=out/'readiness_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve readiness')
    current=ROOT/'outputs/blue_axis_source_held_comparison_v1';old=ROOT/'outputs/joint_colour_source_held_comparison_v1'
    auditfolder=ROOT/'outputs/blue_axis_review_reuse_audit_v1';audit=read(auditfolder/'audit_PRIVATE.json');receipt=read(out/'preparation_PRIVATE.json')
    oldp={p['case_id']:p for p in read(old/'predictions_PRIVATE.json')};newp=read(current/'predictions_PRIVATE.json')
    freeze=read(ROOT/'outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json');priorpath=ROOT/'outputs/joint_colour_acceptability_review_v2/ratings'/freeze['review_revision'];assert sha(priorpath)==freeze['review_sha256'];prior=read(priorpath)
    supportids={s['source']:s['source_id'] for s in read(ROOT/'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json')['support_sources']}
    def rgb(folder,p,key):
        panel=p['output_panel'] if key=='output' else ('B' if p['output_panel']=='A' else 'A') if key=='input' else 'R'
        return cv2.imread(str(folder/'review_assets'/f'{p["review_id"]}_{panel}.png'))
    eligible=[]
    for p in newp:
        if p['case_id'] not in oldp:continue
        previous=oldp[p['case_id']];assert previous['role']==p['role'] and previous['source']==p['source']
        images=all(np.array_equal(rgb(current,p,k),rgb(old,previous,k)) for k in ['input','output','reference'])
        support=all((current/'supports'/supportids[p['source']]/n).read_bytes()==(old/'supports'/supportids[p['source']]/n).read_bytes() for n in ['correction_mask.png','measurement_mask.png','protected_mask.png','alpha.npy'])
        if images and support:eligible.append(p['review_id'])
    assert set(eligible)==set(audit['eligible_ids']) and len(eligible)==22
    assert audit['user_viewing_setup_confirmation']=='Yes, the same viewing setup'
    assert prior['display']==audit['prior_display']
    seed=read(out/'carry_forward_seed_PRIVATE.json');assert set(seed['ratings'])==set(eligible)
    assert len(list((out/'ratings').glob('*.json')))==1 and read(out/'ratings'/receipt['seed_revision'])['ratings']==seed['ratings']
    byid={p['review_id']:p for p in newp}
    for ident,rating in seed['ratings'].items():
        p=byid[ident];previous=oldp[p['case_id']];expected=prior['ratings'][previous['review_id']].copy()
        if p['output_panel']!=previous['output_panel']:
            for k in ['preference','artifact']:
                if expected.get(k) in ['A','B']:expected[k]='B' if expected[k]=='A' else 'A'
        assert rating==expected
    public=read(out/'review_public.json');assert len(public['cases'])==66 and all(c['kind']=='identity' for c in public['cases'][:11])
    assert set(public['carried_ids'])==set(eligible) and len([c for c in public['cases'] if c['id'] not in eligible])==44
    assert sha(out/'review_public.json')==receipt['public_sha256']
    for rel,h in receipt['assets_sha256'].items():assert sha(out/rel)==h
    qa=ROOT/'outputs/blue_axis_review_readiness_v1';qa.mkdir()
    scripts=re.findall(r'<script[^>]*>(.*?)</script>',page(public).decode(),re.S)
    js=qa/'generated_page.js';js.write_text('\n'.join(scripts),encoding='utf-8')
    result=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
    (qa/'javascript_syntax.txt').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(out));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    try:
        assert b'carried_ids' in urlopen(base+'/').read()
        assert json.loads(urlopen(base+'/public').read())==public
        assert json.loads(urlopen(base+'/latest').read())['ratings']==seed['ratings']
        assert not json.loads(urlopen(base+'/review-status').read())['closed']
        for rel,h in receipt['assets_sha256'].items():
            import hashlib
            assert hashlib.sha256(urlopen(base+'/'+rel).read()).hexdigest()==h
        for rel in ['summary_PRIVATE.json','predictions_PRIVATE.json','carry_forward_seed_PRIVATE.json','provenance_PRIVATE.json','../AGENTS.md']:
            try:urlopen(base+'/'+rel)
            except HTTPError as e:assert e.code==404
            else:raise AssertionError('Private path served')
    finally:server.shutdown();server.server_close();thread.join()
    assert len(list((out/'ratings').glob('*.json')))==1
    files=['src/demo/blue_axis_review.py','src/demo/blue_axis_review_policy.py','src/demo/acceptability_review.py','src/demo/oblique_comparison_review.html','src/demo/joint_colour_review_status.js','scripts/audit_blue_axis_review_reuse.py','scripts/prepare_blue_axis_review.py','scripts/review_blue_axis.py','scripts/verify_blue_axis_review_readiness.py','tests/test_blue_axis_review.py','review_blue_axis.cmd']
    report=dict(passed=True,independent_exact_reuse_passed=True,carried_forward=22,fresh=44,total=66,identity_first=11,served_assets=len(receipt['assets_sha256']),read_only_HTTP_passed=True,private_paths_denied=True,javascript_syntax_passed=True,generated_tests_passed=4,live_browser_visual_QA_claimed=False,new_agent_ratings=0,scores_unblinded=False,new_fits=0,new_predictions=0,code_sha256={n:sha(ROOT/n) for n in files},preparation_sha256=sha(out/'preparation_PRIVATE.json'),seed_sha256=sha(out/'carry_forward_seed_PRIVATE.json'),reuse_audit_sha256=sha(auditfolder/'audit_PRIVATE.json'))
    write(dest,report);write(qa/'verification_PRIVATE.json',report)
    print(f'Readiness PASS:22exact carried/44fresh/66total/{len(receipt["assets_sha256"])}assets; private paths denied; no new ratings')
if __name__=='__main__':main()
