"""Independently verify saved residual summaries; no models or image reads."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,math,statistics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/combined_calibration_residual_review_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bindings=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bindings.items())
    summary=read(OUT/'summary_PRIVATE.json');records=read(OUT/'residuals_PRIVATE.json');pairs=read(OUT/'matched_pairs_PRIVATE.json')
    saved={p['case_id']:p for p in read(ROOT/'outputs/combined_reviewed_mst_validation_v1/results_PRIVATE.json')['predictions']}
    assert len(records)==len(saved)==60 and len(pairs)==30
    def close(a,b):assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11),(a,b)
    for r in records:
        assert all(r[k]==v for k,v in saved[r['case_id']].items())
        close(r['candidate_signed_error'],r['candidate_score']-r['label'])
        close(r['comparator_signed_error'],r['comparator_score']-r['label'])
        close(sum(r['saved_affine_shift_terms'].values()),r['candidate_raw']-r['comparator_raw'])
    bycase={r['case_id']:r for r in records}
    for p in pairs:
        a,b=bycase[p['case_600']],bycase[p['case_1200']]
        assert a['subject_id']==b['subject_id']==p['subject_id'] and a['label']==b['label']==p['reference_label']
        assert a['family']==b['family']==p['family']
        close(p['candidate_score_change'],b['candidate_score']-a['candidate_score'])
        close(p['comparator_score_change'],b['comparator_score']-a['comparator_score'])
        close(p['l_star_change'],b['features']['input_mean_l_star']-a['features']['input_mean_l_star'])
    for key,field in [('by_condition','condition'),('by_subject','subject_id'),('by_illumination','illumination')]:
        for value,m in summary[key].items():
            group=[r for r in records if r[field]==value]
            assert len(group)==m['n']
            for prefix in ('candidate','comparator'):
                close(m[prefix+'_signed_bias'],sum(r[prefix+'_score']-r['label'] for r in group)/len(group))
                close(m[prefix+'_MAE'],sum(abs(r[prefix+'_score']-r['label']) for r in group)/len(group))
            assert m['better']==sum(r['candidate_error']<r['comparator_error']-1e-12 for r in group)
            assert m['worse']==sum(r['candidate_error']>r['comparator_error']+1e-12 for r in group)
    for family,m in [('all',summary['pairs'])]+list(summary['pairs_by_family'].items()):
        group=pairs if family=='all' else [p for p in pairs if p['family']==family]
        assert len(group)==m['n']
        for prefix in ('candidate','comparator'):
            close(m[prefix+'_mean_shift'],sum(p[prefix+'_score_change'] for p in group)/len(group))
            assert m[prefix+'_decreases']==sum(p[prefix+'_score_change']<0 for p in group)
    # A separate covariance formula checks within-person-centered correlations.
    for feature,expected in summary['within_subject_centered_error_feature_correlations'].items():
        groups=defaultdict(list)
        for r in records:groups[r['subject_id']].append(r)
        xy=[]
        for group in groups.values():
            mx=statistics.mean(r['features'][feature] for r in group);my=statistics.mean(r['candidate_signed_error'] for r in group)
            xy += [(r['features'][feature]-mx,r['candidate_signed_error']-my) for r in group]
        close(sum(x*y for x,y in xy)/math.sqrt(sum(x*x for x,y in xy)*sum(y*y for x,y in xy)),expected)
    result=dict(passed=True,residuals=60,matched_pairs=30,all_condition_subject_illumination_biases_checked=True,
        affine_shift_checks=60,correlations_checked=4,new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,
        summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result,indent=2)+'\n');print('PASS:60 saved residuals,30 matched pairs,group biases,affine shifts and4 centered correlations;zero fits.')


if __name__=='__main__':main()
