"""Launch the isolated eleven-reference FFHQ support queue."""
from pathlib import Path
import argparse,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def main():
    p=argparse.ArgumentParser();p.add_argument('--compat',action='store_true');p.add_argument('--worker-python',default=str(ROOT/'venv/Scripts/python.exe'));a=p.parse_args()
    import tkinter as tk
    try:root=tk.Tk()
    except tk.TclError:
        if a.compat:raise
        executable=Path(sys.base_prefix).parent/'pythoncore-3.13-64/pythonw.exe';env=os.environ.copy()
        env['TCL_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6';env['TK_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
        subprocess.run([str(executable),str(Path(__file__).resolve()),'--compat','--worker-python',a.worker_python],cwd=ROOT,env=env,check=True);return
    from src.demo.photographic_support_window import PhotographicSupportQueue
    PhotographicSupportQueue(root,ROOT/'outputs/reviewed_ffhq_support_tasks_v1',a.worker_python,annotations_parent=ROOT/'outputs/reviewed_ffhq_support_annotations_v1',jobs_parent=ROOT/'outputs/reviewed_ffhq_support_jobs_v1',drafts_parent=ROOT/'outputs/reviewed_ffhq_support_drafts_v1')
    root.mainloop()

if __name__=='__main__':main()
