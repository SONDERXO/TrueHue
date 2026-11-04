"""Exercise real Tk widgets with controlled inference/dialogs; no model-quality claims."""
import json
from types import SimpleNamespace
import cv2
import numpy as np
import pytest
import tkinter as tk
from src.demo.desktop import DemoApp


@pytest.fixture
def app():
    root=tk.Tk();root.withdraw()
    instance=DemoApp(root)
    yield instance
    instance.close()


def test_open_run_display_save_and_corrupt_selection_clear_stale_result(app,tmp_path,monkeypatch):
    import src.demo.desktop as desktop
    path=tmp_path/'input.png';image=np.full((20,20,3),100,np.uint8)
    assert cv2.imwrite(str(path),image)
    original=path.read_bytes()
    result=SimpleNamespace(report=dict(status='development_experimental_mst',measurement=dict(status='success',face_count=1),
        mst=dict(label=4),features=dict(input_ita_degrees=20.)),image=image,mask=np.full((20,20),255,np.uint8),corrected=image.copy())
    app.pipeline=SimpleNamespace(run=lambda pixels:result);app.provenance={'experiment':'widget-test'}
    monkeypatch.setattr(desktop.filedialog,'askopenfilename',lambda **kw:str(path))
    monkeypatch.setattr(desktop.filedialog,'askdirectory',lambda **kw:str(tmp_path/'exports'))
    app.choose.invoke();assert str(app.analyze.cget('state'))=='normal'
    app.set_details('old report');app.analyze.invoke()
    assert app.details.get('1.0','end').strip()==''
    assert str(app.save.cget('state'))=='disabled'
    app.future.result(timeout=10);app.poll()
    assert app.run.success and len(app.photos)==3
    assert 'Estimated MST: 4' in app.metrics.cget('text')
    app.save.invoke()
    folders=list((tmp_path/'exports').iterdir());assert len(folders)==1
    assert (folders[0]/'experimental_correction.png').exists()
    assert json.loads((folders[0]/'report.json').read_text())['demo']['scientifically_validated'] is False
    assert path.read_bytes()==original
    broken=tmp_path/'broken.png';broken.write_bytes(b'invalid')
    app.select(broken)
    assert app.run is None and app.path is None
    assert str(app.save.cget('state'))==str(app.analyze.cget('state'))=='disabled'
    assert app.metrics.cget('text')=='' and app.steps.cget('text')==''


def test_failure_export_cancel_and_save_error_allow_retry(app,tmp_path,monkeypatch):
    import src.demo.desktop as desktop
    path=tmp_path/'input.png';image=np.zeros((20,20,3),np.uint8);assert cv2.imwrite(str(path),image)
    result=SimpleNamespace(report=dict(status='failed',failed_stage='face_detection',measurement=dict(face_count=0)),
        image=image,mask=None,corrected=np.ones_like(image))
    app.pipeline=SimpleNamespace(run=lambda pixels:result);app.provenance={}
    app.select(path);app.start();app.future.result(timeout=10);app.poll()
    assert not app.run.success and app.run.result.corrected is None
    assert 'No clear face' in app.message.cget('text')
    assert str(app.save.cget('state'))=='normal'
    monkeypatch.setattr(desktop.filedialog,'askdirectory',lambda **kw:'')
    app.save.invoke();assert not list(tmp_path.glob('truehue_demo_*'))
    errors=[];monkeypatch.setattr(desktop.messagebox,'showerror',lambda *args:errors.append(args))
    blocked=tmp_path/'not_a_folder';blocked.write_text('occupied')
    monkeypatch.setattr(desktop.filedialog,'askdirectory',lambda **kw:str(blocked))
    app.save.invoke();assert errors and app.run is not None
    monkeypatch.setattr(desktop.filedialog,'askdirectory',lambda **kw:str(tmp_path/'retry'))
    app.save.invoke()
    saved=next((tmp_path/'retry').iterdir())
    assert (saved/'report.json').exists() and not (saved/'experimental_correction.png').exists()
    assert str(app.analyze.cget('state'))=='normal'
