"""Fixed 44-input extraction audit; no reference/alpha/mask decode or fits."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.histogram_gap_features import histogram_gap_features,NAMES
OUT=ROOT/'outputs/histogram_gap_exposed_input_audit_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    if OUT.exists():raise FileExistsError('Preserve complete or partial audit')
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';rows=read(prep/'rows_PRIVATE.json')
    assert len(rows)==44 and len({r['publisher_group'] for r in rows})==11
    assert all(r['status']=='available' and r['generated_fixture'] is False and '29863' not in r['case_id'] for r in rows)
    assert len({r['case_id'] for r in rows})==44
    assert {r['experimental_role'] for r in rows}=={'identity','exposure_under','exposure_over','colour_cool'}
    files=['src/model_training/histogram_gap_features.py','tests/test_histogram_gap_features.py',
        'scripts/860_audit_histogram_gap_exposed_inputs.py','docs/histogram-gap-exposed-cache-protocol-2026-11-12.md',
        'outputs/histogram_gap_generated_robustness_v1/verification_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json']
    bound={name:sha(ROOT/name) for name in files}
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(ordered_cases=[r['case_id'] for r in rows],
        input_sha256=bound,pixel_containers=[dict(path=r['pixels_file'],sha256=r['pixels_sha256']) for r in rows],
        allowed_array_key='input_rgb8',features=list(NAMES),fits=0,reference_arrays_allowed=False))
    records=[]
    for r in rows:
        path=Path(r['pixels_file']);assert path.resolve()==(prep/r['case_id']/'paired_pixels.npz').resolve()
        assert sha(path)==r['pixels_sha256']
        with np.load(path,allow_pickle=False) as pack:image=pack['input_rgb8']
        assert image.dtype==np.uint8 and image.shape==(256,256,3)
        result=histogram_gap_features(image);assert result['valid']
        exact=[]
        for j in range(3):
            observed={int(v) for v in image[:,:,j].flat}
            for low,high in [(0,127),(128,255)]:
                eligible=set(range(max(low,min(observed)),min(high,max(observed))+1))
                exact.append(float(Fraction(len(eligible-observed),len(eligible))) if eligible else 0.)
        assert exact==list(result['features'].values())
        records.append(dict(case_id=r['case_id'],source=r['publisher_group'],role=r['experimental_role'],
            features=result['features'],diagnostics=result['channels'],input_pixels=65536,generated_fixture=False))
        write(OUT/'features_PRIVATE.json',records)
    groups=defaultdict(dict)
    for r in records:groups[r['source']][r['role']]=r
    paired=[]
    for source,group in groups.items():
        identity=group['identity']['features'];base=identity[NAMES[3]]-identity[NAMES[2]]
        for role in ['exposure_under','exposure_over','colour_cool']:
            values=group[role]['features'];diff=[values[n]-identity[n] for n in NAMES]
            paired.append(dict(source=source,role=role,descriptor_difference=diff,
                L1_difference=sum(abs(v) for v in diff),exact_equal_to_identity=not any(diff),
                green_asymmetry_change=(values[NAMES[3]]-values[NAMES[2]])-base))
    shared=defaultdict(list)
    for r in records:shared[tuple(r['features'].values())].append(dict(case_id=r['case_id'],role=r['role']))
    collisions=[dict(features=list(vector),cases=cases) for vector,cases in shared.items() if len({c['role'] for c in cases})>1]
    intervals={}
    for n in NAMES:
        intervals[n]={role:dict(min=min(r['features'][n] for r in records if r['role']==role),
            max=max(r['features'][n] for r in records if r['role']==role),
            mean=sum(r['features'][n] for r in records if r['role']==role)/11) for role in groups[next(iter(groups))]}
    signs={role:dict(positive=sum(p['green_asymmetry_change']>0 for p in paired if p['role']==role),
        negative=sum(p['green_asymmetry_change']<0 for p in paired if p['role']==role),
        zero=sum(p['green_asymmetry_change']==0 for p in paired if p['role']==role),
        exact_equal_to_identity=sum(p['exact_equal_to_identity'] for p in paired if p['role']==role)) for role in ['exposure_under','exposure_over','colour_cool']}
    assert all(sha(ROOT/n)==h for n,h in bound.items())
    assert all(sha(Path(r['pixels_file']))==r['pixels_sha256'] for r in rows)
    write(OUT/'paired_differences_PRIVATE.json',paired);write(OUT/'descriptor_collisions_PRIVATE.json',collisions)
    write(OUT/'role_intervals_PRIVATE.json',intervals)
    summary=dict(status='FIXED_INPUT_AUDIT_COMPLETE_NO_FIT',inputs=44,sources=11,features=6,independent_values_checked=264,
        paired_green_asymmetry_signs=signs,cross_role_collision_groups=len(collisions),
        all_zero_descriptor_cases=[r['case_id'] for r in records if not any(r['features'].values())],
        model_fits=0,correction_predictions=0,reference_arrays_decoded=0,mask_arrays_decoded=0,
        raw_original_reads=0,final_locked_reads=0)
    write(OUT/'summary_PRIVATE.json',summary)
    write(OUT/'verification_PRIVATE.json',dict(passed=True,input_sha256=bound,container_hashes_unchanged=True,
        arrays_loaded=['input_rgb8'],independent_scalar_values=264,
        feature_records_sha256=sha(OUT/'features_PRIVATE.json'),fits=0,predictions=0))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
