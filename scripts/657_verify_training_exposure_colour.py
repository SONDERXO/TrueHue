"""Independent paired-delta and pre-veto colour-cost reconciliation."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/training_exposure_colour_audit_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'audit_PRIVATE.json');m=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json');f=m['full'];ids=f['training_cases'];lookup={c:i for i,c in enumerate(ids)};checks=0
    for r in d['source_pairs']:
        i=lookup[r['source_case']+'__'+r['recipe']];j=lookup[r['source_case']+'__clean']
        for k,n in enumerate(m['feature_names']):assert r['feature_delta'][n]==f32(f32(f['training_features'][i][k])-f32(f['training_features'][j][k]));checks+=1
    for r in d['pre_veto_leaves']:
        t=f['pre_veto_model']['trace'][r['leaf']];a=t['action'];cost=f['pre_veto_model']['costs'];colour=[i for i in t['rows'] if ids[i].split('__',1)[1].startswith('colour_') or ids[i].endswith('__stress_color_none')]
        assert [ids[i] for i in colour if cost[i][a]>cost[i][0]]==r['colour_harm_cases']
        assert abs(sum(cost[i][a] for i in colour)-r['colour_selected_cost'])<1e-8
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,paired_feature_checks=checks,leaf_checks=len(d['pre_veto_leaves']),new_fits=0,new_inference=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
