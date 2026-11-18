"""Eight fixed CPU forwards, identical tensors, no correction mask changes."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np,onnxruntime as ort
from src.skin_masking.face_parsing_experiment import preprocess,decode
OUT=ROOT/'outputs/parser_backend_parity_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve forwards; do not rerun')
    bound={}
    def bind(p):
        p=Path(p);bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p
    def read(p):return json.loads(bind(p).read_text())
    base=ROOT/'models/face_parser_experimental_v1';model=bind(base/'resnet18.onnx');prov=read(base/'resnet18.provenance.json');assert bound[str(model)]==prov['sha256']
    cases=read(ROOT/'outputs/fragmented_correction_support_trace_v1/trace_PRIVATE.json')['records']
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    for p in (Path(__file__),ROOT/'src/skin_masking/face_parsing_experiment.py',ROOT/'docs/parser-backend-parity-protocol-2026-11-08.md'):bind(p)
    net=cv2.dnn.readNetFromONNX(str(model));net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV);net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    session=ort.InferenceSession(str(model),providers=['CPUExecutionProvider']);assert session.get_providers()==['CPUExecutionProvider']
    assert 'output' in [x.name for x in session.get_outputs()];name=session.get_inputs()[0].name
    OUT.mkdir();rows=[]
    for item in cases:
        cid=item['case_id'];folder=Path(prep[cid]['alpha_path']).parent
        image=cv2.imread(str(bind(folder/'input.png')));cached=cv2.imread(str(bind(folder/'categories.png')),0);tensor=preprocess(image)
        net.setInput(tensor.copy());a=net.forward('output');b=session.run(['output'],{name:tensor.copy()})[0]
        assert a.shape==b.shape==(1,19,512,512) and np.isfinite(a).all() and np.isfinite(b).all()
        dest=OUT/cid;dest.mkdir();np.save(dest/'opencv_logits.npy',a);np.save(dest/'ort_logits.npy',b)
        ca=decode(a,256,256);cb=decode(b,256,256);cv2.imwrite(str(dest/'opencv_categories.png'),ca);cv2.imwrite(str(dest/'ort_categories.png'),cb)
        diff=np.abs(a.astype(float)-b.astype(float))
        row=dict(case_id=cid,max_abs_logit_difference=float(diff.max()),mean_abs_logit_difference=float(diff.mean()),
            disagree_512=int((a.argmax(1)!=b.argmax(1)).sum()),disagree_256=int((ca!=cb).sum()),opencv_vs_cached=int((ca!=cached).sum()),ort_vs_cached=int((cb!=cached).sum()))
        rows.append(row);print(json.dumps(row),flush=True)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in bound.items())
    result=dict(records=rows,opencv_version=cv2.__version__,ort_version=ort.__version__,providers=session.get_providers(),input_sha256=bound,forwards=8,new_fits=0,holdout_image_reads=0)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
