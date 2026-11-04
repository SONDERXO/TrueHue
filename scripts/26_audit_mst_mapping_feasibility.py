"""Audit recovered historical MST-E measurements and exploratory subject CV.

No final thresholds, official labels, source images or correction models are
changed. Pending reviews are NEVER treated as trusted reviewed observations.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import shutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ita_estimation.mapping_feasibility import leave_subject_out


def read(path):
    for encoding in ('utf-8-sig','cp1252'):
        try:
            with path.open(encoding=encoding,newline='') as stream:
                return list(csv.DictReader(stream))
        except UnicodeDecodeError:
            if encoding=='cp1252':
                raise


def write(path,rows,fields=None):
    fields=fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def metrics(rows):
    errors=[abs(r['predicted_mst']-r['source_mst_label']) for r in rows]
    subjects=sorted({r['subject_id'] for r in rows})
    return dict(images=len(rows),subjects=len(subjects),
        exact_accuracy=sum(e==0 for e in errors)/len(errors),within_one_accuracy=sum(e<=1 for e in errors)/len(errors),
        ordinal_mae=statistics.mean(errors),
        subject_macro_exact_accuracy=statistics.mean(sum(r['predicted_mst']==r['source_mst_label'] for r in rows if r['subject_id']==s)/sum(r['subject_id']==s for r in rows) for s in subjects),
        subject_macro_ordinal_mae=statistics.mean(statistics.mean(abs(r['predicted_mst']-r['source_mst_label']) for r in rows if r['subject_id']==s) for s in subjects))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review',type=Path,required=True)
    args=parser.parse_args()
    metadata_path=ROOT/'data/raw/mst-e_data/mst-e_image_details.csv'
    out=ROOT/'data/manifests/mst_mapping_feasibility_v1'
    if out.exists():
        raise FileExistsError('Audit exists; refusing overwrite')
    fingerprints={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (metadata_path,args.review)}
    metadata=read(metadata_path);review=read(args.review)
    if len({r['image_id'] for r in review})!=len(review):
        raise ValueError('Duplicate historical measurement IDs')
    lookup={}
    for r in metadata:
        lookup.setdefault((r['subject_name'],r['image_ID']),[]).append(r)
    audited=[];usable=[]
    for row in review:
        path=Path(row['image_path']);subject=path.parent.name
        official=lookup.get((subject,path.name),[])
        audit=dict(image_id=row['image_id'],subject_id=subject,image_path=row['image_path'],
            historical_quality_review=row['quality_review'],historical_ita_use=row['ita_use'],
            measurement_version='historical_v2_no_run_hash_available',metadata_matches=len(official),
            source_mst_label=row['source_mst_label'],source_lighting='',audit_exclusion='')
        if not official:
            audit['audit_exclusion']='no_exact_official_metadata_match'
        elif len({r['MST'] for r in official})!=1 or len({r['lighting'] for r in official})!=1:
            audit['audit_exclusion']='conflicting_label_or_lighting_metadata'
        elif row['source_mst_label']!=official[0]['MST']:
            audit['audit_exclusion']='historical_label_disagrees_with_metadata'
        elif not path.is_file():
            audit['audit_exclusion']='source_image_missing'
        else:
            audit['source_lighting']=official[0]['lighting']
            try:
                ita=float(row['ita_degrees']);label=int(official[0]['MST']);count=float(row['skin_pixels'])
                if not math.isfinite(ita) or label not in range(1,11) or count<1000 or row['landmarks_available'].lower()!='true':
                    raise ValueError('Invalid measurement')
            except (ValueError,TypeError):
                audit['audit_exclusion']='unavailable_or_invalid_historical_measurement'
            else:
                audit.update(ita_degrees=ita,source_mst_label=label)
                usable.append(audit.copy())
        audited.append(audit)
    trusted=[r for r in usable if r['historical_quality_review'].strip().lower() in ('good','acceptable') and r['historical_ita_use'].strip().lower()=='include']
    if not trusted:
        raise ValueError('No reviewed included rows: refusing to fit a trusted feasibility test')
    predictions=leave_subject_out(trusted)
    summaries=[]
    for method in sorted({r['method'] for r in predictions}):
        subset=[r for r in predictions if r['method']==method]
        summaries.append(dict(method=method,view='reviewed_included',label='',lighting='',**metrics(subset)))
        for label in range(1,11):
            group=[r for r in subset if r['source_mst_label']==label]
            if group:
                summaries.append(dict(method=method,view='by_official_label',label=label,lighting='',**metrics(group)))
        for lighting in sorted({r['source_lighting'] for r in subset}):
            summaries.append(dict(method=method,view='by_lighting',label='',lighting=lighting,
                                  **metrics([r for r in subset if r['source_lighting']==lighting])))
    coverage=[]
    for label in range(1,11):
        official_subjects=sorted({r['subject_name'] for r in metadata if r['MST']==str(label)})
        included=[r for r in trusted if r['source_mst_label']==label]
        coverage.append(dict(source_mst_label=label,official_subjects=';'.join(official_subjects),
            official_subject_count=len(official_subjects),exploratory_images=len(included),
            exploratory_subject_count=len({r['subject_id'] for r in included}),
            absent_training_label_in_heldout_fold=len({r['subject_id'] for r in included})==1))
    out.mkdir()
    shutil.copyfile(args.review,out/'review_source_original.csv')
    write(out/'measurement_metadata_audit.csv',audited)
    write(out/'reviewed_included_rows.csv',trusted)
    write(out/'subject_label_coverage.csv',coverage)
    write(out/'exploratory_subject_heldout_predictions.csv',predictions)
    write(out/'exploratory_metrics.csv',summaries)
    from collections import Counter
    report=dict(historical_measurement_rows=len(review),official_metadata_rows=len(metadata),
        duplicate_metadata_keys=sum(len(v)-1 for v in lookup.values()),
        historical_review_status_counts=dict(Counter(r['quality_review'] for r in review)),
        trusted_reviewed_usable_rows=len(trusted),available_numeric_rows=len(usable),
        subjects=len({r['subject_id'] for r in trusted}),
        audit_exclusions=dict(Counter(r['audit_exclusion'] for r in audited if r['audit_exclusion'])),
        single_subject_labels=[r['source_mst_label'] for r in coverage if r['official_subject_count']==1],
        reviewed_single_subject_labels=[r['source_mst_label'] for r in coverage if r['exploratory_subject_count']==1],
        source_sha256=fingerprints,
        warning='Subject-heldout feasibility on historically reviewed development data; not untouched final validation, no production thresholds or FairFace group labels exported.',
        overall_metrics=[r for r in summaries if r['view']=='reviewed_included'])
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=value for p,value in fingerprints.items()):
        raise RuntimeError('Source inputs changed during audit')
    (out/'audit_summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':
    main()
