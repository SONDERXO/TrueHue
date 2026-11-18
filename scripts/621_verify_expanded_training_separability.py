"""Scalar verification of fixed clean ranges and row coverage; no model fitting."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
def main():
    out=ROOT/'outputs/expanded_training_separability_v1'
    d=json.loads((out/'audit_PRIVATE.json').read_text())
    m=json.loads((ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json').read_text())
    fits={f['held_key']:f for f in m['folds']+[m['full']]};count=0
    for r in d['records']:
        fit=fits[r['fit_key']];model=fit['model'];ids=next(t['rows'] for t in model['trace'] if t['node']==r['leaf'])
        clean=[i for i in ids if model['clean'][i]]
        limits=[(min(f32(fit['training_features'][i][j]) for i in clean),max(f32(fit['training_features'][i][j]) for i in clean)) for j in range(12)]
        targets=outsidecount=0
        for i,saved in zip(ids,r['rows'],strict=True):
            cid=fit['training_cases'][i];cost=model['costs'][i]
            useful=min(cost)<cost[0] and not model['clean'][i]
            target=useful and cid.split('__',1)[1] in ('exposure_over','combined_warm_over','combined_cool_over')
            axes=[m['feature_names'][j] for j,(lo,hi) in enumerate(limits) if f32(fit['training_features'][i][j])<lo or f32(fit['training_features'][i][j])>hi]
            assert saved==dict(case_id=cid,useful=useful,useful_overexposure=target,outside_clean_axes=axes)
            targets+=target;outsidecount+=bool(target and axes);count+=1
        assert targets==r['useful_overexposure_rows'] and outsidecount==r['useful_overexposure_outside_any']
        assert targets-outsidecount==r['useful_overexposure_inside_all']
        for j,a in enumerate(r['axes']):assert (a['clean_min'],a['clean_max'])==limits[j]
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,leaves=len(d['records']),scalar_row_checks=count,new_fits=0,holdout_image_reads=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
