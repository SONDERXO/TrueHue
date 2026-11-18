"""Saved full-fit source-paired feature/direction audit; zero classifiers or fits."""
from pathlib import Path
from collections import Counter
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/training_exposure_colour_audit_v1'
def family(recipe):
    if recipe=='clean':return 'clean'
    if recipe.startswith('colour_') or recipe=='stress_color_none':return 'colour_only'
    if recipe in ('exposure_under','exposure_over','stress_exposure_under','stress_exposure_over'):return 'exposure_only'
    return 'combined'
def main():
    if OUT.exists():raise FileExistsError('Preserve audit')
    bound={}
    def read(p):
        p=ROOT/p;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    m=read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json');f=m['full'];names=m['feature_names']
    assert read('outputs/reserved_clean_veto_models_v1/verification_PRIVATE.json')['passed']
    ids=f['training_cases'];x=np.asarray(f['training_features'],np.float32);cost=np.asarray(f['model']['costs']);groups={};rows=[]
    for i,cid in enumerate(ids):groups.setdefault(cid.split('__',1)[0],{})[cid.split('__',1)[1]]=i
    pairrecords=[]
    for source,recipes in sorted(groups.items()):
        clean=recipes.get('clean')
        if clean is None:continue
        for recipe,i in recipes.items():
            if recipe=='clean':continue
            delta=x[i]-x[clean]
            pairrecords.append(dict(source_case=source,recipe=recipe,family=family(recipe),feature_delta=dict(zip(names,map(float,delta)))))
    pairsummary={}
    for fam in ('colour_only','exposure_only','combined'):
        rr=[r for r in pairrecords if r['family']==fam];pairsummary[fam]=dict(conditions=len(rr),sources=len({r['source_case'] for r in rr}),features={})
        for n in names:
            v=np.asarray([r['feature_delta'][n] for r in rr]);pairsummary[fam]['features'][n]=dict(min=float(v.min()),median=float(np.median(v)),max=float(v.max()))
    # Fixed direction check: sign of paired facial/scene brightness, not a fitted threshold.
    signs={}
    for recipe in ('colour_cool','colour_warm','stress_color_none','exposure_under','exposure_over','stress_exposure_under','stress_exposure_over'):
        rr=[r for r in pairrecords if r['recipe']==recipe];signs[recipe]={}
        for n in ('input_mean_l_star','scene_l_p50'):
            v=[r['feature_delta'][n] for r in rr];signs[recipe][n]=dict(pairs=len(v),lower=sum(z<0 for z in v),equal=sum(z==0 for z in v),higher=sum(z>0 for z in v))
    full=f['pre_veto_model'];leafrows=[]
    for t in full['trace']:
        if full['tree']['nodes'][t['node']]['kind']!='leaf':continue
        ix=t['rows'];a=t['action'];families=Counter(family(ids[i].split('__',1)[1]) for i in ix)
        colour=[i for i in ix if family(ids[i].split('__',1)[1])=='colour_only']
        harms=[i for i in colour if cost[i,a]>cost[i,0]]
        leafrows.append(dict(leaf=t['node'],action=a,controls=full['actions'][a],families=dict(families),colour_rows=len(colour),colour_harms=len(harms),
            colour_harm_cases=[ids[i] for i in harms],colour_selected_cost=float(cost[colour,a].sum()) if colour else 0.,colour_identity_cost=float(cost[colour,0].sum()) if colour else 0.,
            all_selected_cost=float(cost[ix,a].sum()),all_identity_cost=float(cost[ix,0].sum())))
    summary=dict(full_training_conditions=len(ids),unique_sources=len(groups),families=dict(Counter(family(cid.split('__',1)[1]) for cid in ids)),
        colour_harmed_in_pre_veto_fit=sum(r['colour_harms'] for r in leafrows),colour_harm_leaves=[r['leaf'] for r in leafrows if r['colour_harms']],
        source_pair_deltas=pairsummary,brightness_direction_counts=signs)
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();(OUT/'audit_PRIVATE.json').write_text(json.dumps(dict(summary=summary,source_pairs=pairrecords,pre_veto_leaves=leafrows,input_sha256=bound,
        new_fits=0,new_inference=0,new_predictions=0,holdout_image_reads=0,limitation='Same-source clean differences are reference diagnostics unavailable to inference. No fitted classifier or proof of separability.'),indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!='source_pair_deltas'},indent=2));print('harm leaves',json.dumps([r for r in leafrows if r['colour_harms']],indent=2))
if __name__=='__main__':main()
