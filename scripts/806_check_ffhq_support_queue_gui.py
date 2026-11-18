"""Generated-only visible-control and isolated worker/draft/resume check."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
QA=ROOT/'outputs/reviewed_ffhq_support_gui_check_v2'

def gui():
    import tkinter as tk
    from types import SimpleNamespace
    from src.demo.photographic_support_window import PhotographicSupportQueue
    root=tk.Tk();root.geometry('800x640+0+0');root.winfo_screenheight=lambda:720
    kwargs=dict(annotations_parent=QA/'annotations',jobs_parent=QA/'jobs',drafts_parent=QA/'drafts')
    app=PhotographicSupportQueue(root,QA/'package',str(ROOT/'venv/Scripts/python.exe'),**kwargs);root.update()
    try:
        assert app.photo.width()==256 and app.photo.height()==256
        assert '904' not in app.warning.get() and '29863 excluded' in app.warning.get()
        assert app.edit_button.winfo_ismapped() and app.edit_button.winfo_y()+app.edit_button.winfo_height()<=app.edit_button.master.winfo_height()
        app.edit();e=app.editor;root.update();assert e.scale==1
        e.window.geometry(f'{e.window.winfo_width()}x450+20+20');root.update()
        for w in [e.buttons[3],e.buttons[4],*e.review_checkbuttons]:
            y=w.winfo_rooty()-e.window.winfo_rooty();assert w.winfo_ismapped() and y>=0 and y+w.winfo_height()<=e.window.winfo_height()
        e.down(SimpleNamespace(x=110,y=110));e.up(SimpleNamespace(x=110,y=110));e.note.set('generated-only FFHQ queue smoke')
        assert e.draft_file.parent.parent==QA/'drafts'
        e.measurement_reviewed.set(True);e.correction_reviewed.set(True);e.buttons[3].invoke()
        deadline=time.monotonic()+45
        while e.process is not None and time.monotonic()<deadline:root.update();time.sleep(.05)
        assert e.process is None and not e.window.winfo_exists()
        reports=list((QA/'annotations').glob('support_*/report.json'));assert len(reports)==1
        report=json.loads(reports[0].read_text());assert report['generated_fixture'] and report['measurement_review']=='user_reviewed' and report['correction_review']=='user_reviewed'
        assert json.loads(e.draft_file.read_text())['status']=='saved'
        app.scan();assert len(app.saved)==1
        root.destroy();root=tk.Tk();root.withdraw()
        resumed=PhotographicSupportQueue(root,QA/'package',str(ROOT/'venv/Scripts/python.exe'),**kwargs);assert len(resumed.saved)==1
        (QA/'verification.json').write_text(json.dumps(dict(passed=True,generated_only=True,compact_256_queue=True,save_review_controls_in_450px_window=True,paint_worker_save=True,separate_annotation_jobs_drafts=True,resume=True,screenshot=False,real_annotations_created=0),indent=2)+'\n')
        print('PASS: generated-only compact queue, mapped save controls, paint/worker/save/draft/resume; no screenshot claim.')
    finally:root.destroy()

def main():
    p=argparse.ArgumentParser();p.add_argument('--gui',action='store_true');a=p.parse_args()
    if a.gui:gui();return
    if QA.exists():raise FileExistsError('Preserve existing GUI QA')
    QA.mkdir();shutil.copytree(ROOT/'outputs/photographic_support_gui_check_v1',QA/'package')
    q=json.loads((QA/'package/queue.json').read_text());q['presentation']=json.loads((ROOT/'outputs/reviewed_ffhq_support_tasks_v1/queue.json').read_text())['presentation'];(QA/'package/queue.json').write_text(json.dumps(q,indent=2))
    env=os.environ.copy();env['TCL_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6';env['TK_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
    executable=Path(sys.base_prefix).parent/'pythoncore-3.13-64/python.exe'
    r=subprocess.run([str(executable),str(Path(__file__).resolve()),'--gui'],cwd=ROOT,env=env,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (QA/'gui.log').write_text(r.stdout+r.stderr);print(r.stdout+r.stderr);r.check_returncode()

if __name__=='__main__':main()
