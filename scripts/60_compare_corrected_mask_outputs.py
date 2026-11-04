"""Frozen-model application-mask comparison on all38 square development attempts.

Recompute baseline input features once; predict once; reuse those parameters
for every mask. No fitting, target/oracle parameters or held-case promotion.
"""
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(path):
    with path.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def save(path,image_rgb):
    if not cv2.imwrite(str(path),cv2.cvtColor(image_rgb,cv2.COLOR_RGB2BGR)):raise OSError(path)


def main():
    config=get_config();output=ROOT/'outputs/corrected_mask_comparison_v1'
    if output.exists():raise FileExistsError(output)
    source=ROOT/'data/manifests/controlled_square256_v1/all_pairs_audit.csv'
    rows=read(source)
    if len(rows)!=38:raise ValueError('Expected all38 attempted pairs')
    generation=ROOT/'outputs/hair_clean_generation_v1'
    ycb=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    additions=ROOT/'outputs/additions_only_boundary_v1'
    ablation=json.loads((ycb/'summary.json').read_text())
    original={r['pair_id']:r for r in ablation['square_pairs']}
    model_path=ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH
    metadata_path=model_path.with_name('metadata.json');metadata=json.loads(metadata_path.read_text())
    if digest(model_path)!=metadata['model_sha256']:raise ValueError('Model checksum mismatch')
    if tuple(metadata['feature_columns'])!=FEATURES or tuple(metadata['target_columns'])!=TARGETS:raise ValueError('Schema mismatch')
    model=load_model(str(model_path))
    mask_policies={'original':(ycb,'_baseline_support.png'),
                   'unrestricted_ycrcb':(ycb,'_ycrcb_support.png'),
                   'additions_boundary':(additions,'_support.png')}
    tracked=[Path(__file__),source,model_path,metadata_path,ycb/'summary.json',additions/'summary.json',
             ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/ita_estimation/compute_ita.py',
             ROOT/'src/distortion_generation/generate_distortions.py',
             ROOT/'data/manifests/square_mask_quality_v1/screen_pass_train.csv',
             ROOT/'data/manifests/square_mask_quality_v1/held_train.csv',
             ROOT/'data/manifests/material_review_v1/material_review_labels.json']
    for row in rows:
        pair=row['pair_id'];stem=row['source_image_id'].replace('/','_')
        tracked += [generation/(pair+'_input.png'),generation/(stem+'_generation_mask.png'),
                    ROOT/row['reference_path'],ycb/(pair+'_baseline_estimate.png')]
        tracked += [folder/(pair+suffix) for folder,suffix in mask_policies.values()]
    hashes={str(p):digest(p) for p in tracked}
    output.mkdir(parents=True);(output/'images').mkdir();(output/'review_boards').mkdir()
    status=output/'run_status.json';status.write_text('{"state":"running"}',encoding='utf-8')
    policy=dict(status='Fixed development comparison only',model_sha256=metadata['model_sha256'],
        parameters='One prediction from four recomputed original HSV/YCrCb input features, reused identically for all3 masks',
        methods=['no_correction',*mask_policies],scoring='Same hair-clean generation region and resized source reference for every method',
        source_roles='All38attempts, including held training candidates; no filtering by quality screen, no final-test use',
        warning='Frozen model trained on tiny224pilot, now used for diagnostic256inputs. Not retrained,selected or validated for deployment.')
    (output/'comparison_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    attempts=[];metrics=[];boards=defaultdict(list)
    try:
        for row in rows:
            pair=row['pair_id'];stem=row['source_image_id'].replace('/','_')
            bgr=cv2.imread(str(generation/(pair+'_input.png')))
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            scoring=cv2.imread(str(generation/(stem+'_generation_mask.png')),0)>0
            estimate=cv2.imread(str(ycb/(pair+'_baseline_estimate.png')),0)
            statistics=compute_masked_lab_statistics(bgr,estimate,1000)
            record=dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],historical_table_use=row['table_use'],
                        source_partition=row['partition'],mask_application_status='excluded',reason='')
            if not statistics['valid'] or original[pair]['methods']['baseline']['status']!='success':
                record['reason']=statistics['reason']
                record['baseline_status']=original[pair]['methods']['baseline']['status']
                attempts.append(record)
                with (output/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
                continue
            values=np.asarray([statistics[key] for key in FEATURE_KEYS],float)
            np.testing.assert_allclose(values,[original[pair]['methods']['baseline'][key] for key in FEATURE_KEYS],atol=.00001,rtol=0)
            if not np.isfinite(values).all():raise ValueError('Nonfinite baseline features')
            predicted=np.asarray(model.predict(values[None,:]),float)
            if predicted.shape!=(1,3) or not np.isfinite(predicted).all() or np.any(predicted<=0):raise ValueError('Invalid prediction')
            parameters=predicted[0]
            record.update(mask_application_status='success',features=dict(zip(FEATURES,map(float,values))),
                          parameters=dict(zip(TARGETS,map(float,parameters))))
            masks={name:cv2.imread(str(folder/(pair+suffix)),0)>0 for name,(folder,suffix) in mask_policies.items()}
            assert not np.any(masks['original']&~masks['additions_boundary'])
            outputs={'no_correction':rgb}
            for method,mask in masks.items():
                corrected=apply_correction(rgb,mask,parameters)
                np.testing.assert_array_equal(corrected[~mask],rgb[~mask])
                save(output/'images'/(pair+'_'+method+'.png'),corrected)
                outputs[method]=corrected
            for method,corrected in outputs.items():
                error=image_errors(reference,corrected,scoring)
                metric=dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],historical_table_use=row['table_use'],method=method,**error,
                    changed_pixels=int(np.any(corrected!=rgb,axis=2).sum()),
                    changed_pixels_outside_generation=int((np.any(corrected!=rgb,axis=2)&~scoring).sum()))
                metrics.append(metric)
            panels=[]
            for label,image in [('Input',rgb),('Original mask',outputs['original']),('Additions boundary',outputs['additions_boundary']),('Source reference',reference)]:
                panel=cv2.copyMakeBorder(image,34,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,row['variant']+' '+label,(3,14),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
                cv2.putText(panel,row['table_use'],(3,29),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
                panels.append(panel)
            boards[row['source_image_id']].append(np.hstack(panels));attempts.append(record)
            with (output/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
            print(pair,flush=True)
        groups={}
        for role in ['train','development_validation','stress_only']:
            groups[role]={}
            for method in ['no_correction',*mask_policies]:
                cohort=[r for r in metrics if r['historical_table_use']==role and r['method']==method]
                groups[role][method]=dict(pairs=len(cohort),sources=len({r['source_image_id'] for r in cohort}),
                    mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in cohort])) if cohort else None,
                    mean_rgb_mae_source=float(np.mean([r['rgb_mae_source_mask'] for r in cohort])) if cohort else None,
                    mean_rgb_mae_outside=float(np.mean([r['rgb_mae_outside_source_mask'] for r in cohort])) if cohort else None)
        variants={}
        for variant in sorted({r['variant'] for r in metrics if r['historical_table_use']=='train'}):
            variants[variant]={method:dict(pairs=len(cohort),mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in cohort])))
                for method in ['no_correction',*mask_policies]
                if (cohort:=[r for r in metrics if r['historical_table_use']=='train' and r['variant']==variant and r['method']==method])}
        assert len(attempts)==38
        assert hashes=={p:digest(p) for p in hashes},'Tracked input changed'
        summary=dict(status='complete',attempted_pairs=38,status_counts=dict(Counter(r['mask_application_status'] for r in attempts)),
            groups=groups,training_variants=variants,attempts=attempts,metrics=metrics,input_sha256=hashes,
            warning=policy['warning'],evaluation_note='Relative synthetic reconstruction, selected development sources, not final fairness/clinical skin-color truth.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        with (output/'metrics.csv').open('x',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,list(metrics[0]));writer.writeheader();writer.writerows(metrics)
        links=[]
        for source,panels in boards.items():
            filename=source.replace('/','_')+'_corrected.png';save(output/'review_boards'/filename,np.vstack(panels));links.append(f'- [{source}](review_boards/{filename})')
        (output/'review-index.md').write_text('# Corrected images: original versus additions boundary\n\nIdentical frozen-model parameters for both masks; reference is a reconstruction target.\n\n'+'\n'.join(links),encoding='utf-8')
        status.write_text('{"state":"complete"}',encoding='utf-8')
        print(json.dumps(dict(counts=summary['status_counts'],groups=groups,training_variants=variants),indent=2))
    except Exception as error:
        status.write_text(json.dumps(dict(state='failed',error=str(error),attempts_completed=len(attempts))),encoding='utf-8');raise


if __name__=='__main__':main()
