"""Generated-only hidden Tk interaction and real project-worker check."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
QA = ROOT / 'outputs/labelled_measurement_gui_check_v1'


def prepare():
    import cv2
    import numpy as np
    from src.demo.labelled_measurement import write, seal, digest
    if QA.exists():
        raise FileExistsError('Preserve earlier GUI checks')
    QA.mkdir()
    queue = []
    for index in range(2):
        folder = QA / ('generated_' + str(index))
        folder.mkdir()
        cv2.imwrite(str(folder / 'image.png'), np.full((256, 256, 3), [90, 120, 160], np.uint8))
        cv2.imwrite(str(folder / 'seed.png'), np.zeros((256, 256), np.uint8))
        write(folder / 'task.json', dict(case_id=folder.name, generated_fixture=True, subject_id='generated', method_sha256='generated_only'))
        seal(folder)
        queue.append(dict(case_id=folder.name, task_folder=folder.name, task_manifest_sha256=digest(folder / 'manifest.json'),
                          seed_origin='empty_manual_annotation_start', historical_status='generated_fixture'))
    write(QA / 'queue.json', dict(tasks=queue))


def gui():
    import tkinter as tk
    from src.demo.labelled_measurement_window import MeasurementQueueWindow
    root = tk.Tk()
    root.withdraw()
    app = MeasurementQueueWindow(root, QA, ROOT / 'venv/Scripts/python.exe',
                                 annotations_parent=QA / 'annotations', jobs_parent=QA / 'jobs')
    root.update()
    try:
        assert app.heading.get().startswith('0/2 reviews saved')
        from tkinter import messagebox
        original_question = messagebox.askyesno
        messagebox.askyesno = lambda *a, **k: False
        try:
            app.navigate(1)
            assert app.index == 0, 'Unsaved review must prompt even without brush edits'
        finally:
            messagebox.askyesno = original_question
        app.mode.set('add')
        app.radius.set(24)
        from types import SimpleNamespace
        event = SimpleNamespace(x=100*app.scale, y=100*app.scale)
        app.down(event)
        app.up(event)
        assert len(app.strokes) == 1
        app.undo()
        assert not app.strokes
        app.down(event)
        app.up(event)
        app.reset()
        assert not app.strokes
        app.down(event)
        app.up(event)
        app.note.set('Generated GUI interaction only')
        app.save('reviewed_selection')
        deadline = time.monotonic() + 45
        while app.process is not None and time.monotonic() < deadline:
            root.update()
            time.sleep(.05)
        assert app.process is None, 'Worker timeout'
        records = list((QA / 'annotations').glob('*/annotation.json'))
        assert len(records) == 1
        record = json.loads(records[0].read_text())
        assert record['generated_fixture'] and record['statistics']['valid']
        assert not record['training_admitted'] and not app.dirty
        assert app.heading.get().startswith('1/2 reviews saved')
        app.load()
        assert len(app.strokes) == 1 and app.note.get() == 'Generated GUI interaction only'
        app.navigate(1)
        assert not app.strokes and app.index == 1
        app.save('unjudgeable')
        deadline = time.monotonic() + 45
        while app.process is not None and time.monotonic() < deadline:
            root.update()
            time.sleep(.05)
        assert app.process is None
        records = [json.loads(p.read_text()) for p in (QA / 'annotations').glob('*/annotation.json')]
        assert len(records) == 2 and all(r['generated_fixture'] for r in records)
        assert any(r['reason'] == 'user_unjudgeable' and r['status'] == 'unavailable' for r in records)
        assert app.heading.get().startswith('2/2 reviews saved')
        app.go_to_unsaved()
        assert app.status.get().startswith('All cases have a saved review')
        (QA / 'verification.json').write_text(json.dumps(dict(passed=True, generated_only=True,
            draw_undo_reset=True, project_worker=True, resume=True, navigation=True,
            explicit_review_and_unjudgeable=True, completion_count=True, unsaved_review_prompt=True,
            model_calls=0, screenshot=False,
            visual_layout_review=False), indent=2), encoding='utf-8')
        print('PASS: generated GUI draw/undo/reset, project worker, resume/navigation, unjudgeable')
    finally:
        root.destroy()


def main():
    global QA
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--qa-dir', type=Path, default=QA)
    args = parser.parse_args()
    QA = args.qa_dir.resolve()
    if args.gui:
        gui()
        return
    prepare()
    executable = Path(sys.base_prefix).parent / 'pythoncore-3.13-64/python.exe'
    environment = os.environ.copy()
    environment['TCL_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tcl8.6'
    environment['TK_LIBRARY'] = 'outputs/desktop_tk_compat_20261107_v1/tcl/tk8.6'
    result = subprocess.run([str(executable), str(Path(__file__).resolve()), '--gui', '--qa-dir', str(QA)], cwd=ROOT,
        env=environment, capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (QA / 'gui.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    print(result.stdout + result.stderr)
    result.check_returncode()


if __name__ == '__main__':
    main()
