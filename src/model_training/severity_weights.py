"""Fitting-only experimental control/severity weights; never inference features."""
import numpy as np


def control_severity_weights(rows):
    if not rows:raise ValueError('Nonempty fitting rows required')
    variants=[r.get('variant') for r in rows]
    if any(v not in ['identity','table2_light','table2_medium','table2_dark'] for v in variants):raise ValueError('Explicit experimental variants required')
    controls=sum(v=='identity' for v in variants);groups=sorted(set(variants)-{'identity'})
    if not controls or not groups:raise ValueError('Both fitting controls and distortions required')
    counts={g:variants.count(g) for g in groups}
    return np.asarray([.5/controls if v=='identity' else .5/len(groups)/counts[v] for v in variants],float)
