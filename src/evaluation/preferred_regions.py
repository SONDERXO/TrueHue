"""Fixed-reference regional scoring; never selects regions from predictions."""
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000

REGIONS=('face','neck','brows','lips','peribrow')


def evaluate_regions(reference_rgb,input_rgb,output_rgb,reference_regions,application_mask,*,identity_control=False):
    arrays=[np.asarray(a) for a in (reference_rgb,input_rgb,output_rgb)]
    if any(a.dtype!=np.uint8 or a.ndim!=3 or a.shape[-1]!=3 or a.shape!=arrays[0].shape for a in arrays):
        raise ValueError('Same-shaped uint8 RGB reference/input/output required')
    if set(reference_regions)!=set(REGIONS):raise ValueError('Exactly five reference region masks required')
    shape=arrays[0].shape[:2];union=np.zeros(shape,bool)
    for mask in list(reference_regions.values())+[application_mask]:
        if not isinstance(mask,np.ndarray) or mask.dtype!=bool or mask.shape!=shape:
            raise ValueError('Matching explicit boolean masks required')
    for mask in reference_regions.values():
        if np.any(union&mask):raise ValueError('Reference regions must be disjoint; no double counting')
        union|=mask
    if not union.any():raise ValueError('Nonempty reference generation support required')
    if type(identity_control) is not bool:raise ValueError('Explicit identity-control flag required')
    reference,original,output=arrays
    if identity_control and not np.array_equal(reference,original):raise ValueError('Identity control must be the unchanged reference')
    ref=reference.astype(float)/255;out=output.astype(float)/255
    rgb_error=np.abs(ref-out).mean(axis=2);delta=deltaE_ciede2000(rgb2lab(ref),rgb2lab(out))
    changed=np.any(output!=original,axis=2)
    def score(mask):
        n=int(mask.sum())
        return dict(pixels=n,available=bool(n),rgb_mae=float(rgb_error[mask].mean()) if n else None,
                    ciede2000=float(delta[mask].mean()) if n else None,
                    changed_pixels=int((changed&mask).sum()),
                    generation_pixels_outside_application=int((mask&~application_mask).sum()))
    regions={name:score(reference_regions[name]) for name in REGIONS}
    outside_changes=int((changed&~application_mask).sum())
    return dict(regions=regions,union=score(union),
        changed_pixels=int(changed.sum()),outside_application_changed_pixels=outside_changes,
        outside_application_preserved=outside_changes==0,
        application_pixels_outside_generation=int((application_mask&~union).sum()),
        changed_pixels_outside_generation=int((changed&~union).sum()),
        identity_control=identity_control,clean_gate_pass=(not changed.any()) if identity_control else None,
        limitation='Fixed photographed-reference sRGB reconstruction, not intrinsic color or independent validation.')
