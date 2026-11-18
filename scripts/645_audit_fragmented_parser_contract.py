"""Four distorted saved inputs plus archived author contract; no network forwards."""
from pathlib import Path
import ast,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.face_parsing_experiment import preprocess,decode,LABELS
OUT=ROOT/'outputs/fragmented_parser_contract_audit_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve audit')
    bound={}
    def bind(p):
        p=Path(p);bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p
    def read(p):return json.loads(bind(p).read_text())
    def im(p):return cv2.imread(str(bind(p)))
    base=ROOT/'models/face_parser_experimental_v1';prov=read(base/'resnet18.provenance.json');model=bind(base/'resnet18.onnx')
    assert bound[str(model)]==prov['sha256']
    for name,h in prov['author_source_sha256'].items():assert hashlib.sha256(bind(base/('upstream_'+name.replace('/','_'))).read_bytes()).hexdigest()==h
    common=ast.parse((base/'upstream_utils_common.py').read_text())
    attrs=next(ast.literal_eval(n.value) for n in common.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ATTRIBUTES' for t in n.targets))
    expected=['skin','l_brow','r_brow','l_eye','r_eye','eye_g','l_ear','r_ear','ear_r','nose','mouth','u_lip','l_lip','neck','neck_l','cloth','hair','hat']
    assert attrs==expected and len(LABELS)==19
    # Archived list names 18 foreground classes; local schema explicitly adds background.
    text=(base/'upstream_utils_common.py').read_text();assert 'ATTRIBUTES' in text
    net=cv2.dnn.readNetFromONNX(str(model));outputs=list(net.getUnconnectedOutLayersNames());assert 'output' in outputs
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    ids=[r['case_id'] for r in read(ROOT/'outputs/fragmented_correction_support_trace_v1/trace_PRIVATE.json')['records']];checks=[]
    for cid in ids:
        r=prep[cid];folder=Path(r['alpha_path']).parent;scene=im(r['scene_path']);native=im(folder/'native_input.png');image=im(folder/'input.png');l,t,rr,b=r['input_bridge']['native_bounds']
        assert np.array_equal(native,scene[t:b,l:rr]) and np.array_equal(image,cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR))
        rgb=cv2.resize(image[:,:,::-1],(512,512),interpolation=cv2.INTER_LINEAR).astype(np.float32)/np.float32(255)
        expected=((rgb-np.asarray([.485,.456,.406],np.float32))/np.asarray([.229,.224,.225],np.float32)).transpose(2,0,1)[None]
        assert np.array_equal(expected,preprocess(image))
        cats=cv2.imread(str(bind(folder/'categories.png')),0);assert cats.shape==(256,256) and cats.max()<19
        checks.append(dict(case_id=cid,crop_resize_exact=True,author_preprocess_exact=True,category_shape_valid=True))
    logits=np.zeros((1,19,19,19),np.float32)
    for c in range(19):logits[0,c,c,:]=1
    assert np.array_equal(decode(logits,19,19),np.tile(np.arange(19,dtype=np.uint8)[:,None],(1,19)))
    for p in (Path(__file__),ROOT/'src/skin_masking/face_parsing_experiment.py',ROOT/'src/ita_estimation/semantic_measurement.py'):bind(p)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in bound.items())
    result=dict(checks=checks,model_sha256=prov['sha256'],archived_revision=prov['source_revision'],outputs=outputs,
        local_labels=list(LABELS),archived_foreground_labels=attrs,all19_synthetic_decode_pass=True,input_sha256=bound,
        limitations=['No fresh logits, backend numerical parity or architecture graph inspection; ONNX Python package not installed.',
        'Saved category bytes cannot be independently regenerated without inference. Framing suitability and prediction accuracy not established.'],new_fits=0,new_inference=0,holdout_image_reads=0)
    OUT.mkdir();(OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(checked_inputs=4,model_hash_pass=True,archived_sources_pass=True,outputs=outputs,decode_classes=19,new_inference=0)))
if __name__=='__main__':main()
