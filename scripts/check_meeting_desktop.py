"""Exercise the fallback meeting window with the real demo worker.

Run with installed Python 3.13 and project-relative TCL_LIBRARY / TK_LIBRARY.
Artifacts are private and this check performs no fitting or new-data selection.
"""
import hashlib
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.demo.desktop_compat import CompatDemoApp


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/desktop_meeting_check_20261107_v1')
    parser.add_argument('--no-screenshots',action='store_true',help='Record widget checks only when screen capture is unavailable')
    args=parser.parse_args()
    out = args.output_dir
    out.mkdir(exist_ok=False)
    root = tk.Tk()
    app = CompatDemoApp(root, ROOT/'venv/Scripts/python.exe')

    def wait():
        deadline = time.monotonic()+90
        while app.process is not None:
            root.update()
            if time.monotonic() > deadline:
                raise TimeoutError('Desktop worker timed out')
            time.sleep(.04)
        root.update()

    def capture(name, window):
        window.lift()
        window.update()
        if args.no_screenshots:
            assert window.winfo_viewable()
            return
        time.sleep(.3)
        box = (window.winfo_rootx(), window.winfo_rooty(),
               window.winfo_rootx()+window.winfo_width(), window.winfo_rooty()+window.winfo_height())
        subprocess.run([str(ROOT/'venv/Scripts/python.exe'), '-c',
                        'from PIL import ImageGrab; import sys; ImageGrab.grab(bbox=tuple(map(int,sys.argv[2:]))).save(sys.argv[1])',
                        str(out/name), *map(str, box)], check=True)

    try:
        root.update()
        app.open_example()
        source = app.path
        original = hashlib.sha256(source.read_bytes()).hexdigest()
        app.start()
        wait()
        assert app.export is not None, app.message.cget('text')
        report = json.loads((app.export/'report.json').read_text(encoding='utf-8'))
        assert report['demo']['preset']['experiment'] == 'baseline5'
        assert report['demo']['scientifically_validated'] is False
        assert report['masking_mode']=='current'
        assert report['mst']['measurement_source']=='historical_mask'
        assert (app.export/'facial_measurement.png').exists()
        app.mask_view.set('Facial measurement');app.refresh_mask();root.update()
        app.mask_view.set('Correction area');app.refresh_mask();root.update()
        assert len(app.photos) == 3
        assert str(app.save.cget('state')) == 'normal'
        for widget in [app.choose,app.analyze,app.save,app.metrics]:
            assert widget.winfo_rooty()+widget.winfo_height() <= root.winfo_rooty()+root.winfo_height()
        capture('success.png', root)
        import src.demo.desktop_compat as ui
        ui.filedialog.askdirectory = lambda **kwargs: str(out)
        app.save_files()
        saved = next(out.glob('truehue_demo_*'))
        assert (saved/'manifest.json').exists()
        app.show_progress()
        root.update()
        progress = next(w for w in root.winfo_children() if isinstance(w, tk.Toplevel))
        capture('progress.png', progress)
        progress.destroy()
        app.select(ROOT/'outputs/correction_training_preparation_v1/images/31367_reference.png')
        app.start()
        wait()
        assert app.export is not None
        assert not (app.export/'experimental_correction.png').exists()
        assert 'No clear face' in app.message.cget('text')
        capture('failure.png', root)
        broken = out/'not_photo.png'
        broken.write_bytes(b'not a photo')
        app.select(broken)
        app.start()
        wait()
        assert app.export is None and not app.photos
        assert str(app.save.cget('state')) == 'disabled'
        assert hashlib.sha256(source.read_bytes()).hexdigest() == original
        summary = dict(status='pass', actual_tk_window=True, actual_current_mask_worker=True,
                       separate_mask_views=True, legacy_mst_provenance_preserved=True,
                       screenshots_captured=not args.no_screenshots, visual_review_complete=False,
                       example_has_three_panels=True, export_manifest_preserved=True,
                       no_face_has_no_correction=True, corrupt_file_clears_stale_result=True,
                       original_unchanged=True, new_model_fitted=False)
        (out/'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(json.dumps(summary, indent=2))
    finally:
        app.close()


if __name__ == '__main__':
    main()
