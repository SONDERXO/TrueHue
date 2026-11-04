from src.data_preparation.source_partition import connected_groups,allocate_group,classify_pair


def test_duplicate_groups_are_transitive_and_order_independent():
    assert connected_groups(['c','b','a','d'],[('a','b'),('b','c')])==[['a','b','c'],['d']]


def test_original_validation_and_exposed_sources_never_become_training_or_final_test():
    splits={'a':'validation','b':'validation'}
    assert allocate_group(['a','b'],splits,set())=='reserved_test'
    assert allocate_group(['a','b'],splits,{'b'})=='development_validation'
    assert allocate_group(['a','b'],{'a':'train','b':'validation'},set())=='quarantine_cross_source_split'


def test_train_allocation_stable_and_no_test_from_original_train():
    a=allocate_group(['a','b'],{'a':'train','b':'train'},set())
    assert a==allocate_group(['b','a'],{'a':'train','b':'train'},{'a'})
    assert a in {'train','development_validation'}


def test_failure_handling_preserves_priority_and_clipped_stress_cases():
    assert classify_pair('excluded',5)=='excluded_input_pipeline_failure'
    assert classify_pair('success',5)=='stress_only_clipped'
    assert classify_pair('success',0)=='technical_candidate'
