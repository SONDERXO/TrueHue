"""Existing scalar/metadata cue readiness; never follows image paths."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/existing_illumination_cue_readiness_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial readiness audit')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    rows=read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')
    inventory=read(ROOT/'outputs/stellenbosch_received_data_v1/files_PRIVATE.json')
    byhash={r['sha256']:r for r in inventory}
    matches=[]
    for r in rows:
        m=byhash[r['source_sha256']]
        assert m['subject_key']==r['subject_id'] and m['dimensions']==[224,224]
        matches.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],condition=r['condition'],source_sha256=r['source_sha256'],
            inherited_relative_path=m['path'],ICC_present=m['ICC_present'],EXIF_present=m['EXIF_present'],dimensions=m['dimensions'],
            current_feature_names=sorted(r['features']),calibration_admitted=False))
    photo=read(ROOT/'outputs/reviewed_feature_control_contract_v1/partial_features_and_targets_PRIVATE.json')
    old=read(ROOT/'outputs/fitting_green_features_v1/features_PRIVATE.json')['records']
    fitting=[r for r in old if r['role']=='fitting' and r['recipe']=='clean']
    scene=('scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90','scene_any_zero_fraction','scene_any_full_fraction')
    green=('input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast')
    counts=dict(reviewed_captures=len(rows),subjects=len({r['subject_id'] for r in rows}),
        inherited_EXIF=sum(m['EXIF_present'] for m in matches),inherited_ICC=sum(m['ICC_present'] for m in matches),
        current_rows_with_scene_summaries=sum(all(k in r['features'] for k in scene) for r in rows),
        current_rows_with_green_summaries=sum(all(k in r['features'] for k in green) for r in rows),
        photographic_roles_with_scene_summaries=sum(all(k in r['features_partial'] for k in scene) for r in photo),
        photographic_roles_with_green_summaries=sum(all(k in r['features_partial'] for k in green) for r in photo),
        photographic_roles_with_provided_MST_label=sum(r.get('provided_mst_label') is not None for r in photo),
        historical_real_clean_fitting_rows=len(fitting),historical_clean_green_rows=sum(all(k in r['features'] for k in green) for r in fitting),
        ready_current_60row_additional_cue_vectors=0)
    ledger=[dict(cue='Camera exposure/WB/illuminant metadata',status='unavailable_in_inherited_headers',
        evidence='No EXIF in exact60; ICC also absent. Condition names are not camera settings or runtime inputs.'),
        dict(cue='Seven existing whole-scene summaries',status='available_on14_photographic_roles_not_prepared_for_current60',
        evidence='Content-dependent rendered RGB summaries; not illuminant truth. Fixed computation already exists; requires separate exact60 full-frame extraction to assess paired behaviour.'),
        dict(cue='Four existing facial green summaries',status='14current_photo_roles_and82historical_clean_rows_only',
        evidence='Historical masks differ from reviewed masks; no current60 prepared vectors. These describe face appearance, not an independent physical illuminant.'),
        dict(cue='Known neutral reflectance/chart',status='not_established_in_bound_records',
        evidence='No declared registered chart/known-reflectance ROI in current task/core contracts. White-looking clothes/background are not verified neutral.'),
        dict(cue='Capture conditions and subject IDs',status='reporting_and_grouping_only',
        evidence='Must not enter single-photo inference or be copied to photographic roles.'),
        dict(cue='Editor target or paired second capture',status='training_reference_only',
        evidence='Unavailable for single-photo inference; target pixels and paired differences must not become inference features.')]
    for relative in ('src/model_training/whole_scene_features.py','src/model_training/green_distribution_features.py',
                     'docs/green-feature-correction-results-2026-11-09.md',
                     'docs/stellenbosch-received-data-results-2026-11-05.md'):
        p=ROOT/relative;bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',dict(counts=counts,cue_ledger=ledger,new_fits=0,new_predictions=0,image_reads=0,
                        holdout_reads=0,calibration_admitted=False,runtime_adopted=False)),
                       ('exact60_metadata_PRIVATE.json',matches),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(counts,indent=2))


if __name__=='__main__':main()
