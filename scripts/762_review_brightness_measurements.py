"""Launch the research annotation queue, with the installed Tk fallback."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--worker-python', default=str(ROOT / 'venv/Scripts/python.exe'))
    cli.add_argument('--compat', action='store_true')
    args = cli.parse_args()
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError:
        if args.compat:
            raise
        executable = Path(sys.base_prefix).parent / 'pythoncore-3.13-64/pythonw.exe'
        library = ROOT / 'outputs/desktop_tk_compat_20261107_v1/tcl'
        if not executable.is_file() or not library.is_dir():
            raise RuntimeError('Installed compatibility Python/Tcl unavailable')
        env = os.environ.copy()
        env['TCL_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6'
        env['TK_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
        subprocess.run([str(executable), str(Path(__file__).resolve()), '--compat', '--worker-python', args.worker_python],
                       cwd=ROOT, env=env, check=True)
        return
    from src.demo.labelled_measurement_window import MeasurementQueueWindow
    MeasurementQueueWindow(root, ROOT / 'outputs/brightness_measurement_queue_v1', args.worker_python,
        annotations_parent=ROOT / 'outputs/brightness_measurement_annotations_v1',
        jobs_parent=ROOT / 'outputs/brightness_measurement_jobs_v1', compact_controls=True)
    root.mainloop()


if __name__ == '__main__':
    main()
