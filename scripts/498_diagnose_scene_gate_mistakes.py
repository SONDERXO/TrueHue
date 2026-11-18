"""Read-only error attribution; never uses held outcomes to fit or tune a gate."""
from collections import defaultdict
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
PARENT=ROOT/'outputs/scene_gate_comparison_v1';SOURCE=ROOT/'outputs/whole_scene_correction_v1'
OUT=ROOT/'outputs/scene_gate_mistake_diagnosis_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def describe(rr):
    available=[r for r in rr if r.get('gate') is not None];selected=[r for r in available if r['gate']['apply_correction']];missed=[r for r in available if not r['gate']['apply_correction']]
    def gain(r):return r['input_metrics']['rgb8_mae_codes']-r['ungated_metrics']['rgb8_mae_codes']
    return dict(attempts=len(rr),available=len(available),unavailable=len(rr)-len(available),
        corrections=len(selected),noops=len(missed),
        noops_suppressing_rgb_improvement=sum(gain(r)>0 for r in missed),
        noops_avoiding_rgb_harm=sum(gain(r)<0 for r in missed),noops_unchanged_rgb_error=sum(gain(r)==0 for r in missed),
        applied_rgb_improvements=sum(gain(r)>0 for r in selected),applied_rgb_harms=sum(gain(r)<0 for r in selected),
        suppressed_rgb_improvement_sum=float(sum(max(0.,gain(r)) for r in missed)),
        avoided_rgb_harm_sum=float(sum(max(0.,-gain(r)) for r in missed)),
        input_mae=float(np.mean([r['input_metrics']['rgb8_mae_codes'] for r in available])) if available else None,
        ungated_mae=float(np.mean([r['ungated_metrics']['rgb8_mae_codes'] for r in available])) if available else None,
        gated_mae=float(np.mean([r['metrics']['rgb8_mae_codes'] for r in available])) if available else None)


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={}
    for p in [PARENT,SOURCE]:bindings.update({str(p/n):h for n,h in read(p/'sha256.json').items()})
    bindings[str(ROOT/'scripts/498_diagnose_scene_gate_mistakes.py')]=sha(ROOT/'scripts/498_diagnose_scene_gate_mistakes.py')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    value=read(PARENT/'results_PRIVATE.json');records=value['records']['scene_gate'];other={r['case_id']:r for r in value['records']['face_gate']}
    rows={r['case_id']:r for r in read(SOURCE/'prepared_rows_PRIVATE.json')};folds={f['held_key']:f for f in value['folds']}
    recipes=defaultdict(list);layers=defaultdict(list);conditions=defaultdict(list);details=[];falsepositives=[];metricchecks=0
    for r in records:
        source=rows[r['case_id']];recipes[source['case']['id']].append(r);layers[r['layer']].append(r);conditions[r['condition']].append(r)
        if r.get('gate') is None:continue
        apply=r['gate']['apply_correction'];expected=r['ungated_metrics'] if apply else r['input_metrics']
        assert expected==r['metrics'];metricchecks+=1
        gain=r['input_metrics']['rgb8_mae_codes']-r['ungated_metrics']['rgb8_mae_codes']
        cause='applied_useful_correction' if apply and gain>0 else 'applied_harmful_correction' if apply and gain<0 else 'suppressed_useful_correction' if not apply and gain>0 else 'avoided_harmful_correction' if not apply and gain<0 else 'no_rgb_error_difference'
        details.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],condition=r['condition'],recipe=source['case']['id'],
            synthetic_membership_error=(r['layer']=='clean' and apply) or (r['layer']!='clean' and not apply),
            classification=cause,ungated_rgb_gain=gain,logit=r['gate']['logit']))
        if r['layer']=='clean' and apply:
            model=folds[r['subject_id']]['models']['scene_gate']['model'];x=np.array(r['features'])
            contributions=(x-model['mean'])/model['scale']*model['coefficient']
            assert abs(float(contributions.sum())+model['intercept']-r['gate']['logit'])<1e-12
            names=CONTINUOUS_FEATURES+SCENE_FEATURES
            falsepositives.append(dict(case_id=r['case_id'],condition=r['condition'],logit=r['gate']['logit'],mae=r['metrics']['rgb8_mae_codes'],
                intercept=model['intercept'],feature_contributions=dict(zip(names,map(float,contributions))),
                facial_contribution=float(contributions[:5].sum()),scene_contribution=float(contributions[5:].sum()),
                facial_gate_applies=other[r['case_id']]['gate']['apply_correction']))
    summary=dict(total_attempts=len(records),available_metric_attributions=metricchecks,clean_false_positive_explanations=len(falsepositives),
        by_layer={k:describe(rr) for k,rr in layers.items()},by_recipe={k:describe(rr) for k,rr in recipes.items()},
        by_condition={k:describe(rr) for k,rr in conditions.items()},new_fits=0,thresholds_examined=1,thresholds_changed=0,
        interpretation='Posthoc error attribution only; gain sums are sums of case MAEs, not pixel pooled or independent subject effects.')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    OUT.mkdir(parents=True)
    for n,v in [('diagnosis_PRIVATE.json',dict(summary=summary,case_attributions=details,clean_false_positives=falsepositives)),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(dict(metric_attributions=metricchecks,false_positives=len(falsepositives),layers=summary['by_layer'],core_recipes={k:v for k,v in summary['by_recipe'].items() if k.startswith('colour_')}),indent=2))


if __name__=='__main__':main()
