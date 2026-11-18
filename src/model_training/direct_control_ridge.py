"""One fixed experimental control regressor; no I/O, fitting or inference on import."""
import numpy as np

WIDTH = 314
ALPHA = 1.0


def fit(records):
    x = np.asarray([r['x314'] for r in records], dtype=np.float64)
    y = np.asarray([r['y'] for r in records], dtype=np.float64)
    if x.shape != (60, WIDTH) or y.shape != (60, 5):
        raise ValueError('Exact60x314 fitting features and60x5 controls required')
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Nonfinite fitting input')
    mean, scale, intercept = x.mean(axis=0), x.std(axis=0), y.mean(axis=0)
    scale[scale == 0] = 1.0
    z = (x - mean) / scale
    centered = y - intercept
    # One joint dual solve. No held examples or feature/penalty selection.
    slopes = z.T @ np.linalg.solve(z @ z.T + ALPHA * np.eye(len(z)), centered)
    return dict(schema='truehue_camera_control_global_ridge_research_v1', width=WIDTH,
                alpha=ALPHA, mean=mean.tolist(), scale=scale.tolist(),
                intercept=intercept.tolist(), slopes=slopes.tolist(),
                fitting_cases=[r['case_id'] for r in records])


def predict(model, x):
    x = np.asarray(x, dtype=np.float64)
    if x.shape != (WIDTH,) or not np.isfinite(x).all():
        raise ValueError('Finite314feature query required')
    return (((x - model['mean']) / model['scale']) @ np.asarray(model['slopes'])
            + model['intercept']).tolist()
