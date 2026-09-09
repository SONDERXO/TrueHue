"""
Individual Typology Angle (ITA) estimation.

ITA is computed from CIELAB L* and b* values:

    ITA = arctan((L* − 50) / b*) × 180 / π

The angle classifies skin into Fitzpatrick / Monk Skin Tone categories.
"""

from __future__ import annotations

import math


def compute_ita(L: float, b: float) -> float:
    """Compute the Individual Typology Angle.

    Parameters
    ----------
    L : float
        CIE L* (lightness) of the skin patch.
    b : float
        CIE b* (yellow–blue) of the skin patch.

    Returns
    -------
    float
        ITA in degrees, range roughly (−90, 90).

    Raises
    ------
    ValueError
        If ``b`` is zero (undefined angle).

    Examples
    --------
    >>> compute_ita(70.0, 20.0)
    45.0
    """
    if b == 0:
        raise ValueError("b* must not be zero (division by zero).")
    angle_rad = math.atan((L - 50) / b)
    return math.degrees(angle_rad)


if __name__ == "__main__":
    # Quick sanity check
    pairs = [
        (80.0, 30.0),
        (50.0, 25.0),
        (30.0, 15.0),
    ]
    for L, b in pairs:
        print(f"L={L}, b={b}  →  ITA={compute_ita(L, b):.2f}°")
