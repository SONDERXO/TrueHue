"""Inner development folds over training sources/known duplicate groups only."""
from collections import defaultdict


def source_group_folds(rows):
    """Hold out each known duplicate group once; do not infer subject identity."""
    if not rows:raise ValueError('Training rows required')
    pair_ids=set();source_groups={};groups=defaultdict(list)
    for row in rows:
        if row.get('partition')!='train' or row.get('table_use')!='train':
            raise ValueError('Only eligible training rows may enter inner folds')
        pair=row.get('pair_id');source=row.get('source_image_id');group=row.get('duplicate_group_id')
        if not pair or not source or not group or pair in pair_ids:raise ValueError('Unique pairs and nonempty source/group IDs required')
        if source in source_groups and source_groups[source]!=group:raise ValueError('One source has inconsistent duplicate groups')
        pair_ids.add(pair);source_groups[source]=group;groups[group].append(row)
    if len(groups)<2:raise ValueError('At least two training groups required')
    folds=[]
    for index,group in enumerate(sorted(groups),1):
        validation=groups[group];training=[r for key,values in groups.items() if key!=group for r in values]
        train_sources={r['source_image_id'] for r in training};validation_sources={r['source_image_id'] for r in validation}
        if train_sources&validation_sources:raise ValueError('Source overlap across inner fold')
        folds.append(dict(fold_id=index,held_out_duplicate_group=group,
            train_source_ids=sorted(train_sources),inner_validation_source_ids=sorted(validation_sources),
            train_pair_ids=sorted(r['pair_id'] for r in training),inner_validation_pair_ids=sorted(r['pair_id'] for r in validation)))
    return folds
