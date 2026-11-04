"""Exercise our own Tk window with actual inference; save local QA screenshots."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import tkinter as tk
from PIL import ImageGrab
from src.demo.desktop import DemoApp,enable_dpi_awareness
from src.demo.service import example_path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/python_demo_window_check_v1')
    out=parser.parse_args().output_dir
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);enable_dpi_awareness();root=tk.Tk();app=DemoApp(root)
    root.update()
    def wait():
        deadline=time.monotonic()+50
        while app.future is not None:
            root.update()
            if time.monotonic()>deadline:raise TimeoutError('GUI inference did not finish')
            time.sleep(.03)
        root.update()
    def screenshot(name):
        root.update();root.lift();root.update();time.sleep(.2)
        x,y=root.winfo_rootx(),root.winfo_rooty()
        assert x+root.winfo_width()<=root.winfo_screenwidth()
        assert y+root.winfo_height()<=root.winfo_screenheight()
        ImageGrab.grab(bbox=(x,y,x+root.winfo_width(),y+root.winfo_height())).save(out/name)
    try:
        sample=example_path();before=hashlib.sha256(sample.read_bytes()).hexdigest()
        app.select(sample);app.start();wait()
        assert app.run is not None and app.run.success
        assert str(app.save['state'])=='normal'
        screenshot('success.png')
        app.details_visible.set(True);app.toggle_details();root.update()
        assert app.details_window.winfo_viewable()
        assert 'development_experimental_mst' in app.details.get('1.0','end')
        app.hide_details();root.update()
        bad=out/'not_a_photo.png';bad.write_bytes(b'not a photo')
        app.select(bad);root.update()
        assert app.run is None and app.path is None and str(app.save['state'])=='disabled'
        assert str(app.analyze['state'])=='disabled'
        app.select(ROOT/'outputs/correction_training_preparation_v1/images/31367_reference.png')
        app.start();wait()
        assert not app.run.success and app.run.result.corrected is None
        assert 'No clear face' in app.message['text']
        screenshot('failure.png')
        assert hashlib.sha256(sample.read_bytes()).hexdigest()==before
        summary=dict(status='pass',actual_tk_window=True,actual_pipeline_in_worker=True,
            example_completes=True,corrupt_selection_clears_old_result=True,
            failed_photo_has_clear_message_and_no_correction=True,original_example_unchanged=True,
            model_quality='experimental only; this is GUI/integration verification, not correction validation')
        (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print(json.dumps(summary,indent=2))
    finally:app.close()


if __name__=='__main__':main()
