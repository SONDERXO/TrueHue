"""Two fixed input probes with a frozen synthetic-ranking head; no I/O."""
import numpy as np
from .synthetic_exposure_ranking import score, SCHEMA
from .portrait_exposure_quality import exposure_probe


def measure(head, encoder, rgb, cached_base):
    if head.get('schema') != SCHEMA:
        raise ValueError('A synthetic-ranking head is required')
    if not isinstance(rgb, np.ndarray) or rgb.shape != (256, 256, 3) or rgb.dtype != np.uint8:
        raise ValueError('Prepared256RGB8 input required')
    base_vector = np.asarray(cached_base)
    if base_vector.shape != (4096,) or base_vector.dtype != np.float32 or not np.isfinite(base_vector).all():
        raise ValueError('Finite cached4096float32 base required')
    base = score(head, base_vector)
    shifted = {}; vectors = {}; values = {'base': base}
    for name, ev in [('minus', -.5), ('plus', .5)]:
        shifted[name] = exposure_probe(rgb, ev)
        vector = encoder.encode(shifted[name])
        if vector.shape != (4096,) or vector.dtype != np.float32 or not np.isfinite(vector).all():
            raise ValueError('Finite4096float32 encoder response required')
        vectors[name] = vector.copy()
        values[name] = score(head, vector)
    return dict(scores=values, cues=[values['minus'] - base, values['plus'] - base],
                shifted=shifted, vectors=vectors)
