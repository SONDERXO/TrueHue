"""Artificial66 pipeline and prospective review safeguards; temporary IO only."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys,json,hashlib,shutil
import cv2,numpy as np,pytest
from src.model_training.blue_axis_workflow import numerical_gate,fit_all,fitting_rows,load_case,after_fit_barrier
from src.model_training.blue_axis_training import fit_once
from src.model_training.blue_axis_preparation import read,write,sha
from src.demo.blue_axis_review_policy import carry_forward,assess,EVIDENCE

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location('generated_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
BASE=module('test_blue_axis_feasibility');OLD=module('test_joint_colour_workflow')

def predictions():
    return [dict(case_id=f'GENERATED_{s}_{r}',source=f'GENERATED_{s}',role=r,primary=dict(input=dict(DE=2.,RGB=2.),output=dict(DE=1.,RGB=1.),protected_unchanged=True,zero_alpha_unchanged=True)) for s in range(11) for r in BASE.ROLES]

@pytest.mark.parametrize('family',BASE.ROLES[1:])
def test_each_family_failure_blocks_review(family):
    p=predictions()
    for r in p:
        if r['role']==family:r['primary']['output']['DE']=3.
    assert not numerical_gate(p)[1]

def test_numerical_integrity_equal_missing_and_identity_tolerance():
    p=predictions();assert numerical_gate(p)[1]
    for r in p:
        if r['role']=='identity':r['primary']['output']['DE']=100.
    assert numerical_gate(p)[1] # visual policy, not invented numerical identity cutoff
    p[1]['primary']['protected_unchanged']=False
    with pytest.raises(ValueError):numerical_gate(p)
    with pytest.raises(ValueError):numerical_gate(predictions()[:-1])
    p=predictions()
    for r in p:
        if r['role']=='blue_decrease':r['primary']['output']['DE']=2.
    assert not numerical_gate(p)[1]

@pytest.mark.parametrize('field',EVIDENCE)
def test_carryforward_requires_every_exact_field(field):
    a={k:'GENERATED' for k in EVIDENCE};b=deepcopy(a);b[field]='different'
    assert carry_forward(a,b,{},dict(revision_sha256='GENERATED',case_id='id'),'A','B','GENERATED') is None

def test_carryforward_mapping_provenance_and_display():
    a={k:'GENERATED' for k in EVIDENCE};rating=dict(preference='A',artifact='B',reason='GENERATED');before=deepcopy(rating)
    result=carry_forward(a,a,rating,dict(revision_sha256='GENERATED',case_id='id'),'A','B','GENERATED')
    assert result['rating']['preference']=='B' and result['rating']['artifact']=='A' and rating==before
    assert carry_forward(a,a,rating,{},'A','B','GENERATED') is None
    assert carry_forward(a,a,rating,dict(revision_sha256='GENERATED',case_id='id'),'A','B','different') is None

def test_unwanted_stops_and_partial_cannot_unblind():
    public=dict(protocol_id='GENERATED',cases=[dict(id='i',kind='identity'),dict(id='d',kind='distorted')]);saved=dict(protocol_id='GENERATED',display={k:'GENERATED' for k in ['browser','resolution','os_scale','colour_settings']},ratings={})
    def forbidden():raise RuntimeError('Private scores accessed')
    with pytest.raises(ValueError):assess(public,saved,forbidden)
    saved['ratings']['i']=dict(identity='unwanted_change');assert not assess(public,saved,forbidden)['scores_unblinded']
    saved['ratings']['i']=dict(identity='slight_acceptable_change');saved['ratings']['d']=dict(preference='cannot_judge',artifact='none')
    with pytest.raises(ValueError,match='Unresolved'):assess(public,saved,forbidden)

def test_slight_acceptable_all_five_useful_required():
    cases=[dict(id='i',kind='identity')]+[dict(id=f,kind='distorted') for f in BASE.ROLES[1:]]
    public=dict(protocol_id='GENERATED',cases=cases);saved=dict(protocol_id='GENERATED',display={k:'GENERATED' for k in ['browser','resolution','os_scale','colour_settings']},ratings={'i':dict(identity='slight_acceptable_change')})
    saved['ratings'].update({f:dict(preference='A',artifact='none') for f in BASE.ROLES[1:]})
    private=dict(mapping={c['id']:dict(role=c['id'],output_panel='A') for c in cases},benefits={f:1. for f in BASE.ROLES[1:]})
    assert assess(public,saved,lambda:private)['status']=='DEVELOPMENT_ACCEPTABLE'
    saved['ratings']['blue_decrease']['preference']='no_noticeable_difference'
    assert assess(public,saved,lambda:private)['status']=='NOT_READY'

def test_missing_fit_barrier_blocks_array_load(tmp_path):
    write(tmp_path/'all_fits_verified_PRIVATE.json',dict(passed=True,folds=10))
    def forbidden(*a):raise RuntimeError('array load')
    with pytest.raises(AssertionError):after_fit_barrier(tmp_path,dict(folds=[{}]*11),[{}]*11,forbidden,forbidden)

def test_full66_pipeline_and_independent_replay(tmp_path,monkeypatch):
    import scripts.run_blue_axis_source_held as runner
    import scripts.verify_blue_axis_source_held as independent
    from src.model_training.gap_source_held_workflow import render
    root=tmp_path;records=[];supports=[]
    def store(rel,data):
        p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);write(p,data)
    for s in range(11):
        source=f'GENERATED_source{s:02}';box=root/f'GENERATED_support{s}';box.mkdir();item,_,_=OLD.support_fixture(box,shape=256)
        item.update(source=source,source_id=f'GENERATED_{s}',old_support_directory=str(Path(box.name)/'old'));item['selected']['directory']=str(Path(box.name)/'selected')
        if s!=10:
            item['selected']=dict(directory=str(Path(box.name)/'old'),receipt='manifest_PRIVATE.json',receipt_sha256=sha(box/'old/manifest_PRIVATE.json'),files=item['old_files'],alpha_filename='alpha.npy',manual_assisted=False);item['protection_rule']='exact_old'
        supports.append(item);protected=cv2.imread(str(box/'old/protected_mask.png'),0)>0
        ref=np.full((256,256,3),[120+s,90+s,70+s],np.uint8)
        for k,role in enumerate(BASE.ROLES):
            c=f'GENERATED_{s}_{role}';y=BASE.TARGETS[k];fwd=[1/y[0],1/y[1],1/y[2]];image=render(ref,np.ones((256,256)),fwd)
            folder=root/('outputs/blue_axis_preparation_v1' if k>=4 else 'outputs/reviewed_ffhq_restoration_preparation_v1')/c;folder.mkdir(parents=True);path=folder/'paired_pixels.npz'
            arrays=dict(input_rgb8=image,reference_rgb8=ref)
            if k<4:arrays['protected']=protected
            np.savez_compressed(path,**arrays)
            records.append(dict(case_id=c,source=source,role=role,x=[float(k)]+[0.]*280,y=y,generated_fixture=False,status='available',old_record_reused=k<4,pixels_file=str(path),pixels_sha256=sha(path)))
    folds=[dict(held_publisher_group=f'GENERATED_source{s:02}',fitting_cases=[r['case_id'] for r in records if r['source']!=f'GENERATED_source{s:02}'],evaluation_cases=[r['case_id'] for r in records if r['source']==f'GENERATED_source{s:02}']) for s in range(11)]
    plan=dict(protocol_id='GENERATED_BLUE_ONLY',feature_names=BASE.NAMES,folds=folds,reuse=dict(held_source=folds[0]['held_publisher_group']),support_sources=supports,
        anonymous_case_order=[r['case_id'] for r in records],review_order=[r['case_id'] for r in records if r['role']=='identity']+[r['case_id'] for r in records if r['role']!='identity'],input_sha256={},inherited_input_sha256={},
        declared_pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256'],new_blue_pack=not r['old_record_reused']) for r in records])
    first=root/'outputs/blue_axis_first_fit_v1';fit_once(first,fitting_rows(plan,folds[0],records),BASE.NAMES,dict(generated_fixture_only=True))
    plan['reuse'].update(path=str((first/'candidate_PRIVATE.json').relative_to(root)),sha256=sha(first/'candidate_PRIVATE.json'))
    store('outputs/blue_axis_preparation_v1/rows_PRIVATE.json',records);store('outputs/blue_axis_preparation_v1/verification_PRIVATE.json',dict(rows_sha256=sha(root/'outputs/blue_axis_preparation_v1/rows_PRIVATE.json')))
    store('outputs/blue_axis_preparation_v1/role_ledger_PRIVATE.json',[dict(generated_fixture_only=True,case=i) for i in range(72)])
    store('outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json',plan);store('outputs/blue_axis_source_held_design_v1/verification_PRIVATE.json',dict(plan_sha256=sha(root/'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json')))
    store('outputs/blue_axis_workflow_engineering_v1/verification_PRIVATE.json',dict(passed=True,runtime_versions=runner.versions(),input_sha256={}))
    (root/'scripts').mkdir();shutil.copyfile(ROOT/'scripts/867_verify_gap_source_held_comparison.py',root/'scripts/867_verify_gap_source_held_comparison.py')
    monkeypatch.setattr(runner,'ROOT',root);monkeypatch.setattr(sys,'argv',['run','--execute-fixed-development']);runner.main()
    out=root/'outputs/blue_axis_source_held_comparison_v1';result=independent.replay_all(root,out,plan)
    assert result['fitting_routes']==660 and result['held_routes']==66 and result['render_metric_replays']==66
    assert not (out/'review_public.json').exists() and len(read(out/'models_PRIVATE.json'))==11
    with pytest.raises(FileExistsError):runner.main()
    # Saved output corruption must fail the independent pixel replay.
    png=next((out/'review_assets').glob('*_A.png'));arr=cv2.imread(str(png));arr[0,0]=[1,2,3];cv2.imwrite(str(png),arr)
    with pytest.raises(AssertionError):independent.replay_all(root,out,plan)
