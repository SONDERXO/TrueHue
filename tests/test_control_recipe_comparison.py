import copy
import pytest
from src.model_training.control_recipe_comparison import plan_control_folds

def probes():
    return [dict(pair_id=s+'_'+v,source_image_id=s,duplicate_group_id=s,variant=v,partition='train',table_use='train',
        clipped_pixel_count=0,input_processing_status='success') for s in ['A','B','C'] for v in ['dark','identity_control']]

def test_all_variants_stay_out_and_held_ids_never_fit_any_recipe():
    rows=probes();held=['A_dark'];eligible=[r['pair_id'] for r in rows if r['pair_id'] not in held]
    plans=plan_control_folds(rows,eligible,held);assert len(plans)==3
    seen=[]
    for p in plans:
        seen+=p['evaluation_pair_ids']
        for method,ids in p['fit_pair_ids'].items():
            assert not set(ids)&set(p['evaluation_pair_ids']) and not set(ids)&set(held)
            assert all(not pair.startswith(p['held_out_source_ids'][0]+'_') for pair in ids)
            if method=='older_recipe':assert all(pair.endswith('_dark') for pair in ids)
    assert sorted(seen)==sorted(r['pair_id'] for r in rows)

def test_source_with_only_held_probes_has_diagnostic_fold_without_promotion():
    rows=probes();held=['A_dark','A_identity_control'];eligible=[r['pair_id'] for r in rows if r['pair_id'] not in held]
    plan=next(p for p in plan_control_folds(rows,eligible,held) if p['held_out_source_ids']==['A'])
    assert plan['primary_pair_ids']==[] and plan['held_diagnostic_pair_ids']==held
    assert not set(held)&set(plan['fit_pair_ids']['with_controls'])

@pytest.mark.parametrize('mutation',[
    lambda r:r[0].update(partition='reserved_test'),lambda r:r[0].update(table_use='stress_only'),
    lambda r:r[0].update(clipped_pixel_count=1),lambda r:r[0].update(input_processing_status='excluded'),
    lambda r:r[1].update(duplicate_group_id='wrong'),lambda r:r.append(copy.deepcopy(r[0]))])
def test_ineligible_rows_and_inconsistent_groups_fail_closed(mutation):
    rows=probes();eligible=[r['pair_id'] for r in rows];mutation(rows)
    with pytest.raises(ValueError):plan_control_folds(rows,eligible,[])

def test_missing_overlapping_or_duplicate_eligibility_ids_fail():
    rows=probes();ids=[r['pair_id'] for r in rows]
    for eligible,held in [(ids[:-1],[]),(ids,[ids[0]]),(ids+[ids[0]],[])]:
        with pytest.raises(ValueError):plan_control_folds(rows,eligible,held)
