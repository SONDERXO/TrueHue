"""Verify prediction-hidden package and synthetic UI, without actual answers."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_reference_points_v1'
OUT=ROOT/'outputs/stellenbosch_reference_points_verification_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Data(HTMLParser):
    def __init__(self):super().__init__();self.active=False;self.parts=[]
    def handle_starttag(self,tag,attrs):self.active=tag=='script' and dict(attrs).get('id')=='data'
    def handle_endtag(self,tag):
        if tag=='script':self.active=False
    def handle_data(self,text):
        if self.active:self.parts.append(text)

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json');manifest=read(PARENT/'manifest.json')
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    parser=Data();parser.feed((PARENT/'review.html').read_text(encoding='utf-8'));data=json.loads(''.join(parser.parts))
    assert set(data)=={'manifest_sha256','rows'} and data['manifest_sha256']==sha(PARENT/'manifest.json')
    assert data['rows']==manifest['rows'] and len(data['rows'])==6
    bindings=read(PARENT/'prediction_bindings_PRIVATE.json')
    for row in data['rows']:
        assert set(row)=={'review_id','width','height','image_path','context_path','image_sha256'}
        assert sha(PARENT/row['image_path'])==row['image_sha256']
        binding=bindings[row['review_id']]
        assert sha(PARENT/row['context_path'])==binding['source_sha256']==sha(binding['source_path'])
        assert sha(binding['native_crop_path'])==row['image_sha256']
    assert sum(r['native_grid_path'] is None for r in bindings.values())==1
    assert not (ROOT/'outputs/stellenbosch_reference_points_import_v1').exists()
    run=subprocess.run(['node',str(ROOT/'scripts/461_verify_native_reference_ui.cjs')],cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'No actual responses written' in run.stdout
    assert all(sha(p)==h for p,h in bound.items())
    report=dict(fixed_cases=6,predictions_and_scores_absent_from_ui_payload=True,
        original_image_source_hash_parities=6,unavailable_prediction_cases=1,
        synthetic_UI_harness_passed=True,actual_browser_render_checked=False,actual_reviewer_exports_created=0,
        actual_review_pending=True,new_forwards=0,new_fits=0,admissions=0,
        package_manifest_sha256=sha(PARENT/'manifest.json'),script_sha256=sha(__file__),
        UI_harness_script_sha256=sha(ROOT/'scripts/461_verify_native_reference_ui.cjs'))
    OUT.mkdir();(OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'synthetic_ui.txt').write_text(run.stdout,encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
