"""Read-only parser contract and cached-coordinate audit; no model forwards."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.face_parsing_experiment import preprocess,decode
OUT=ROOT/'outputs/parser_input_contract_audit_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve existing audit')
    bound={}
    def bind(p):p=Path(p);bound[str(p)]=sha(p);return p
    def read(p):return json.loads(bind(p).read_text(encoding='utf-8'))
    def im(p):
        a=cv2.imread(str(bind(p)),cv2.IMREAD_UNCHANGED);assert a is not None;return a
    for rel in ('scripts/580_audit_parser_input_contract.py','src/skin_masking/face_parsing_experiment.py',
        'src/ita_estimation/semantic_measurement.py','scripts/569_prepare_aligned_pipeline.py',
        'src/skin_masking/fixed_face_input_bridge.py','models/face_parser_experimental_v1/upstream_onnx_inference.py',
        'docs/stellenbosch-parser-appearance-results-2026-11-05.md',
        'docs/resnet34-parser-comparison-results-2026-11-06.md'):bind(ROOT/rel)
    model=ROOT/'models/face_parser_experimental_v1/resnet18.onnx'
    provenance=read(model.parent/'resnet18.provenance.json')
    assert sha(bind(model))==provenance['sha256']
    assert sha(model.parent/'upstream_onnx_inference.py')==provenance['author_source_sha256']['onnx_inference.py']
    prep=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']
    checks=[]
    for r in prep:
        if r['recipe']!='clean' or not r.get('input_bridge'):continue
        folder=Path(r['scene_path']).parent
        if not (folder/'input.png').exists():continue
        scene=im(r['scene_path']);native=im(folder/'native_input.png');image=im(folder/'input.png')
        x0,y0,x1,y1=r['input_bridge']['native_bounds']
        assert np.array_equal(scene[y0:y1,x0:x1],native)
        assert np.array_equal(cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR),image)
        original=image.copy()
        # Independent transcription of archived author's preprocessing; no upstream code execution.
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        rgb=cv2.resize(rgb,(512,512),interpolation=cv2.INTER_LINEAR).astype(np.float32)/255.0
        expected=((rgb-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)).transpose(2,0,1)[None].astype(np.float32)
        assert np.array_equal(expected,preprocess(image)) and np.array_equal(image,original)
        checks.append(dict(case_id=r['case_id'],native_side=x1-x0,category_coordinates_checked=(folder/'categories.png').exists()))
        if (folder/'categories.png').exists():assert im(folder/'categories.png').shape==image.shape[:2]
    # Pure synthetic logits verify the archived argmax-then-nearest output convention.
    logits=np.zeros((1,19,3,5),np.float32)
    for y in range(3):
        for x in range(5):logits[0,(x+5*y)%19,y,x]=1
    expected=cv2.resize(logits.squeeze(0).argmax(0).astype(np.uint8),(17,11),interpolation=cv2.INTER_NEAREST)
    assert np.array_equal(expected,decode(logits,17,11))
    prior=read(ROOT/'outputs/stellenbosch_parser_appearance_v1/preparation_PRIVATE.json')['records']
    pairs=[]
    for r in prep:
        if r['recipe']!='clean':continue
        match=[p for p in prior if p['case_id']==r['source_case']]
        if not match:continue
        p=match[0];old=ROOT/'outputs/stellenbosch_face_crop_v1'/p['case_id']/'input.png'
        current=Path(r['scene_path']).parent/'input.png'
        if old.exists() and current.exists():
            pairs.append(dict(case_id=r['case_id'],same_original256=np.array_equal(im(old),im(current)),
                same_native_bounds=p['input_bridge']['native_bounds']==r['input_bridge']['native_bounds']))
    result=dict(clean_coordinate_and_preprocessing_checks=checks,cached_prior_pairs=pairs,
        synthetic_output_convention_pass=True,model_sha256=provenance['sha256'],
        conclusion='No mismatch found in checked crop/resize, channel order, normalization or output coordinate convention. Raw appearance differs intentionally from earlier CLAHE candidate.',
        limitations=['No fresh logits or OpenCV-versus-ONNXRuntime parity check.',
        'Cached maps do not prove mask accuracy; matching coordinates do not make different appearance inputs equivalent.'],new_fits=0,new_inference=0)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps(dict(clean_checks=len(checks),prior_pairs=len(pairs),same_prior_pixels=sum(p['same_original256'] for p in pairs),same_prior_bounds=sum(p['same_native_bounds'] for p in pairs),bound_hashes=len(bound),conclusion=result['conclusion']),indent=2))

if __name__=='__main__':main()
