"""Fixed-parameter/fixed-mask diagnostics; never used to choose inference inputs."""
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000


def region_errors(reference_rgb,output_rgb,source_mask,current_mask):
    """Partition the full image into shared, missed, extra and untouched support.

    Source support is synthetic generation metadata, not human skin truth.
    Empty regions have no mean, rather than an invented zero error.
    """
    reference=np.asarray(reference_rgb);output=np.asarray(output_rgb)
    source=np.asarray(source_mask);current=np.asarray(current_mask)
    if reference.dtype!=np.uint8 or reference.ndim!=3 or reference.shape[2]!=3 or output.dtype!=np.uint8 or output.shape!=reference.shape:
        raise ValueError('Expected matching uint8 RGB images')
    if source.dtype!=bool or current.dtype!=bool or source.shape!=reference.shape[:2] or current.shape!=source.shape:
        raise ValueError('Expected matching boolean masks')
    ref=reference.astype(float)/255;out=output.astype(float)/255
    rgb=np.abs(ref-out).mean(axis=2);delta=deltaE_ciede2000(rgb2lab(ref),rgb2lab(out))
    regions=dict(shared_source_and_current=source&current,source_missed_by_current=source&~current,
                 current_outside_source=current&~source,neither_source_nor_current=~(source|current))
    return {name:dict(pixels=int(mask.sum()),rgb_mae=float(rgb[mask].mean()) if mask.any() else None,
        ciede2000=float(delta[mask].mean()) if mask.any() else None) for name,mask in regions.items()}


def factorial_gaps(errors):
    """Signed metric differences, not percentages of independent error causes.

    Parameter quality can interact with mask coverage; smaller applied support
    can hide wrong-parameter errors. Preserve negative gaps rather than clamp.
    """
    names=('tree_current_mask','known_current_mask','tree_source_mask_oracle','known_source_mask_oracle')
    if any(k not in errors or not np.isfinite(errors[k]) for k in names):raise ValueError('All four finite factorial measurements required')
    tree,known,tree_source,known_source=(float(errors[k]) for k in names)
    return dict(parameter_gap_at_current_mask=tree-known,mask_gap_at_known_parameters=known-known_source,
        parameter_gap_at_source_mask=tree_source-known_source,mask_gap_at_tree_parameters=tree-tree_source,
        parameter_mask_interaction=(tree-known)-(tree_source-known_source),
        tree_above_source_oracle=tree-known_source)
