"""Reuse independent output verifier/assessment against explicitly redirected assets."""
from pathlib import Path
import runpy,json,hashlib
import cv2
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/distortion_aware_mst_action_comparison_v1'
M=ROOT/'outputs/distortion_aware_mst_action_models_v1/models_PRIVATE.json'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    old=ROOT/'outputs/face_local_action_models_v1/models_PRIVATE.json'
    def redirected(p):return read(M if Path(p)==old else p)
    for filename in ('591_verify_face_local_outputs.py','592_assess_face_local_actions.py'):
        ns=runpy.run_path(str(ROOT/'scripts'/filename));fn=ns['main'];fn.__globals__.update(OUT=OUT,read=redirected);fn()
    assessment=read(OUT/'assessment_PRIVATE.json')
    for item in assessment['diagnostics']:
        p=Path(item['path']);im=cv2.imread(str(p));im[:28]=255
        cv2.putText(im,'OUTCOME SELECTED '+item['case_id']+' ref|input|parent|paired-MST',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
        assert cv2.imwrite(str(p),im)
    html=OUT/'review_PRIVATE.html';html.write_text(html.read_text(encoding='utf-8').replace('face-local','paired-MST'),encoding='utf-8')
    p=OUT/'verification_PRIVATE.json';v=read(p);v.update(wrapper_sha256=sha(Path(__file__)),
        reused_verifier_sha256=sha(ROOT/'scripts/591_verify_face_local_outputs.py'),
        assessment_source_sha256=sha(ROOT/'scripts/592_assess_face_local_actions.py'))
    p.write_text(json.dumps(v,indent=2),encoding='utf-8')

if __name__=='__main__':main()
