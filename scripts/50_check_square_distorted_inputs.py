"""Compare existing saved development distortions at native and 256-square size.

This is resize-after-distortion robustness evidence, not a newly generated
256-resolution training table. No model fitting, predictions or target changes.
"""
import csv
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, image):
    if not cv2.imwrite(str(path), image):
        raise OSError(path)


def main():
    config = get_config()
    prepare = importlib.import_module('11_prepare_training_manifests')
    output = ROOT / 'outputs/square_distorted_inputs_v1'
    if output.exists():
        raise FileExistsError(output)
    manifest = ROOT / 'data/manifests/controlled_training_v2/all_pairs_audit.csv'
    with manifest.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 38 or len({r['pair_id'] for r in rows}) != 38:
        raise ValueError('Expected 38 unique existing attempts')
    tracked = [manifest, Path(__file__), ROOT/'scripts/11_prepare_training_manifests.py',
               ROOT/'src/skin_masking/skin_mask.py', ROOT/'src/skin_masking/mouth_exclusion.py',
               ROOT/'src/skin_masking/landmark_exclusion.py',
               ROOT/'src/ita_estimation/compute_ita.py',
               ROOT/config.FACE_MODEL_PATH, ROOT/config.FACE_LANDMARKER_MODEL_PATH,
               ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    tracked += [ROOT/r['input_path'] for r in rows]
    hashes = {str(p): digest(p) for p in tracked}
    output.mkdir(parents=True)
    (output/'run-status.json').write_text('{"status":"running"}', encoding='utf-8')
    measurements = []
    boards = {}

    def measure(image, stem):
        boxes = prepare._detect_face_boxes(image, ROOT/config.FACE_MODEL_PATH, .85)
        record = dict(width=image.shape[1], height=image.shape[0], face_count=len(boxes),
                      face_boxes=[[int(v) for v in box] for box in boxes])
        mask = np.zeros(image.shape[:2], np.uint8)
        if len(boxes) != 1:
            record['status'] = 'expected_single_face'
        else:
            x,y,w,h = boxes[0]
            crop = image[y:y+h,x:x+w].copy()
            result = prepare.compute_versioned_skin_mask(crop,image,boxes[0],
                ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
            mask[y:y+h,x:x+w] = result.mask
            record.update(compute_masked_lab_statistics(crop,result.mask,1000))
            record['landmarks_available'] = bool(result.landmarks_available)
            record['status'] = ('landmarks_unavailable' if not result.landmarks_available
                                else 'success' if record['valid'] else record['reason'])
            record['skin_fraction_of_image'] = float(np.count_nonzero(mask)/mask.size)
        save(output/f'{stem}_mask.png',mask)
        return record,mask

    feature_columns = {'mean_l_star':'input_mean_l_star','mean_a_star':'input_mean_a_star',
                       'mean_b_star':'input_mean_b_star','ita_degrees':'input_ita_degrees'}
    for row in rows:
        pair = row['pair_id']
        native_image = cv2.imread(str(ROOT/row['input_path']))
        if native_image is None:
            raise ValueError(row['input_path'])
        square_image = cv2.resize(native_image,(config.IMAGE_SIZE,config.IMAGE_SIZE),
                                  interpolation=cv2.INTER_LINEAR)
        native,native_mask = measure(native_image,pair+'_native')
        square,square_mask = measure(square_image,pair+'_square')
        save(output/f'{pair}_square_input.png',square_image)
        mapped = cv2.resize(native_mask,(config.IMAGE_SIZE,config.IMAGE_SIZE),
                             interpolation=cv2.INTER_NEAREST)>0
        union = np.count_nonzero(mapped | (square_mask>0))
        entry = dict(pair_id=pair,source_image_id=row['source_image_id'],
                     partition=row['partition'],historical_table_use=row['table_use'],
                     historical_status=row['input_processing_status'],variant=row['variant'],
                     clipped_pixel_count=int(row['clipped_pixel_count']),native=native,square=square,
                     mask_agreement_iou=float(np.count_nonzero(mapped & (square_mask>0))/union) if union else None)
        if native['status']=='success':
            deltas = {key:native[key]-float(row[col]) for key,col in feature_columns.items()}
            entry['native_minus_stored']=deltas
            if max(abs(v) for v in deltas.values()) > .00011:
                raise ValueError('Native feature reproduction failed: '+pair)
        if native['status']==square['status']=='success':
            entry['square_minus_native']={key:square[key]-native[key] for key in feature_columns}
        panels=[]
        for label,image,mask in [('native',native_image,native_mask),('256',square_image,square_mask)]:
            overlay=image.copy()
            overlay[mask>0]=np.rint(.55*overlay[mask>0]+.45*np.array([0,220,0])).astype(np.uint8)
            panel=cv2.resize(overlay,(256,256))
            panel=cv2.copyMakeBorder(panel,34,0,0,0,cv2.BORDER_CONSTANT)
            status=native['status'] if label=='native' else square['status']
            cv2.putText(panel,f"{row['variant']} {label}: {status}",(3,20),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
            panels.append(panel)
        boards.setdefault(row['source_image_id'],[]).append(np.hstack(panels))
        measurements.append(entry)
        # Incremental machine-readable records preserve progress on interruption.
        with (output/'attempts.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(entry)+'\n')
        print(f"{pair}: {native['status']} -> {square['status']}",flush=True)
    groups={}
    for use in sorted({r['historical_table_use'] for r in measurements}):
        cohort=[r for r in measurements if r['historical_table_use']==use]
        groups[use]=dict(attempts=len(cohort),
                        native=dict(Counter(r['native']['status'] for r in cohort)),
                        square=dict(Counter(r['square']['status'] for r in cohort)))
    report=dict(status='complete',attempts=len(measurements),groups=groups,
                measurements=measurements,input_sha256=hashes,
                interpolation='INTER_LINEAR',minimum_skin_pixels=1000,detection_threshold=.85,
                warning='Resize after existing distortion; not resize before generation. Agreement is not accuracy. No eligibility or target changes.')
    assert hashes=={str(p):digest(p) for p in tracked},'Inputs changed'
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    links=[]
    for source,panels in boards.items():
        name=source.replace('/','_')+'_comparison.png'
        save(output/name,np.vstack(panels))
        links.append(f'- [{source}]({name})')
    (output/'review-index.md').write_text('# Distorted input resolution check\n\nEstimation masks only; historical partitions unchanged.\n\n'+'\n'.join(links),encoding='utf-8')
    (output/'run-status.json').write_text('{"status":"complete"}',encoding='utf-8')
    print(json.dumps(groups,indent=2))


if __name__=='__main__':
    main()
