"""Fixed39 arithmetic probes for a proposed five-control family; no fitter or image IO."""
from pathlib import Path
import json
import hashlib
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/affine_prepower_operator_algebra_v1'


def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def clip(v):return min(1.,max(0.,v))


def candidate(y,q,r,b,a,d):
    assert all(math.isfinite(v) for v in [q,r,b,a,d]) and min(q,r,b,a)>0
    return [clip(max(0.,a*v+d)**q*gain) for v,gain in zip(y,[r,1.,b])]


def forward(x,role):
    if role=='identity':return x.copy(),1.,1.,0.
    under=role.endswith('under')
    p=1/.7 if under else .7
    c=1.08;t=1-c-35/255 if under else 35/255
    raw=[c*v**p+t for v in x]
    if role.startswith('combined'):
        raw=[v+d for v,d in zip(raw,[-10/255,0.,10/255])]
    return raw,p,c,t


def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial probe run')
    protocol=ROOT/'docs/affine-prepower-operator-candidate-2026-11-14.md'
    bindings={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [protocol,Path(__file__)]}
    values=[.35,.40,.45,.50,.55,.60,.65]
    triples=[[values[i],values[(i+2)%7],values[(i+4)%7]] for i in range(7)]
    probes=[dict(kind='ideal' if role in ['identity','exposure_under','exposure_over'] else 'combined',
        role=role,reference=x) for role in ['identity','exposure_under','exposure_over','combined_under','combined_over'] for x in triples]
    probes += [dict(kind='clipping_collision',role=role,reference=[v]*3)
               for role,vs in [('exposure_under',[0.,.05]),('exposure_over',[.9,1.])]
               for v in vs]
    assert len(probes)==39
    OUT.mkdir()
    write('plan_PRIVATE.json',dict(scope='generated_known_parameter_algebra_only',probes=probes,
        input_sha256=bindings,optimizer_calls=0,photo_reads=0,tree_fits=0))
    try:
        records=[];ideal_errors=[];inverse_errors=[];nesting_errors=[]
        for probe in probes:
            x=probe['reference'];raw,p,c,t=forward(x,probe['role']);y=[clip(v) for v in raw]
            params=[1/p,1.,1.,1/c,-t/c]
            recovered=candidate(y,*params)
            quantized=[round(v*255)/255 for v in y]
            quantized_recovered=candidate(quantized,*params)
            error=max(abs(a-b) for a,b in zip(x,recovered))
            if probe['kind']=='ideal':
                assert all(0<=v<=1 for v in raw)
                ideal_errors.append(error)
                if probe['role']!='identity':
                    independent=[math.exp(math.log((v-t)/c)/p) for v in y]
                    inverse_errors.extend(abs(a-b) for a,b in zip(independent,recovered))
            nested=candidate(x,.8,1.1,.9,1.,0.)
            baseline=[clip(v**.8*gain) for v,gain in zip(x,[1.1,1.,.9])]
            nesting_errors.extend(abs(a-b) for a,b in zip(nested,baseline))
            assert all(math.isfinite(v) and 0<=v<=1 for v in recovered+quantized_recovered)
            records.append(dict(**probe,generated_fixture=True,raw_forward=raw,input=y,
                clipped_channels=sum(v<0 or v>1 for v in raw),analytic_controls=params,
                recovered=recovered,max_continuous_error=error,quantized_input=quantized,
                quantized_recovered=quantized_recovered,
                max_quantized_error=max(abs(a-b) for a,b in zip(x,quantized_recovered))))
        assert len(ideal_errors)==21 and max(ideal_errors)<=1e-12
        assert max(inverse_errors)<=1e-12 and max(nesting_errors)<=1e-12
        for role in ['exposure_under','exposure_over']:
            a,b=[r for r in records if r['kind']=='clipping_collision' and r['role']==role]
            assert a['reference']!=b['reference'] and a['input']==b['input'] and a['recovered']==b['recovered']
            assert max(a['max_continuous_error'],b['max_continuous_error'])>0
        write('records_PRIVATE.json',records)
        result=dict(passed=True,status='UNCLIPPED_EXPOSURE_MECHANISM_ONLY_NOT_ADOPTED',
            generated_records=39,ideal_records=21,combined_records=14,collision_records=4,
            maximum_ideal_continuous_error=max(ideal_errors),
            maximum_independent_inverse_error=max(inverse_errors),
            maximum_current_three_control_nesting_error=max(nesting_errors),
            combined_max_continuous_error=max(r['max_continuous_error'] for r in records if r['kind']=='combined'),
            ideal_max_quantized_error=max(r['max_quantized_error'] for r in records if r['kind']=='ideal'),
            clipping_collision_pairs_preserved=2,optimizer_calls=0,tree_fits=0,photo_or_mask_reads=0,
            five_output_method_adopted=False,real_combined_or_learned_correction_qualified=False,input_sha256=bindings)
        assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in bindings.items())
        write('verification_PRIVATE.json',result)
        print(json.dumps(result,indent=2))
    except Exception as error:
        write('failure_PRIVATE.json',dict(error_type=type(error).__name__,error=str(error)))
        raise


if __name__=='__main__':main()
