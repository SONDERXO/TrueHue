"""One detector fallback on the frozen 48 zero-face failures only."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/detector_appearance_inference_v1';BASE=ROOT/'outputs/input_derived_mask_check_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
if not OUT.exists():
    old=read(BASE/'results_PRIVATE.json')['records'];target=[r for r in old if (r['stage']=='source_anchor' and r.get('anchor_face_count')==0) or (r.get('parent_report',{}).get('stage')=='face_detection' and r.get('parent_report',{}).get('face_count')==0)]
    assert len(target)==48 and sum(r['recipe']=='clean' for r in target)==1
    selected={r['case_id'] for r in target};plan=read(BASE/'plan_PRIVATE.json');rows=[r for r in plan['selection'] if r['case_id'] in selected]
    paths=[Path(__file__),ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py',ROOT/'src/skin_masking/detector_appearance_fallback.py',ROOT/'docs/detector-appearance-fallback-protocol-2026-11-06.md',BASE/'results_PRIVATE.json']
    bound=dict(plan['input_sha256']);bound.update({str(p):sha(p) for p in paths})
    OUT.mkdir();(OUT/'logits').mkdir();(OUT/'plan_PRIVATE.json').write_text(json.dumps(dict(selection=rows,input_sha256=bound),indent=2),encoding='utf-8')
source=(ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py').read_text()
source=source.replace('outputs/stellenbosch_new_subjects_v1','outputs/detector_appearance_inference_v1').replace('range(10)','range(16)').replace('range(1,11)','range(1,17)').replace('attempts=30,new_publisher_keys=10','attempts=48,new_publisher_keys=8')
source=source.replace('from src.utilities.config import get_config','from src.utilities.config import get_config\nfrom src.skin_masking.detector_appearance_fallback import detect_with_appearance_fallback')
source=source.replace("    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)","    def detector(im):\n        boxes,trace=detect_with_appearance_fallback(im,lambda a:helper._detect_face_boxes(a,ROOT/cfg.FACE_MODEL_PATH,.85))\n        detector_trace.append(trace);return boxes")
source=source.replace(";cached={}",";cached={};detector_trace=[]")
source=source.replace("        records.append(rec);print(","        rec['detector_trace']=detector_trace\n        records.append(rec);print(")
source=source.replace("+'/30; parser forwards '","+'/48; parser forwards '")
exec(compile(source,str(ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
