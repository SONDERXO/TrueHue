"""Saved nine-record metadata binding + generated-only blue features/control algebra."""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.joint_log_colour import extract
OUT=ROOT/'outputs/qualification_eligibility_blue_check_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def group(v):return 'light' if 1<=v<=3 else 'medium' if 4<=v<=7 else 'dark' if 8<=v<=10 else 'unavailable'
def centroid(values):return [math.fsum(values[3+i*16+j]*(-2+4*(i if axis==0 else j)/15) for i in range(16) for j in range(16)) for axis in [0,1]]

def main():
    if sys.argv[1:]!=['--execute-metadata-and-generated-only']:raise SystemExit('Explicit metadata/generated-only flag required')
    if OUT.exists():raise FileExistsError('Preserve completed/partial step')
    files=['docs/qualification-eligibility-blue-check-protocol-2026-11-13.md','scripts/bind_qualification_eligibility_and_check_blue.py',
        'outputs/existing_data_feasibility_v2/scin_readiness.json','outputs/existing_data_feasibility_v2/summary.json',
        'outputs/mst_retention_checkpoint_v1/summary.json','outputs/joint_colour_qualification_plan_v1/plan_PRIVATE.json',
        'outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json','src/model_training/joint_log_colour.py',
        'scripts/check_joint_log_colour_generated.py','outputs/joint_log_colour_generated_v1/verification_PRIVATE.json']
    bindings={n:sha(ROOT/n) for n in files};qa=read(ROOT/files[-1]);assert qa['passed']
    for n,h in qa['input_sha256'].items():assert sha(ROOT/n)==h
    saved=read(ROOT/files[2]);summary=read(ROOT/files[3])
    local=[r for r in saved if r['confirmed_local_paths']]
    assert len(saved)==368 and len(local)==summary['scin_confirmed_local_records']==9
    ledger=[]
    for r in local:
        a,b=r['india_label'],r['us_label']
        ledger.append(dict(case_id=r['case_id'],image_slot=r['image_slot'],india_label=a,us_label=b,label_status=r['label_status'],
            india_group=group(a),us_group=group(b),group_disagreement=group(a)!=group(b),
            historical_role=r['role'],historical_exposure=r['exposure'],face_suitability=r['face_suitability'],
            duplicate_screen=r['duplicate_screen'],person_independence=r['person_independence'],
            reference_colour_evidence=r['reference_colour_evidence'],current_measurement_admitted=r['current_measurement_admitted'],
            training_admitted=r['training_admitted'],independent_final_eligibility_established=False,
            reason='Previously inspected/historicaltraining-candidate; no verified independent-person/reference/current-measurement admission; preserve holds',
            image_path_checked=False))
    assert Counter(r['label_status'] for r in ledger)==dict(agree=3,disagree=6)
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(input_sha256=bindings,scope='saved9metadata+40generatedrecords',real_photo_reads=0,source_allocations_changed=False))
    write(OUT/'eligibility_ledger_PRIVATE.json',ledger)
    spec=importlib.util.spec_from_file_location('frozen_generated_scenes',ROOT/'scripts/check_joint_log_colour_generated.py')
    generated=importlib.util.module_from_spec(spec);spec.loader.exec_module(generated)
    scenes=generated.scenes();roles=dict(identity=(1.,1.),blue_decrease=(1.,245/255),blue_increase=(1.,255/245),under_blue_decrease=(1/.7,245/255),over_blue_increase=(.7,255/245))
    records=[];maxerr=0.;algebra=0
    for name,image in scenes.items():
        before=image.copy()
        for role,(p,b) in roles.items():
            x=image.astype(float)/255;raw=x**p;raw[:,:,2]*=b
            transformed=np.rint(np.clip(raw,0,1)*255).astype(np.uint8)
            result=extract(transformed);values=list(result['features'].values());scalar=generated.scalar(transformed)
            error=max(abs(a-b) for a,b in zip(values,scalar));assert error<=1e-12;maxerr=max(maxerr,error)
            assert np.array_equal(image,before)
            records.append(dict(generated_fixture=True,scene=name,role=role,features=values,centroid=centroid(values),
                clipped_channel_samples=int(((raw<0)|(raw>1)).sum()),positive_fraction=values[1],
                nominal_inverse=[1/p,1.,b**(-1/p)],independent_scalar_error=error))
            # Three fixed unclipped positive scalar triples, not data/reference pixels.
            for triple in [( .2,.3,.4),(.6,.4,.2),(.1,.1,.1)]:
                y=[v**p for v in triple];y[2]*=b
                assert max(y)<1
                restored=[v**(1/p) for v in y];restored[2]*=b**(-1/p)
                assert all(math.isclose(a,z,abs_tol=1e-12) for a,z in zip(triple,restored));algebra+=1
                if p==1:
                    assert math.isclose(math.log(y[0]/y[1]),math.log(triple[0]/triple[1]),abs_tol=1e-12)
                    assert math.isclose(math.log(y[2]/y[1]),math.log(triple[2]/triple[1])+math.log(b),abs_tol=1e-12)
    assert len(records)==40
    changes=[]
    for name in scenes:
        own={r['role']:r for r in records if r['scene']==name};base=own['identity']
        for role in roles:
            if role=='identity':continue
            r=own[role];changes.append(dict(scene=name,role=role,histogram_L1=math.fsum(abs(a-b) for a,b in zip(base['features'][3:],r['features'][3:])),
                u_shift=r['centroid'][0]-base['centroid'][0],v_shift=r['centroid'][1]-base['centroid'][1],clipped_channel_samples=r['clipped_channel_samples']))
    write(OUT/'generated_blue_records_PRIVATE.json',records);write(OUT/'generated_blue_changes_PRIVATE.json',changes)
    result=dict(status='METADATA_BINDING_AND_GENERATED_CHECK_COMPLETE',saved_metadata_records=9,independent_final_sources_admitted=0,
        per_annotator_groups={label:dict(Counter(r[label+'_group'] for r in ledger)) for label in ['india','us']},
        group_disagreements=sum(r['group_disagreement'] for r in ledger),both_annotator_dark=sum(r['india_group']==r['us_group']=='dark' for r in ledger),
        either_annotator_dark=sum('dark' in (r['india_group'],r['us_group']) for r in ledger),
        generated_records=40,scalar_values=40*259,algebra_checks=algebra,
        generated_responses={role:dict(nonzero=sum(r['histogram_L1']>0 for r in changes if r['role']==role),
            min_v_shift=min(r['v_shift'] for r in changes if r['role']==role),max_v_shift=max(r['v_shift'] for r in changes if r['role']==role),
            clipped_records=sum(r['clipped_channel_samples']>0 for r in changes if r['role']==role)) for role in list(roles)[1:]},
        maximum_scalar_error=maxerr,blue_learning_established=False,real_photo_reads=0,real_fits=0,predictions=0,locked_reads=0,
        next_training_recipe_selected=False)
    write(OUT/'summary_PRIVATE.json',result)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,input_sha256=bindings,metadata_counts_reconciled=True,
        scalar_values=10360,algebra_checks=algebra,source_files_unchanged=True,real_images=0,fits=0,predictions=0,locked_access=False))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
