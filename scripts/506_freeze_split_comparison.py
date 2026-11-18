"""Read-only development checkpoint, not model fitting/deployment/ensemble."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/split_comparison_checkpoint_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={}
    for name in ['split_control_comparison_v1','benefit_aware_gate_v1','split_benefit_gate_v1']:
        root=ROOT/'outputs'/name
        for n,h in json.loads((root/'sha256.json').read_text()).items():
            assert sha(root/n)==h;bindings[str(root/n)]=h
    for rel in ['docs/split-control-predictors-results-2026-11-06.md','docs/split-benefit-gate-results-2026-11-06.md',
        'scripts/506_freeze_split_comparison.py','src/model_training/split_control_candidate.py','src/model_training/correction_gate_candidate.py']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    value=dict(status='frozen_development_comparison_only',retained_benchmark='split predictor with previous frozen benefit gate',
        negative_comparison='gate retrained with split-head held benefit labels',models_are='ten fold-specific predictor pairs and gates, not one deployable model',
        all_data_model_fitted=False,ensemble_created=False,scientific_admission=False,runtime_adoption=False,new_evaluation_started=False,
        source_bindings=bindings)
    OUT.mkdir(parents=True);(OUT/'checkpoint_PRIVATE.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'checkpoint_PRIVATE.json':sha(OUT/'checkpoint_PRIVATE.json')},indent=2),encoding='utf-8')
    print('Frozen development comparison bindings; no model fit, ensemble, deployment or new evaluation.')


if __name__=='__main__':main()
