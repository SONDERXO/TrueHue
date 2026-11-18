"""Generated log-colour shape rationale only. No optimizer or image files."""
from pathlib import Path
import math,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE=[[.20,.30,.25],[.40,.35,.30],[.60,.50,.45],[.30,.25,.40]]
def scale(source,r=1.,b=1.):return [[x*r,y,z*b] for x,y,z in source]
def descriptor(rgb):
    xy=[[math.log(r/g),math.log(b/g)] for r,g,b in rgb];mu=[math.fsum(p[j] for p in xy)/len(xy) for j in [0,1]]
    centered=[[p[j]-mu[j] for j in [0,1]] for p in xy]
    covariance=[[math.fsum(p[i]*p[j] for p in centered)/len(xy) for j in [0,1]] for i in [0,1]]
    return dict(center=mu,centered=centered,covariance=covariance)
def main():
    out=ROOT/'outputs/source_shape_context_generated_v1'
    if out.exists():raise FileExistsError('Preserve rationale check')
    sources=dict(base=BASE,acceptable_red_shift=scale(BASE,.97),acceptable_blue_shift=scale(BASE,1.,1.03),nonuniform_source_change=[p.copy() for p in BASE])
    sources['nonuniform_source_change'][0][0]*=1.1
    roles=dict(identity=(1.,1.),red_decrease=(245/255,1.),blue_decrease=(1.,245/255),blue_increase=(1.,255/245))
    records=[];checks=0;worst=0.
    for name,source in sources.items():
        before=descriptor(source)
        for role,(r,b) in roles.items():
            image=scale(source,r,b);assert all(0<v<1 for p in image for v in p)
            d=descriptor(image)
            for j,g in enumerate([r,b]):
                error=abs(d['center'][j]-before['center'][j]-math.log(g));assert error<1e-12;checks+=1;worst=max(worst,error)
            for p,q in zip(d['centered'],before['centered']):
                for a,c in zip(p,q):error=abs(a-c);assert error<1e-12;checks+=1;worst=max(worst,error)
            for p,q in zip(d['covariance'],before['covariance']):
                for a,c in zip(p,q):error=abs(a-c);assert error<1e-12;checks+=1;worst=max(worst,error)
            records.append(dict(generated_fixture=True,source=name,role=role,RGB=image,descriptor=d))
    base=descriptor(BASE)
    for name in ['acceptable_red_shift','acceptable_blue_shift']:
        d=descriptor(sources[name]);assert all(abs(a-b)<1e-12 for p,q in zip(base['centered'],d['centered']) for a,b in zip(p,q))
    changed=descriptor(sources['nonuniform_source_change']);assert max(abs(a-b) for p,q in zip(base['centered'],changed['centered']) for a,b in zip(p,q))>1e-3
    assert sources['acceptable_red_shift']==scale(BASE,.97)
    result=dict(engineering_passed=True,records=records,scalar_checks=checks,max_abs_difference=worst,global_gain_invariant=True,source_global_shift_also_removed=True,nonuniform_source_shape_signal=True,
        full_generated_input_collision=dict(acceptable_source_identity=sources['acceptable_red_shift'],base_plus_red_097=scale(BASE,.97),identity_target=[1,1,1],edited_target=[1,1/.97,1],actual_dataset_collision=False),
        qualified_new_input=False,method_selected=False,real_fits=0,new_candidate_predictions=0,photo_arrays=0)
    out.mkdir();(out/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (out/'verification.json').write_text(json.dumps(dict(passed=True,records=16,scalar_checks=checks,max_abs_difference=worst,results_sha256=sha(out/'results.json'),code_sha256=sha(Path(__file__)),protocol_sha256=sha(ROOT/'docs/source-shape-context-generated-protocol-2026-11-13.md'),real_fits=0,photo_arrays=0),indent=2)+'\n',encoding='utf-8')
    print(f'PASS16generated/{checks}scalarchecks/maxerror{worst:.3g}; shape does not identify global source offset; no feature/fit selected')
if __name__=='__main__':main()
