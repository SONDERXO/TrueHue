"""Independent metadata-only recipe/role/fold verification; no generation."""
from pathlib import Path
from collections import Counter
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/source_matched_restoration_design_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bindings=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bindings.items())
    plan=read(OUT/'plan_PRIVATE.json');bases=read(OUT/'bases_PRIVATE.json');ledger=read(OUT/'role_ledger_PRIVATE.json');folds=read(OUT/'folds_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/reviewed_correction_comparison_design_v1/rows_PRIVATE.json')}
    assert len(bases)==7 and len(ledger)==len({r['case_id'] for r in ledger})==40 and len(folds)==8
    assert Counter(r['role'] for r in ledger)=={'identity':8,'original_source':8,'exposure_under':8,'exposure_over':8,'colour_cool':8}
    recipes=plan['generation']['recipes'];assert len(recipes)==3
    assert recipes[0]['gamma']==1/.7 and recipes[1]['gamma']==.7
    assert math.isclose(recipes[2]['red_gain'],1-10/255,abs_tol=1e-15) and recipes[2]['gamma']==1
    for b in bases:
        old=rows[b['base_case_id']];assert old['role']=='target' and old['publisher_group']==b['publisher_group']
        assert b['pixels_file']==old['pixels_file'] and b['pixels_sha256']==old['pixels_sha256']
        assert b['annotation_manifest_sha256']==old['annotation_manifest_sha256']
        assert b['provided_MST_label'] is None
    bycase={r['case_id']:r for r in ledger};evaluated=[];fitting_folds=0
    for f in folds:
        held=f['held_publisher_group'];assert len(f['attempted_evaluation_cases'])==5
        if held=='904':
            assert f['fitting_cases']==f['evaluation_cases']==[] and not f['fit_required'];continue
        fitting_folds+=1;assert len(f['fitting_cases'])==24 and len(f['evaluation_cases'])==5
        fit=[bycase[c] for c in f['fitting_cases']];test=[bycase[c] for c in f['evaluation_cases']]
        assert all(r['publisher_group']!=held and r['fitting_allowed'] and r['role']!='original_source' for r in fit)
        assert len({r['publisher_group'] for r in fit})==6
        assert Counter(r['role'] for r in fit)=={'identity':6,'exposure_under':6,'exposure_over':6,'colour_cool':6}
        assert all(r['publisher_group']==held for r in test) and len({r['role'] for r in test})==5
        assert all(v==1 for v in f['fitting_role_weights'].values());evaluated+=f['evaluation_cases']
    assert fitting_folds==7 and len(evaluated)==len(set(evaluated))==35
    assert set(evaluated)=={r['case_id'] for r in ledger if r['publisher_group']!='904'}
    oldplan=read(ROOT/'outputs/reviewed_correction_comparison_design_v1/plan_PRIVATE.json')
    assert plan['training']['tree']==oldplan['candidate']
    assert plan['images_generated']==plan['new_fits']==plan['new_predictions']==plan['image_reads']==0
    assert not plan['generation_authorized_by_this_specification'] and not plan['fit_authorized_by_this_specification']
    assert not plan['runtime_adopted'] and all(not r['training_admitted'] and not r['calibration_admitted'] for r in ledger)
    report=dict(passed=True,existing_reference_bases=7,planned_new_derivatives=21,attempted_roles=40,planned_available_roles=35,
        folds=7,fit_rows_per_fold=24,held_rows_per_fold=5,original_sources_never_fitting=True,
        fixed_recipe_values_checked=3,tree_features_actions_unchanged=True,source_derivatives_grouped=True,
        images_generated=0,new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,
        input_sha256={str(p):sha(p) for p in OUT.iterdir() if p.is_file()},verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n');print('PASS:7bases/3fixedrecipes/21plannedimages/40roles/7folds24fit5eval;originalsourcesneverfit;zero generation.')


if __name__=='__main__':main()
