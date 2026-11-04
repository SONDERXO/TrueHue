"""Freeze an exploratory support screen and audit every square development pair.

No thresholds are tuned, masks repaired, labels changed or learner fitted.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.evaluation.mask_support_quality import support_retention
from src.data_preparation.source_group_folds import source_group_folds


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def write(path,rows,fields):
    with path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def main():
    base=ROOT/'data/manifests/controlled_square256_v1'
    generated=ROOT/'outputs/controlled_square256_v1'
    output=ROOT/'outputs/square_mask_quality_v1'
    tables=ROOT/'data/manifests/square_mask_quality_v1'
    if output.exists() or tables.exists():raise FileExistsError('Screen outputs already exist')
    rows=read(base/'all_pairs_audit.csv')
    if len(rows)!=38:raise ValueError('Expected all38 attempted pairs')
    prior=json.loads((generated/'mask_quality_assessment.json').read_text())
    concerns={r['pair_id']:r for r in prior['pairs']}
    tracked=[*base.glob('*'),generated/'mask_quality_assessment.json',Path(__file__),
             ROOT/'src/evaluation/mask_support_quality.py',ROOT/'src/skin_masking/skin_mask.py',
             ROOT/'models/correction_prototype_v1/decision_tree.joblib']
    for row in rows:
        tracked += [ROOT/row['input_path'],ROOT/row['generation_mask_path'],
                    generated/'masks'/(row['pair_id']+'_estimation.png'),
                    generated/'masks'/(row['pair_id']+'_correction.png')]
    hashes={str(p):digest(p) for p in tracked if p.is_file()}
    output.mkdir(parents=True);tables.mkdir(parents=True)
    settings=dict(minimum_region_pixels=100,minimum_estimation_retention=.5,
                  minimum_correction_retention=.8)
    policy=dict(version='square_mask_quality_v1',**settings,
        status='Exploratory rule designed after reviewing development failures, frozen before batch scoring; not an independently validated cutoff.',
        reference='Synthetic generation region, not manually annotated true skin',
        screening='All38 attempts; whole region plus bounding-box quadrants with at least100 reference pixels',
        hold_policy='Any quantitative flag or existing Codex visual concern holds a training candidate. Historical excluded/stress/development roles unchanged.',
        restriction='Not a runtime gate or model feature. Do not use clean reference support at inference. No mask repair or retuning.',
        interpretation='Passing only means no major loss by this rule; no hair/paint correctness or final eligibility guarantee.')
    (tables/'screen_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    audit=[];screened=[];held=[]
    for row in rows:
        pair=row['pair_id']
        reference=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        estimation=cv2.imread(str(generated/'masks'/(pair+'_estimation.png')),0)>0
        correction=cv2.imread(str(generated/'masks'/(pair+'_correction.png')),0)>0
        result=support_retention(reference,estimation,correction,**settings)
        image=cv2.imread(str(ROOT/row['input_path']))
        hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        ycrcb=cv2.cvtColor(image,cv2.COLOR_BGR2YCrCb)
        pass_hsv=cv2.inRange(hsv,np.array([0,48,0],np.uint8),np.array([20,255,255],np.uint8))>0
        pass_ycrcb=cv2.inRange(ycrcb,np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))>0
        missing=reference&~estimation
        rejection=dict(missed_reference_pixels=int(missing.sum()),
                       rejected_hsv_only=int((missing&~pass_hsv&pass_ycrcb).sum()),
                       rejected_ycrcb_only=int((missing&pass_hsv&~pass_ycrcb).sum()),
                       rejected_both=int((missing&~pass_hsv&~pass_ycrcb).sum()),
                       passed_raw_but_missing=int((missing&pass_hsv&pass_ycrcb).sum()))
        assert sum(rejection[k] for k in rejection if k!='missed_reference_pixels')==rejection['missed_reference_pixels']
        concern=concerns[pair]['concern']
        hold=not result['screen_pass'] or bool(concern)
        status=('held_training_candidate' if hold else 'screen_pass_training_candidate') if row['table_use']=='train' else 'historical_role_preserved'
        record=dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],
                    historical_table_use=row['table_use'],status=status,
                    quantitative=result,existing_visual_concern=concern,threshold_diagnostic=rejection)
        audit.append(record)
        if row['table_use']=='train':
            (held if hold else screened).append(row)
        panel=image.copy();panel[reference&~correction]=np.rint(.4*panel[reference&~correction]+.6*np.array([0,0,255])).astype(np.uint8)
        panel[reference&correction]=np.rint(.5*panel[reference&correction]+.5*np.array([0,200,0])).astype(np.uint8)
        board=output/(pair+'_support_loss.png')
        if not cv2.imwrite(str(board),panel):raise OSError(board)
    fields=list(rows[0]);write(tables/'screen_pass_train.csv',screened,fields);write(tables/'held_train.csv',held,fields)
    folds=source_group_folds(screened) if len({r['duplicate_group_id'] for r in screened})>=2 else []
    (tables/'source_group_folds.json').write_text(json.dumps(dict(status='plans_only_no_fitting',folds=folds),indent=2),encoding='utf-8')
    assert len(screened)+len(held)==30
    assert hashes=={p:digest(p) for p in hashes},'Existing artifacts changed'
    summary=dict(status='complete',screened_pairs=len(audit),training_candidates=30,
                 screen_pass_training_candidates=len(screened),held_training_candidates=len(held),
                 variant_counts_before=dict(Counter(r['variant'] for r in rows if r['table_use']=='train')),
                 variant_counts_screen_pass=dict(Counter(r['variant'] for r in screened)),
                 training_sources_before=7,training_sources_screen_pass=len({r['source_image_id'] for r in screened}),
                 historical_role_counts=dict(Counter(r['table_use'] for r in rows)),
                 quantitative_flags_by_role={use:sum(not a['quantitative']['screen_pass'] for a in audit if a['historical_table_use']==use) for use in sorted({r['table_use'] for r in rows})},
                 input_sha256=hashes,pairs=audit,
                 warning='Screen selection conditions on robustness; compare coverage and disclose exclusions. No fairness or final evaluation claim; no model refit.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (output/'review-index.md').write_text('# Mask support retention screen\n\nGreen: retained generation support. Red: missed generation support. Reference is not true-skin annotation.\n\n'+'\n'.join(f'- [{r["pair_id"]} ({r["status"]})]({r["pair_id"]}_support_loss.png)' for r in audit),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['pairs','input_sha256']},indent=2))


if __name__=='__main__':main()
