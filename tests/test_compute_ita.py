"""Tests for src.ita_estimation.compute_ita."""

from src.ita_estimation.compute_ita import compute_ita


def test_light_skin():
    """High L*, moderate b* → positive ITA (light skin)."""
    result = compute_ita(70.0, 20.0)
    assert abs(result - 45.0) < 0.01, f"Expected ~45°, got {result}"


def test_medium_skin():
    """L* near 50 → ITA close to 0."""
    result = compute_ita(50.0, 25.0)
    assert abs(result - 0.0) < 0.01, f"Expected ~0°, got {result}"


def test_dark_skin():
    """Low L*, small b* → negative ITA (dark skin)."""
    result = compute_ita(30.0, 15.0)
    assert result < 0, f"Expected negative ITA, got {result}"


def test_zero_b_raises():
    """b* == 0 should raise ValueError."""
    try:
        compute_ita(60.0, 0.0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
