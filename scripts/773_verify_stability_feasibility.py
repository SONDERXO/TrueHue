"""Stdlib exact-decimal rank witnesses; no fitted models or image reads."""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/illumination_stability_feasibility_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def det(matrix):
    value=Fraction(0)
    for perm in permutations(range(4)):
        sign=(-1)**sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
        term=Fraction(sign)
        for i,j in enumerate(perm):term*=matrix[i][j]
        value+=term
    return value


def main():
    target=OUT/'verification_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve verification')
    bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    d=read(OUT/'geometry_PRIVATE.json');pairs=read(OUT/'pairs_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')}
    assert len(pairs)==30
    exact={}
    for pair in pairs:
        a,b=rows[pair['case_600']],rows[pair['case_1200']]
        assert a['subject_id']==b['subject_id']==pair['subject_id']
        delta=[Fraction(str(b['features'][f]))-Fraction(str(a['features'][f])) for f in d['features']]
        for x,y in zip(pair['delta'],delta):assert math.isclose(x,float(y),abs_tol=1e-12)
        exact[(pair['subject_id'],pair['family'])]=delta
    groups=[('all',d['overall'],pairs)]
    groups += [('held_'+s,g,[p for p in pairs if p['subject_id']!=s]) for s,g in d['nine_subject_fitting_geometry'].items()]
    groups += [(f,g,[p for p in pairs if p['family']==f]) for f,g in d['by_family_geometry'].items()]
    witnesses={}
    for key,g,selected in groups:
        witness=g['rank_witness_pairs'];assert len(witness)==4
        assert all(p in selected for p in witness)
        value=det([exact[(p['subject_id'],p['family'])] for p in witness])
        assert value!=0 and g['rank']==4 and g['nullspace_dimension']==0
        normalized=float(value)/math.prod(g['column_rms'])
        assert math.isclose(normalized,g['normalized_witness_determinant'],rel_tol=1e-10,abs_tol=1e-10)
        witnesses[key]=str(value)
        for i,scale in enumerate(g['column_rms']):
            expected=math.sqrt(sum(float(exact[(p['subject_id'],p['family'])][i])**2 for p in selected)/len(selected))
            assert math.isclose(scale,expected,rel_tol=1e-12,abs_tol=1e-12)
    result=dict(passed=True,exact_decimal_pair_checks=30,nonzero_exact_four_by_four_rank_witnesses=witnesses,
        rank_four_geometry_checks=len(groups),new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,
        scope='Exact rank of recorded rounded decimal feature differences; not robustness to measurement uncertainty or physical impossibility.',
        geometry_sha256=sha(OUT/'geometry_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    target.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:30 exact-decimal pairs;14 nonzero exact determinant rank witnesses (all,10folds,3families);zero fits.')


if __name__=='__main__':main()
