"""Generated GUI geometry and draft recovery check, including a 720px display."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
QA=ROOT/'outputs/photographic_support_visibility_check_v1'


def gui():
    import tkinter as tk
    from tkinter import messagebox
    from types import SimpleNamespace
    from src.demo.photographic_support_window import PhotographicSupportQueue
    from src.demo.refinement_window import RefinementWindow
    root=tk.Tk();root.geometry('820x680+0+0')
    root.winfo_screenheight=lambda:720
    app=PhotographicSupportQueue(root,ROOT/'outputs/photographic_support_gui_check_v1',str(ROOT/'venv/Scripts/python.exe'),
        annotations_parent=QA/'annotations',jobs_parent=QA/'jobs')
    root.update()
    geometry=[]
    def check_visible(editor,label):
        root.update()
        measured=[]
        for widget in [editor.buttons[3],editor.buttons[4],*editor.review_checkbuttons]:
            x=widget.winfo_rootx()-editor.window.winfo_rootx();y=widget.winfo_rooty()-editor.window.winfo_rooty()
            width,height=widget.winfo_width(),widget.winfo_height()
            assert widget.winfo_ismapped(), 'Save/review control not mapped'
            assert x>=0 and y>=0 and x+width<=editor.window.winfo_width() and y+height<=editor.window.winfo_height(), 'Save/review control outside client area'
            measured.append(dict(x=x,y=y,width=width,height=height))
        geometry.append(dict(scenario=label,window_width=editor.window.winfo_width(),window_height=editor.window.winfo_height(),controls=measured))
    try:
        app.edit();editor=app.editor;root.update()
        assert editor.scale==1
        check_visible(editor,'simulated_720px_display')
        editor.window.geometry(f'{editor.window.winfo_width()}x450+20+20');root.update()
        check_visible(editor,'short_450px_window')
        event=SimpleNamespace(x=100,y=100)
        editor.down(event);editor.up(event);editor.note.set('generated recovered draft')
        draft=editor.draft_file
        assert json.loads(draft.read_text())['strokes']==editor.strokes
        editor.cancel();root.update()
        original=messagebox.askyesno;messagebox.askyesno=lambda *a,**k:True
        try:app.edit()
        finally:messagebox.askyesno=original
        editor=app.editor;root.update()
        assert len(editor.strokes)==1 and editor.note.get()=='generated recovered draft'
        assert not editor.measurement_reviewed.get() and not editor.correction_reviewed.get()
        check_visible(editor,'reopened_restored_draft')
        editor.measurement_reviewed.set(True);editor.correction_reviewed.set(True)
        editor.buttons[3].invoke();deadline=time.monotonic()+45
        while editor.process is not None and time.monotonic()<deadline:root.update();time.sleep(.05)
        assert editor.process is None and not editor.window.winfo_exists()
        records=list((QA/'annotations').glob('support_*/report.json'));assert len(records)==1
        record=json.loads(records[0].read_text())
        assert record['generated_fixture'] and record['status']=='reviewed_support_pending_admission'
        assert json.loads(editor.draft_file.read_text())['status']=='saved'
        normal=RefinementWindow(root,ROOT/'outputs/manual_refinement_gui_fixture_v1/truehue_demo_419251b92835',str(ROOT/'venv/Scripts/python.exe'),lambda _:None)
        root.update();assert not normal.research;normal.cancel()
        (QA/'verification.json').write_text(json.dumps(dict(passed=True,generated_only=True,
            save_and_confirmation_controls_visible=True,geometry=geometry,automatic_draft=True,
            close_reopen_recovery=True,restored_draft_not_approved=True,visible_save_button_invoked=True,
            project_worker_saved=True,ordinary_editor_smoke=True,model_calls=0,
            screenshot=False,verification_kind='mapped_widget_geometry_and_interaction'),indent=2),encoding='utf-8')
        print('PASS: mapped save/review controls in 720px and450px scenarios; draft close/reopen recovery; real worker save')
    finally:root.destroy()


def main():
    p=argparse.ArgumentParser();p.add_argument('--gui',action='store_true');a=p.parse_args()
    if a.gui:gui();return
    if QA.exists():raise FileExistsError('Preserve previous visibility check')
    QA.mkdir();executable=Path(sys.base_prefix).parent/'pythoncore-3.13-64/python.exe';env=os.environ.copy()
    env['TCL_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6';env['TK_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
    result=subprocess.run([str(executable),str(Path(__file__).resolve()),'--gui'],cwd=ROOT,env=env,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (QA/'gui.log').write_text(result.stdout+result.stderr,encoding='utf-8');print(result.stdout+result.stderr);result.check_returncode()


if __name__=='__main__':main()
