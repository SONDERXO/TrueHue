"""ROI preprocessing and two fixed score differences; no I/O on import."""
import numpy as np
from .portrait_exposure_quality import exposure_probe
from .exposure_quality_training import score


def preprocess_roi(image):
    from PIL import Image
    if not isinstance(image,Image.Image):raise ValueError('Decoded image required')
    return np.asarray(image.convert('RGB').resize((256,256),Image.Resampling.BICUBIC)).copy()


def probe_features(head,encoder,rgb):
    if rgb.shape!=(256,256,3) or rgb.dtype!=np.uint8:raise ValueError('Prepared256RGB8 required')
    base=score(head,encoder.encode(rgb))
    minus=score(head,encoder.encode(exposure_probe(rgb,-.5)))
    plus=score(head,encoder.encode(exposure_probe(rgb,.5)))
    return [minus-base,plus-base],dict(base=base,minus=minus,plus=plus)
