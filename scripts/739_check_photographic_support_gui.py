"""Generated-only research support queue, shared editor and worker interaction."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
QA=ROOT/'outputs/photographic_support_gui_check_v1'


def prepare():
    import cv2,numpy as np
    from src.demo.labelled_measurement import write,seal,digest
    if QA.exists():raise FileExistsError('Preserve prior GUI check')
    QA.mkdir();folder=QA/'generated_source';folder.mkdir()
    image=np.full((256,256,3),[90,120,160],np.uint8);c=np.zeros((256,256),np.uint8);c[30:220,30:220]=255
    m=np.zeros_like(c);m[60:180,60:180]=255;p=np.zeros_like(c);p[:,:25]=255
    for name,a in [('photo_used.png',image),('correction_mask.png',c),('measurement_mask.png',m),('protected_mask.png',p)]:assert cv2.imwrite(str(folder/name),a)
    np.save(folder/'correction_alpha.npy',(c>0).astype(np.float32),allow_pickle=False)
    write(folder/'report.json',dict(schema_version='truehue_photographic_support_task_v1',case_id='generated_source',frame='generated',
        role='source',face_width=180,generated_fixture=True,method_sha256='generated_only'))
    seal(folder);write(QA/'queue.json',dict(tasks=[dict(case_id='generated_source',folder=folder.name,manifest_sha256=digest(folder/'manifest.json'))],blocked=[]))


def gui():
    import tkinter as tk
    from types import SimpleNamespace
    from src.demo.photographic_support_window import PhotographicSupportQueue
    root=tk.Tk();root.withdraw()
    app=PhotographicSupportQueue(root,QA,str(ROOT/'venv/Scripts/python.exe'),annotations_parent=QA/'annotations',jobs_parent=QA/'jobs')
    root.update()
    try:
        assert app.heading.get().startswith('0/1')
        app.edit();editor=app.editor;editor.window.withdraw();root.update()
        assert editor.research and editor.target.get()=='measurement' and not editor.unlock.get()
        event=SimpleNamespace(x=100*editor.scale,y=100*editor.scale)
        editor.down(event);editor.up(event);assert len(editor.strokes)==1
        editor.undo();assert not editor.strokes
        editor.down(event);editor.up(event);editor.reset();assert not editor.strokes
        editor.down(event);editor.up(event)
        editor.measurement_reviewed.set(True);editor.correction_reviewed.set(True);editor.note.set('Generated GUI check only')
        editor.apply();deadline=time.monotonic()+45
        while editor.process is not None and time.monotonic()<deadline:root.update();time.sleep(.05)
        assert editor.process is None and not editor.window.winfo_exists()
        assert app.heading.get().startswith('1/1')
        reports=list((QA/'annotations').glob('support_*/report.json'));assert len(reports)==1
        r=json.loads(reports[0].read_text());assert r['generated_fixture'] and r['status']=='reviewed_support_pending_admission'
        assert not r['training_admitted'] and r['identity_render_only']
        app.edit();app.editor.window.withdraw();root.update()
        assert app.editor.folder==reports[0].parent
        assert not app.editor.measurement_reviewed.get() and not app.editor.correction_reviewed.get()
        app.editor.cancel()
        (QA/'verification.json').write_text(json.dumps(dict(passed=True,generated_only=True,shared_editor=True,
            draw_undo_reset=True,protected_additions_locked_by_default=True,explicit_two_mask_review=True,
            project_worker_save=True,progress_resume=True,model_calls=0,screenshot=False,visual_layout_review=False),indent=2),encoding='utf-8')
        print('PASS: generated research queue/editor/worker save, locked defaults, dual review, progress/resume')
    finally:root.destroy()


def main():
    p=argparse.ArgumentParser();p.add_argument('--gui',action='store_true');a=p.parse_args()
    if a.gui:gui();return
    prepare();executable=Path(sys.base_prefix).parent/'pythoncore-3.13-64/python.exe';env=os.environ.copy()
    env['TCL_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6';env['TK_LIBRARY']='outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
    result=subprocess.run([str(executable),str(Path(__file__).resolve()),'--gui'],cwd=ROOT,env=env,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (QA/'gui.log').write_text(result.stdout+result.stderr,encoding='utf-8');print(result.stdout+result.stderr);result.check_returncode()


if __name__=='__main__':main()
