"""Conservative source checks; no inferred low-saturation rejection threshold."""
import numpy as np


def assess_color_reference(image_bgr, *, human_rejected=False):
    """Reject an explicit source rejection or exactly achromatic encoded pixels.

    Equal channels identify exact monochrome, not every filter. Color images
    are not automatically suitable; casts, near-monochrome and source lighting
    still need review. This check supplies no skin tone label.
    """
    image=np.asarray(image_bgr)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8 BGR reference required')
    if not isinstance(human_rejected,bool):raise ValueError('Explicit boolean source decision required')
    exact_achromatic=bool(np.array_equal(image[:,:,0],image[:,:,1]) and np.array_equal(image[:,:,1],image[:,:,2]))
    reasons=[]
    if human_rejected:reasons.append('human_rejected_reference')
    if exact_achromatic:reasons.append('exact_achromatic_reference')
    return dict(status='excluded_reference' if reasons else 'requires_reference_review',
        reasons=reasons,exact_achromatic=exact_achromatic,training_eligible=False,
        limitation='Does not detect every monochrome filter or certify color/reference suitability')
