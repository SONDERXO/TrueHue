"""Verify saved revision/folds and export a compact coverage/readiness report."""
import csv
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.utilities.config import get_config
from src.evaluation.correction_prototype import apply_correction,model_arrays
import importlib


def main():
    api=importlib.import_module('39_correct_image');helper=importlib.import_module('29_compare_correction_boundaries')
    config=get_config();tables=ROOT/'data/manifests/controlled_training_v2';out=ROOT/config.OUTPUTS_ROOT/'controlled_training_v2'
    if (out/'readiness_checks.json').exists():raise FileExistsError('Readiness report already exists')
    summary=json.loads((tables/'schema_and_summary.json').read_text());rows=helper.read(tables/'train.csv')
    augmentation=helper.read(tables/'augmentation_attempts.csv');folds=json.loads((tables/'source_group_folds.json').read_text())['folds']
    assert all(api.digest(Path(p))==value for p,value in summary['input_sha256'].items())
    assert all(api.digest(tables/name)==value for name,value in summary['output_table_sha256'].items())
    x,y=model_arrays(rows);assert x.shape==(30,4) and y.shape==(30,3)
    all_ids={r['pair_id'] for r in rows};all_sources={r['source_image_id'] for r in rows}
    validation_ids=[]
    for fold in folds:
        a=set(fold['train_pair_ids']);b=set(fold['inner_validation_pair_ids'])
        assert not a&b and a|b==all_ids
        assert not set(fold['train_source_ids'])&set(fold['inner_validation_source_ids'])
        assert set(fold['train_source_ids'])|set(fold['inner_validation_source_ids'])==all_sources
        validation_ids+=fold['inner_validation_pair_ids']
    assert len(validation_ids)==len(all_ids) and set(validation_ids)==all_ids
    quantization=[]
    for row in augmentation:
        reference=cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
        saved=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        np.testing.assert_array_equal(saved[~mask],reference[~mask])
        if row['variant']=='identity_control':np.testing.assert_array_equal(saved,reference)
        else:
            assert (saved[mask]>=reference[mask]).all() and (saved[mask]>reference[mask]).any()
        targets=[float(row[k]) for k in ('target_gamma','target_red_gain','target_blue_gain')]
        reconstructed=apply_correction(saved,mask,targets)
        max_error=int(np.abs(reconstructed.astype(int)-reference.astype(int)).max())
        assert max_error<=1
        quantization.append(dict(pair_id=row['pair_id'],max_source_oracle_channel_error_uint8=max_error))
    old=ROOT/'data/manifests/controlled_training_v1'
    for name in ('development_validation.csv','clipped_stress.csv','excluded_pairs.csv'):assert api.digest(old/name)==api.digest(tables/name)
    # Carry the historical mask concern into the review pack without changing rows.
    old_rows={r['pair_id']:r for r in helper.read(old/'train.csv')}
    prior=[r for r in helper.read(ROOT/config.OUTPUTS_ROOT/'mask_parameter_diagnosis_v1/image_metrics.csv') if r['table_use']=='train' and r['method']=='known_current_mask']
    history=[dict(pair_id=r['pair_id'],source_image_id=old_rows[r['pair_id']]['source_image_id'],
        known_current_color_residual=r['ciede2000_source_mask'],missed_source_pixels=r['missed_source_pixels'],
        context='Historical v1 pair diagnostic, not a new augmentation mask-quality label') for r in prior]
    with (out/'prior_mask_diagnostics.csv').open('x',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,list(history[0]));writer.writeheader();writer.writerows(history)
    names=('dark','color_shift','bright_warm','mild_bright_exposure','identity_control')
    old_counts=[sum(r['variant']==name for r in old_rows.values()) for name in names]
    new_counts=[sum(r['variant']==name for r in rows) for name in names]
    fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained');positions=np.arange(5)
    bars1=ax.bar(positions-.18,old_counts,.36,label='Original training table',color='#8093a4')
    bars2=ax.bar(positions+.18,new_counts,.36,label='Revised training table',color='#2c8b76')
    ax.bar_label(bars1,padding=3);ax.bar_label(bars2,padding=3)
    ax.set_xticks(positions,('Darkened','Color shift','Bright/warm','Mild brightening','Unchanged control'))
    ax.set_ylim(0,9);ax.set_ylabel('Eligible training pairs');ax.set_title('30 training pairs from the same seven sources')
    ax.legend(frameon=False,loc='upper right');ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.savefig(out/'training_coverage.png',dpi=150);fig.savefig(out/'training_coverage.svg');plt.close(fig)
    report=dict(training_rows=30,feature_shape=list(x.shape),target_shape=list(y.shape),source_groups=7,
        augmentation_inputs_checked=len(augmentation),zero_introduced_clipping=True,unchanged_controls_exact=True,
        source_oracle_max_channel_errors=quantization,folds_source_disjoint=True,every_training_pair_inner_held_once=True,
        frozen_tables_byte_identical=True,old_input_hashes_unchanged=True,
        human_review_status='No new human approval assigned; prior mask failures remain explicit',
        learner_status='No model fitted or selected. Frozen runtime calls only check pipeline availability; no learned-score improvement claimed.')
    (out/'readiness_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    index=['# Exposure and identity revision','',
        'Two rows per source: unchanged control, then mild brightening. Columns: source / saved input / current correction-mask overlay.',
        '','No learned correction images or new model results are shown. Mask overlays are pipeline checks, not new human acceptance labels.','']
    for path in sorted((out/'review_boards').glob('*.png')):index.append('- ['+path.stem.replace('__augmentation','')+'](review_boards/'+path.name+')')
    index += ['', '[Training coverage](training_coverage.png)',
        '', 'Historical mask-limited cases remain in `prior_mask_diagnostics.csv`; data augmentation does not fix those masks.']
    (out/'review-index.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
    print('Verified 30 rows,14 saved inputs,7 source-disjoint folds,unchanged held-out tables; exported coverage/readiness report.')


if __name__=='__main__':main()
