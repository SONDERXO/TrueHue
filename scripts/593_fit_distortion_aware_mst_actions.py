"""One fixed supervision change: paired-distortion MST calibration, same action trees."""
from pathlib import Path
from itertools import combinations
import json,hashlib,sys,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.contextual_mst_experiment import _ridge,predict,FEATURES
from src.model_training.image_loss_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree
P=ROOT/'outputs/aligned_correction_preparation_v1'
OUT=ROOT/'outputs/distortion_aware_mst_action_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve existing fits')
    oldpath=ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json';old=read(oldpath)
    prep=read(P/'results_PRIVATE.json');rows={r['case_id']:r for r in prep['records']}
    # Exact full-tree source/condition cohort, not later data or a favorable subset.
    cohort=[rows[cid] for cid in old['full']['training_cases']]
    keys=sorted({r['subject_id'] for r in cohort});assert len(keys)==10 and len(cohort)==227
    bound=dict(old['input_sha256'])
    for p in (oldpath,P/'results_PRIVATE.json',Path(__file__),ROOT/'docs/distortion-aware-mst-protocol-2026-11-08.md',
              ROOT/'src/ita_estimation/contextual_mst_experiment.py',ROOT/'src/model_training/image_loss_action_tree.py'):
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();calibrations={}
    for excluded in [()]+[(k,) for k in keys]+list(combinations(keys,2)):
        training=[dict(case_id=r['case_id'],subject_id=r['subject_id'],features=r['raw_features'],source_mst_exact_decimal=r['source_mst_exact_decimal']) for r in cohort if r['subject_id'] not in excluded]
        model=_ridge(training,FEATURES)
        calibrations['|'.join(excluded)]=dict(excluded_keys=list(excluded),training_cases=[r['case_id'] for r in training],
            training_keys=sorted({r['subject_id'] for r in training}),model=model,status='fitted',calibration_admitted=False)
    assert len(calibrations)==56;print('Completed56paired-condition calibrations',flush=True)
    def vector(cid,base,excluded):
        mst=predict(calibrations['|'.join(sorted(excluded))]['model'],rows[cid]['raw_features'])
        x=list(base);x[4]=mst['score'];return x,mst
    fits=[]
    for parent in old['folds']+[old['full']]:
        fit={k:copy.deepcopy(v) for k,v in parent.items() if k not in ('model','training_features','training_trace')}
        features=[];traces=[]
        for cid,x,t in zip(parent['training_cases'],parent['training_features'],parent['training_trace'],strict=True):
            v,mst=vector(cid,x,t['excluded_keys']);features.append(v);traces.append(dict(case_id=cid,excluded_keys=t['excluded_keys'],mst_prediction=mst))
        m=parent['model'];new=fit_action_tree(features,m['costs'],m['clean'],m['actions'],old['feature_names'],max_depth=3)
        new.update(costs=copy.deepcopy(m['costs']),clean=copy.deepcopy(m['clean']))
        fit.update(training_features=features,training_trace=traces,model=new);fits.append(fit)
        print('Fitted',fit['held_key'],len(features),flush=True)
    bykey={f['held_key']:f for f in fits};predictions=[]
    for p in old['predictions']:
        q=copy.deepcopy(p)
        if p['features'] is not None:
            q['features'],q['mst_prediction']=vector(p['case_id'],p['features'],p['excluded_keys'])
            fit=bykey[p['subject_id']] if p['cohort']=='development' else fits[-1]
            q['parameters']=PortableTree(fit['model']['tree']).predict_one(q['features'])
        predictions.append(q)
    result=dict(folds=fits[:-1],full=fits[-1],calibrations=calibrations,predictions=predictions,feature_names=old['feature_names'],
        input_sha256=bound,new_matching_MST_fits=56,new_action_tree_fits=11,new_target_fits=0,
        measurement_contract_sha256=old['measurement_contract_sha256'],production_adopted=False,training_admitted=False,calibration_admitted=False,
        calibration_cohort=[r['case_id'] for r in cohort],supervision='Same source-score label across available original and synthetic conditions')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('Saved exactly56MST+11action fits; no mask/model adoption.')

if __name__=='__main__':main()
