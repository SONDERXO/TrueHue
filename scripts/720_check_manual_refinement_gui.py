"""Exercise the real compatibility editor with a generated fixture, no inference."""
from pathlib import Path
import argparse,json,os,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import tkinter as tk
from src.demo.desktop_compat import CompatDemoApp
from src.demo import refinement_window as editor_module

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--fixture',type=Path,required=True);cli.add_argument('--worker',required=True)
    cli.add_argument('--qa-dir',type=Path,required=True);args=cli.parse_args()
    args.qa_dir.mkdir(parents=True,exist_ok=False)
    root=tk.Tk();app=CompatDemoApp(root,args.worker);root.update()
    app.export=args.fixture;app.refine.configure(state='normal');seen={}
    original=editor_module.open_refinement
    def capture(*a,**kw):seen['editor']=original(*a,**kw);return seen['editor']
    editor_module.open_refinement=capture
    try:
        app.refine.invoke();root.update();editor=seen['editor']
        assert editor.canvas.winfo_width()>=256
        x=128*editor.scale;y=128*editor.scale
        for event,xx in [('<ButtonPress-1>',x),('<B1-Motion>',x+15),('<ButtonRelease-1>',x+15)]:
            editor.canvas.event_generate(event,x=xx,y=y);root.update()
        assert len(editor.strokes)==1
        editor.undo();assert not editor.strokes
        editor.canvas.event_generate('<ButtonPress-1>',x=x,y=y);editor.canvas.event_generate('<ButtonRelease-1>',x=x+15,y=y);root.update()
        editor.reset();assert not editor.strokes and not editor.unlock.get()
        editor.canvas.event_generate('<ButtonPress-1>',x=x,y=y);editor.canvas.event_generate('<ButtonRelease-1>',x=x+15,y=y);root.update()
        assert len(editor.strokes)==1
        captures=[]
        def screenshot(widget,path):
            if captures and not captures[0]['available']:return
            widget.lift();widget.focus_force();root.update();time.sleep(.25)
            bounds=[widget.winfo_rootx(),widget.winfo_rooty(),widget.winfo_rootx()+widget.winfo_width(),widget.winfo_rooty()+widget.winfo_height()]
            code='from PIL import ImageGrab; import json,sys; ImageGrab.grab(bbox=tuple(json.loads(sys.argv[1]))).save(sys.argv[2])'
            completed=subprocess.run([args.worker,'-c',code,json.dumps(bounds),str(path)],cwd=ROOT,capture_output=True,text=True,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            captures.append(dict(path=str(path),available=completed.returncode==0,bounds=bounds))
            if completed.returncode:(args.qa_dir/'screenshot_unavailable.txt').write_text(completed.stderr or completed.stdout,encoding='utf-8')
        screenshot(editor.window,args.qa_dir/'editor.png')
        editor.apply();deadline=time.monotonic()+60
        while app.export==args.fixture and time.monotonic()<deadline:
            root.update();time.sleep(.05)
        assert app.export!=args.fixture,'Worker did not apply edits; inspect editor job log'
        assert not editor.window.winfo_exists()
        report=json.loads((app.export/'report.json').read_text(encoding='utf-8'))
        assert report['manual_refinement']['removed_correction_pixels']>0
        assert report['manual_refinement']['removed_measurement_pixels']>0
        assert not report['manual_refinement']['model_reinferred']
        assert app.message.cget('text').startswith('Mask refined by you')
        screenshot(root,args.qa_dir/'result.png')
        summary=dict(passed=True,generated_fixture=True,new_model_forwards=0,brush_events=True,undo=True,reset=True,
            worker_apply=True,result_display=True,screen_captures=captures,export=str(app.export),report=report['manual_refinement'])
        (args.qa_dir/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print('PASS: actual compatibility UI draw/undo/reset, project-worker apply, display and export; zero inference.')
    finally:
        editor_module.open_refinement=original;root.destroy()
if __name__=='__main__':main()
