"""Input-only core orchestration with explicit failures and unavailable MST."""
from dataclasses import dataclass
import time
import cv2
import numpy as np
from src.correction.correct_image import correct_from_estimate,LEGACY_POLICY,ESTIMATION_VERSION
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

STAGES=('input','face_detection','skin_mask','measurement','mst','correction')

@dataclass
class CorePipelineResult:
    report: dict
    correction: object=None

class CorePipeline:
    """Dependencies are frozen/injected; no reference image or targets accepted."""
    def __init__(self,detector,mask_estimator,model):
        if getattr(model,'n_features_in_',None)!=len(FEATURES):raise ValueError('Four-feature correction model required')
        if hasattr(model,'feature_names') and tuple(model.feature_names)!=FEATURES:raise ValueError('Feature order mismatch')
        if hasattr(model,'target_names') and tuple(model.target_names)!=TARGETS:raise ValueError('Target order mismatch')
        self.detector=detector;self.mask_estimator=mask_estimator;self.model=model

    def run(self,image_bgr):
        report=dict(status='failed',proposal_complete=False,failed_stage=None,stages={s:dict(status='not_run') for s in STAGES},
            mask_version=ESTIMATION_VERSION,mask_policy=LEGACY_POLICY,
            mst=dict(status='not_run',label=None,config_index=None),
            limitations=['No validated operational ITA-to-MST mapping; correction uses continuous Lab/ITA',
                'Frozen development model; correction quality not established',
                'Paint/makeup protection incomplete; face/visible-neck and Android remain unfinished'])
        stage='input';started=time.perf_counter();stage_started=started
        def complete(name,**details):
            report['stages'][name]=dict(status='success',elapsed_ms=(time.perf_counter()-stage_started)*1000,**details)
        try:
            if not isinstance(image_bgr,np.ndarray) or image_bgr.dtype!=np.uint8 or image_bgr.ndim!=3 or image_bgr.shape[2]!=3 or not image_bgr.size:
                raise ValueError('Nonempty uint8 BGR image required')
            image=image_bgr.copy();complete(stage,width=image.shape[1],height=image.shape[0])
            stage='face_detection';stage_started=time.perf_counter();boxes=self.detector(image)
            report['stages'][stage]['detected_faces']=len(boxes)
            if len(boxes)!=1:raise ValueError('Expected exactly one detected face; found '+str(len(boxes)))
            box=boxes[0]
            if len(box)!=4 or any(isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,np.integer)) for v in box):raise ValueError('Integer face bounds required')
            x,y,w,h=map(int,box)
            if min(x,y)<0 or min(w,h)<=0 or x+w>image.shape[1] or y+h>image.shape[0]:raise ValueError('Face bounds outside image')
            box=(x,y,w,h);complete(stage,detected_faces=1,face_box=list(box))
            stage='skin_mask';stage_started=time.perf_counter();masked=self.mask_estimator(image,box)
            if not masked.landmarks_available:raise ValueError('Required anatomical landmarks unavailable; no mask fallback')
            mask=np.asarray(masked.mask);exclusion=np.asarray(masked.exclusion_mask)
            for value in (mask,exclusion):
                if value.dtype!=np.uint8 or value.shape!=(h,w) or not set(np.unique(value))<={0,255}:raise ValueError('Native crop binary uint8 masks required')
            if np.any((mask>0)&(exclusion>0)):raise ValueError('Skin mask overlaps anatomical exclusions')
            complete(stage,selected_pixels=int(np.count_nonzero(mask)),landmarks_available=True)
            stage='measurement';stage_started=time.perf_counter();stats=compute_masked_lab_statistics(image[y:y+h,x:x+w],mask,1000)
            if not stats['valid']:raise ValueError(stats['reason'])
            features={name:float(stats[key]) for name,key in zip(FEATURES,FEATURE_KEYS)}
            complete(stage,statistics=stats,features=features)
            stage='mst';stage_started=time.perf_counter()
            report['mst']=dict(status='unavailable',label=None,config_index=None,reason='No validated operational ITA-to-MST lookup; no category guessed')
            report['stages'][stage]=dict(report['mst'],elapsed_ms=(time.perf_counter()-stage_started)*1000)
            stage='correction';stage_started=time.perf_counter()
            result=correct_from_estimate(image,box,mask>0,exclusion>0,self.model,LEGACY_POLICY)
            if result.features!=features:raise RuntimeError('Correction feature extraction drifted from measurement stage')
            complete(stage,parameters=result.parameters,selected_pixels=int(result.correction_mask.sum()),outside_mask_unchanged=True)
            report.update(status='development_partial_mst_unavailable',elapsed_ms=(time.perf_counter()-started)*1000)
            return CorePipelineResult(report,result)
        except (ValueError,RuntimeError,cv2.error) as error:
            report['stages'][stage].update(status='failed',reason=str(error),elapsed_ms=(time.perf_counter()-stage_started)*1000)
            report.update(failed_stage=stage,elapsed_ms=(time.perf_counter()-started)*1000)
            return CorePipelineResult(report)
