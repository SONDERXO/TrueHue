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
DEMO_NOTICE='Experimental demo: current masks with older correction controls. The model and MST estimate remain unvalidated.'


def build_demo_pipeline(masking='current',glasses='uncertain'):
    runner=import_module('scripts.180_run_development_mst_pipeline')
    pipeline,provenance=runner.build_pipeline(PRESET['experiment'],PRESET['fold_id'])
    if masking not in ('current','legacy'):raise ValueError('Known masking mode required')
    if masking=='current':
        from src.demo.current_masking import CurrentMaskDemoPipeline
        pipeline=CurrentMaskDemoPipeline(pipeline,glasses)
    provenance.update(demo_masking=masking,combined_pipeline_validated=False,
        model_features_measurement_contract_sha256=provenance.get('measurement_contract_sha256'))
    return pipeline,provenance


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
    if stage=='legacy_correction':return 'The new mask succeeded, but the older correction model could not run. '+report.get('reason','No correction was applied.')
    if stage=='current_masking':return 'Current masking could not finish. No correction was applied. '+report.get('reason','Inspect the technical report.')
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
    def message(self):
        if not self.success:return plain_failure(self.result.report)
        if self.result.report.get('manual_refinement'):
            return 'Mask refined by you. Correction controls and MST remain experimental.'
        if self.result.report.get('masking',{}).get('requires_glasses_choice'):
            return 'Finished with glasses protected. Choose clear for transparent lenses or opaque for sunglasses, then rerun.'
        return 'Finished. Compare the trial result with your photo.'


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


def load_refined_run(folder):
    from types import SimpleNamespace
    from src.demo.manual_refinement import verify_export
    folder=Path(folder);verify_export(folder)
    report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
    demo=report['demo']
    result=SimpleNamespace(report=report,image=cv2.imread(str(folder/'photo_used.png')),
        mask=cv2.imread(str(folder/'correction_mask.png'),0),measurement_mask=cv2.imread(str(folder/'measurement_mask.png'),0),
        protected_mask=cv2.imread(str(folder/'protected_mask.png'),0),alpha=np.load(folder/'correction_alpha.npy',allow_pickle=False),
        corrected=cv2.imread(str(folder/'experimental_correction.png')),refinement_export_folder=str(folder))
    return DemoRun(demo['source_path'],demo['source_sha256'],result,report.get('provenance',{}),
        preset=demo['preset'],run_id=demo['run_id'],analyzed_utc=demo['analyzed_utc'])


def skin_overlay(run):
    image=run.result.image;mask=run.result.mask
    if image is None or mask is None or run.result.report.get('measurement',{}).get('status')!='success':return None
    shown=image.copy()
    if mask is not None:
        selected=mask>0
        shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
    return shown


def measurement_overlay(run):
    mask=getattr(run.result,'measurement_mask',None)
    if mask is None:return skin_overlay(run)
    shown=run.result.image.copy();selected=mask>0
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
    if run.result.report.get('manual_refinement') and hasattr(run.result,'refinement_export_folder'):
        import shutil
        from src.demo.manual_refinement import verify_export
        source=Path(run.result.refinement_export_folder);verify_export(source)
        shutil.copytree(source,folder)
        return folder
    folder.mkdir(parents=True,exist_ok=False)
    report=run_report(run)
    (folder/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    for name,image in [('photo_used.png',run.result.image),('skin_mask.png',run.result.mask),
        ('selected_skin.png',skin_overlay(run)),('experimental_correction.png',run.result.corrected if run.success else None),
        ('facial_measurement.png',measurement_overlay(run) if hasattr(run.result,'measurement_mask') else None),
        ('measurement_mask.png',getattr(run.result,'measurement_mask',None)),
        ('correction_mask.png',run.result.mask if hasattr(run.result,'measurement_mask') else None),
        ('protected_mask.png',getattr(run.result,'protected_mask',None))]:
        if image is not None:
            ok,data=cv2.imencode('.png',image)
            if not ok:raise OSError('Could not encode demo image')
            (folder/name).write_bytes(data.tobytes())
    if hasattr(run.result,'alpha'):np.save(folder/'correction_alpha.npy',run.result.alpha,allow_pickle=False)
    manifest=dict(schema_version='truehue_demo_export_v1',run_id=run.run_id,
        saved_utc=datetime.now(timezone.utc).isoformat(),
        files={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
            for p in sorted(folder.iterdir()) if p.is_file()})
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False),encoding='utf-8')
    return folder
