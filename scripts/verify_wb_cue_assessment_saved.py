"""Independent saved-coefficient arithmetic; no portrait or model inference."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/wb_cue_portrait_assessment_v2'


def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    dest=OUT/'independent_verification.json'
    if dest.exists():raise RuntimeError('Refuse overwrite')
    vectors=read(OUT/'sealed_features.json');scores=read(OUT/'scored_cues.json');summary=read(OUT/'verification.json')
    assert len(vectors)==len(scores)==66
    assert digest(OUT/'sealed_features.json')==read(OUT/'feature_seal.json')['sha256']==summary['feature_sha256']
    for path,h in read(OUT/'bindings.json').items():assert digest(ROOT/path)==h
    probes=[(.2,.2,.2),(.5,.5,.5),(.8,.8,.8),(.2,.4,.6),(.4,.6,.2),(.6,.2,.4)]
    expected=[]
    for p in probes:
        linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in p]
        adjusted=[min(1,v/g) for v,g in zip(linear,(.85,1,1.15))]
        enc=[12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in adjusted]
        expected.extend([enc[c]/sum(enc)-p[c]/sum(p) for c in (0,2)])
    rows={};error=0
    for vector,saved in zip(vectors,scores):
        assert vector['case_id']==saved['case_id'] and len(vector['coefficients'])==33
        coeff=vector['coefficients'];response=[]
        for r,g,b in probes:
            terms=[r,g,b,r*g,r*b,g*b,r**2,g**2,b**2,r*g*b,1]
            output=[min(1,max(0,math.fsum(terms[j]*coeff[11*c+j] for j in range(11)))) for c in range(3)]
            response.extend([output[c]/sum(output)-(r,g,b)[c]/(r+g+b) for c in (0,2)])
        target=expected if saved['role'] in ('colour_only','combined_under','combined_over') else [0]*12
        observed=math.sqrt(math.fsum((v-t)**2 for v,t in zip(response,target)))
        error=max(error,abs(observed-saved['error']),max(abs(a-b) for a,b in zip(response,saved['cue'])))
        assert error<1e-10
        rows.setdefault(saved['source_id'],{})[saved['role']]=(response,observed)
    assert len(rows)==11 and all(len(v)==6 for v in rows.values())
    mean=math.fsum(item[1] for group in rows.values() for item in group.values())/66
    baseline=math.sqrt(math.fsum(v*v for v in expected))/2
    assert abs(mean-summary['mean_cue_error'])<1e-10 and abs(baseline-summary['zero_cue_baseline'])<1e-10
    means=[]
    for pair in summary['pairs']:
        a,b=pair['pair'];projections=[]
        for sid,group in rows.items():
            p=math.fsum((bv-av)*e for av,bv,e in zip(group[a][0],group[b][0],expected))/math.fsum(v*v for v in expected)
            assert abs(p-next(r['projection'] for r in pair['cases'] if r['source_id']==sid))<1e-10
            projections.append(p)
        means.append(math.fsum(projections)/11)
        assert abs(means[-1]-pair['mean_projection'])<1e-10
    passed=all(v>1e-10 for v in means) and mean<baseline-1e-10
    assert not passed and summary['status']=='NOT_ADVANCED_CUE_PROXY_FAILURE'
    result={'passed':True,'scalar_cases':66,'paired_checks':33,'max_error':error,'gate_reproduced':'NOT_ADVANCED',
            'reference_pixel_reads':0,'portrait_pixel_reads':0,'fits':0}
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
