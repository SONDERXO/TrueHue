"""Generated-only hidden Tk choice/save/resume check with isolated outputs."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
QA = ROOT / 'outputs/photographic_reference_gui_check_v1'


def prepare():
    import cv2
    import numpy as np
    from src.demo.labelled_measurement import write, seal, digest
    if QA.exists():
        raise FileExistsError('Preserve GUI check')
    QA.mkdir()
    tasks = []
    for i in range(2):
        folder = QA / ('generated_' + str(i))
        folder.mkdir()
        for role in ['source', 'target']:
            assert cv2.imwrite(str(folder / (role + '.png')), np.full((440, 360, 3), [90, 120, 160], np.uint8))
        write(folder / 'task.json', dict(frame=folder.name, generated_fixture=True, correct_person_pair=False))
        seal(folder)
        tasks.append(dict(frame=folder.name, folder=folder.name, issue='generated fixture', manifest_sha256=digest(folder / 'manifest.json')))
    write(QA / 'queue.json', dict(tasks=tasks))


def gui():
    import tkinter as tk
    from src.demo.photographic_reference_window import PhotographicReferenceWindow
    root = tk.Tk()
    root.withdraw()
    app = PhotographicReferenceWindow(root, QA, QA / 'decisions')
    root.update()
    try:
        assert app.choice.get() == '' and app.heading.get().startswith('0/2 saved')
        app.choice.set('too_bright')
        app.note.set('generated GUI check')
        app.save_button.invoke()
        root.update()
        assert app.index == 1 and app.choice.get() == '' and app.heading.get().startswith('1/2 saved')
        app.choice.set('suitable')
        app.save_button.invoke()
        root.update()
        assert app.heading.get().startswith('2/2 saved')
        assert app.status.get().startswith('All reference choices')
        app.navigate(-1)
        assert app.choice.get() == 'too_bright' and app.note.get() == 'generated GUI check'
        rows = [json.loads(p.read_text()) for p in (QA / 'decisions').glob('*/review.json')]
        assert len(rows) == 2 and all(not r['training_admitted'] for r in rows)
        assert all(r['task']['generated_fixture'] for r in rows)
        (QA / 'verification.json').write_text(json.dumps(dict(passed=True, generated_only=True,
            explicit_choices=True, immutable_save=True, navigation_resume=True, completion_count=True,
            model_calls=0, screenshot=False, visual_layout_review=False), indent=2), encoding='utf-8')
        print('PASS: generated reference choices/save/completion/navigation/resume; zero real decisions')
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    args = parser.parse_args()
    if args.gui:
        gui()
        return
    prepare()
    executable = Path(sys.base_prefix).parent / 'pythoncore-3.13-64/python.exe'
    env = os.environ.copy()
    env['TCL_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6'
    env['TK_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
    result = subprocess.run([str(executable), str(Path(__file__).resolve()), '--gui'], cwd=ROOT,
        env=env, capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (QA / 'gui.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    print(result.stdout + result.stderr)
    result.check_returncode()


if __name__ == '__main__':
    main()
