"""Headless demo service; no training, downloads or active-model replacement."""
from dataclasses import dataclass,field
from copy import deepcopy
from datetime import datetime,timezone
from importlib import import_module
import hashlib
import json
from pathlib import Path
import uuid
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PRESET={'experiment':'baseline5','fold_id':1,'model_status':'experimental_failed_quality_gate'}
DEMO_NOTICE='Experimental demo: older ten-source baseline; failed quality checks. The MST estimate is unvalidated.'


def build_demo_pipeline():
    runner=import_module('scripts.180_run_development_mst_pipeline')
    return runner.build_pipeline(PRESET['experiment'],PRESET['fold_id'])


def example_path():
    plan=json.loads((ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1/fit_plan.json').read_text(encoding='utf-8'))
    ids=set(plan['folds'][0]['inner_validation_pair_ids'])
    row=next(r for r in plan['rows'] if r['pair_id'] in ids and r['variant']!='identity')
    return ROOT/row['input_path']


def read_photo(path):
    data=Path(path).read_bytes()
    image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
    if image is None or not image.size:raise ValueError('This file could not be opened as a photo. Choose a JPG or PNG.')
    return image,hashlib.sha256(data).hexdigest()


def plain_failure(report):
    measured=report.get('measurement',{});stage=report.get('failed_stage') or measured.get('stage')
    count=measured.get('face_count')
    if stage=='face_detection':
        if count==0:return 'No clear face was found. Try a front-facing photo with the whole face visible.'
        if isinstance(count,int) and count>1:return 'More than one face was found. Choose a photo with one person.'
        return 'The face could not be located. Try a clearer photo.'
    if stage=='skin_mask':return 'The face details could not be found. Try a sharper photo without hands or hair over the face.'
    if stage=='measurement':return 'Too little usable facial skin was found. Try a clear photo without heavy shadows or objects covering the face.'
    if stage=='mst':return 'The skin-tone estimate is unavailable for this setup.'
    return 'The demo could not finish this photo. You can save the report or try another photo.'


@dataclass
class DemoRun:
    source_path:str
    source_sha256:str
    result:object
    provenance:dict
    preset:dict=field(default_factory=lambda:dict(PRESET))
    run_id:str=field(default_factory=lambda:uuid.uuid4().hex)
    analyzed_utc:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

    @property
    def success(self):return self.result.corrected is not None and self.result.report.get('status')=='development_experimental_mst'

    @property
    def message(self):return 'Finished. Compare the trial result with your photo.' if self.success else plain_failure(self.result.report)


def analyze_photo(path,pipeline,provenance):
    image,sha=read_photo(path)
    result=pipeline.run(image)
    # Never keep a partial correction if a stage reports failure.
    if result.report.get('status')!='development_experimental_mst':result.corrected=None
    return DemoRun(str(Path(path).resolve()),sha,result,deepcopy(provenance))


def run_report(run):
    """Use the run's captured identity, never a later global preset value."""
    return dict(deepcopy(run.result.report),demo=dict(schema_version='truehue_demo_report_v2',
        run_id=run.run_id,analyzed_utc=run.analyzed_utc,preset=deepcopy(run.preset),
        notice=DEMO_NOTICE,source_path=run.source_path,source_sha256=run.source_sha256,
        message=run.message,original_file_modified=False,scientifically_validated=False),
        provenance=deepcopy(run.provenance))


def skin_overlay(run):
    image=run.result.image;mask=run.result.mask
    if image is None or mask is None or run.result.report.get('measurement',{}).get('status')!='success':return None
    shown=image.copy()
    if mask is not None:
        selected=mask>0
        shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
    return shown


def stage_labels(run):
    r=run.result.report;m=r.get('measurement',{})
    valid=m.get('status')=='success'
    face=m.get('face_count')==1
    mask=valid
    mst=r.get('mst') is not None
    return [('Photo opened',run.result.image is not None),('One face found',face),
        ('Skin measured',mask),('Skin-tone estimate ready',mst),('Trial correction ready',run.success)]


def save_run(run,parent):
    folder=Path(parent)/('truehue_demo_'+uuid.uuid4().hex[:12])
    folder.mkdir(parents=True,exist_ok=False)
    report=run_report(run)
    (folder/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    for name,image in [('photo_used.png',run.result.image),('skin_mask.png',run.result.mask),
        ('selected_skin.png',skin_overlay(run)),('experimental_correction.png',run.result.corrected if run.success else None)]:
        if image is not None:
            ok,data=cv2.imencode('.png',image)
            if not ok:raise OSError('Could not encode demo image')
            (folder/name).write_bytes(data.tobytes())
    manifest=dict(schema_version='truehue_demo_export_v1',run_id=run.run_id,
        saved_utc=datetime.now(timezone.utc).isoformat(),
        files={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
            for p in sorted(folder.iterdir()) if p.is_file()})
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False),encoding='utf-8')
    return folder
