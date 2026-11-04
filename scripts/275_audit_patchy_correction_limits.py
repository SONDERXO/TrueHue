"""Reference-informed operator-limit audit on every full-path stress result."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.evaluation.irrecoverable_rgb import irrecoverable_rgb_floor
from src.evaluation.correction_prototype import image_errors
from src.distortion_generation.paper_gamma import transform_rgb
h=importlib.import_module('256_compare_clean_control_tree_depth')
PARENT=ROOT/'outputs/endpoint_full_path_jpeg_v1';INPUTS=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
OUT=ROOT/'outputs/patchy_correction_limits_v1'


def summarize(records):
    aggregates=[]
    for encoding in ('lossless','jpeg95','jpeg85'):
        for scope in ('all','clean','distorted'):
            part=[r for r in records if r['encoding']==encoding and (scope=='all' or (r['variant']=='identity')==(scope=='clean'))]
            aggregates.append(dict(encoding=encoding,scope=scope,pairs=len(part),
                learned_ciede2000=float(np.mean([r['learned_metrics']['ciede2000_source_mask'] for r in part])),
                target_ciede2000=float(np.mean([r['saved_target_metrics']['ciede2000_source_mask'] for r in part])),
                learned_rgb_mae=float(np.mean([r['learned_metrics']['rgb_mae_source_mask'] for r in part])),
                target_rgb_mae=float(np.mean([r['saved_target_metrics']['rgb_mae_source_mask'] for r in part])),
                rgb_mae_floor=float(np.mean([r['floor']['rgb_mae_lower_bound'] for r in part])),
                outside_support_floor=float(np.mean([r['floor']['outside_support_rgb_mae_floor'] for r in part])),
                inside_endpoint_floor=float(np.mean([r['floor']['inside_endpoint_rgb_mae_floor'] for r in part]))))
    return dict(aggregates=aggregates,attempts=141,models_fitted=0,new_target_fits=0,active_demo_changed=False,
        scope='Reference-informed operator diagnostic; no globally optimal CIEDE2000 or natural-photo accuracy claim')


def load():
    rows={r['pair_id']:r for r in h.read(PARENT/'plan.json')['rows']}
    inputs={(r['pair_id'],r['encoding']):r for r in h.read(INPUTS/'predictions.json')}
    return rows,inputs,h.read(PARENT/'attempts.json')


def run():
    if OUT.exists():raise FileExistsError(OUT)
    verification=h.read(PARENT/'verification.json');assert verification['status']=='pass'
    paths=[Path(__file__),Path(h.__file__),ROOT/'src/evaluation/irrecoverable_rgb.py',ROOT/'docs/patchy-correction-audit-protocol.md',PARENT/'verification.json']
    paths.extend(PARENT/path for path in verification['evidence_sha256'])
    hashes=dict(h.read(PARENT/'plan.json')['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    rows,inputs,attempts=load();assert len(attempts)==141 and all(r['status']=='success' for r in attempts)
    OUT.mkdir();(OUT/'images').mkdir();h.write(OUT/'plan.json',dict(status='frozen_before_audit',input_sha256=hashes,attempts=141,
        parameters='unchanged learned versus original saved recovery targets; no re-fit'))
    records=[]
    for prior in attempts:
        pair=prior['pair_id'];encoding=prior['encoding'];stem=pair+'_'+encoding;row=rows[pair]
        rgb=cv2.cvtColor(cv2.imread(str(INPUTS/inputs[(pair,encoding)]['encoded_input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(PARENT/'images'/(stem+'_mask.png')),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        target=row['paper_target'];assert min(target)>0
        output=rgb.copy();output[mask]=np.rint(transform_rgb(rgb.astype(float)/255,*target)[mask]*255).astype(np.uint8)
        path=OUT/'images'/(stem+'_saved_target.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
        floor=irrecoverable_rgb_floor(rgb,reference,mask,score);metrics=image_errors(reference,output,score)
        assert metrics['rgb_mae_source_mask']+1e-12>=floor['rgb_mae_lower_bound']
        assert prior['metrics']['rgb_mae_source_mask']+1e-12>=floor['rgb_mae_lower_bound']
        records.append(dict(pair_id=pair,encoding=encoding,variant=row['variant'],learned_parameters=prior['parameters'],
            saved_target_parameters=target,floor=floor,learned_metrics=prior['metrics'],saved_target_metrics=metrics,output_sha256=h.digest(path)))
        if pair=='1398__table2_medium' and encoding=='jpeg85':
            learned=cv2.imread(str(PARENT/'images'/(stem+'_result.png')))
            board=np.hstack((cv2.cvtColor(reference,cv2.COLOR_RGB2BGR),cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),learned,cv2.cvtColor(output,cv2.COLOR_RGB2BGR)))
            header=np.full((32,board.shape[1],3),245,np.uint8)
            cv2.putText(header,'1398 JPEG85: reference / input / learned / saved reference-fitted target',(5,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,20,20),1)
            cv2.imwrite(str(OUT/'patch_case_comparison.png'),np.vstack((header,board)))
    h.write(OUT/'records.json',records);h.write(OUT/'summary.json',summarize(records))
    print('Saved 141 fixed-support oracle comparisons and RGB floors; no models or targets fitted.')


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    for path,sha in h.read(OUT/'plan.json')['input_sha256'].items():assert h.digest(ROOT/path)==sha
    rows,inputs,attempts=load();originals={(r['pair_id'],r['encoding']):r for r in attempts};records=h.read(OUT/'records.json')
    assert len(records)==141 and len({(r['pair_id'],r['encoding']) for r in records})==141
    for r in records:
        key=(r['pair_id'],r['encoding']);prior=originals[key];row=rows[r['pair_id']];stem=r['pair_id']+'_'+r['encoding']
        assert r['learned_metrics']==prior['metrics'] and r['learned_parameters']==prior['parameters'] and r['saved_target_parameters']==row['paper_target']
        image=cv2.cvtColor(cv2.imread(str(INPUTS/inputs[key]['encoded_input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(PARENT/'images'/(stem+'_mask.png')),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        # Independent per-channel decomposition; no reuse of floor helper.
        outside_sum=0.;inside_sum=0.;count=int(score.sum())*3
        for channel in range(3):
            difference=np.abs(image[:,:,channel].astype(float)-reference[:,:,channel].astype(float))/255
            outside_sum+=difference[score&~mask].sum()
            fixed=image[:,:,channel]==0
            if channel==1:fixed|=image[:,:,channel]==255
            inside_sum+=difference[score&mask&fixed].sum()
        assert abs(r['floor']['outside_support_rgb_mae_floor']-outside_sum/count)<1e-12
        assert abs(r['floor']['inside_endpoint_rgb_mae_floor']-inside_sum/count)<1e-12
        for params,kind in ((r['learned_parameters'],'learned'),(r['saved_target_parameters'],'target')):
            curve=np.clip((image.astype(float)/255)**params[0]*[params[1],1,params[2]],0,1)
            output=image.copy();output[mask]=np.rint(curve[mask]*255).astype(np.uint8)
            np.testing.assert_array_equal(output[~mask],image[~mask])
            for channel in range(3):
                selected=mask&(image[:,:,channel]==0);assert not output[:,:,channel][selected].any()
            assert np.all(output[:,:,1][mask&(image[:,:,1]==255)]==255)
            path=PARENT/'images'/(stem+'_result.png') if kind=='learned' else OUT/'images'/(stem+'_saved_target.png')
            if kind=='target':assert h.digest(path)==r['output_sha256']
            np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
            metrics=image_errors(reference,output,score)
            assert metrics==(r['learned_metrics'] if kind=='learned' else r['saved_target_metrics'])
            assert metrics['rgb_mae_source_mask']+1e-12>=r['floor']['rgb_mae_lower_bound']
    assert summarize(records)==h.read(OUT/'summary.json')
    h.write(target,dict(status='pass',independent_rgb_floor_decompositions=141,image_metric_replays=282,
        zero_and_green_white_invariants_verified=True,models_fitted=0,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 141 independent RGB bounds, 282 image/metric replays, endpoint invariants and unchanged saved targets.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
