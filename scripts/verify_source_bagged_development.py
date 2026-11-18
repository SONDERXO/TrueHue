"""Independent real-run reconstruction/replay. Never imports a trainer or optimizer."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import struct
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.source_bagged_verification import verify, mean_predict

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,d):
    with Path(p).open('x',encoding='utf-8') as stream:json.dump(d,stream,indent=2,allow_nan=False);stream.write('\n')
def close(a,b):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)

def reconstruct(plan,fold):
    records={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    result=[]
    for case in fold['fitting_cases']:
        row=records[case];gap=gaps[case]
        assert row['generated_fixture'] is False and gap['generated_fixture'] is False
        assert row['publisher_group']==gap['source']!=fold['held_publisher_group']
        assert row['experimental_role']==gap['role'] and row['status']=='available' and '29863' not in case
        extra=[struct.unpack('!f',struct.pack('!f',gap['features'][n]))[0] for n in plan['feature_names'][16:]]
        result.append(dict(case_id=case,source=row['publisher_group'],role=row['experimental_role'],x=row['input_vector_float32']+extra,y=row['nominal_controls']))
    assert len(result)==40 and len({r['source'] for r in result})==10
    return result

def verify_fold(folder,plan,fold):
    expected=reconstruct(plan,fold)
    assert read(folder/'fitting_inputs_PRIVATE.json')==expected
    report=verify(read(folder/'candidate_PRIVATE.json'),expected,read(folder/'training_replay_PRIVATE.json'),plan['feature_names'],fold['held_publisher_group'])
    assert read(folder/'verification_PRIVATE.json')==report
    return report

def verify_first(plan):
    folder=ROOT/plan['first_output'];report=verify_fold(folder,plan,plan['folds'][0])
    seal=read(folder/'sealed_PRIVATE.json')
    assert sha(folder/'candidate_PRIVATE.json')==seal['candidate_sha256']
    assert sha(folder/'fitting_inputs_PRIVATE.json')==seal['snapshot_sha256']
    assert seal['plan_sha256']==sha(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json')
    write_new(folder/'independent_verification_PRIVATE.json',dict(passed=True,**{k:v for k,v in report.items() if k!='passed'},
        artifacts={p.name:sha(p) for p in folder.glob('*.json')}))
    print('PASS first40fit joins/64bootstrap trees/routes/leafmeans/mean; 0held scoring')

def verify_comparison(plan):
    import cv2
    import numpy as np
    # Reuse the old independent per-channel renderer/converter, not scorer code.
    spec=importlib.util.spec_from_file_location('independent_pixel_replay',ROOT/'scripts/867_verify_gap_source_held_comparison.py')
    pixel=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixel)
    out=ROOT/plan['comparison_output']
    assert read(out/'execution_plan_PRIVATE.json')['plan']==plan
    allfits=read(out/'all_fits_verified_PRIVATE.json')
    assert allfits==dict(passed=True,ensembles=11,total_member_fits=704,new_member_fits=640,reused_member_fits=64)
    models=read(out/'models_PRIVATE.json');assert len(models)==11
    leafmeans=0
    for i,(entry,fold) in enumerate(zip(models,plan['folds'])):
        assert entry['fold']==fold and entry['reused']==(i==0) and entry['directory']==fold['held_publisher_group']
        folder=out/entry['directory'];assert sha(folder/'candidate_PRIVATE.json')==entry['candidate_sha256']
        report=verify_fold(folder,plan,fold);leafmeans+=report['leaf_mean_checks']
    first=ROOT/plan['first_output'];seal=read(out/'reuse_seal_PRIVATE.json')
    assert read(first/'independent_verification_PRIVATE.json')['passed']
    assert seal==read(first/'sealed_PRIVATE.json') and sha(first/'candidate_PRIVATE.json')==seal['candidate_sha256']
    assert sha(out/models[0]['directory']/'candidate_PRIVATE.json')==seal['candidate_sha256']
    supports={}
    assert read(out/'all_supports_sealed_PRIVATE.json')==dict(passed=True,supports=plan['supports'])
    for s in plan['supports']:
        folder=ROOT/s['directory'];assert folder.resolve().parent==(ROOT/'outputs/histogram_gap_source_held_comparison_v1/supports').resolve()
        assert sha(folder/'manifest_PRIVATE.json')==s['manifest_sha256']
        for n,h in s['files'].items():assert sha(folder/n)==h
        protection=cv2.imread(str(folder/'protected_mask.png'),0)>0
        mask=cv2.imread(str(folder/'correction_mask.png'),0)
        alpha=np.load(folder/'alpha.npy',allow_pickle=False)
        assert np.array_equal(alpha,pixel.alpha_from_mask(mask,protection,s['face_width']))
        supports[s['source']]=(alpha,protection)
    predictions=read(out/'predictions_PRIVATE.json');public=read(out/'review_public.json')
    records={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    assert len(predictions)==len(public['cases'])==44 and {p['case_id'] for p in predictions}==set(records)
    assert public['protocol_id']==plan['protocol_id']
    byreview={c['id']:c for c in public['cases']};assert len(byreview)==44
    bysource={m['fold']['held_publisher_group']:m for m in models}
    saved={p['case_id']:p for p in read(ROOT/'outputs/histogram_gap_source_held_comparison_v1/predictions_PRIVATE.json')}
    prepared=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    declared={r['case_id']:r for r in plan['pixel_containers']}
    for i,p in enumerate(predictions):
        row=records[p['case_id']];gap=gaps[p['case_id']];entry=bysource[row['publisher_group']]
        assert p['case_id'] in entry['fold']['evaluation_cases'] and p['source']==row['publisher_group'] and p['role']==row['experimental_role']
        values=row['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gap['features'][n]))[0] for n in plan['feature_names'][16:]]
        controls=mean_predict(read(out/entry['directory']/'candidate_PRIVATE.json'),values)
        assert controls==p['controls'] and p['parameter_absolute_error']==[abs(a-b) for a,b in zip(controls,row['nominal_controls'])]
        assert p['review_id']==f'case-{i+1:02}'
        case=byreview[p['review_id']]
        bit=hashlib.sha256((plan['protocol_id']+p['case_id']).encode()).digest()[-1]&1
        assert p['output_panel']==('A' if bit else 'B')
        assert case['kind']==('identity' if p['role']=='identity' else 'distorted')
        for k in ['A','B','R']:
            expected=None if k=='R' and p['role']=='identity' else f'review_assets/{p["review_id"]}_{k}.png'
            assert case[k]==expected
        path=Path(row['pixels_file']);assert path.resolve()==(prepared/p['case_id']/'paired_pixels.npz').resolve()
        assert path.resolve()==Path(declared[p['case_id']]['path']).resolve() and sha(path)==row['pixels_sha256']==declared[p['case_id']]['sha256']
        with np.load(path,allow_pickle=False) as pack:
            image=pack['input_rgb8'];reference=pack['reference_rgb8'];alpha,protection=supports[p['source']]
            assert np.array_equal(protection,pack['protected'])
            output=pixel.replay(image,alpha,controls)
            assert np.array_equal(output[protection],image[protection]) and np.array_equal(output[alpha==0],image[alpha==0])
            panel=cv2.imread(str(out/case[p['output_panel']]))[:,:,::-1]
            other=cv2.imread(str(out/case['B' if bit else 'A']))[:,:,::-1]
            assert np.array_equal(panel,output) and np.array_equal(other,image)
            if case['R']:assert np.array_equal(cv2.imread(str(out/case['R']))[:,:,::-1],reference)
            metric=p['primary'];assert metric['protected_unchanged'] and metric['zero_alpha_unchanged']
            assert metric['changed_pixels']==int(np.any(output!=image,axis=2).sum()) and metric['scoring_pixels']==int((alpha>0).sum())
            for prefix,arr in [('input',image),('output',output)]:
                actual=pixel.metrics(arr,reference,alpha>0)
                for k in ['RGB','DE']:close(actual[k],metric[prefix][k])
            for k in ['RGB','DE']:close(metric['input'][k],saved[p['case_id']]['primary']['input'][k])
    summary=read(out/'summary_PRIVATE.json')
    for role in ['identity','exposure_under','exposure_over','colour_cool']:
        own=[p for p in predictions if p['role']==role];rec=summary['primary']['by_role'][role]
        assert len(own)==len({p['source'] for p in own})==rec['cases']==rec['sources']==11
        deltas=[p['primary']['input']['DE']-p['primary']['output']['DE'] for p in own]
        close(rec['source_equal_DE_improvement'],math.fsum(deltas)/11)
        close(rec['worst_DE_improvement'],min(deltas))
        assert rec['DE_benefits']==sum(v>1e-10 for v in deltas) and rec['DE_harms']==sum(v< -1e-10 for v in deltas)
        assert rec['numerical_equal']==sum(abs(v)<=1e-10 for v in deltas)
        for prefix in ['input','output']:close(rec[prefix+'_RGB'],math.fsum(p['primary'][prefix]['RGB'] for p in own)/11)
    numeric=all(summary['primary']['by_role'][role]['source_equal_DE_improvement']>0 for role in plan['families'])
    assert summary['numeric_families_pass']==numeric and not summary['model_ready']
    assert summary['visual_status']==('PENDING' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE')
    ledger=read(out/'role_ledger_PRIVATE.json');assert len(ledger)==48 and ledger==read(prepared/'role_ledger_PRIVATE.json')
    assert summary['attempted']==48 and summary['available']==44 and summary['excluded']==4
    for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
    write_new(out/'verification_PRIVATE.json',dict(passed=True,member_trees=704,member_fitting_routes=28160,
        member_held_routes=2816,held_means=44,render_metric_replays=44,support_replays=11,leaf_mean_checks=leafmeans,
        exact_first_reuse=True,refits=0,numeric_families_pass=numeric,model_ready=False,
        artifact_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}))
    if not numeric:
        write_new(out/'final_development_assessment_PRIVATE.json',dict(development_status='FAIL_CLOSED_NOT_ADOPTED',
            reason='Required distorted-family numerical benefit failed',numeric_families_pass=False,
            failed_families=[r for r in plan['families'] if summary['primary']['by_role'][r]['source_equal_DE_improvement']<=0],
            visual_review='NOT_REQUESTED_NUMERICAL_FAILURE_ALREADY_ESTABLISHED',model_adopted=False,final_access=False))
    print('PASS independent704trees/28160fit/2816held/44renders/11supports; '+('visual review pending' if numeric else 'numerical failure closes candidate'))

def main():
    if sys.argv[1:] not in [['--first'],['--comparison']]:raise SystemExit('Explicit --first or --comparison required')
    plan=read(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json')
    receipt=read(ROOT/'outputs/source_bagged_design_v1/engineering_PRIVATE.json')
    assert receipt['passed'] and receipt['plan_sha256']==sha(ROOT/'outputs/source_bagged_design_v1/plan_PRIVATE.json')
    for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
    if sys.argv[1]=='--first':verify_first(plan)
    else:verify_comparison(plan)

if __name__=='__main__':main()
