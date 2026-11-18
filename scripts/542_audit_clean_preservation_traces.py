"""Read-only saved-score and nearest-clean decomposition; no fitting or forwards."""
from pathlib import Path
import hashlib,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/clean_preservation_trace_audit_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    paths={
        'models':ROOT/'outputs/clean_constrained_gate_models_v1/models_PRIVATE.json',
        'comparison':ROOT/'outputs/clean_constrained_gate_comparison_v1/results_PRIVATE.json',
        'traces':ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json',
        'full':ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json',
        'table':ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json',
        'unconstrained':ROOT/'outputs/signed_benefit_gate_models_v1/models_PRIVATE.json',
        'protocol':ROOT/'docs/clean-preservation-trace-audit-protocol-2026-11-07.md',
        'script':Path(__file__),
    }
    bindings={str(p):sha(p) for p in paths.values()}
    models=read(paths['models']);comparison=read(paths['comparison']);traces=read(paths['traces']);full=read(paths['full'])
    table={r['case_id']:r for r in read(paths['table'])};old=read(paths['unconstrained'])
    folds={f['held_key']:f for f in models['folds']};trace_by_key={f['held_key']:f for f in traces['folds']}
    names=full['feature_names'];assert len(names)==12 and names[4]=='input_mst_score'
    prepared={};constraint_count=0
    def prepare(key,model,cases,features):
        nonlocal constraint_count
        x=np.asarray(features,float);assert x.shape==(len(cases),12)
        z=(x-np.asarray(model['mean']))/np.asarray(model['scale'])
        weights=np.asarray(model['coefficient']);intercept=model['intercept'];indices=model['clean_indices']
        assert indices==[i for i,c in enumerate(cases) if table[c]['case']['id']=='clean']
        clean_scores=z[indices]@weights+intercept
        np.testing.assert_allclose(clean_scores,model['training_clean_scores'],rtol=0,atol=1e-10)
        assert clean_scores.max()<=-1e-6+1e-8
        constraint_count+=len(indices)
        prepared[key]=dict(model=model,x=x,z=z,weights=weights,intercept=intercept,
            cases=cases,indices=indices,clean_scores=clean_scores)
    for key,fold in folds.items():
        trace=trace_by_key[key]['training_trace']
        assert fold['training_cases']==[r['case_id'] for r in trace]
        assert key not in {r['subject_id'] for r in trace}
        prepare(key,fold['model'],fold['training_cases'],[r['features'] for r in trace])
    assert models['full_training_cases']==full['gate_cases']
    prepare('full',models['full_signed'],models['full_training_cases'],full['gate_features'])
    assert constraint_count==290
    audits=[];replayed=0;summary={}
    for suite,expected in [('fold_working256',(30,29,7,3)),('fallback_native224',(24,23,3,1))]:
        rows=[r for r in comparison['records'] if r['suite']==suite]
        for row in rows:
            if row['features'] is None:continue
            p=prepared[row['subject_id'] if suite=='fold_working256' else 'full'];model=p['model']
            z=(np.asarray(row['features'])-model['mean'])/model['scale'];score=float(z@p['weights']+p['intercept'])
            assert abs(score-row['signed_decision']['predicted_rgb_mae_gain'])<1e-9
            assert (score>0)==row['signed_decision']['apply_correction'];replayed+=1
            if row['recipe']!='clean':continue
            clean=p['z'][p['indices']];dist=np.linalg.norm(clean-z,axis=1);j=int(dist.argmin());index=p['indices'][j]
            delta=(z-clean[j])*p['weights'];nearest_score=float(p['clean_scores'][j])
            assert abs(nearest_score+float(delta.sum())-score)<1e-9
            assert row['reference_available'] and row['input_reference_metrics']['rgb8_mae_codes']==0
            changed=row['paths']['signed']['changed_channels']>0
            assert changed==bool(score>0)
            raw=np.asarray(row['features']);cx=p['x'][p['indices']]
            actual=row['paths']['signed']['reference_metrics']['rgb8_mae_codes']
            parameter=row['paths']['signed']['parameters']
            old_model=next(f['model'] for f in old['folds'] if f['held_key']==row['subject_id']) if suite=='fold_working256' else old['full_signed']
            audits.append(dict(suite=suite,case_id=row['case_id'],subject_id=row['subject_id'],
                score=score,changed=changed,retained_changed=row['paths']['frozen']['changed_channels']>0,
                predicted_gain=score,actual_rgb_mae=actual,parameters=parameter,
                nearest_fitting_clean_case=p['cases'][index],nearest_distance=float(dist[j]),
                nearest_clean_score=nearest_score,score_delta_by_feature=dict(zip(names,delta.tolist())),
                feature_terms=dict(zip(names,(z*p['weights']).tolist())),
                face_score_delta=float(delta[:5].sum()),scene_score_delta=float(delta[5:].sum()),
                largest_positive_delta_feature=names[int(delta.argmax())],
                within_individual_clean_ranges=bool(np.all((raw>=cx.min(axis=0))&(raw<=cx.max(axis=0)))),
                old_signed_score=float(z@np.asarray(old_model['coefficient'])+old_model['intercept']),
                image_path=row['image_path'],board_path=str(ROOT/'outputs/clean_constrained_gate_comparison_v1'/suite/row['case_id']/'board.png')))
        clean=[r for r in audits if r['suite']==suite];bad=[r for r in clean if r['changed']]
        total=sum(r['actual_rgb_mae'] for r in clean);worst=max(bad,key=lambda r:r['actual_rgb_mae'])
        attempts=sum(r['recipe']=='clean' for r in rows)
        assert (attempts,len(clean),len(bad),sum(r['retained_changed'] for r in clean))==expected
        summary[suite]=dict(clean_attempts=attempts,clean_available=len(clean),constrained_changed=len(bad),
            retained_changed=sum(r['retained_changed'] for r in clean),
            both_changed=sum(r['changed'] and r['retained_changed'] for r in clean),
            newly_changed=sum(r['changed'] and not r['retained_changed'] for r in clean),
            retained_harm_suppressed=sum(not r['changed'] and r['retained_changed'] for r in clean),
            mean_clean_rgb_mae=total/len(clean),worst_clean_rgb_mae=worst['actual_rgb_mae'],
            worst_fraction_of_summed_photo_errors=worst['actual_rgb_mae']/total,
            positive_score_range=[min(r['score'] for r in bad),max(r['score'] for r in bad)],
            largest_positive_delta_features={name:sum(r['largest_positive_delta_feature']==name for r in bad) for name in names},
            failed_clean_within_individual_clean_ranges=sum(r['within_individual_clean_ranges'] for r in bad))
    selections=[]
    for suite in summary:
        bad=[r for r in audits if r['suite']==suite and r['changed']]
        selections.append(dict(reason='worst_saved_clean_rgb_error',record=max(bad,key=lambda r:r['actual_rgb_mae'])))
    later=[r for r in audits if r['suite']=='fallback_native224' and r['changed']]
    selections.append(dict(reason='closest_later_failed_clean_to_fitting_clean',record=min(later,key=lambda r:r['nearest_distance'])))
    assert all(sha(p)==h for p,h in bindings.items())
    OUT.mkdir()
    value=dict(summary=summary,clean_records=audits,visual_selection=selections,
        gate_score_replays=replayed,training_constraint_occurrences=constraint_count,
        available_clean_photos=52,predictive_fits=0,image_model_forwards=0,new_renderings=0,
        source_hashes_unchanged=True,production_adopted=False,admissions=0)
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summary,gate_score_replays=replayed,training_constraint_occurrences=constraint_count),indent=2))


if __name__=='__main__':main()
