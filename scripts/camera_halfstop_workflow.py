"""Separate approved condition assessment. Stages never tune the rejected stress task."""
from pathlib import Path
import sys,json,math,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
from src.distortion_generation.camera_inspired_halfstop import generate,inverse,ROLES,settings
from src.model_training.luminance_chroma_operator import render_rgb8,decode
DATA=ROOT/'outputs/camera_halfstop_data_v1'
NEURAL=ROOT/'outputs/camera_halfstop_neural_v1'
RUN=ROOT/'outputs/camera_halfstop_prediction_v1'
QA=ROOT/'outputs/camera_halfstop_engineering_v1/verification_PRIVATE.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def versions():return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']})
def check_qa():
    qa=read(QA);assert qa['passed'] and qa['actual_generated_indices']==11
    for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in qa['artifact_sha256'].items():assert sha(QA.parent/p)==h,p
    return qa

def prepare():
    import cv2
    from src.model_training.blue_axis_preparation import features281
    from src.evaluation.five_control_feature_scalar import features as scalar_features
    from src.evaluation.directional_recoverability import metrics
    if DATA.exists():raise FileExistsError(DATA)
    qa=check_qa();assert versions()==qa['versions']
    parent_path=ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    parent=read(parent_path);assert read(parent_path.parent/'verification_PRIVATE.json')['plan_sha256']==sha(parent_path)
    sources=parent['feature_sources'];old_identity={r['source_id']:r for r in parent['rows'] if r['role']=='identity'}
    assert len(sources)==len(old_identity)==11
    mapping=read(ROOT/parent['mapper_path']);assert sha(ROOT/parent['mapper_path'])==parent['mapper_sha256']
    declared={str(parent_path.relative_to(ROOT)):sha(parent_path),parent['mapper_path']:parent['mapper_sha256']}
    declared.update(qa['input_sha256']);declared[str(QA.relative_to(ROOT))]=sha(QA)
    for s in sources:
        old=old_identity[s['source_id']]
        for pathkey,hashkey in [('input_pack','input_pack_sha256'),('cached_support_pack','cached_support_sha256')]:declared[old[pathkey]]=old[hashkey]
        for pathkey,hashkey in [('measurement_path','measurement_sha256'),('selected_receipt','selected_receipt_sha256')]:declared[s[pathkey]]=s[hashkey]
    # Entire declared barrier before ANY source array or mask decode.
    for p,h in declared.items():assert sha(ROOT/p)==h,p
    DATA.mkdir();(DATA/'cases').mkdir();write(DATA/'bindings_PRIVATE.json',dict(input_sha256=declared,versions=versions(),all_declared_hashes_before_decode=True))
    source_data={};access=[];rows={};case_meta=[];identity_count=0;max_scalar=0.
    try:
        for s in sources:
            source=s['source_id'];old=old_identity[source]
            with np.load(ROOT/old['input_pack'],allow_pickle=False) as pack:reference=pack['input'].copy()
            with np.load(ROOT/old['cached_support_pack'],allow_pickle=False) as pack:alpha=pack['alpha'].copy();protected=pack['protected'].copy()
            mask=cv2.imread(str(ROOT/s['measurement_path']),0)
            assert reference.shape==(256,256,3) and reference.dtype==np.uint8 and mask is not None
            access.extend([dict(source_id=source,path=old['input_pack'],keys=['input']),dict(source_id=source,path=old['cached_support_pack'],keys=['alpha','protected']),dict(source_id=source,path=s['measurement_path'],keys=['measurement_png'])])
            vector,detail=features281(reference,mask,mapping,parent['feature_names'])
            assert vector==s['identity_saved_feature_vector'],source
            independent=scalar_features(reference,mask,mapping,parent['feature_names'])
            assert all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(vector,independent))
            identity_count+=1;source_data[source]=(reference,alpha,protected,mask)
            rows[(source,'identity')]=(vector,detail)
        assert identity_count==11
        write(DATA/'all_identity281_exact_PRIVATE.json',dict(passed=True,identities=11,nonidentity_features=0))
        # No nonidentity generation/extraction before all11identityfeature parity.
        for s in sources:
            source=s['source_id'];reference,alpha,protected,mask=source_data[source]
            for role in ROLES:
                image,generation=generate(reference,role)
                if role=='identity':
                    assert np.array_equal(image,reference);vector,detail=rows[(source,role)]
                else:
                    vector,detail=features281(image,mask,mapping,parent['feature_names'])
                    independent=scalar_features(image,mask,mapping,parent['feature_names'])
                    max_scalar=max(max_scalar,max(abs(a-b) for a,b in zip(vector,independent)))
                    assert all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(vector,independent))
                assert len(vector)==281 and np.isfinite(vector).all() and np.asarray(vector,np.float32).astype(float).tolist()==vector
                case_id=f'camera_halfstop_ffhq_{source}__{role}';p=DATA/'cases'/(case_id+'.npz')
                np.savez(p,input=image,reference=reference,alpha=alpha,protected=protected)
                y=inverse(role);known=render_rgb8(image,alpha,protected,y)
                ev,r,b=settings(role);raw=decode(reference/255.)*2.**ev*np.array([r,1,b]);primary=alpha>0
                generation.update(primary_clipped_pixel_fraction=float(np.any(raw>1,axis=2)[primary].mean()),
                    primary_new_allblack_pixels=int((np.all(image==0,axis=2)&~np.all(reference==0,axis=2)&primary).sum()))
                row=dict(case_id=case_id,source_id=source,role=role,generated_fixture=False,synthetic_condition=True,
                    parent_training_admitted=False,experimental_role='authorized_camera_inspired_exposed_development',
                    x=vector,y=y,feature_details=detail,input_pack=str(p.relative_to(ROOT)),input_pack_sha256=sha(p))
                rows[(source,role)]=row
                case_meta.append({k:row[k] for k in ['case_id','source_id','role','generated_fixture','synthetic_condition','input_pack','input_pack_sha256']}|
                    dict(generation=generation,known_inverse_supervision=y,known_inverse_metrics=metrics(known,reference,primary),input_metrics=metrics(image,reference,primary)))
            print(f'Camera-inspired data/281features {len(case_meta)}/66',flush=True)
        ordered=[rows[(s['source_id'],role)] for s in sources for role in ROLES]
        ids=[s['source_id'] for s in sources]
        folds=[dict(held_source_id=s,fitting_cases=[r['case_id'] for r in ordered if r['source_id']!=s],evaluation_cases=[r['case_id'] for r in ordered if r['source_id']==s]) for s in ids]
        plan=dict(rows=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','input_pack','input_pack_sha256','y']} for r in ordered],
            folds=folds,feature_names=parent['feature_names']+[f'reiqa_quality_{i:04d}' for i in range(4096)],
            target_names=['gamma','exposure_gain','red_balance','blue_balance','chroma_scale'],generated_fixture=False,
            settings=dict(k=1,blocks=[[0,281],[281,4377]],tie='lexical_case_id',scale='fitting_only_centered_total_block_energy'),
            condition_scope='separate_camera_inspired_halfstop_not_old_Table2_PASS',target_fits=0,maximum_indices=11,model_ready=False)
        write(DATA/'rows281_PRIVATE.json',ordered);write(DATA/'case_metadata_PRIVATE.json',case_meta);write(DATA/'plan_PRIVATE.json',plan)
        for p,h in declared.items():assert sha(ROOT/p)==h,p
        write(DATA/'completion_PRIVATE.json',dict(passed=True,cases=66,identity281_exact=11,scalar_features=18546,max_scalar_feature_difference=max_scalar,
            target_optimizer_calls=0,predictor_fits=0,plan_sha256=sha(DATA/'plan_PRIVATE.json'),rows281_sha256=sha(DATA/'rows281_PRIVATE.json')))
    except Exception as e:
        write(DATA/'failure_PRIVATE.json',dict(error_type=type(e).__name__,error=str(e)));raise
    finally:write(DATA/'array_access_PRIVATE.json',access)

