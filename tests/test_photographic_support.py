from pathlib import Path
import json
import cv2,numpy as np,pytest
from src.demo.photographic_support import save_support
from src.demo.labelled_measurement import seal,write,digest
from src.demo.manual_refinement import verify_export


def task(tmp_path):
    folder=tmp_path/'generated_support';folder.mkdir()
    im=np.full((256,256,3),[90,120,160],np.uint8);c=np.zeros((256,256),np.uint8);c[30:220,30:220]=255
    m=np.zeros_like(c);m[60:180,60:180]=255;p=np.zeros_like(c);p[:,:25]=255
    for name,a in [('photo_used.png',im),('correction_mask.png',c),('measurement_mask.png',m),('protected_mask.png',p)]:assert cv2.imwrite(str(folder/name),a)
    np.save(folder/'correction_alpha.npy',(c>0).astype(np.float32),allow_pickle=False)
    write(folder/'report.json',dict(schema_version='truehue_photographic_support_task_v1',case_id='generated_source',
        frame='generated',role='source',face_width=180,generated_fixture=True,method_sha256='generated_only'))
    seal(folder);return folder


def payload(folder,review='reviewed_selection',strokes=None):
    return dict(schema_version='truehue_photographic_support_edits_v1',base_manifest_sha256=digest(folder/'manifest.json'),
        review=review,measurement_reviewed=True,correction_reviewed=True,strokes=strokes or [],note='generated test')


def test_explicit_unchanged_reviews_and_revision_history_are_immutable(tmp_path):
    folder=task(tmp_path);before={p.name:digest(p) for p in folder.iterdir()}
    out=save_support(folder,payload(folder),tmp_path/'annotations');verify_export(out)
    r=json.loads((out/'report.json').read_text());assert r['status']=='reviewed_support_pending_admission'
    assert r['identity_render_only'] and not r['training_admitted'] and not r['mst_recomputed']
    assert r['task_manifest_sha256']==digest(folder/'manifest.json')
    second=save_support(out,payload(out),tmp_path/'annotations')
    assert second!=out and json.loads((second/'report.json').read_text())['task_manifest_sha256']==r['task_manifest_sha256']
    assert (out/'automatic_measurement_mask.png').read_bytes()==(second/'automatic_measurement_mask.png').read_bytes()
    assert {p.name:digest(p) for p in folder.iterdir()}==before


def test_protected_additions_stay_locked_unless_explicit(tmp_path):
    folder=task(tmp_path)
    stroke=dict(target='both',mode='add',radius=5,unlock=False,points=[[12,100]])
    locked=save_support(folder,payload(folder,strokes=[stroke]),tmp_path/'annotations')
    assert cv2.imread(str(locked/'measurement_mask.png'),0)[100,12]==0
    stroke['unlock']=True
    unlocked=save_support(folder,payload(folder,strokes=[stroke]),tmp_path/'annotations')
    assert cv2.imread(str(unlocked/'measurement_mask.png'),0)[100,12]==255
    assert cv2.imread(str(unlocked/'protected_mask.png'),0)[100,12]==0


def test_invalid_measurement_and_unjudgeable_are_preserved_failures(tmp_path):
    folder=task(tmp_path)
    strokes=[dict(target='measurement',mode='remove',radius=32,unlock=False,points=[[x,y] for x in range(60,181,20) for y in range(60,181,20)])]
    invalid=save_support(folder,payload(folder,strokes=strokes),tmp_path/'annotations')
    assert json.loads((invalid/'report.json').read_text())['status']=='unavailable'
    unjudgeable=save_support(folder,payload(folder,'unjudgeable'),tmp_path/'annotations')
    assert json.loads((unjudgeable/'report.json').read_text())['reason']=='user_unjudgeable'


@pytest.mark.parametrize('bad',['no_confirmation','wrong_manifest','tamper'])
def test_missing_review_or_changed_input_is_rejected(tmp_path,bad):
    folder=task(tmp_path);edits=payload(folder)
    if bad=='no_confirmation':edits['correction_reviewed']=False
    elif bad=='wrong_manifest':edits['base_manifest_sha256']='wrong'
    else:(folder/'measurement_mask.png').write_bytes(b'changed')
    with pytest.raises(ValueError):save_support(folder,edits,tmp_path/'annotations')
    assert not (tmp_path/'annotations').exists()


@pytest.mark.parametrize('confirm',[False,True])
def test_navigation_requires_explicit_skip_of_unsaved_review(monkeypatch,confirm):
    from types import SimpleNamespace
    from src.demo.photographic_support_window import PhotographicSupportQueue
    questions=[];loads=[]
    monkeypatch.setattr('src.demo.photographic_support_window.messagebox.askyesno',lambda *a,**k:questions.append(a) or confirm)
    app=SimpleNamespace(index=0,queue=[dict(manifest_sha256='first'),dict(manifest_sha256='second')],
        saved={},root=None,scan=lambda:None,load=lambda:loads.append(True))
    PhotographicSupportQueue.navigate(app,1)
    assert len(questions)==1
    assert app.index==(1 if confirm else 0) and bool(loads)==confirm


def test_atomic_draft_keeps_strokes_and_reset_without_approving_review(tmp_path):
    from types import SimpleNamespace
    from src.demo.refinement_window import RefinementWindow
    app=SimpleNamespace(research=True,draft_file=tmp_path/'draft.json',strokes=[dict(points=[[1,2]])],pending=None,
        note=SimpleNamespace(get=lambda:'draft note'),manifest_sha='generated',folder=tmp_path)
    RefinementWindow._save_draft(app)
    data=json.loads(app.draft_file.read_text())
    assert data['strokes']==app.strokes and data['status']=='draft_not_reviewed' and data['review_approved'] is False
    assert not app.draft_file.with_suffix('.tmp').exists()
    app.strokes=[]
    RefinementWindow._save_draft(app)
    assert json.loads(app.draft_file.read_text())['strokes']==[]
    RefinementWindow._save_draft(app,'saved',tmp_path/'annotation')
    assert json.loads(app.draft_file.read_text())['status']=='saved'


def test_ordinary_editor_has_no_research_draft_side_effects(tmp_path):
    from types import SimpleNamespace
    from src.demo.refinement_window import RefinementWindow
    app=SimpleNamespace(research=False,draft_file=tmp_path/'draft.json')
    RefinementWindow._save_draft(app)
    assert not app.draft_file.exists()
