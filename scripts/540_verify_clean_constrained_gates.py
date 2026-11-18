"""Independent KKT and inherited nested/action audits for constrained gates."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/536_verify_signed_benefit_gates.py').read_text()
source=source.replace('import cv2,numpy as np','import cv2,numpy as np\nfrom scipy.optimize import nnls')
start=source.index('def equation(');end=source.index('def main():',start)
replacement='''def equation(model,x,y,keys):
    x=np.array(x);y=np.array(y);w=np.array(model['weights']);mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean);scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(scale==0,1.,scale)
    np.testing.assert_allclose(mean,model['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(scale,model['scale'],atol=1e-12,rtol=0)
    z=(x-mean)/scale;d=np.column_stack([z,np.ones(len(x))]);theta=np.array(model['coefficient']+[model['intercept']]);reg=np.diag([1.]*x.shape[1]+[0.]);c=d[model['clean_indices']];scores=c@theta;margin=model['constraint_margin'];assert margin==1e-6 and scores.max()<=-margin+1e-8
    np.testing.assert_allclose(scores,model['training_clean_scores'],atol=1e-10,rtol=0)
    gradient=(d.T@(w*(d@theta-y))+reg@theta)/w.sum();active=np.abs(scores+margin)<=1e-6;assert active.any()
    dual,residual=nnls(c[active].T,-gradient,maxiter=10000);assert residual<1e-4;assert np.max(np.abs(dual*(scores[active]+margin)))<1e-5
    initial=np.zeros(len(theta));initial[-1]=-margin
    loss=lambda t:.5*(np.sum(w*(d@t-y)**2)+t@reg@t)/w.sum()
    assert loss(theta)<=loss(initial)+1e-8
    for k in set(keys):
        for sign in [False,True]:assert np.isclose(sum(w[i] for i in range(len(x)) if keys[i]==k and (y[i]>0)==sign),len(x)/(len(set(keys))*2))
'''
source=source[:start]+replacement+source[end:]
source=source.replace('outputs/signed_benefit_gate_comparison_v1','outputs/clean_constrained_gate_comparison_v1').replace('outputs/signed_benefit_gate_models_v1','outputs/clean_constrained_gate_models_v1').replace('outputs/signed_benefit_gate_assessment_v1','outputs/clean_constrained_gate_assessment_v1')
source=source.replace("assert f['held_key']==old['held_key'];trace=", "assert f['held_key']==old['held_key'];assert f['model']['clean_indices']==[i for i,c in enumerate(f['training_cases']) if table[c]['case']['id']=='clean'];trace=")
source=source.replace("preds={r['case_id']", "assert m['full_signed']['clean_indices']==[i for i,c in enumerate(m['full_training_cases']) if table[c]['case']['id']=='clean']\n    preds={r['case_id']")
source=source.replace('signed_normal_equations=11','constrained_KKT_checks=11,training_clean_constraint_occurrences=290').replace('Verified11equations','Verified11KKTsystems')
exec(compile(source,str(ROOT/'scripts/536_verify_signed_benefit_gates.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
