"""Fixed44input-only audit. No references/masks/model training or predictions."""
from pathlib import Path
from collections import defaultdict
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.joint_log_colour import extract,NAMES
from src.model_training.histogram_gap_features import histogram_gap_features
OUT=ROOT/'outputs/joint_log_colour_exposed_audit_v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def l1(a,b):return math.fsum(abs(x-y) for x,y in zip(a,b))
def centroid(vector):
    h=vector[3:]
    return [math.fsum(h[i*16+j]*(-2+4*(i if axis==0 else j)/15) for i in range(16) for j in range(16)) for axis in [0,1]]

def collisions(records,key):
    groups=defaultdict(list)
    for r in records:groups[tuple(r[key])].append(dict(case_id=r['case_id'],role=r['role']))
    return [dict(cases=rs,cross_role=len({r['role'] for r in rs})>1) for rs in groups.values() if len(rs)>1]

def main():
    if sys.argv[1:]!=['--execute-fixed-input-audit']:raise SystemExit('Explicit --execute-fixed-input-audit required')
    if OUT.exists():raise FileExistsError('Preserve complete/partial audit')
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';rows=read(prep/'rows_PRIVATE.json')
    assert len(rows)==44 and len({r['case_id'] for r in rows})==44 and len({r['publisher_group'] for r in rows})==11
    for r in rows:
        assert r['status']=='available' and r['generated_fixture'] is False and '29863' not in r['case_id']
        assert Path(r['pixels_file']).resolve()==(prep/r['case_id']/'paired_pixels.npz').resolve()
    bysource=defaultdict(list)
    for r in rows:bysource[r['publisher_group']].append(r['experimental_role'])
    assert all(v==['identity','exposure_under','exposure_over','colour_cool'] for v in bysource.values())
    qa=read(ROOT/'outputs/joint_log_colour_generated_v1/verification_PRIVATE.json');assert qa['passed']
    assert read(ROOT/'outputs/joint_log_colour_generated_v1/boundary_checks_PRIVATE.json')['passed']
    for n,h in qa['input_sha256'].items():assert sha(ROOT/n)==h,n
    files=['docs/joint-log-colour-exposed-audit-protocol-2026-11-13.md',
        'scripts/audit_joint_log_colour_exposed_inputs.py','src/model_training/joint_log_colour.py',
        'scripts/check_joint_log_colour_generated.py','src/model_training/histogram_gap_features.py',
        'outputs/joint_log_colour_generated_v1/verification_PRIVATE.json','outputs/joint_log_colour_generated_v1/boundary_checks_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json']
    bindings={n:sha(ROOT/n) for n in files}
    gaps={r['case_id']:r for r in read(ROOT/files[-1])}
    spec=importlib.util.spec_from_file_location('independent_generated_math',ROOT/'scripts/check_joint_log_colour_generated.py')
    scalar=importlib.util.module_from_spec(spec);spec.loader.exec_module(scalar)
    OUT.mkdir()
    write(OUT/'execution_plan_PRIVATE.json',dict(ordered_cases=[r['case_id'] for r in rows],input_sha256=bindings,
        allowed_array_key='input_rgb8',pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256']) for r in rows],
        reference_arrays_allowed=False,mask_arrays_allowed=False,features=list(NAMES),fits=0))
    records=[];max_error=0.
    for r in rows:
        path=Path(r['pixels_file']);assert sha(path)==r['pixels_sha256']
        with np.load(path,allow_pickle=False) as pack:image=pack['input_rgb8']
        assert image.dtype==np.uint8 and image.shape==(256,256,3)
        before=image.copy();result=extract(image);values=list(result['features'].values());expected=scalar.scalar(image)
        error=max(abs(a-b) for a,b in zip(values,expected));max_error=max(error,max_error)
        assert error<=1e-12 and np.array_equal(before,image) and all(math.isfinite(v) for v in values)
        assert 0<=values[1]<=1 and 0<=values[2]<=1 and all(v>=0 for v in values[3:])
        assert not result['available'] or abs(math.fsum(values[3:])-1)<1e-12
        gap=gaps[r['case_id']];recomputed=histogram_gap_features(image)
        assert list(recomputed['features'].values())==list(gap['features'].values())
        assert gap['source']==r['publisher_group'] and gap['role']==r['experimental_role']
        records.append(dict(case_id=r['case_id'],source=r['publisher_group'],role=r['experimental_role'],
            generated_fixture=False,available=result['available'],features=values,centroid=centroid(values),
            positive_pixels=result['positive_pixels'],saturated_any_channel_pixels=int(np.any(image==255,axis=2).sum()),
            old22=r['input_vector_float32']+list(gap['features'].values()),independent_scalar_error=error))
        write(OUT/'features_PRIVATE.json',records)
    groups=defaultdict(dict)
    for r in records:groups[r['source']][r['role']]=r
    pairs=[]
    for source,g in groups.items():
        a=g['identity']
        for role in ['exposure_under','exposure_over','colour_cool']:
            b=g[role]
            pairs.append(dict(source=source,role=role,histogram_L1=l1(a['features'][3:],b['features'][3:]),
                centroid_change=[b['centroid'][j]-a['centroid'][j] for j in range(2)],
                exact_descriptor_equal=a['features']==b['features']))
    identities=[g['identity'] for g in groups.values()]
    inter=[l1(a['features'][3:],b['features'][3:]) for i,a in enumerate(identities) for b in identities[i+1:]]
    assert len(inter)==55
    cool=[dict(source=s,own_identity_L1=l1(g['colour_cool']['features'][3:],g['identity']['features'][3:]),
        nearest_other_identity_L1=min(l1(g['colour_cool']['features'][3:],x['features'][3:]) for x in identities if x['source']!=s)) for s,g in groups.items()]
    newcoll=collisions(records,'features');oldcoll=collisions(records,'old22')
    role_stats={}
    for role in ['exposure_under','exposure_over','colour_cool']:
        own=[p for p in pairs if p['role']==role];dist=sorted(p['histogram_L1'] for p in own)
        role_stats[role]=dict(pairs=len(own),nonzero_L1=sum(p['histogram_L1']>0 for p in own),min_L1=min(dist),median_L1=dist[5],max_L1=max(dist),
            u_shift_min=min(p['centroid_change'][0] for p in own),u_shift_max=max(p['centroid_change'][0] for p in own),
            v_shift_min=min(p['centroid_change'][1] for p in own),v_shift_max=max(p['centroid_change'][1] for p in own))
    for n,h in bindings.items():assert sha(ROOT/n)==h
    for r in rows:assert sha(Path(r['pixels_file']))==r['pixels_sha256']
    write(OUT/'paired_diagnostics_PRIVATE.json',dict(pairs=pairs,cool_nearest_identity=cool,inter_identity_L1=inter,
        old22_collision_groups=oldcoll,new_descriptor_collision_groups=newcoll))
    summary=dict(status='INPUT_ONLY_AUDIT_COMPLETE_NO_FIT',inputs=44,sources=11,features=259,
        available=sum(r['available'] for r in records),positive_fraction_range=[min(r['features'][1] for r in records),max(r['features'][1] for r in records)],
        clipped_fraction_range=[min(r['features'][2] for r in records),max(r['features'][2] for r in records)],
        same_source_role_stats=role_stats,ideal_cool_u_shift=math.log(245/255),
        identity_inter_source_L1=dict(min=min(inter),median=sorted(inter)[27],max=max(inter)),
        old22_collision_groups=len(oldcoll),new_descriptor_collision_groups=len(newcoll),
        no_proof_incremental_beyond_old22=not bool(oldcoll),fits=0,correction_predictions=0,
        reference_arrays_decoded=0,mask_arrays_decoded=0,raw_original_reads=0,locked_reads=0)
    write(OUT/'summary_PRIVATE.json',summary)
    write(OUT/'verification_PRIVATE.json',dict(passed=True,input_sha256=bindings,inputs=44,scalar_values_verified=44*259,
        maximum_scalar_error=max_error,old_gap_values_replayed=264,source_container_hashes_unchanged=True,
        arrays_loaded=['input_rgb8'],reference_mask_arrays_decoded=0,old16_values_preserved=True,fits=0,predictions=0,
        features_sha256=sha(OUT/'features_PRIVATE.json')))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
