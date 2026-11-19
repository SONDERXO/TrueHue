"""Finalize unchanged-production-code evidence after fixing a generated test fixture.

No trained model or guard is run here. Historical sequencing/test records remain
explicit; the successful cached replay is not disguised as an ordered QA pass.
"""
from pathlib import Path
import sys
import base64
from html.parser import HTMLParser

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assess_wb314_exposure_headroom import read,sha,write,data

OUT=ROOT/'outputs/wb314_headroom_advisory_integration_v1'
DELIVERY=ROOT/'output/wb314-headroom-advisory-2026-11-19'


class Images(HTMLParser):
    def __init__(self):super().__init__();self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img':self.images.append(dict(attrs))


def main():
    if (OUT/'finalization_verification.json').exists():raise FileExistsError('Preserve finalization')
    qa=read(ROOT/'outputs/wb314_headroom_advisory_authorization_v1/generated_QA.json');assert qa['passed'] and qa['tests']==7
    wrapper=ROOT/'scripts/wb314_headroom_advisory.py';test=ROOT/'tests/test_wb314_headroom_advisory.py'
    assert sha(wrapper)==qa['wrapper_sha256'] and sha(test)==qa['test_sha256']
    old=read(OUT/'verification.json');assert old['passed'] and sha(wrapper)==old['wrapper_sha256']
    assert sha(ROOT/'scripts/check_wb314_headroom_advisory.py')==old['source_sha256']
    for path,digest in read(OUT/'bindings.json').items():
        actual=OUT/'initial_test_fixture_snapshot.py' if Path(path)==test else Path(path)
        assert sha(actual)==digest
    for path,digest in old['artifacts'].items():assert sha(DELIVERY/path)==digest
    scoped=ROOT/'outputs/wb314_facial_headroom_assessment_v1'
    rows=read(scoped/'controls_sealed.json')['records'];outcomes=read(scoped/'results_PRIVATE.json')
    primary_checks=0;candidate_checks=0
    for r,s in zip(rows,outcomes):
        if r['group']!='normal20':continue
        image,alpha,protected,primary=data(r)
        with np.load(s['output_path'],allow_pickle=False) as z:alternative=z['candidate'].copy()
        x,y,w,h=r['face_box'];path=DELIVERY/'primary-pairs'/(r['key']+'.png')
        baseline=ROOT/'output/wb314-normal-photo-preview-2026-11-19/pairs'/(r['key']+f'_mst{r["MST"]:02d}.png')
        assert path.read_bytes()==baseline.read_bytes();primary_checks+=1
        candidate_path=DELIVERY/'candidate-pairs'/(r['key']+'.png')
        if candidate_path.exists():
            pair=np.concatenate([image[y:y+h,x:x+w],alternative[y:y+h,x:x+w]],axis=1)
            with Image.open(candidate_path) as im:
                assert np.array_equal(np.asarray(im),np.repeat(np.repeat(pair,4,axis=0),4,axis=1))
            candidate_checks+=1
    p=Images();p.feed((DELIVERY/'START_HERE.html').read_text(encoding='utf-8'))
    assert len(p.images)==primary_checks+candidate_checks==22
    files=list((DELIVERY/'primary-pairs').glob('*.png'))+list((DELIVERY/'candidate-pairs').glob('*.png'))
    known={sha(path) for path in files}
    import hashlib,io
    for item in p.images:
        raw=base64.b64decode(item['src'].split(',')[1],validate=True)
        assert hashlib.sha256(raw).hexdigest() in known
        with Image.open(io.BytesIO(raw)) as im:assert im.size==(int(item['width']),int(item['height']))
    summary=read(OUT/'summary.json')
    summary.update(finalized=True,generated_wrapper_tests=7,generated_fixture_and_sequence_issue_recorded=True,
        production_wrapper_unchanged_after_cached_replay=True,primary_preview_PNG_byte_joins=primary_checks,
        candidate_preview_PNG_checks=candidate_checks,embedded_PNG_byte_and_dimension_checks=22,
        trained_model_calls_during_finalization=0,new_fits_during_finalization=0,
        research_advisory_integrated=True,scoped_cap_automatically_adopted=False)
    write(OUT/'final_summary.json',summary)
    write(OUT/'finalization_verification.json',dict(passed=True,corrected_generated_QA_sha256=sha(ROOT/'outputs/wb314_headroom_advisory_authorization_v1/generated_QA.json'),
        old_replay_verification_sha256=sha(OUT/'verification.json'),wrapper_sha256=sha(wrapper),test_sha256=sha(test),
        sequencing_issue_sha256=sha(OUT/'sequencing_issue.json'),summary_sha256=sha(OUT/'final_summary.json'),
        no_replay_or_model_rerun=True))
    print('PASS106prior cached primary/candidate replays retained;20primary PNG byte joins/2candidate pixel checks/22embeds;corrected7-test suite;0newmodelcalls.')


if __name__=='__main__':main()
