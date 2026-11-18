"""Freeze a metadata-only development reservation; does not fit or evaluate."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/reserved_clean_veto_plan_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve fixed plan')
    source=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json';m=json.loads(source.read_text())
    data=ROOT/'outputs/expanded_correction_inputs_v1/results_PRIVATE.json';rows={r['case_id']:r for r in json.loads(data.read_text())['records']}
    oldplan=ROOT/'outputs/expanded_correction_training_plan_v1/plan_PRIVATE.json';closed=json.loads(oldplan.read_text())['closed_holdout_keys']
    seed='TrueHue-reserved-clean-veto-v1:'
    groups=sorted(m['new_publisher_groups'],key=lambda k:(hashlib.sha256((seed+k).encode()).hexdigest(),k))[:8]
    assert len(groups)==8 and not set(groups)&set(closed)
    reserved=[c for c in m['new_fitting_cases'] if rows[c]['subject_id'] in groups]
    clean=[c for c in reserved if rows[c]['recipe']=='clean']
    assert all(any(rows[c]['subject_id']==g for c in clean) for g in groups)
    fits=[]
    for f in m['folds']+[m['full']]:
        kept=[c for c in f['training_cases'] if c not in set(reserved)]
        assert not set(kept)&set(reserved)
        fits.append(dict(held_key=f['held_key'],remaining_fitting_rows=len(kept),remaining_clean_rows=sum(flag for c,flag in zip(f['training_cases'],f['model']['clean']) if c in set(kept))))
    paths=[source,data,oldplan,Path(__file__)]
    result=dict(seed=seed,reserved_development_groups=groups,reserved_all_available_conditions=reserved,reserved_usable_clean=clean,
        reserved_condition_count=len(reserved),reserved_clean_count=len(clean),fits=fits,new_fits=0,holdout_image_reads=0,
        input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    OUT.mkdir();(OUT/'plan_PRIVATE.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(reserved_groups=len(groups),reserved_conditions=len(reserved),reserved_clean=len(clean),full=fits[-1],new_fits=0)))
if __name__=='__main__':main()
