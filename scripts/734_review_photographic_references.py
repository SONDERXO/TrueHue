"""Launch the local eight-pair photographic reference review."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compat', action='store_true')
    args = parser.parse_args()
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError:
        if args.compat:
            raise
        executable = Path(sys.base_prefix).parent / 'pythoncore-3.13-64/pythonw.exe'
        if not executable.is_file():
            raise RuntimeError('Installed Tk compatibility Python unavailable')
        env = os.environ.copy()
        env['TCL_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6'
        env['TK_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
        subprocess.run([str(executable), str(Path(__file__).resolve()), '--compat'], cwd=ROOT, env=env, check=True)
        return
    from src.demo.photographic_reference_window import PhotographicReferenceWindow
    PhotographicReferenceWindow(root, ROOT / 'outputs/photographic_reference_review_v1')
    root.mainloop()


if __name__ == '__main__':
    main()
