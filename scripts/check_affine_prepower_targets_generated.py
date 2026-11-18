"""Fixed fourteen-record five-control generated fitter rehearsal; no dataset IO."""
from pathlib import Path
import json
import hashlib
import math
import platform
import importlib.metadata
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training import affine_prepower_targets as target
from src.evaluation import affine_prepower_scalar as scalar
from src.distortion_generation.directional_exposure_recipe import render_rgb

OUT=ROOT/'outputs/affine_prepower_target_engineering_v1'
KNOWN=[[.8,1.08,.92,.95,.03],[1.2,.95,1.05,1.05,-.02],
       [.7,1.,1.,1/1.08,(.08+35/255)/1.08],
       [1/.7,1.,1.,1/1.08,-35/255/1.08]]


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def create_output(path):
    if Path(path).exists():raise FileExistsError('Preserve completed or partial generated run')
    Path(path).mkdir(parents=True)


def record_failure(path,error):
    write(Path(path)/'failure_PRIVATE.json',dict(status='failed_preserved',error_type=type(error).__name__,error=str(error)))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if sys.argv[1:]!=['--generated-only']:raise SystemExit('Explicit --generated-only required')
    create_output(OUT)
    files=['docs/affine-prepower-target-fitter-protocol-2026-11-14.md',
        'src/model_training/affine_prepower_targets.py','src/evaluation/affine_prepower_scalar.py',
        'scripts/check_affine_prepower_targets_generated.py','tests/test_affine_prepower_targets.py',
        'src/model_training/blended_recovery_targets.py','src/distortion_generation/directional_exposure_recipe.py',
        'src/distortion_generation/table2_composite.py','src/distortion_generation/paper_gamma.py']
    bindings={n:sha(ROOT/n) for n in files}
    versions={'Python':platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy']}}
    write(OUT/'execution_plan_PRIVATE.json',dict(scope='generated_only_five_control_research',
        planned_records=14,maximum_local_solver_calls=11,identity_start=target.IDENTITY.tolist(),
        lower=target.LOWER.tolist(),upper=target.UPPER.tolist(),input_sha256=bindings,versions=versions))
    calls=[];original=target.least_squares
    def counted(fun,start,**kwargs):
        assert len(calls)<11
        np.testing.assert_array_equal(start,[1,1,1,1,0])
        assert kwargs['method']=='trf' and kwargs['loss']=='linear' and kwargs['max_nfev']==500
        calls.append(True)
        return original(fun,start,**kwargs)
    target.least_squares=counted
    try:
        palette=np.random.default_rng(145).uniform(.2,.8,(12,12,3))
        alpha=np.ones((12,12),float);protected=np.zeros((12,12),bool)
        cases=[]
        for index,p in enumerate(KNOWN):
            reference=target.render_float(palette,alpha,protected,p)
            independent,_=scalar.replay(palette,palette,alpha,p)
            np.testing.assert_allclose(reference,independent,atol=1e-12,rtol=0)
            cases.append(dict(case_id=f'known_{index}',kind='known_float',image=palette.copy(),
                reference=reference,alpha=alpha.copy(),protected=protected.copy(),controls=p,rgb8=False))
        rgb=np.random.default_rng(145).integers(0,256,(12,12,3),dtype=np.uint8)
        for role,variant,direction in [('identity','clean','none'),('colour_only','color','none'),
            ('exposure_under','exposure','under'),('exposure_over','exposure','over'),
            ('combined_under','combined','under'),('combined_over','combined','over')]:
            im,_=render_rgb(rgb,alpha,'medium',variant,direction)
            cases.append(dict(case_id=role,kind='directional_rgb8',image=im,reference=rgb.copy(),
                alpha=alpha.copy(),protected=protected.copy(),controls=None,rgb8=True))
        for kind in ['flat','near_flat']:
            image=np.full_like(palette,.4)
            if kind=='near_flat':image[::2]+=.001
            cases.append(dict(case_id=kind,kind='unavailable',image=image,reference=np.full_like(image,.5),
                alpha=alpha.copy(),protected=protected.copy(),controls=None,rgb8=False))
        spatial=alpha.copy();spatial[[0,-1],:]=0;spatial[:,[0,-1]]=0;spatial[1,1:-1]=.25
        protection=protected.copy();protection[5,5]=True;spatial[protection]=0
        cases.append(dict(case_id='known_spatial',kind='known_float',image=palette.copy(),
            reference=target.render_float(palette,spatial,protection,KNOWN[0]),alpha=spatial,
            protected=protection,controls=KNOWN[0],rgb8=False))
        im=np.rint(palette*255).astype(np.uint8)
        cases.append(dict(case_id='known_quantized',kind='known_rgb8',image=im,
            reference=target.render_rgb8(im,alpha,protected,KNOWN[0]),alpha=alpha.copy(),
            protected=protected.copy(),controls=KNOWN[0],rgb8=True))
        assert len(cases)==14
        write(OUT/'case_plan_PRIVATE.json',[{k:v for k,v in c.items()
            if k not in ['image','reference','alpha','protected']} for c in cases])
        records=[];max_control_error=0.;max_replay_error=0.
        for case in cases:
            snapshot={k:sha_array(case[k]) for k in ['image','reference','alpha','protected']}
            fitter=target.fit_rgb8_target if case['rgb8'] else target.fit_float_target
            result=fitter(case['image'],case['reference'],case['alpha'],case['protected'],generated_fixture=True)
            assert result['generated_fixture'] and not result['model_ready']
            if case['kind']=='known_float':
                assert result['parameters'] is not None and result['float_rmse']<=1e-6
                discrepancy=max(abs(a-b) for a,b in zip(case['controls'],result['parameters']))
                max_control_error=max(max_control_error,discrepancy)
                assert discrepancy<=1e-3
            if case['kind']=='unavailable':assert result['parameters'] is None and result['evaluations']==0
            assert scalar.verify(case['image'],case['reference'],case['alpha'],case['protected'],result,rgb8=case['rgb8'])
            if result['parameters'] is not None:
                im=case['image']/255 if case['rgb8'] else case['image']
                ref=case['reference']/255 if case['rgb8'] else case['reference']
                separate,_=scalar.replay(im,ref,case['alpha'],result['parameters'])
                actual=target.render_float(im,case['alpha'],case['protected'],result['parameters'])
                error=float(np.abs(separate-actual).max());max_replay_error=max(max_replay_error,error)
                assert error<=1e-12
                if case['rgb8']:
                    rounded=np.empty_like(case['image'])
                    for position in np.ndindex(rounded.shape):rounded[position]=round(255*float(separate[position]))
                    rounded[case['alpha']==0]=case['image'][case['alpha']==0]
                    np.testing.assert_array_equal(target.render_rgb8(case['image'],case['alpha'],case['protected'],result['parameters']),rounded)
            assert snapshot=={k:sha_array(case[k]) for k in snapshot}
            np.savez(OUT/(case['case_id']+'.npz'),**{k:case[k] for k in snapshot})
            record=dict(case_id=case['case_id'],kind=case['kind'],known_controls=case['controls'],result=result)
            write(OUT/(case['case_id']+'.json'),record);records.append(record)
        assert len(calls)==11
        assert all(sha(ROOT/n)==h for n,h in bindings.items())
        conditions=[r['result']['jacobian_condition_number'] for r in records if 'jacobian_condition_number' in r['result'] and r['result']['jacobian_condition_number'] is not None]
        report=dict(passed=True,scope='generated_target_fitter_engineering_not_model_quality',
            records=14,actual_local_solver_calls=11,known_float_records=5,
            known_control_max_error=max_control_error,scalar_render_max_error=max_replay_error,
            unavailable_records=[r['case_id'] for r in records if r['result']['parameters'] is None],
            jacobian_condition_number_range=[min(conditions),max(conditions)],
            records_summary=[dict(case_id=r['case_id'],status=r['result']['status'],
                float_rmse=r['result'].get('float_rmse'),RGB8_MAE=r['result'].get('rgb8_mae_codes'),
                jacobian_condition=r['result'].get('jacobian_condition_number'),
                active_bounds=r['result'].get('active_bounds')) for r in records],
            photo_reads=0,real_target_fits=0,tree_fits=0,model_adopted=False,
            input_sha256=bindings,versions=versions)
        write(OUT/'verification_PRIVATE.json',report)
        print(json.dumps(report,indent=2))
    except Exception as error:
        record_failure(OUT,error)
        raise
    finally:
        target.least_squares=original


def sha_array(a):return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


if __name__=='__main__':main()
