"""Reference-informed RGB error floor for the retained masked gamma/gain family."""
import numpy as np


def irrecoverable_rgb_floor(input_rgb, reference_rgb, application_mask, scoring_mask):
    """Bound RGB MAE, not CIEDE2000, for any positive gamma/R/B gains.

    Outside support pixels are fixed. Inside support zero channels stay zero,
    and green=255 stays 255 because green gain is fixed to one. Other white
    channels are not fixed: their red/blue gains may reduce them. Reference is
    used only for this diagnostic, never for selecting runtime parameters.
    """
    image, reference = np.asarray(input_rgb), np.asarray(reference_rgb)
    application, scoring = np.asarray(application_mask), np.asarray(scoring_mask)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or reference.dtype != np.uint8 or reference.shape != image.shape:
        raise ValueError('Matching uint8 RGB images required')
    if any(m.dtype != bool or m.shape != image.shape[:2] for m in (application, scoring)) or not scoring.any():
        raise ValueError('Matching boolean masks and nonempty scoring region required')
    difference = np.abs(image.astype(float) - reference.astype(float)) / 255
    outside = scoring & ~application
    endpoints = image == 0
    endpoints[:, :, 1] |= image[:, :, 1] == 255
    fixed_endpoints = endpoints & (application & scoring)[:, :, None]
    denominator = int(scoring.sum()) * 3
    support_floor = float(difference[outside].sum() / denominator)
    endpoint_floor = float(difference[fixed_endpoints].sum() / denominator)
    return dict(rgb_mae_lower_bound=support_floor + endpoint_floor,
        outside_support_rgb_mae_floor=support_floor, inside_endpoint_rgb_mae_floor=endpoint_floor,
        scored_pixels=int(scoring.sum()), fixed_inside_channel_samples=int(fixed_endpoints.sum()),
        mismatching_fixed_inside_channel_samples=int((fixed_endpoints & (image != reference)).sum()),
        zero_channel_counts_rgb=[int(((image[:, :, c] == 0) & application & scoring).sum()) for c in range(3)],
        limitation='Lower bound for positive direct gamma/red/blue masked transforms; not a global CIEDE2000 bound or proof of true skin color.')
