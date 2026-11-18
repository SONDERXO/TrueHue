"""Independent scalar pixels/objective and descriptive RGB/DE; zero fits."""
from pathlib import Path
import sys,json,math
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.evaluation.luminance_chroma_scalar import replay
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/luminance_chroma_two_case_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError(dest)
    plan=read(OUT/'execution_plan_PRIVATE.json');assert len(plan['rows'])==2
    assert read(OUT/'completion_PRIVATE.json')['local_solver_calls']==2
    for p,h in plan['input_sha256'].items():assert sha(ROOT/p)==h
    records=[]
    for c in plan['rows']:
        record=read(OUT/(c['case_id']+'.json'));assert record['generated_fixture'] is False
        with np.load(OUT/(c['case_id']+'.npz'),allow_pickle=False) as pack:image,ref,alpha,protected,actual=[pack[k] for k in ['input','reference','alpha','protected','output']]
        with np.load(ROOT/c['pack'],allow_pickle=False) as original:
            for key,value in [('input',image),('reference',ref),('alpha',alpha),('protected',protected)]:np.testing.assert_array_equal(value,original[key])
        expected,mse=replay(image,ref,alpha,protected,record['target']['parameters'])
        np.testing.assert_array_equal(actual,expected)
        assert math.isclose(mse,record['target']['float_mse'],abs_tol=1e-12,rel_tol=1e-12)
        assert np.array_equal(actual[alpha==0],image[alpha==0]) and np.array_equal(actual[protected],image[protected])
        assert np.all(actual[np.all(image==0,axis=2)]==0)
        mask=alpha>0;n=int(mask.sum());values={}
        for name,value in [('input',image),('output',actual)]:
            diffs=np.abs(value.astype(float)-ref);de=deltaE_ciede2000(rgb2lab(value/255.),rgb2lab(ref/255.))
            values[name]=dict(RGB=math.fsum(float(x) for x in diffs[mask].flat)/(3*n),DE=math.fsum(float(x) for x in de[mask])/n)
        records.append(dict(case_id=c['case_id'],source_id=c['source_id'],role=c['role'],parameters=record['target']['parameters'],rank=record['target']['rank'],
            condition=record['target']['condition'],active_bounds=record['target']['active_bounds'],nfev=record['target']['nfev'],primary=values,float_mse=mse))
        assert sha(ROOT/c['pack'])==c['sha256']
        print(c['case_id']+' independent scalar pixels/objective PASS',flush=True)
    result=dict(passed=True,status='TWO_LOCAL_OPERATOR_DIAGNOSTICS_VERIFIED_NOT_MODEL_OR_APPEARANCE',scalar_renders=2,records=records,
        local_solver_calls=2,verifier_fits=0,predictor_fits=0,model_ready=False,artifact_sha256={p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(records,indent=2))
if __name__=='__main__':main()