def neural():
    from src.model_training.reiqa_frozen_features import FrozenQualityEncoder,generated_inputs
    if NEURAL.exists():raise FileExistsError(NEURAL)
    check_qa();done=read(DATA/'completion_PRIVATE.json');assert done['passed'] and done['identity281_exact']==11
    assert sha(DATA/'rows281_PRIVATE.json')==done['rows281_sha256'] and sha(DATA/'plan_PRIVATE.json')==done['plan_sha256']
    rows=read(DATA/'rows281_PRIVATE.json')
    for r in rows:assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
    old_report=read(ROOT/'outputs/reiqa_frozen_generated_v1/verification_PRIVATE.json')
    import torch,torchvision,PIL
    assert dict(torch=torch.__version__,torchvision=torchvision.__version__,numpy=np.__version__,pillow=PIL.__version__)==old_report['versions']
    assert platform.python_version()==old_report['python']
    old_prep=ROOT/'outputs/reiqa_development_representation_v1'
    assert sha(old_prep/'features.npz')==read(old_prep/'completion_PRIVATE.json')['feature_sha256']
    NEURAL.mkdir();access=[];vectors={};model=FrozenQualityEncoder(ROOT)
    with np.load(ROOT/'outputs/reiqa_frozen_generated_v1/generated_features.npz',allow_pickle=False) as expected:
        for name,image in generated_inputs():assert np.array_equal(model.encode(image),expected[name].reshape(-1)),name
    with np.load(old_prep/'features.npz',allow_pickle=False) as old:
        for identity_stage in [True,False]:
            for r in rows:
                if (r['role']=='identity')!=identity_stage:continue
                with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:image=pack['input'].copy()
                vector=model.encode(image)
                if identity_stage:
                    assert np.array_equal(vector,old[f"five_prediction_ffhq_{r['source_id']}__identity"])
                    assert np.array_equal(vector,model.encode(image))
                vectors[r['case_id']]=vector;access.append(dict(case_id=r['case_id'],path=r['input_pack'],keys=['input']))
                if len(vectors)%11==0:print(f'Camera-inspired frozen vectors {len(vectors)}/66',flush=True)
            if identity_stage:write(NEURAL/'all_identity4096_exact_PRIVATE.json',dict(passed=True,identities=11,nonidentity_decodes=0))
    model.verify_unchanged()
    np.savez(NEURAL/'features.npz',**{r['case_id']:vectors[r['case_id']] for r in rows})
    write(NEURAL/'array_access_PRIVATE.json',access)
    write(NEURAL/'completion_PRIVATE.json',dict(passed=True,vectors=66,finite_values=270336,identity4096_exact=11,generated_vectors_exact=6,
        encoder_unchanged=True,predictor_fits=0,feature_sha256=sha(NEURAL/'features.npz'),data_plan_sha256=sha(DATA/'plan_PRIVATE.json')))

