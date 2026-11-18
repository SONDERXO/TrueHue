"""Fixed comparison helpers; no IO or fits at import. Saved supports only."""
from pathlib import Path
import hashlib,json,shutil
import cv2,numpy as np
from .gap_training_feasibility import f32
from .joint_colour_training import join,run_once
from .joint_colour_verification import verify
from .gap_source_held_workflow import score_context,aggregate
from src.correction.seamless_blend import inward_alpha

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def fitting_rows(plan,fold,records,gaps,audited):
    base=[];roster=[]
    for c in fold['fitting_cases']:
        r=records[c];g=gaps[c]
        if r['generated_fixture'] is not False or r['status']!='available' or g['generated_fixture'] is not False:raise ValueError('Real available fitting records required')
        if g['source']!=r['publisher_group'] or g['role']!=r['experimental_role']:raise ValueError('Gap provenance mismatch')
        base.append(dict(case_id=c,source=r['publisher_group'],role=r['experimental_role'],
            x=r['input_vector_float32']+[f32(g['features'][n]) for n in plan['feature_names'][16:22]],y=r['nominal_controls']))
        roster.append(dict(case_id=c,source=r['publisher_group'],role=r['experimental_role']))
    return join(dict(feature_names=plan['feature_names'],fitting_records=roster,excluded_group=fold['held_publisher_group']),base,audited)

def fit_all(out,plan,parents,records,gaps,audited,reuse,*,fit=run_once):
    if len(parents)!=len(plan['folds']):raise ValueError('Exact parent fold count required')
    models=[]
    for i,(fold,parent) in enumerate(zip(plan['folds'],parents)):
        assert parent['definition']==fold
        rows=fitting_rows(plan,fold,records,gaps,audited);folder=Path(out)/fold['held_publisher_group']
        if i==0:
            assert fold['held_publisher_group']==plan['reuse']['fold'] and sha(reuse/'candidate_PRIVATE.json')==plan['reuse']['sha256']
            assert read(reuse/'fitting_inputs_PRIVATE.json')==rows and read(reuse/'baseline_SAVED_PRIVATE.json')==parent['tree']
            folder.mkdir()
            for n in ['candidate_PRIVATE.json','fitting_inputs_PRIVATE.json','baseline_SAVED_PRIVATE.json','training_replay_PRIVATE.json']:
                shutil.copyfile(reuse/n,folder/n)
        else:fit(folder,rows,plan['feature_names'],parent['tree'],dict(protocol_id=plan['protocol_id'],fold=fold))
        candidate=read(folder/'candidate_PRIVATE.json');replay=read(folder/'training_replay_PRIVATE.json')
        checked=verify(candidate,parent['tree'],rows,replay,plan['feature_names'])
        write(folder/'fitting_verification_PRIVATE.json',checked)
        models.append(dict(definition=fold,directory=folder.name,reused=i==0,candidate_sha256=sha(folder/'candidate_PRIVATE.json')))
        write(Path(out)/'models_PRIVATE.json',models)
    assert len(models)==len(plan['folds'])
    write(Path(out)/'all_fits_verified_PRIVATE.json',dict(passed=True,folds=len(models),new_fits=len(models)-1,reused_fits=1))
    return models

def seal_support(root,out,item):
    root=Path(root);selected=item['selected'];src=root/selected['directory'];old=root/item['old_support_directory']
    assert sha(src/selected['receipt'])==selected['receipt_sha256']
    for n,h in selected['files'].items():assert sha(src/n)==h
    for n,h in item['old_files'].items():assert sha(old/n)==h
    gray=lambda p:cv2.imread(str(p),cv2.IMREAD_GRAYSCALE)
    c=gray(src/'correction_mask.png');m=gray(src/'measurement_mask.png');p=gray(src/'protected_mask.png')>0
    oldp=gray(old/'protected_mask.png')>0
    assert c is not None and m is not None and c.shape==m.shape==p.shape==oldp.shape
    assert set(np.unique(c))<={0,255} and set(np.unique(m))<={0,255}
    assert (src/'measurement_mask.png').read_bytes()==(old/'measurement_mask.png').read_bytes()
    assert not np.any(oldp&~p)
    if item['protection_rule']=='exact_old':assert np.array_equal(oldp,p)
    else:assert item['protection_rule']=='old_subset_new'
    assert not c[p].any()
    alpha=np.load(src/selected['alpha_filename'],allow_pickle=False)
    rebuilt,_=inward_alpha(c,face_width=item['face_width'],protected=p);assert np.array_equal(alpha,rebuilt)
    # Preserve original explicit correction removals for either selected support.
    oldreceipt=read(old/'manifest_PRIVATE.json');annotation=Path(oldreceipt['source_annotation'])
    original_manifest=read(annotation/'manifest.json')
    for n in ['automatic_correction_mask.png','correction_mask.png']:assert sha(annotation/n)==original_manifest['files'][n]['sha256']
    reviewed=gray(annotation/'correction_mask.png');automatic=gray(annotation/'automatic_correction_mask.png')
    removed=(automatic>0)&(reviewed==0);assert not c[removed].any()
    dest=Path(out)/'supports'/item['source_id'];dest.mkdir(parents=True)
    for n in ['correction_mask.png','measurement_mask.png','protected_mask.png']:shutil.copyfile(src/n,dest/n)
    shutil.copyfile(src/selected['alpha_filename'],dest/'alpha.npy')
    receipt=dict(source=item['source'],selected_directory=selected['directory'],selected_receipt_sha256=selected['receipt_sha256'],
        new_manual_revision=selected['manual_assisted'],measurement_unchanged=True,manual_removals_preserved=True,
        old_protection_retained=True,files={p.name:sha(p) for p in dest.iterdir() if p.is_file()})
    write(dest/'manifest_PRIVATE.json',receipt)
    return dict(alpha=alpha,mask=alpha>0,protected=p,old_protected=oldp,receipt=receipt)

def after_fit_barrier(out,plan,models,load_supports,score):
    barrier=read(Path(out)/'all_fits_verified_PRIVATE.json')
    assert barrier['passed'] and barrier['folds']==len(plan['folds'])==len(models)
    supports=load_supports()
    write(Path(out)/'all_supports_sealed_PRIVATE.json',dict(passed=True,supports=[s['receipt'] for s in supports.values()]))
    return score(supports)
