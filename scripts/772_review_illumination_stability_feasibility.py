"""Feature-geometry feasibility only: no regression, predictions or images."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/illumination_stability_feasibility_v1'
FEATURES=('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star')


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial feasibility review')
    bindings={}
    def read(path):
        path=Path(path);raw=path.read_bytes();bindings[str(path)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    receipt=read(ROOT/'outputs/combined_calibration_residual_review_v1/review_PRIVATE.json')
    assert receipt['passed']
    for p,h in receipt['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    rows=read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')
    assert len(rows)==60 and len({r['subject_id'] for r in rows})==10
    pairs=[]
    for subject in sorted({r['subject_id'] for r in rows}):
        for family in ('F_cool','H_warm','L_warm'):
            own={r['illumination']:r for r in rows if r['subject_id']==subject and r['condition'].rsplit('_',1)[0]==family}
            a,b=own['600'],own['1200']
            assert a['source_mst_exact_decimal']==b['source_mst_exact_decimal']
            pairs.append(dict(subject_id=subject,family=family,case_600=a['case_id'],case_1200=b['case_id'],
                              delta=[b['features'][f]-a['features'][f] for f in FEATURES]))
    def geometry(selected):
        matrix=np.array([r['delta'] for r in selected],float)
        # Invertible column scaling changes numerical conditioning, not the nullspace dimension.
        scale=np.sqrt(np.mean(matrix**2,axis=0));assert np.all(scale>0)
        normalized=matrix/scale
        singular=np.linalg.svd(normalized,compute_uv=False)
        tolerance=max(normalized.shape)*np.finfo(float).eps*singular[0]
        rank=int(np.count_nonzero(singular>tolerance))
        # Save a four-row rank witness for independent scalar verification.
        chosen=[];current=0
        for i in range(len(selected)):
            candidate=normalized[chosen+[i]]
            new=int(np.linalg.matrix_rank(candidate))
            if new>current:chosen.append(i);current=new
            if current==4:break
        return dict(pairs=len(selected),column_rms=scale.tolist(),singular_values=singular.tolist(),rank=rank,
                    rank_tolerance=float(tolerance),condition_number=float(singular[0]/singular[-1]),
                    nullspace_dimension=4-rank,rank_witness_pairs=[selected[i] for i in chosen],
                    normalized_witness_determinant=float(np.linalg.det(normalized[chosen])) if len(chosen)==4 else None)
    overall=geometry(pairs)
    folds={s:geometry([p for p in pairs if p['subject_id']!=s]) for s in sorted({r['subject_id'] for r in rows})}
    families={f:geometry([p for p in pairs if p['family']==f]) for f in ('F_cool','H_warm','L_warm')}
    summary=dict(status='feasibility_review_not_model_selection',features=list(FEATURES),overall=overall,
        nine_subject_fitting_geometry=folds,by_family_geometry=families,
        exact_affine_stability_requires='D beta=0; nonzero column scaling preserves rank. Full rank4 forces beta=0.',
        scope='Global affine raw MST map in these exact four recorded features; not all nonlinear estimators or physical identifiability.',
        implication='Exact paired invariance would force a constant raw affine predictor on these data.',
        clipping_scope='Rank conclusion concerns raw affine outputs; clipping can create constant saturated regions and is not an invariant accurate calibration design.',
        soft_penalty='May trade accuracy against stability; no evidence here of meeting all frozen preservation gates. No penalty value selected or fitted.',
        new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,calibration_admitted=False,runtime_adopted=False,
        next_step='Assess genuinely additional single-photo illumination information and its provenance before selecting another calibration fit; no new input selected.')
    OUT.mkdir()
    for name,value in [('geometry_PRIVATE.json',summary),('pairs_PRIVATE.json',pairs),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(overall=overall,fold_ranks={k:v['rank'] for k,v in folds.items()},family_ranks={k:v['rank'] for k,v in families.items()}),indent=2))


if __name__=='__main__':main()
