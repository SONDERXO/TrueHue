"""Launch the local TrueHue desktop demo or run a reproducible headless check."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--analyze-photo',type=Path,help='Run unchanged demo inference for the compatible desktop frontend')
    parser.add_argument('--masking',choices=['current','legacy'],default='current')
    parser.add_argument('--glasses',choices=['clear','opaque','uncertain'],default='uncertain')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/python_demo_smoke_v1')
    args=parser.parse_args()
    if args.analyze_photo is not None:
        import json
        from src.demo.service import build_demo_pipeline,analyze_photo,save_run
        args.output_dir.mkdir(parents=True,exist_ok=False)
        pipeline,provenance=build_demo_pipeline(args.masking,args.glasses)
        run=analyze_photo(args.analyze_photo,pipeline,provenance)
        folder=save_run(run,args.output_dir)
        summary=dict(export=str(folder.resolve()),success=run.success,message=run.message)
        (args.output_dir/'desktop_result.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        return
    if not args.smoke_test:
        # The local 3.14 installation can lack Tcl scripts. Use the installed
        # stdlib-only 3.13 window while keeping all inference in this venv.
        import tkinter
        try:
            probe=tkinter.Tk();probe.withdraw();probe.destroy()
        except tkinter.TclError:
            import subprocess
            import os
            import shutil
            candidates=[Path(sys.base_prefix).parent/'pythoncore-3.13-64'/'pythonw.exe',
                        Path(sys.base_prefix).parent/'pythoncore-3.13-64'/'python.exe']
            executable=next((p for p in candidates if p.is_file()),None)
            if executable is None:raise
            library=ROOT/'outputs/desktop_tk_compat_20261107_v1/tcl'
            if not library.exists():
                shutil.copytree(executable.parent/'tcl',library)
            environment=os.environ.copy()
            # Relative paths also avoid Tcl's native path issue with this
            # workspace's OneDrive alias. Scope these variables to the UI child.
            environment['TCL_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6'
            environment['TK_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
            completed=subprocess.run([str(executable),str(ROOT/'src/demo/desktop_compat.py'),
                '--worker-python',str(ROOT/'venv/Scripts/python.exe')],cwd=ROOT,env=environment)
            if completed.returncode:raise RuntimeError('Compatible desktop window failed to open')
            return
        from src.demo.desktop import launch
        launch();return
    import json
    from src.demo.service import build_demo_pipeline,example_path,analyze_photo,save_run
    if args.output_dir.exists():raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)
    pipeline,provenance=build_demo_pipeline(args.masking,args.glasses)
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
