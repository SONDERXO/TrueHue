"""Read-only assessment of independently verified direct-test JSON artifacts."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/wb_feature_direct_prediction_v1'

def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    dest=OUT/'assessment.json'
    if dest.exists():raise FileExistsError(dest)
    verified=read(OUT/'verification.json');assert verified['passed'] and verified['real_tree_fits']==22
    rows=read(OUT/'records.json');summary=read(OUT/'summary.json');cert=read(OUT/'all_fits_verified.json')
    parent=read(ROOT/'outputs/camera_halfstop_data_v1/plan_PRIVATE.json')
    names=parent['feature_names'][:281];assert len(names)==len(set(names))==281
    schema={'281':names,'314':names+[f'wb_mapping_flat_{j:02d}' for j in range(33)]}
    assert len(schema['314'])==314
    (OUT/'feature_schema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
    role_mae={};harms={}
    for arm in ['281','314']:
        harms[arm]={}
        for role in summary['by_role']:
            own=[r for r in rows if r['role']==role];assert len(own)==11
            role_mae.setdefault(role,{})[arm]=[math.fsum(r['parameter_MAE'][arm][j] for r in own)/11 for j in range(5)]
            harms[arm][role]={metric:[r['case_id'] for r in own if r['regions']['primary'][arm][metric]>r['regions']['primary']['input'][metric]+1e-10] for metric in ['RGB','DE']}
    assert harms==summary['case_harms']
    usage=[]
    for e in cert['models']:
        model=read(OUT/e['path']);splits=[n for n in model['nodes'] if n['kind']=='split']
        usage.append(dict(arm=e['arm'],source_id=e['source_id'],splits=len(splits),wb_splits=sum(n['feature']>=281 for n in splits)))
    identities={arm:{'changed':sum(r['identity_changed_pixels'][arm]>0 for r in rows if r['role']=='identity'),
                     'cases':[{k:r[k] for k in ['case_id','source_id','identity_changed_pixels']} for r in rows if r['role']=='identity']} for arm in ['281','314']}
    report=dict(parameter_MAE_by_role=role_mae,harms_independently_recounted=True,split_usage=usage,identities=identities,
                candidate_numeric_eligible=summary['candidate_numeric_eligible'],baseline_numeric_eligible=summary['baseline_numeric_eligible'],
                real_fits=22,additional_fits=0,additional_pixel_reads=0,ratings=0)
    dest.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'roles':summary['by_role'],'candidate_numeric_eligible':report['candidate_numeric_eligible'],
                      'baseline_numeric_eligible':report['baseline_numeric_eligible'],'candidate_wb_splits':sum(r['wb_splits'] for r in usage),
                      'candidate_total_splits':sum(r['splits'] for r in usage if r['arm']=='314'),
                      'identity_changed':{k:v['changed'] for k,v in identities.items()}},indent=2))

if __name__=='__main__':main()
