"""Fixed66 comparison helpers. Import performs no scientific IO or fit."""
from pathlib import Path
import math,shutil
import numpy as np
from .blue_axis_preparation import read,write,sha
from .blue_axis_training import join60,fit_once
from .blue_axis_verification import verify
from .joint_colour_workflow import seal_support,after_fit_barrier
from .gap_source_held_workflow import score_context,aggregate

FAMILIES=['exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']

def fitting_rows(plan,fold,records):
    bindings=[dict(case_id=r['case_id'],source=r['source'],role=r['role'],nominal_controls=r['y']) for r in records if r['case_id'] in fold['fitting_cases']]
    return join60(dict(cases=bindings,first_fitting_cases=fold['fitting_cases'],first_excluded_source=fold['held_publisher_group']),records)

def fit_all(out,plan,records,reuse,*,fit=fit_once):
    out=Path(out);reuse=Path(reuse);models=[]
    for i,fold in enumerate(plan['folds']):
        rows=fitting_rows(plan,fold,records);folder=out/fold['held_publisher_group']
        if i==0:
            assert fold['held_publisher_group']==plan['reuse']['held_source'] and sha(reuse/'candidate_PRIVATE.json')==plan['reuse']['sha256']
            assert read(reuse/'fitting_inputs_PRIVATE.json')==rows
            folder.mkdir()
            for n in ['candidate_PRIVATE.json','fitting_inputs_PRIVATE.json','training_replay_PRIVATE.json']:shutil.copyfile(reuse/n,folder/n)
        else:fit(folder,rows,plan['feature_names'],dict(protocol_id=plan['protocol_id'],fold=fold))
        checked=verify(read(folder/'candidate_PRIVATE.json'),rows,read(folder/'training_replay_PRIVATE.json'),plan['feature_names'],fold['held_publisher_group'])
        write(folder/'fitting_verification_PRIVATE.json',checked)
        models.append(dict(definition=fold,directory=folder.name,reused=i==0,candidate_sha256=sha(folder/'candidate_PRIVATE.json')))
        write(out/'models_PRIVATE.json',models)
    write(out/'all_fits_verified_PRIVATE.json',dict(passed=True,folds=len(models),new_fits=len(models)-1,reused_fits=1))
    return models

def numerical_gate(predictions):
    if len(predictions)!=66 or len({p['case_id'] for p in predictions})!=66:raise ValueError('Complete66 required')
    stats=aggregate(predictions,'primary')
    if set(stats)!=set(['identity']+FAMILIES):raise ValueError('Six roles required')
    for role in stats:
        own=[p for p in predictions if p['role']==role]
        if len(own)!=11 or len({p['source'] for p in own})!=11:raise ValueError('Eleven sources per role required')
        for p in own:
            m=p['primary']
            if not m['protected_unchanged'] or not m['zero_alpha_unchanged']:raise ValueError('Protection failed')
            if any(not math.isfinite(m[a][b]) or m[a][b]<0 for a in ['input','output'] for b in ['DE','RGB']):raise ValueError('Finite metrics required')
    return stats,all(stats[r]['source_equal_DE_improvement']>0 for r in FAMILIES)

def load_case(path,declared,support):
    path=Path(path)
    assert path.resolve()==Path(declared['path']).resolve() and sha(path)==declared['sha256']
    with np.load(path,allow_pickle=False) as pack:
        image=pack['input_rgb8'];reference=pack['reference_rgb8']
        if declared['new_blue_pack']:assert set(pack.files)=={'input_rgb8','reference_rgb8'}
        else:assert np.array_equal(pack['protected'],support['old_protected'])
    assert image.dtype==reference.dtype==np.uint8 and image.shape==reference.shape==(256,256,3)
    return image,reference
