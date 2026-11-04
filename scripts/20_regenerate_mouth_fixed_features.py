"""Regenerate the existing 650 candidates using explicit complete-mouth version.

Run from the project root. Preserves original manifests, selection, reviews
and raw images. No grouping, splitting, distortion or training is performed.
"""
import csv
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from src.utilities.config import get_config

VERSION='v2_complete_mouth_v1'


def main():
    common=importlib.import_module('16_compare_face_outline')
    prepare=importlib.import_module('11_prepare_training_manifests')
    checks=importlib.import_module('15_prepare_fairface_mask_review')
    source=ROOT/'data/manifests/fairface_candidate_processed_manifest.csv'
    output=ROOT/'data/manifests'/VERSION
    if output.exists():
        raise FileExistsError('Versioned output exists; refusing overwrite')
    records=common.read(source)
    ids=[r['image_id'] for r in records]
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate input IDs')
    config=get_config()
    yunet,model=ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH
    inputs=[source,yunet,model,ROOT/'src/skin_masking/mouth_exclusion.py',
            ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'src/skin_masking/skin_mask.py',
            ROOT/'src/skin_masking/landmark_exclusion.py']
    hashes={str(p):checks.digest(p) for p in inputs}
    output.mkdir()
    rows=[]
    for i,record in enumerate(records,1):
        result=prepare.process_record(record,dataset_name='FairFace',source_mst_label=None,
            source_label='',dataset_root=ROOT/'data/raw/FairFace',yunet_model=yunet,
            landmarker_model=model,minimum_skin_pixels=1000,score_threshold=.85,
            estimated_rule=None,mask_version=VERSION)
        result.update(mask_version=VERSION,visual_screening_status='not_revalidated_for_this_version',
            landmark_quality_flag='known_misplaced_geometry' if record['image_id']=='fairface__train/83184.jpg' else 'not_individually_validated')
        rows.append(result)
        if i%50==0:
            print(f'Regenerated {i}/{len(records)}',flush=True)
    assert set(r['image_id'] for r in rows)==set(ids)
    # Confirm production integration reproduces every already tested example.
    previous={}
    for folder in ('complete_mouth_experiment_v1','complete_mouth_fresh30_seed42'):
        path=ROOT/'outputs'/folder/'comparison.csv'
        previous.update({r['image_id']:r for r in common.read(path) if r['experiment_status']=='compared'})
    for row in rows:
        if row['image_id'] not in previous:
            continue
        expected=previous[row['image_id']]
        if int(float(row['skin_pixels']))!=int(expected['experiment_pixels']):
            raise ValueError('Integrated pixel count differs: '+row['image_id'])
        if expected['experiment_ita'] and abs(float(row['ita_degrees'])-float(expected['experiment_ita']))>.00005:
            raise ValueError('Integrated ITA differs: '+row['image_id'])
    destination=output/'fairface_candidate_processed_manifest.csv'
    with destination.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader();writer.writerows(rows)
    assert all(checks.digest(Path(p))==h for p,h in hashes.items())
    from collections import Counter
    summary=dict(mask_version=VERSION,images=len(rows),status_counts=dict(Counter(r['processing_status'] for r in rows)),
        exclusion_counts=dict(Counter(r['exclusion_reason'] for r in rows if r['processing_status']!='success')),
        experiment_reproduction_checks=len(previous),source_sha256=hashes,
        note='Computed candidate features only; no training eligibility or new visual acceptance implied.')
    (output/'provenance.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':
    main()
