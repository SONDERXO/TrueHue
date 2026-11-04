"""Verify saved square pairs against references, transforms, masks and folds."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS
from src.data_preparation.source_group_folds import source_group_folds


def main():
    base=ROOT/'data/manifests/controlled_square256_v1'
    out=ROOT/'outputs/controlled_square256_v1'
    result_path=out/'readiness_checks.json'
    if result_path.exists():raise FileExistsError(result_path)
    summary=json.loads((base/'schema_and_summary.json').read_text())
    with (base/'all_pairs_audit.csv').open(encoding='utf-8',newline='') as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==38 and len({r['pair_id'] for r in rows})==38
    checks={r['pair_id']:r for r in summary['pair_checks']}
    inverse_errors=[]
    for row in rows:
        image=cv2.imread(str(ROOT/row['input_path']))
        reference=cv2.imread(str(ROOT/row['reference_path']))
        source=cv2.imread(row['source_path'])
        assert image.shape==reference.shape==(256,256,3)
        np.testing.assert_array_equal(reference,cv2.resize(source,(256,256),interpolation=cv2.INTER_LINEAR))
        mask=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        assert mask.shape==(256,256) and mask.sum()==int(row['generation_skin_pixels'])
        rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB)
        params={k:float(row['distortion_'+k]) for k in ['gamma','red_gain','blue_gain']}
        target=inverse_parameters(**params)
        np.testing.assert_allclose([float(row[k]) for k in TARGETS],list(target.values()),atol=1e-12,rtol=0)
        raw=transform_rgb(rgb.astype(float)/255,**params,clip=False)
        clipping=int((mask & ((raw<0)|(raw>1)).any(axis=2)).sum())
        assert clipping==int(row['clipped_pixel_count'])
        generated=rgb.astype(float)/255;generated[mask]=np.clip(raw[mask],0,1)
        encoded=np.rint(generated*255).astype(np.uint8)
        np.testing.assert_array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),encoded)
        np.testing.assert_array_equal(encoded[~mask],rgb[~mask])
        if row['variant']=='identity_control':np.testing.assert_array_equal(encoded,rgb)
        stem=out/'masks'/row['pair_id']
        estimate=cv2.imread(str(stem)+'_estimation.png',0)
        correction=cv2.imread(str(stem)+'_correction.png',0)
        assert estimate.shape==correction.shape==(256,256)
        assert np.count_nonzero(correction)==checks[row['pair_id']]['correction_pixels']
        statistics=compute_masked_lab_statistics(image,estimate,1000)
        if row['input_processing_status']=='success':
            assert statistics['valid']
            np.testing.assert_allclose([statistics[k] for k in FEATURE_KEYS],[float(row[k]) for k in FEATURES],atol=.00001,rtol=0)
        else:assert all(row[k]=='' for k in FEATURES)
        if row['table_use']=='train':assert row['partition']=='train' and clipping==0
        if row['historical_table_use']=='stress_only':assert row['table_use'] in ['stress_only','excluded']
        if row['historical_table_use']=='excluded':assert row['table_use']=='excluded'
        oracle=encoded.astype(float)/255;oracle[mask]=transform_rgb(oracle,**target)[mask]
        error=int(np.abs(np.rint(oracle*255).astype(int)-rgb.astype(int))[mask].max())
        assert error==checks[row['pair_id']]['source_mask_inverse_max_channel_error']
        if not clipping:inverse_errors.append(error)
    train=[r for r in rows if r['table_use']=='train']
    saved=json.loads((base/'source_group_folds.json').read_text())['folds']
    assert saved==source_group_folds(train)
    assert sorted(pair for f in saved for pair in f['inner_validation_pair_ids'])==sorted(r['pair_id'] for r in train)
    for filename,expected in summary['input_sha256'].items():assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==expected
    for filename,expected in summary['output_table_sha256'].items():assert hashlib.sha256((base/filename).read_bytes()).hexdigest()==expected
    report=dict(status='passed',pairs_checked=len(rows),training_matrix_shape=[len(train),len(FEATURES)],
        targets_shape=[len(train),len(TARGETS)],folds_checked=len(saved),
        unclipped_inverse_max_channel_error=max(inverse_errors),
        note='Transform/storage/features/fold checks only; masks not human approved, no learned performance.')
    result_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