def predict():
    from src.model_training import camera_halfstop_neighbour as work
    if RUN.exists():raise FileExistsError(RUN)
    qa=check_qa();assert versions()==qa['versions']
    data_done=read(DATA/'completion_PRIVATE.json');neural_done=read(NEURAL/'completion_PRIVATE.json')
    assert data_done['passed'] and neural_done['passed'] and neural_done['identity4096_exact']==11
    assert sha(DATA/'plan_PRIVATE.json')==data_done['plan_sha256']==neural_done['data_plan_sha256']
    assert sha(DATA/'rows281_PRIVATE.json')==data_done['rows281_sha256'] and sha(NEURAL/'features.npz')==neural_done['feature_sha256']
    plan=read(DATA/'plan_PRIVATE.json');rows=read(DATA/'rows281_PRIVATE.json')
    with np.load(NEURAL/'features.npz',allow_pickle=False) as pack:
        for r in rows:r['x']=r['x']+pack[r['case_id']].tolist()
    for r in rows:assert sha(ROOT/r['input_pack'])==r['input_pack_sha256'] and len(r['x'])==4377
    RUN.mkdir();work.write(RUN/'execution_plan.json',plan);work.write(RUN/'prepared_rows.json',rows)
    binding={str(p.relative_to(ROOT)):sha(p) for p in [QA,DATA/'plan_PRIVATE.json',DATA/'rows281_PRIVATE.json',NEURAL/'features.npz',NEURAL/'completion_PRIVATE.json']}
    binding.update(qa['input_sha256']);work.write(RUN/'bindings_PRIVATE.json',binding)
    models=work.fit_all(plan,rows,RUN/'models')
    inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
    work.write(RUN/'inference_inputs.json',inference)
    predictions=work.predict_held(plan,inference,models,RUN/'models')
    # References ONLY decoded after all11indices verified AND all66held controls sealed.
    cases=[];access=[]
    for r in rows:
        with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:a={k:pack[k].copy() for k in ['input','reference','alpha','protected']}
        cases.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(image=a.pop('input'),**a))
        access.append(dict(case_id=r['case_id'],keys=['input','reference','alpha','protected'],stage='after_all_indices_and_66sealed_controls'))
    work.score(plan,cases,predictions,RUN/'evaluation');work.write(RUN/'scoring_access_PRIVATE.json',access)
    for p,h in binding.items():assert sha(ROOT/p)==h
    for r in rows:assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
    work.write(RUN/'completion_PRIVATE.json',dict(index_constructions=11,block_dispersions=22,held_controls=66,renders=132,
        target_optimizer_calls=0,tree_encoder_mapper_baseline_fits=0,model_ready=False,human_review_launched=False))
    print('Separate camera-inspired source-held prediction complete; independent verification pending.',flush=True)

if __name__=='__main__':{'--prepare':prepare,'--neural':neural,'--predict':predict}[sys.argv[1]]()
