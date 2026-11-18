"""Summarize preparation coverage and limitations; never admits or fits a model."""
from pathlib import Path
from collections import Counter
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/expanded_correction_inputs_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'results_PRIVATE.json');v=read(OUT/'verification_PRIVATE.json');assert v['passed']
    old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    nb=read(OUT/'final_input_sha256_PRIVATE.json');common={p:h for p,h in nb.items() if p in old['input_sha256'] and ('src' in Path(p).parts or 'models' in Path(p).parts)}
    assert len(common)>=32 and all(h==old['input_sha256'][p] and sha(p)==h for p,h in common.items())
    rows=d['records'];generated=[r for r in rows if r['recipe']!='clean'];ready=[r for r in generated if r['status']=='available']
    # Each source stays in its role; no condition-dependent resampling.
    failures=Counter('insufficient_skin_pixels' if 'insufficient skin pixels' in r.get('reason','') else r.get('reason','unspecified') for r in generated if r['status']!='available')
    clean=[r for r in rows if r['recipe']=='clean' and r['status']=='available']
    source_counts={r['source_case']:sum(q['source_case']==r['source_case'] for q in ready) for r in clean}
    bylayer={layer:dict(attempts=sum(r['layer']==layer for r in generated),available=sum(r['layer']==layer for r in ready)) for layer in ('core','composite_stress_design')}
    bykey={key:dict(source_references=sum(r['subject_id']==key for r in clean),available_conditions=sum(r['subject_id']==key for r in ready)+sum(r['subject_id']==key for r in clean)) for key in sorted({r['subject_id'] for r in rows})}
    result=dict(technical_preparation_verified=True,scientifically_admitted=False,production_adopted=False,new_fits=0,
        unchanged_runtime_model_bindings=len(common),new_fitting_candidates=len(ready)+len(clean),
        maximum_full_fit_rows_if_all_features_available=len(old['full']['training_cases'])+len(ready)+len(clean),
        sources_with_all_13_distorted_measurements=sum(c==13 for c in source_counts.values()),
        sources_with_no_distorted_measurements=sum(c==0 for c in source_counts.values()),
        by_layer=bylayer,by_publisher_group=bykey,failure_reasons=dict(failures),
        native_measurement_range=[min(r['native_measurement_accounting']['selected_native_grid_locations'] for r in ready),max(r['native_measurement_accounting']['selected_native_grid_locations'] for r in ready)],
        selection_for_fixed_review='All80source underexposure masks plus first frozen source for each other12recipes;92boards, not all1040visual inspections',
        limitations=['Unverified skin coverage/beard/glasses and native sample adequacy.',
                    'Technical failures and repeated conditions are not independent people.',
                    'Eight holdout groups remain byte-unread; no fresh highest interval.',
                    'No learned correction benefit or clean preservation demonstrated by preparation.'],
        result_sha256=sha(OUT/'results_PRIVATE.json'),verification_sha256=sha(OUT/'verification_PRIVATE.json'),script_sha256=sha(Path(__file__)))
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='by_publisher_group'},indent=2))

if __name__=='__main__':main()
