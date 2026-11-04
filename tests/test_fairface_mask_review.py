"""Guard review evidence against drift in the frozen baseline measurements."""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
review = importlib.import_module("15_prepare_fairface_mask_review")


def baseline():
    return dict(skin_pixels="1200", skin_ratio_percent="31.25",
                mean_l_star="40.1234", mean_a_star="10.1234",
                mean_b_star="12.1234", ita_degrees="-39.1234")


def test_comparison_accepts_equivalent_numeric_csv_values():
    stored = baseline()
    assert review.measurement_differences(stored, {k: float(v) for k, v in stored.items()}) == []


def test_comparison_rejects_changed_mask_and_lab_even_when_ita_matches():
    stored = baseline()
    current = dict(stored, skin_pixels=1201, mean_l_star=41)
    assert review.measurement_differences(stored, current) == ["skin_pixels", "mean_l_star"]


def test_comparison_rejects_missing_and_nonfinite_measurements():
    current = baseline()
    del current["mean_b_star"]
    current["ita_degrees"] = float("nan")
    assert review.measurement_differences(baseline(), current) == ["mean_b_star", "ita_degrees"]
