"""Freeze public expected image/annotation roster without accessing image files."""
from pathlib import Path,PurePosixPath
import sys,json,csv,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portrait_exposure_quality import ranking_pairs

OUT=ROOT/'outputs/piq23_expected_admission_v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def csv_rows(p):
    with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    prior=ROOT/'outputs/portrait_exposure_prior_review_v1';prep=ROOT/'outputs/portrait_exposure_stage_preparation_v1'
    verification=read(prep/'verification.json');assert verification['joined_exposure_rows']==5116
    receipt=next(x for x in read(prior/'annotation_feasibility.json')['cache_files'] if x['file']=='Scores_Exposure.csv')
    sources={str((prior/'Scores_Exposure.csv').relative_to(ROOT)):receipt['sha256']}
    for x in verification['cache_sources']:sources[str((prep/x['file']).relative_to(ROOT))]=x['sha256']
    for p,h in sources.items():assert sha(ROOT/p)==h,p
    scores=csv_rows(prior/'Scores_Exposure.csv');split=csv_rows(prep/'Scene_Split.csv');metadata=csv_rows(prep/'Image_Metadata.csv')
    partitions={r['SCENE']:r['SPLIT'] for r in split};devices={r['Image']:r['Device'] for r in metadata}
    assert len(devices)==len(metadata) and len(partitions)==len(split)==50
    expected=[]
    for r in sorted(scores,key=lambda r:r['IMAGE']):
        relative=PurePosixPath(r['IMAGE PATH'].replace('\\','/'))
        assert not relative.is_absolute() and '..' not in relative.parts and relative.parts[0]=='Exposure'
        assert relative.name==r['IMAGE'] and len(relative.parts)==2
        assert r['IMAGE'] in devices and r['SCENE'] in partitions
        expected.append(dict(id=r['IMAGE'],image_relative_path=str(relative),scene=r['SCENE'],scene_index=int(r['SCENE IDX']),
            device=devices[r['IMAGE']],partition=partitions[r['SCENE']],low=float(r['CI LOW']),score=float(r['JOD']),high=float(r['CI HIGH']),
            generated_fixture=False,admitted_for_experiment=False,image_sha256=None,feature_sha256=None,provided_MST=None))
    assert len({r['id'] for r in expected})==len({r['image_relative_path'] for r in expected})==5116
    pair_counts={};scene_counts={}
    for partition in ['Train','Test']:
        rows=[r for r in expected if r['partition']==partition]
        pairs=ranking_pairs(rows)
        pairs.sort(key=lambda p:(rows[p[0]]['id'],rows[p[1]]['id']))
        pair_counts[partition]=len(pairs)
        scene_counts[partition]=dict(Counter(rows[i]['scene'] for i,j in pairs))
    assert pair_counts=={'Train':71178,'Test':27981}
    assert len(scene_counts['Train'])==35 and len(scene_counts['Test'])==15
    OUT.mkdir();path=OUT/'expected_roster.json';path.write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
    report=dict(status='EXPECTED_PUBLIC_ROSTER_ONLY_NOT_IMAGE_ADMISSION',images=5116,
        partitions=dict(Counter(r['partition'] for r in expected)),scene_counts={'Train':35,'Test':15},
        derived_pair_counts=pair_counts,pairs_per_scene=scene_counts,roster_sha256=sha(path),source_sha256=sources,
        all_pixel_feature_hashes_pending=True,admitted_images=0,image_files_accessed=0,head_fits=0,
        person_separation='UNKNOWN_PUBLIC_METADATA_DEVICE_ONLY',tone_labels='NOT_SUPPLIED_NOT_INFERRED',
        code_sha256=sha(Path(__file__)))
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in report.items() if k not in ['pairs_per_scene','source_sha256']})


if __name__=='__main__':main()
