"""Fixed ordinary-tree comparison core; no dataset IO or fitting at import."""
from pathlib import Path
import hashlib,json,importlib.util
from collections import defaultdict
import numpy as np
import cv2
from skimage.color import rgb2lab,deltaE_ciede2000
from .gap_training_feasibility import join_inputs,run_once
from .portable_tree import PortableTree
from src.skin_masking.approved_ear_support import extend_support
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.correction.seamless_blend import inward_alpha

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_verifier(root):
    spec=importlib.util.spec_from_file_location('gap_independent',root/'scripts/863_verify_histogram_gap_training_feasibility.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def fit_models(out,plan,parents,records,audited,reuse,verifier,*,fit_run=run_once):
    results=[]
    for index,(fold,parent) in enumerate(zip(plan['folds'],parents)):
        assert parent['definition']==fold
        fit_records={c:records[c] for c in fold['fitting_cases']}
        local=dict(fitting_records=[dict(case_id=c,source=fit_records[c]['publisher_group'],role=fit_records[c]['experimental_role']) for c in fold['fitting_cases']],
            feature_names=plan['feature_names'],new_feature_names=plan['feature_names'][16:],excluded_group=fold['held_publisher_group'])
        snapshot=join_inputs(local,fit_records,audited)
        folder=out/fold['held_publisher_group']
        if index==0:
            assert fold['held_publisher_group']==plan['reuse']['fold'] and sha(reuse/'candidate_PRIVATE.json')==plan['reuse']['sha256']
            assert read(reuse/'fitting_inputs_PRIVATE.json')==snapshot
            folder.mkdir()
            for name in ['candidate_PRIVATE.json','baseline_SAVED_PRIVATE.json','fitting_inputs_PRIVATE.json','training_replay_PRIVATE.json']:
                (folder/name).write_bytes((reuse/name).read_bytes())
            assert read(folder/'baseline_SAVED_PRIVATE.json')==parent['tree']
            write(folder/'reuse_PRIVATE.json',dict(exact=True,source=str(reuse),candidate_sha256=sha(folder/'candidate_PRIVATE.json')))
        else:fit_run(folder,snapshot,plan['feature_names'],parent['tree'],dict(fold=fold,comparison_protocol=plan['protocol_id']))
        candidate=read(folder/'candidate_PRIVATE.json');replay=read(folder/'training_replay_PRIVATE.json')
        checked=verifier.verify(candidate,parent['tree'],snapshot,replay,plan['feature_names'])
        write(folder/'fitting_verification_PRIVATE.json',checked)
        results.append(dict(definition=fold,tree=candidate,reused=index==0,candidate_sha256=sha(folder/'candidate_PRIVATE.json')))
        write(out/'models_PRIVATE.json',results)
    assert len(results)==len(plan['folds'])==len(parents)
    write(out/'all_fits_verified_PRIVATE.json',dict(passed=True,models=len(results)))
    return results

def prepare_support(root,out,item):
    source=Path(item['annotation']);manifest=read(source/'manifest.json')
    assert sha(source/'manifest.json')==item['manifest_sha256']
    for name,entry in item['declared_files'].items():
        assert manifest['files'][name]==entry and sha(source/name)==entry['sha256']
    category_path=root/item['categories_path'];assert sha(category_path)==item['categories_sha256']
    load=lambda name:cv2.imread(str(source/name),cv2.IMREAD_GRAYSCALE)
    c=load('correction_mask.png');m=load('measurement_mask.png');p=load('protected_mask.png')>0
    automatic=load('automatic_correction_mask.png');cat=cv2.imread(str(category_path),cv2.IMREAD_GRAYSCALE)
    assert c.shape==m.shape==p.shape==automatic.shape==cat.shape==(256,256)
    oldalpha=np.load(source/'correction_alpha.npy',allow_pickle=False)
    original_replay,_=inward_alpha(c,face_width=item['face_width'],protected=p)
    assert np.array_equal(original_replay,oldalpha)
    revised=extend_support(FaceNeckSupport(m,np.zeros_like(m),c,{}),cat,protected=p,manual_removed=(automatic>0)&(c==0))
    alpha,blend=inward_alpha(revised.correction_mask,face_width=item['face_width'],protected=p)
    if item['already_approved_exact_preview']:
        approved=root/'outputs/approved_ear_support_integration_v1'/item['source_id'];receipt=read(approved/'manifest_PRIVATE.json')
        for name,digest in receipt['files'].items():assert sha(approved/name)==digest
        assert np.array_equal(revised.correction_mask,cv2.imread(str(approved/'correction_mask.png'),0))
        assert np.array_equal(alpha,np.load(approved/'correction_alpha.npy',allow_pickle=False))
    folder=out/'supports'/item['source_id'];folder.mkdir(parents=True)
    assert cv2.imwrite(str(folder/'correction_mask.png'),revised.correction_mask)
    for name in ['measurement_mask.png','protected_mask.png']:(folder/name).write_bytes((source/name).read_bytes())
    np.save(folder/'alpha.npy',alpha,allow_pickle=False)
    record=dict(source=item['source'],source_annotation=str(source),face_width=item['face_width'],ear_report=revised.report['ear_coverage'],blend=blend,
        measurement_unchanged=True,protection_unchanged=True,files={p.name:sha(p) for p in folder.iterdir()})
    write(folder/'manifest_PRIVATE.json',record)
    return dict(alpha=alpha,mask=alpha>0,protected=p,record=record)

def render(image,alpha,controls):
    u=image.astype(np.float64)/255.
    target=np.clip(u**controls[0]*[controls[1],1.,controls[2]],0,1)
    return np.rint(255*(u*(1-alpha[:,:,None])+target*alpha[:,:,None])).astype(np.uint8)

def metrics(image,reference,mask):
    assert mask.dtype==bool and mask.any() and mask.shape==image.shape[:2]
    return dict(RGB=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),
        DE=float(deltaE_ciede2000(rgb2lab(image[mask]/255.),rgb2lab(reference[mask]/255.)).mean()))

def score_context(image,reference,alpha,mask,protected,controls):
    output=render(image,alpha,controls)
    assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
    return output,dict(input=metrics(image,reference,mask),output=metrics(output,reference,mask),
        changed_pixels=int(np.any(output!=image,axis=2).sum()),scoring_pixels=int(mask.sum()),
        protected_unchanged=True,zero_alpha_unchanged=True)

def aggregate(predictions,context):
    result={}
    for role in sorted({p['role'] for p in predictions}):
        own=[p for p in predictions if p['role']==role];groups=defaultdict(list)
        for p in own:groups[p['source']].append(p[context]['input']['DE']-p[context]['output']['DE'])
        d=[p[context]['input']['DE']-p[context]['output']['DE'] for p in own]
        result[role]=dict(cases=len(own),sources=len(groups),
            source_equal_DE_improvement=sum(sum(g)/len(g) for g in groups.values())/len(groups),
            DE_benefits=sum(v>1e-10 for v in d),DE_harms=sum(v < -1e-10 for v in d),numerical_equal=sum(abs(v)<=1e-10 for v in d),
            worst_DE_improvement=min(d),input_RGB=sum(p[context]['input']['RGB'] for p in own)/len(own),
            output_RGB=sum(p[context]['output']['RGB'] for p in own)/len(own))
    return result
