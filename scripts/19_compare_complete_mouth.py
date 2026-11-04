"""Compare complete-mouth exclusion against frozen V2 on 80 development images."""
import csv
import importlib
import json
from pathlib import Path
import sys
import argparse
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion_experiment import exclude_complete_mouth


def select_fresh_ids(source, development_ids, count, seed):
    """Sample by stable ID, independent of metadata order and measurement values."""
    pool = sorted(k for k,r in source.items() if r['processing_status']=='success' and k not in development_ids)
    return random.Random(seed).sample(pool,count), len(pool)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh-sample', type=int, default=0,
                        help='Draw this many successes outside the 80 development IDs')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.fresh_sample < 0:
        parser.error('--fresh-sample must be nonnegative')
    common = importlib.import_module('16_compare_face_outline')
    prepare = importlib.import_module('11_prepare_training_manifests')
    check = importlib.import_module('15_prepare_fairface_mask_review')
    output = ROOT / ('outputs/complete_mouth_fresh30_seed42' if args.fresh_sample == 30 and args.seed == 42
                     else f'outputs/complete_mouth_fresh{args.fresh_sample}_seed{args.seed}' if args.fresh_sample
                     else 'outputs/complete_mouth_experiment_v1')
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing experiment')
    manifests = ROOT / 'data/manifests'
    paths = [manifests / name for name in ('fairface_candidate_processed_manifest.csv',
             'fairface_candidate_mask_quality_review.csv', 'fairface_random50_review_seed42.csv')]
    source = {r['image_id']: r for r in common.read(paths[0])}
    reviewed = {r['image_id']: r for r in common.read(paths[1]) if r['visual_review'] != 'pending'}
    reviewed.update({r['image_id']: r for r in common.read(paths[2])})
    development_ids = set(reviewed)
    pool_size = 0
    if args.fresh_sample:
        selected, pool_size = select_fresh_ids(source,development_ids,args.fresh_sample,args.seed)
        reviewed = {k: dict(visual_review='unreviewed') for k in selected}
    config = get_config()
    yunet, model = ROOT / config.FACE_MODEL_PATH, ROOT / config.FACE_LANDMARKER_MODEL_PATH
    inputs = paths + [yunet, model, ROOT/'src/skin_masking/landmark_exclusion.py', ROOT/'src/skin_masking/skin_mask.py',
                      ROOT/'src/skin_masking/mouth_exclusion_experiment.py']
    hashes = {str(p): check.digest(p) for p in inputs}
    (output/'grids').mkdir(parents=True)
    rows = []
    for i, (image_id, review) in enumerate(sorted(reviewed.items()), 1):
        row = dict(image_id=image_id, baseline_review={'deny':'reject'}.get(review['visual_review'].lower(),review['visual_review'].lower()),
                   experiment_status='blocked', experiment_visual_review='pending', experiment_review_notes='')
        try:
            stored = source[image_id]
            image = cv2.imread(stored['image_path'])
            if image is None:
                raise ValueError('Unreadable image')
            boxes = prepare._detect_face_boxes(image,yunet,.85)
            if len(boxes) != 1:
                raise ValueError('Single face required')
            x,y,w,h = boxes[0]
            crop = image[y:y+h,x:x+w].copy()
            baseline = prepare.compute_v2_skin_mask_with_margin(crop,image,boxes[0],model)
            if not baseline.landmarks_available:
                raise ValueError('V2 landmarks unavailable')
            before = compute_masked_lab_statistics(crop,baseline.mask,1000)
            before['skin_ratio_percent'] = round(np.count_nonzero(baseline.mask)/(w*h)*100,2)
            if stored['processing_status']=='success':
                differences = check.measurement_differences(stored,before)
                if differences:
                    raise ValueError('Baseline drift: '+','.join(differences))
            elif np.count_nonzero(baseline.mask) != int(float(stored['skin_pixels'])):
                raise ValueError('Excluded baseline mask changed')
            landmarks,_,_ = prepare.detect_landmarks_with_margin(image,boxes[0],model)
            if landmarks is None or not np.array_equal(build_feature_exclusion_mask(crop,landmarks),baseline.exclusion_mask):
                raise ValueError('Repeated landmark geometry differs')
            final,mouth = exclude_complete_mouth(baseline.mask,landmarks)
            after = compute_masked_lab_statistics(crop,final,1000)
            old_count, new_count = int(np.count_nonzero(baseline.mask)),int(np.count_nonzero(final))
            assert not np.any((final>0)&(baseline.mask==0))
            overlay=crop.copy()
            selected=mouth>0
            overlay[selected]=(.45*crop[selected]+.55*np.array([0,0,255])).astype(np.uint8)
            grid=np.vstack([np.hstack([common.panel(crop,'Original'),common.panel(overlay,'Complete mouth (red)')]),
                np.hstack([common.panel(cv2.cvtColor(baseline.mask,cv2.COLOR_GRAY2BGR),'V2 baseline'),
                           common.panel(cv2.cvtColor(final,cv2.COLOR_GRAY2BGR),'V2 + complete mouth')])])
            destination=output/'grids'/(image_id.replace('/','_')+'.png')
            if not cv2.imwrite(str(destination),grid):
                raise OSError(destination)
            row.update(experiment_status='compared',baseline_pixels=old_count,experiment_pixels=new_count,
                removed_pixels=old_count-new_count,retained_fraction=new_count/old_count if old_count else '',
                baseline_ita=before['ita_degrees'],experiment_ita=after['ita_degrees'],
                ita_delta=after['ita_degrees']-before['ita_degrees'] if after['valid'] and before['valid'] else '',
                experiment_ita_valid=after['valid'],experiment_ita_reason=after['reason'],
                lost_ita_validity=bool(before['valid'] and not after['valid']),
                comparison_grid=destination.relative_to(ROOT).as_posix())
        except Exception as error:
            row['error']=str(error)
        rows.append(row)
        if i%20==0:
            print(f'Compared {i}/{len(reviewed)}',flush=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (output/'comparison.csv').open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields); writer.writeheader(); writer.writerows(rows)
    assert all(check.digest(Path(p))==h for p,h in hashes.items())
    summary=dict(images=len(rows),compared=sum(r['experiment_status']=='compared' for r in rows),
        blocked=sum(r['experiment_status']=='blocked' for r in rows),
        changed=sum(r.get('removed_pixels',0)>0 for r in rows),
        lost_ita_validity=sum(r.get('lost_ita_validity',False) for r in rows),
        accepted_losing_validity=sum(r['baseline_review']=='accept' and r.get('lost_ita_validity',False) for r in rows),
        sampling_seed=args.seed if args.fresh_sample else None,
        sampling_pool_size=pool_size if args.fresh_sample else None,
        excluded_development_ids=sorted(development_ids) if args.fresh_sample else [],
        input_sha256=hashes,note='Fresh comparison sample outside 80 development IDs; not final thesis evaluation.' if args.fresh_sample
        else 'Development experiment; no face-outline restriction. Baseline unchanged.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
