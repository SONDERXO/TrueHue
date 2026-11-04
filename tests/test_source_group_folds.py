import pytest
from src.data_preparation.source_group_folds import source_group_folds


def row(pair,source,group):
    return dict(pair_id=pair,source_image_id=source,duplicate_group_id=group,partition='train',table_use='train')


def test_variants_and_known_duplicate_sources_never_split_across_inner_folds():
    rows=[row('a1','a','shared'),row('a2','a','shared'),row('b1','b','shared'),row('c1','c','other')]
    folds=source_group_folds(rows)
    assert len(folds)==2
    assert sorted(p for f in folds for p in f['inner_validation_pair_ids'])==['a1','a2','b1','c1']
    for fold in folds:
        assert not set(fold['train_source_ids'])&set(fold['inner_validation_source_ids'])
        assert not set(fold['train_pair_ids'])&set(fold['inner_validation_pair_ids'])
        assert ('a' in fold['inner_validation_source_ids'])==('b' in fold['inner_validation_source_ids'])


@pytest.mark.parametrize('use',['development_validation','stress_only','excluded'])
def test_nontraining_rows_cannot_enter_folds(use):
    rows=[row('a','a','a'),row('b','b','b')];rows[1]['table_use']=use
    with pytest.raises(ValueError,match='training'):source_group_folds(rows)


def test_duplicate_pairs_and_inconsistent_source_groups_fail():
    for rows in ([row('a','a','a'),row('a','b','b')],[row('a1','a','a'),row('a2','a','b')]):
        with pytest.raises(ValueError):source_group_folds(rows)
