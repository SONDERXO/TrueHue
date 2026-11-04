"""Saved-fold routing and feature-neighbor diagnostic; no fitting or new rule."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.model_training.train_model import load_model
from src.evaluation.tree_training_audit import trace_tree
from src.evaluation.feature_target_diagnostic import neighbor_diagnostic

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parent=ROOT/'outputs/core_control_comparison_v1';out=ROOT/'outputs/core_feature_conflict_v1'
    if out.exists():raise FileExistsError(out)
    prior=json.loads((parent/'summary.json').read_text());verification=json.loads((parent/'verification.json').read_text());final=json.loads((parent/'final_verification.json').read_text())
    hashes=dict(prior['input_sha256']);hashes.update(verification['output_sha256']);hashes.update(final['artifact_sha256'])
    tracked=[Path(__file__),parent/'summary.json',parent/'verification.json',parent/'final_verification.json',ROOT/'docs/core-feature-conflict-protocol.md',ROOT/'src/evaluation/feature_target_diagnostic.py',ROOT/'src/evaluation/tree_training_audit.py']
    hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked});assert all(digest(ROOT/p)==h for p,h in hashes.items())
    rows={p['pair_id']:p for p in prior['predictions'] if p['method']=='no_correction'};predictions={(p['pair_id'],p['method']):p for p in prior['predictions']};eligible=set(prior['eligible_ids'])
    audits={(a['fold_id'],a['method']):a for a in prior['fit_audits']};models={};records=[]
    out.mkdir()
    for p in prior['predictions']:
        if p['method'] not in ['older_recipe','with_controls']:continue
        key=(p['fold_id'],p['method']);audit=audits[key]
        if key not in models:models[key]=load_model(str(parent/'fold_models'/f"fold{key[0]}_{key[1]}.joblib"))
        model=models[key];fit_ids=audit['fit_pair_ids'];fit=[rows[i] for i in fit_ids]
        assert p['source_image_id'] not in {r['source_image_id'] for r in fit}
        x=np.array([r['features'] for r in fit]);y=np.array([r['target_parameters'] for r in fit]);query=np.array(p['features']);target=np.array(p['target_parameters'])
        path=trace_tree(model,query,audit['feature_columns']);leaves=model.apply(x);member_indices=np.flatnonzero(leaves==path['leaf_id'])
        np.testing.assert_allclose(y[member_indices].mean(axis=0),p['predicted_parameters'],rtol=0,atol=1e-12)
        matching=np.all(abs(y-target)<=1e-12,axis=1);member_matching=matching[member_indices]
        unique_targets=np.unique(np.round(y[member_indices],12),axis=0)
        neighborhoods={name:neighbor_diagnostic(fit_ids,x,y,query,target,axes) for name,axes in [('Lab3',[0,1,2]),('Lab_ITA4_sensitivity',[0,1,2,3])]}
        for n in neighborhoods.values():
            for near in n['top3']:
                near['same_leaf']=bool(leaves[fit_ids.index(near['pair_id'])]==path['leaf_id'])
            nearest=n['nearest_matching_target']
            n['nearest_matching_target_in_leaf']=bool(leaves[fit_ids.index(nearest['pair_id'])]==path['leaf_id']) if nearest else None
        baseline=predictions[(p['pair_id'],'no_correction')]
        records.append(dict(pair_id=p['pair_id'],source_image_id=p['source_image_id'],variant=p['variant'],reference_status=p['reference_status'],
            method=p['method'],fold_id=p['fold_id'],features=p['features'],target_parameters=p['target_parameters'],predicted_parameters=p['predicted_parameters'],
            worsened_vs_no_correction=p['ciede2000_source_mask']>baseline['ciede2000_source_mask']+1e-12,
            no_correction_ciede2000=baseline['ciede2000_source_mask'],corrected_ciede2000=p['ciede2000_source_mask'],
            routing=path,leaf_target_count=len(unique_targets),leaf_matching_members=int(member_matching.sum()),leaf_members=len(member_indices),
            leaf_only_different_targets=bool(not member_matching.any()),leaf_mixed_targets=bool(len(unique_targets)>1),
            members=[dict(pair_id=fit[i]['pair_id'],variant=fit[i]['variant'],source_image_id=fit[i]['source_image_id'],features=fit[i]['features'],target_parameters=fit[i]['target_parameters']) for i in member_indices],
            fitting_pair_ids=fit_ids,neighborhoods=neighborhoods))
    assert len(records)==60
    collisions=[];eligible_rows=[rows[p] for p in sorted(eligible)]
    for i,a in enumerate(eligible_rows):
        for b in eligible_rows[i+1:]:
            if a['source_image_id']==b['source_image_id']:continue
            target_conflict=not np.allclose(a['target_parameters'],b['target_parameters'],rtol=0,atol=1e-12)
            for name,dtype in [('rounded_features',float),('float32_features',np.float32)]:
                if np.array_equal(np.asarray(a['features'],dtype),np.asarray(b['features'],dtype)):
                    collisions.append(dict(a=a['pair_id'],b=b['pair_id'],representation=name,target_conflict=target_conflict))
    ita_errors=[]
    for r in rows.values():
        L,a,b,ita=r['features'];assert abs(b)>1e-6
        ita_errors.append(abs(ita-round(math.degrees(math.atan((L-50)/b)),4)))
    counts=[]
    for method in ['older_recipe','with_controls']:
        for subset in ['all_primary','primary_controls','harmful_primary_controls','held_diagnostics']:
            part=[]
            for r in records:
                if r['method']!=method:continue
                primary=r['reference_status']=='primary_eligible_ID';control=r['variant'] in ['identity_control','mild_bright_exposure']
                include=(not primary) if subset=='held_diagnostics' else primary and (subset=='all_primary' or control and (subset=='primary_controls' or r['worsened_vs_no_correction']))
                if include:part.append(r)
            for metric in ['Lab3','Lab_ITA4_sensitivity']:
                counts.append(dict(method=method,subset=subset,distance=metric,probes=len(part),
                    matching_target_available=sum(r['neighborhoods'][metric]['nearest_matching_target'] is not None for r in part),
                    different_target_closer=sum(r['neighborhoods'][metric]['different_target_strictly_closer'] is True for r in part),
                    matching_nearest_target_but_leaf_excludes_it=sum(r['neighborhoods'][metric]['ranking'][0]['target_matches'] and r['neighborhoods'][metric]['nearest_matching_target_in_leaf'] is False for r in part),
                    leaves_only_different_targets=sum(r['leaf_only_different_targets'] for r in part),mixed_target_leaves=sum(r['leaf_mixed_targets'] for r in part)))
    # Descriptive projection only: neighbors use all3Lab dimensions, never this picture.
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    colors=dict(dark='#4477aa',color_shift='#aa3377',bright_warm='#ccbb44',identity_control='#228833',mild_bright_exposure='#ee7733')
    for variant,color in colors.items():
        part=[r for r in eligible_rows if r['variant']==variant];x=np.array([r['features'] for r in part])
        axes[0].scatter(x[:,0],x[:,2],label=variant,c=color,s=45,edgecolors='black',linewidths=.3)
        axes[1].scatter(x[:,0],x[:,3],c=color,s=45,edgecolors='black',linewidths=.3)
    axes[0].set(xlabel='Input mean L*',ylabel='Input mean b*',title='Eligible development measurements (2D projection)')
    axes[1].set(xlabel='Input mean L*',ylabel='Input ITA (degrees)',title='ITA is derived from L* and b*')
    for ax in axes:ax.grid(alpha=.2)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='outside lower center',ncol=3,fontsize=8)
    fig.savefig(out/'feature_projection.png',dpi=160);fig.savefig(out/'feature_projection.pdf');plt.close(fig)
    result=dict(status='complete_read_only_diagnostic',records=records,counts=counts,exact_feature_collisions=collisions,
        ita_max_recomputed_error=max(ita_errors),input_sha256=hashes,new_model_fits=0,new_prediction_rules=0,training_pairs_regenerated=0,
        limitations='Nearest is descriptive and can be distant. Near conflicts are not proof of universal nonidentifiability. Exposed selected development set, not final evaluation.')
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(ita_max_error=max(ita_errors),exact_collisions=len(collisions),counts=counts),indent=2))
if __name__=='__main__':main()
