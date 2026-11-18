"""Read-only local release audit; private per-subject records stay in ignored outputs."""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import zlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PIL import Image
from src.data_preparation.stellenbosch_metadata import parse_mst_value

OUT=ROOT/'outputs/stellenbosch_received_data_v1'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path);parser.add_argument('--archive',required=True,type=Path)
    args=parser.parse_args();data=args.root.resolve();archive=args.archive.resolve()
    if OUT.exists():raise FileExistsError(OUT)
    if not data.is_dir() or not archive.is_file():raise ValueError('Existing extraction and archive required')
    source_hashes={str(p):sha(p) for p in [Path(__file__),ROOT/'src/data_preparation/stellenbosch_metadata.py',
        ROOT/'tests/test_stellenbosch_metadata.py',ROOT/'docs/stellenbosch-received-data-protocol-2026-11-05.md']}
    archive_before=sha(archive);folders=sorted([p for p in data.iterdir() if p.is_dir()],key=lambda p:int(p.name))
    allfiles=sorted(p for p in data.rglob('*') if p.is_file())
    start_inventory={p.relative_to(data).as_posix():(p.stat().st_size,p.stat().st_mtime_ns) for p in allfiles}
    OUT.mkdir()
    write(OUT/'protocol.json',dict(dataset_location=str(data),archive_location=str(archive),archive_sha256=archive_before,
        source_sha256=source_hashes,read_only=True,header_only_no_pixel_decode=True,
        author_terms_source='user_pasted_reply_2026-11-05_not_inbox_verified',
        permission_conditions=['cite_source_paper','research_only_not_commercial','no_sharing_with_other_groups_or_individuals_without_author_consent'],
        calibration_admitted=False))
    issues=[];files=[];subjects=[];dimensions=Counter();modes=Counter();icc=exif=0
    values=Counter();types=Counter();fractional=0;exact=[]
    z=zipfile.ZipFile(archive)
    members={}
    marker=data.name+'/'
    for info in z.infolist():
        if info.is_dir():continue
        if marker not in info.filename:
            issues.append(dict(type='archive_file_outside_data_root',path=info.filename));continue
        relative=info.filename.split(marker,1)[1]
        if relative in members:issues.append(dict(type='duplicate_archive_member',path=relative))
        members[relative]=info
    if set(members)!=set(start_inventory):issues.append(dict(type='archive_extraction_membership_mismatch'))
    for index,folder in enumerate(folders,1):
        label=folder/'monk_scale_value.json';record=dict(subject_key='stellenbosch_'+folder.name,
            publisher_folder=folder.name,person_group_basis='publisher_folder_only_not_cross_source_identity',
            label_available=False,calibration_admitted=False,training_admitted=False)
        try:
            raw=label.read_bytes();parsed=parse_mst_value(json.loads(raw.decode('utf-8-sig')))
            record.update(parsed,label_sha256=hashlib.sha256(raw).hexdigest(),label_available=True)
            value=Decimal(parsed['exact_decimal']);exact.append(value)
            values[format(value.normalize(),'f')]+=1;types[parsed['raw_type']]+=1
            fractional+=int(not parsed['is_integral'])
        except (ValueError,OSError) as error:issues.append(dict(type='invalid_label',subject=folder.name,reason=str(error)))
        jpgs=sorted(folder.rglob('*.jpeg'));pose_counts=Counter(p.parent.name for p in jpgs)
        record.update(images=len(jpgs),pose_counts=dict(pose_counts),condition_names=sorted({p.stem for p in jpgs}))
        if len(jpgs)!=75 or set(pose_counts.values())!={15}:issues.append(dict(type='subject_image_structure',subject=folder.name))
        subjects.append(record)
        for path in sorted(p for p in folder.rglob('*') if p.is_file()):
            relative=path.relative_to(data).as_posix();content=path.read_bytes();checksum=zlib.crc32(content)&0xffffffff
            entry=members.get(relative);match=entry is not None and entry.file_size==len(content) and entry.CRC==checksum
            if not match:issues.append(dict(type='archive_size_CRC_mismatch',path=relative))
            item=dict(path=relative,bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),
                archive_size_CRC_match=match,subject_key=record['subject_key'])
            if path.suffix.lower()=='.jpeg':
                try:
                    with Image.open(path) as image:
                        shape=str(image.width)+'x'+str(image.height);dimensions[shape]+=1;modes[image.mode]+=1
                        hasicc=bool(image.info.get('icc_profile'));hasexif=bool(image.info.get('exif'))
                        icc+=hasicc;exif+=hasexif
                        item.update(dimensions=list(image.size),mode=image.mode,ICC_present=hasicc,EXIF_present=hasexif)
                except (ValueError,OSError) as error:issues.append(dict(type='image_header_failure',path=relative,reason=str(error)))
            files.append(item)
        if index%25==0 or index==len(folders):print(str(index)+'/'+str(len(folders))+' subject metadata/header/CRC checks',flush=True)
    z.close()
    endfiles=sorted(p for p in data.rglob('*') if p.is_file())
    end_inventory={p.relative_to(data).as_posix():(p.stat().st_size,p.stat().st_mtime_ns) for p in endfiles}
    assert start_inventory==end_inventory and archive_before==sha(archive)
    assert all(sha(Path(p))==h for p,h in source_hashes.items())
    if {p.name for p in folders}!={str(i) for i in range(1,286)}:issues.append(dict(type='publisher_subject_keys_not_1_through_285'))
    summary=dict(subject_folders=len(folders),images=sum(r['images'] for r in subjects),label_JSONs=len(list(data.glob('*/monk_scale_value.json'))),
        total_files=len(files),archive_members_matched=sum(r['archive_size_CRC_match'] for r in files),
        archive_bytes=archive.stat().st_size,archive_sha256=archive_before,dimensions=dict(dimensions),modes=dict(modes),
        ICC_images=icc,EXIF_images=exif,label_types=dict(types),fractional_MST_subjects=fractional,
        integral_MST_subjects=len(exact)-fractional,min_source_score=str(min(exact)) if exact else None,
        max_source_score=str(max(exact)) if exact else None,
        score_histogram_NOT_integer_categories=dict(sorted(values.items(),key=lambda p:Decimal(p[0]))),
        label_rounding_or_category_mapping=False,issues=issues,raw_data_location=str(data),
        pixel_decode=False,segmentation_inference=0,calibration_fits=0,tree_fits=0,calibration_admissions=0,
        files_not_moved_or_modified=True,archive_unchanged=True,
        publication_or_redistribution_allowed=False,terms_acceptance_basis='author_reply_supplied_by_user')
    write(OUT/'subjects_PRIVATE.json',subjects);write(OUT/'files_PRIVATE.json',files);write(OUT/'summary_PRIVATE.json',summary)
    with (OUT/'subjects_PRIVATE.csv').open('w',newline='',encoding='utf-8') as stream:
        fields=['subject_key','publisher_folder','images','label_available','raw_value','raw_type','exact_decimal','is_integral','integer_category','calibration_admitted']
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(subjects)
    with (OUT/'subjects_PRIVATE.csv').open(newline='',encoding='utf-8') as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==285 and all(a['subject_key']==b['subject_key'] and a['exact_decimal']==b.get('exact_decimal','') for a,b in zip(rows,subjects))
    write(OUT/'verification.json',dict(files_checked=len(files),subject_CSV_JSON_parity=True,source_inventory_unchanged=True,
        archive_hash_unchanged=True,raw_data_written=False,source_code_hashes_unchanged=True,
        header_checks_only_NOT_full_JPEG_decode_or_face_validation=True))
    write(OUT/'sha256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps({k:v for k,v in summary.items() if k not in ['raw_data_location','score_histogram_NOT_integer_categories','archive_sha256','issues']},indent=2))
    print('Integrity/schema issues: '+str(len(issues)))


if __name__=='__main__':main()
