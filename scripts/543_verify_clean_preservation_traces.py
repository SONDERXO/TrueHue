"""Independently replay the audit using raw affine slopes and saved RGB outputs."""
from pathlib import Path
import hashlib,json
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/clean_preservation_trace_audit_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    target=BASE/'verification_PRIVATE.json'
    if target.exists():raise FileExistsError(target)
    binding=read(BASE/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in binding.items())
    audit=read(BASE/'audit_PRIVATE.json')
    models=read(ROOT/'outputs/clean_constrained_gate_models_v1/models_PRIVATE.json')
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    traces=read(ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json')
    comparison=read(ROOT/'outputs/clean_constrained_gate_comparison_v1/results_PRIVATE.json')
    rows={(r['suite'],r['case_id']):r for r in comparison['records']}
    folds={f['held_key']:f for f in models['folds']}
    trace={f['held_key']:f for f in traces['folds']}
    errors={};photo_hashes={}
    for r in audit['clean_records']:
        key=r['suite'],r['case_id'];original=rows[key]
        if r['suite']=='fold_working256':
            fold=folds[r['subject_id']];model=fold['model'];cases=fold['training_cases']
            features={p['case_id']:p['features'] for p in trace[r['subject_id']]['training_trace']}
        else:
            model=models['full_signed'];cases=models['full_training_cases'];features=dict(zip(cases,full['gate_features']))
        near=features[r['nearest_fitting_clean_case']]
        slopes=[c/s for c,s in zip(model['coefficient'],model['scale'])]
        raw_intercept=model['intercept']-sum(a*b for a,b in zip(slopes,model['mean']))
        raw_score=raw_intercept+sum(a*b for a,b in zip(slopes,original['features']))
        assert abs(raw_score-r['score'])<1e-9
        differences=[a*(b-c) for a,b,c in zip(slopes,original['features'],near)]
        np.testing.assert_allclose(differences,list(r['score_delta_by_feature'].values()),rtol=0,atol=1e-10)
        distances=[]
        for i in model['clean_indices']:
            vec=features[cases[i]]
            distances.append(sum(((a-b)/s)**2 for a,b,s in zip(vec,original['features'],model['scale'])))
        assert cases[model['clean_indices'][int(np.argmin(distances))]]==r['nearest_fitting_clean_case']
        folder=ROOT/'outputs/clean_constrained_gate_comparison_v1'/r['suite']/r['case_id']
        image_path=Path(original['image_path']);output_path=folder/'signed.png';ref_path=Path(original['reference_path']);mask_path=Path(original['reference_mask_path'])
        for path in [image_path,output_path,ref_path,mask_path]:photo_hashes[str(path)]=sha(path)
        image=cv2.imread(str(image_path));output=cv2.imread(str(output_path));reference=cv2.imread(str(ref_path));mask=cv2.imread(str(mask_path),0)>0
        assert image is not None and output is not None and reference is not None
        assert int(np.count_nonzero(output!=image))==original['paths']['signed']['changed_channels']
        error=float(np.abs(output.astype(float)-reference.astype(float))[mask].mean())
        assert abs(error-r['actual_rgb_mae'])<1e-10
        errors.setdefault(r['suite'],[]).append(error)
    for suite,values in errors.items():
        assert abs(float(np.mean(values))-audit['summary'][suite]['mean_clean_rgb_mae'])<1e-12
        assert abs(max(values)/sum(values)-audit['summary'][suite]['worst_fraction_of_summed_photo_errors'])<1e-12
    assert len(audit['clean_records'])==52
    assert audit['training_constraint_occurrences']==290 and audit['gate_score_replays']==688
    assert all(sha(p)==h for p,h in binding.items())
    target.write_text(json.dumps(dict(status='pass',clean_rgb_replays=52,raw_affine_decompositions=52,
        independent_nearest_reference_checks=52,source_hashes_unchanged=True,
        predictive_fits=0,image_forwards=0,input_image_sha256=photo_hashes),indent=2),encoding='utf-8')
    print('Verified52RGB/affine/nearest replays; original sources unchanged; no fits or image forwards.')


if __name__=='__main__':main()
