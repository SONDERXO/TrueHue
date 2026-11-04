"""Run all existing38 attempts; references are evaluation-only, never inference."""
import csv
import hashlib
import html
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.controlled_training_table import FEATURES
from src.evaluation.correction_prototype import image_errors

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as stream:return list(csv.DictReader(stream))
def main():
    out=ROOT/get_config().OUTPUTS_ROOT/'core_pipeline_check_v1'
    if out.exists():raise FileExistsError(out)
    runtime=importlib.import_module('116_run_core_pipeline');pipeline,model_provenance=runtime.build_pipeline()
    tables=ROOT/'data/manifests/controlled_training_v2';rows=[];paths=[]
    for name,count in [('train',30),('development_validation',3),('clipped_stress',4),('excluded_pairs',1)]:
        path=tables/(name+'.csv');part=read(path);assert len(part)==count;rows.extend(dict(r,diagnostic_table=name) for r in part);paths.append(path)
    selected_path=ROOT/'data/manifests/controlled_development_v1/selected_sources.csv';selected={r['image_id']:r for r in read(selected_path)}
    for r in rows:
        source=selected[r['source_image_id']]
        assert source['known_pipeline_development_exposure']=='True'
        assert source['partition']==r['partition'] and source['duplicate_group_id']==r['duplicate_group_id']
        assert r['mask_version']=='v2_complete_mouth_v1'
        paths.extend([ROOT/r['input_path'],Path(r['source_path']),ROOT/r['generation_mask_path']])
    paths.extend([Path(__file__),ROOT/'scripts/116_run_core_pipeline.py',ROOT/'src/correction/core_pipeline.py',
        ROOT/'src/correction/correct_image.py',ROOT/'scripts/11_prepare_training_manifests.py',selected_path,
        ROOT/'docs/core-pipeline-check-protocol.md',ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/face_boundary_reference_v1/original_export.json',
        ROOT/get_config().FACE_MODEL_PATH,ROOT/get_config().FACE_LANDMARKER_MODEL_PATH,
        ROOT/'outputs/core_tree_portability_v2/decision_tree.json',ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths};out.mkdir();(out/'cases').mkdir();(out/'boards').mkdir()
    (out/'run_status.json').write_text('{"status":"running"}')
    records=[];boards={}
    for row in rows:
        pair=row['pair_id'];image=cv2.imread(str(ROOT/row['input_path']));result=pipeline.run(image)
        destination=out/'cases'/pair;runtime.save_result(destination,image,result,{**model_provenance,'input_sha256':digest(ROOT/row['input_path'])})
        record=dict(pair_id=pair,source_image_id=row['source_image_id'],variant=row['variant'],diagnostic_table=row['diagnostic_table'],
            original_table_use=row['table_use'],original_pair_status=row['pair_status'],clipped_pixels=int(row['clipped_pixel_count']),
            report_path=(destination/'report.json').relative_to(ROOT).as_posix(),status=result.report['status'],failed_stage=result.report['failed_stage'],
            training_eligibility_changed=False,metrics=None)
        # Reference and generation scoring mask enter only after prediction is complete.
        reference=cv2.imread(row['source_path']);generation=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        assert reference.shape==image.shape and generation.shape==image.shape[:2] and generation.any()
        ref_rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB);input_rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        no_correction=image_errors(ref_rgb,input_rgb,generation)
        if result.correction is not None:
            corrected=result.correction.corrected_bgr;corr_rgb=cv2.cvtColor(corrected,cv2.COLOR_BGR2RGB)
            metrics=image_errors(ref_rgb,corr_rgb,generation)
            measured=np.array([result.correction.features[f] for f in FEATURES]);expected=np.array([float(row[f]) for f in FEATURES])
            record.update(features_match_saved=bool(np.allclose(measured,expected,rtol=0,atol=.00005)),
                features=result.correction.features,parameters=result.correction.parameters,
                metrics=dict(no_correction=no_correction,decision_tree=metrics,
                    ciede2000_change=metrics['ciede2000_source_mask']-no_correction['ciede2000_source_mask'],
                    worsened=metrics['ciede2000_source_mask']>no_correction['ciede2000_source_mask']+1e-12),
                output_changed_pixels=int(np.any(corrected!=image,axis=2).sum()),
                outside_mask_changed_pixels=int(np.any(corrected!=image,axis=2)[~result.correction.correction_mask].sum()))
            if row['variant']=='identity_control':assert np.array_equal(reference,image)
            preview=cv2.imread(str(destination/'comparison.png'));reference_panel=cv2.resize(reference,(256,256));reference_panel=cv2.copyMakeBorder(reference_panel,28,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(reference_panel,row['variant'],(3,18),cv2.FONT_HERSHEY_SIMPLEX,.39,(255,255,255),1)
            board=np.hstack([reference_panel,preview])
        else:
            record['failure_no_correction_metrics']=no_correction
            panels=[]
            for label,value in [('Reference',reference),('Input',image),('FAILED '+str(result.report['failed_stage']),image),('No corrected output',image)]:
                shown=cv2.resize(value,(256,256));shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.38,(0,0,255),1);panels.append(shown)
            board=np.hstack(panels)
        ident=Path(row['source_image_id']).stem;boards.setdefault(ident,[]).append(board);records.append(record)
        print(pair+': '+result.report['status'],flush=True)
    for ident,panels in boards.items():assert cv2.imwrite(str(out/'boards'/(ident+'.png')),np.vstack(panels))
    available=[r for r in records if r['metrics'] is not None];aggregate=[]
    for table in ['train','development_validation','clipped_stress']:
        variants=sorted({r['variant'] for r in available if r['diagnostic_table']==table})
        for variant in ['all']+variants:
            subset=[r for r in available if r['diagnostic_table']==table and (variant=='all' or r['variant']==variant)]
            if not subset:continue
            source_means=[]
            for ident in {r['source_image_id'] for r in subset}:
                source_means.append(float(np.mean([r['metrics']['ciede2000_change'] for r in subset if r['source_image_id']==ident])))
            aggregate.append(dict(table=table,variant=variant,pairs=len(subset),sources=len(source_means),
                no_correction_mean_ciede2000=float(np.mean([r['metrics']['no_correction']['ciede2000_source_mask'] for r in subset])),
                tree_mean_ciede2000=float(np.mean([r['metrics']['decision_tree']['ciede2000_source_mask'] for r in subset])),
                source_balanced_mean_change=float(np.mean(source_means)),worsened_pairs=sum(r['metrics']['worsened'] for r in subset)))
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_development_diagnostic_no_adoption',records=records,aggregate=aggregate,input_sha256=hashes,
        available=len(available),failed=len(records)-len(available),proposal_complete=False,mst_available=0,new_model_fits=0,training_pairs_regenerated=0,
        limitations='Known exposed controlled inputs. Original-reference reconstruction only, not calibrated skin truth/final accuracy. Paint/makeup and neck incomplete; MST unavailable; no final-model adoption.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'run_status.json').write_text('{"status":"complete"}')
    page=['<!doctype html><meta charset="utf-8"><title>TrueHue core pipeline check</title><style>body{font:16px system-ui;background:#182028;color:#eee;max-width:1200px;margin:24px auto}a{color:#9cd9ff}img{max-width:100%}</style><h1>Core pipeline development check</h1><p>38 known attempts; frozen portable tree, legacy HSV/YCrCb complete-mouth support. MST explicitly unavailable; this is a partial development pipeline. Panels: reference for evaluation only, actual input, correction, application support. No new fit, source admission or final quality claim.</p><p><a href="summary.json">All results and baseline comparison</a></p>']
    for ident in boards:page.append('<h2>'+html.escape(ident)+'</h2><img loading="lazy" src="boards/'+ident+'.png">')
    (out/'review.html').write_text('\n'.join(page),encoding='utf-8')
    print(json.dumps(dict(available=len(available),failed=38-len(available),aggregate=aggregate)))
if __name__=='__main__':main()
