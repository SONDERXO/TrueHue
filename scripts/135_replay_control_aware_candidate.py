"""Replay the fixed candidate on all38known core attempts, with explicit cohorts."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.controlled_training_table import FEATURES
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import apply_correction, image_errors


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    config=get_config(); out=ROOT/config.OUTPUTS_ROOT/'control_aware_candidate_replay_v1'
    if out.exists():raise FileExistsError(out)
    build=ROOT/config.OUTPUTS_ROOT/'control_aware_model_build_v1'
    report=json.loads((build/'build_report.json').read_text())
    assert report['quality_gate']['status']=='held_quality_failure'
    assert all(digest(build/p)==h for p,h in report['artifact_sha256'].items())
    assert all(digest(ROOT/p)==h for p,h in report['input_sha256'].items())
    model=PortableTree(json.loads((build/'decision_tree.json').read_text()))
    fit=set(json.loads((build/'fit_manifest.json').read_text())['fitting_pair_ids'])
    core_folder=ROOT/config.OUTPUTS_ROOT/'core_pipeline_check_v1'
    core=json.loads((core_folder/'summary.json').read_text())
    core_verification=json.loads((core_folder/'verification.json').read_text())
    assert digest(core_folder/'summary.json')==core_verification['summary_sha256']
    tables=ROOT/config.DATA_ROOT/'manifests/controlled_training_v2'; rows={}
    tracked=[Path(__file__),build/'build_report.json',build/'decision_tree.json',
             ROOT/'docs/control-aware-model-evaluation-protocol.md',
             core_folder/'summary.json',core_folder/'verification.json',
             ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/distortion_generation/generate_distortions.py']
    for name in ['train','development_validation','clipped_stress','excluded_pairs']:
        table=tables/(name+'.csv');tracked.append(table)
        with table.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):rows[row['pair_id']]=row
    assert len(rows)==len(core['records'])==38
    for old in core['records']:
        row=rows[old['pair_id']]
        tracked += [ROOT/row['input_path'],Path(row['source_path']),ROOT/row['generation_mask_path']]
        if old['metrics'] is not None:
            tracked.append(core_folder/'cases'/old['pair_id']/'correction_mask.png')
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in tracked}
    out.mkdir();(out/'corrected').mkdir();(out/'boards').mkdir()
    records=[];boards={}
    for old in core['records']:
        pair=old['pair_id'];row=rows[pair]
        group=('eligible_seen_source' if pair in fit else 'held_ID_seen_source_diagnostic') if old['diagnostic_table']=='train' else old['diagnostic_table']
        record=dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],cohort=group,
                    fitted=pair in fit,status=old['status'],original_failed_stage=old['failed_stage'])
        if old['metrics'] is None:
            record.update(candidate_metrics=None,reason='Original input failure retained; no fallback')
            records.append(record);continue
        features=old['features'];vector=model.predict_one(features)
        image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
        support=cv2.imread(str(core_folder/'cases'/pair/'correction_mask.png'),0)>0
        scoring=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        corrected=apply_correction(image,support,vector)
        np.testing.assert_array_equal(corrected[~support],image[~support])
        baseline=image_errors(reference,image,scoring)
        for key,value in baseline.items():
            assert value is None or abs(value-old['metrics']['no_correction'][key])<1e-12
        metrics=image_errors(reference,corrected,scoring)
        target=np.asarray([float(row['target_'+k]) for k in ['gamma','red_gain','blue_gain']])
        record.update(features=features,parameters=vector,candidate_metrics=metrics,
            no_correction_metrics=baseline,original_runtime_metrics=old['metrics']['decision_tree'],
            parameter_absolute_error=np.abs(np.asarray(vector)-target).tolist(),outside_mask_unchanged=True,
            corrected_path='corrected/'+pair+'.png')
        assert cv2.imwrite(str(out/record['corrected_path']),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
        panels=[]
        for title,pixels in [('Photographic reference',reference),('Input / no correction',image),('Candidate: '+group,corrected)]:
            shown=cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR)
            shown=cv2.copyMakeBorder(shown,40,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,title,(2,13),cv2.FONT_HERSHEY_SIMPLEX,.27,(255,255,255),1)
            cv2.putText(shown,row['variant'],(2,30),cv2.FONT_HERSHEY_SIMPLEX,.32,(0,220,255),1)
            panels.append(shown)
        boards.setdefault(row['source_image_id'],[]).append(np.hstack(panels));records.append(record)
    aggregates=[]
    for cohort in sorted({r['cohort'] for r in records}):
        for variant in ['all']+sorted({r['variant'] for r in records if r['cohort']==cohort}):
            selected=[r for r in records if r['cohort']==cohort and (variant=='all' or r['variant']==variant)]
            available=[r for r in selected if r['candidate_metrics'] is not None]
            if not available:continue
            mean=lambda key:float(np.mean([r[key]['ciede2000_source_mask'] for r in available]))
            aggregates.append(dict(cohort=cohort,variant=variant,attempts=len(selected),available=len(available),
                sources=len({r['source_image_id'] for r in available}),candidate_mean_ciede2000=mean('candidate_metrics'),
                no_correction_mean_ciede2000=mean('no_correction_metrics'),original_runtime_mean_ciede2000=mean('original_runtime_metrics'),
                worsened_pairs=sum(r['candidate_metrics']['ciede2000_source_mask']>r['no_correction_metrics']['ciede2000_source_mask']+1e-12 for r in available)))
    for source,strips in boards.items():
        assert cv2.imwrite(str(out/'boards'/(Path(source).stem+'.png')),np.vstack(strips))
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='development_replay_quality_hold_unchanged',records=records,aggregate=aggregates,
        available=sum(r['candidate_metrics'] is not None for r in records),failed=sum(r['candidate_metrics'] is None for r in records),
        quality_gate=report['quality_gate'],new_model_fits=0,runtime_replaced=False,proposal_complete=False,
        input_sha256=hashes,limitations='Seen-source fitting probes, previously exposed single-source development and clipped stress remain separate. No final accuracy or calibrated complexion claim.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    page=['<!doctype html><meta charset="utf-8"><title>Control-aware candidate replay</title><style>body{font:16px system-ui;max-width:1100px;margin:24px auto}img{max-width:100%}</style><h1>Held development candidate</h1><p>All-row development fit; primary source-held-out recipe quality gate FAILED. Training-source images below are seen-source diagnostics. External development is one previously exposed source; stress is clipped. No runtime replacement or MST estimate.</p><a href="summary.json">Metrics and provenance</a>']
    for source in sorted(boards):page.append('<h2>'+html.escape(source)+'</h2><img src="boards/'+Path(source).stem+'.png">')
    page.append('<p>Original failed input retained in JSON; no fallback output.</p>')
    (out/'review.html').write_text('\n'.join(page),encoding='utf-8')
    print(json.dumps(dict(available=summary['available'],failed=summary['failed'],source_boards=len(boards),aggregate=[r for r in aggregates if r['variant']=='all']),indent=2))


if __name__=='__main__':main()
