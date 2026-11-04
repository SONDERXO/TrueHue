"""Launch the local TrueHue desktop demo or run a reproducible headless check."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/python_demo_smoke_v1')
    args=parser.parse_args()
    if not args.smoke_test:
        from src.demo.desktop import launch
        launch();return
    import json
    from src.demo.service import build_demo_pipeline,example_path,analyze_photo,save_run
    if args.output_dir.exists():raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)
    pipeline,provenance=build_demo_pipeline()
    success=analyze_photo(example_path(),pipeline,provenance)
    assert success.success,success.result.report
    good=save_run(success,args.output_dir)
    failed=analyze_photo(ROOT/'outputs/correction_training_preparation_v1/images/31367_reference.png',pipeline,provenance)
    assert not failed.success and failed.result.corrected is None
    bad=save_run(failed,args.output_dir)
    assert not (bad/'experimental_correction.png').exists()
    summary=dict(status='pass',example_success=success.success,known_failure_rejected=True,
        success_output=str(good),failure_output=str(bad),failure_message=failed.message,
        model='fixed historical baseline5 fold1; failed quality gate, not a finished model',
        trained_new_model=False,active_assets_changed=False)
    (args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
