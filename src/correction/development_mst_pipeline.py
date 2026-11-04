"""Explicit experimental MST orchestration; never the default runtime model."""
from dataclasses import dataclass
import time
import cv2
import numpy as np
from src.ita_estimation.square_measurement import measure
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.chroma_distribution import ADDITIONS,chroma_distribution_features
from src.evaluation.correction_prototype import apply_correction


@dataclass
class DevelopmentMSTResult:
    report:dict
    image:object=None
    mask:object=None
    corrected:object=None


class DevelopmentMSTPipeline:
    """Input-only dependencies; explicit measured-contract and feature checks."""
    def __init__(self,detector,masker,lookup,model,measurement_contract_sha256):
        if lookup.measurement_contract_sha256!=measurement_contract_sha256:
            raise ValueError('Measurement contract mismatch')
        names=tuple(getattr(model,'feature_names',()))
        if names not in [tuple(MST_FEATURES),tuple(MST_FEATURES)+ADDITIONS]:
            raise ValueError('Explicit five/nine-feature development schema required')
        if tuple(getattr(model,'target_names',()))!=tuple(TARGETS):raise ValueError('Target schema mismatch')
        self.detector=detector;self.masker=masker;self.lookup=lookup;self.model=model;self.names=names
        self.identity=measurement_contract_sha256

    def run(self,image):
        started=time.perf_counter();timings={}
        report=dict(status='failed',proposal_complete=False,experimental=True,quality_gate_passed=False,
            measurement_contract_sha256=self.identity,mst=None,features=None,parameters=None,failed_stage=None,
            limitations=['Experimental MST mapping, not validated production categories',
                'Development correction candidate failed quality gate; no deployment claim',
                'Photographic color, clipping and support limits; face only, no neck/Android integration'])
        def timed(name,fn,*args):
            before=time.perf_counter()
            try:return fn(*args)
            finally:timings[name]=(time.perf_counter()-before)*1000
        measured=timed('square_measurement',measure,image,
            lambda im:timed('face_detection',self.detector,im),
            lambda im,box:timed('skin_mask',self.masker,im,box))
        report['measurement']=measured.report
        result=DevelopmentMSTResult(report,measured.image,measured.mask)
        stage=measured.report['stage']
        try:
            if measured.report['status']!='success':raise ValueError(measured.report.get('reason','Measurement failed'))
            stage='mst';features=dict(measured.report['features'])
            label=timed('mst_lookup',self.lookup.label,features['input_ita_degrees'])
            report['mst']=dict(status='experimental_not_final_validated',label=label,config_index=label-1)
            features['input_mst_index']=label-1
            if len(self.names)==9:
                stage='distribution_features'
                extra=timed('distribution_features',chroma_distribution_features,measured.image,measured.mask>0)
                if not extra['valid']:raise ValueError(extra['reason'])
                features.update(extra['features'])
            report['features']=features
            stage='tree_prediction';parameters=timed('tree_prediction',self.model.predict_one,[features[k] for k in self.names])
            values=np.asarray(parameters,float)
            if values.shape!=(3,) or not np.isfinite(values).all() or np.any(values<=0):raise ValueError('Positive finite three-parameter prediction required')
            stage='application'
            corrected=timed('application',apply_correction,cv2.cvtColor(measured.image,cv2.COLOR_BGR2RGB),measured.mask>0,parameters)
            result.corrected=cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR)
            if not np.array_equal(result.corrected[measured.mask==0],measured.image[measured.mask==0]):raise RuntimeError('Outside-support pixel change')
            report.update(status='development_experimental_mst',parameters=list(map(float,values)),application_pixels=int(np.count_nonzero(measured.mask)))
        except (ValueError,TypeError,RuntimeError,cv2.error) as error:
            report.update(failed_stage=stage,reason=str(error))
        report['timings_ms']=timings
        report['elapsed_ms']=(time.perf_counter()-started)*1000
        report['timing_note']='Wall-clock Python execution; total includes nested measurement. Stage times overlap; not Android latency.'
        return result
