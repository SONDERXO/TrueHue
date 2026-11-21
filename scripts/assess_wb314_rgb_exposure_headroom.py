"""Assess one RGB exposure rule using the saved WB314 development inputs."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.correction.original_resolution import render_original_rgb8
from src.evaluation.directional_recoverability import metrics
from src.model_training.luminance_chroma_operator import W, decode, render_rgb8
from src.model_training.rgb_exposure_headroom import cap_facial_rgb_exposure

OUT = ROOT / "outputs"
DEST = OUT / "wb314_rgb_exposure_headroom_v1"
ARCHIVE = OUT / "wb314_facial_headroom_assessment_v1"
PHONE = OUT / "wb314_phone_headroom_followup_v1" / "research_run"
SOURCE = OUT / "wb314_phone_exposure_component_v1" / "phone_input.png"
MODEL = OUT / "wb314_final_training_v1" / "model.json"
PRIORITY_PAIRS = (1, 2, 11, 16)
TOLERANCE = 1e-10


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    with path.open("x", encoding="utf-8") as target:
        json.dump(value, target, indent=2, allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_image(path, grayscale=False):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read bound image: {Path(path).name}")
    return image if grayscale else image[..., ::-1]


def new_full_count(image, output, chosen):
    return int(np.count_nonzero(chosen & ~np.any(image == 255, axis=-1) & np.any(output == 255, axis=-1)))


def main():
    prior_receipt = read(ARCHIVE / "verification.json")
    for name in ("bindings.json", "summary.json", "controls_sealed.json"):
        assert sha(ARCHIVE / name) == prior_receipt["artifacts"][name]
    assert not read(ARCHIVE / "summary.json")["passed"]
    phone = read(PHONE / "report.json")
    assert phone["status"] == "research_output_ready" and sha(SOURCE) == phone["source_sha256"]
    assert sha(MODEL) == phone["model_sha256"] == read(ARCHIVE / "summary.json")["model_sha256"]
    phone_manifest = read(PHONE / "manifest.json")
    for name in ("measurement_mask.png", "original_application_alpha.npy",
                 "original_protected_mask.png", "primary_correction.png", "report.json"):
        assert sha(PHONE / name) == phone_manifest["artifacts"][name]
    bindings = read(ARCHIVE / "bindings.json")
    archive = {(row["group"], row["key"]): row for row in read(ARCHIVE / "controls_sealed.json")["records"]}
    references = read(OUT / "wb314_brightness_triage_v1" / "refinement_baseline_PRIVATE.json")["reference_checks"]
    assert Counter(row["role"] for row in references) == {
        "identity": 11, "exposure_under": 11, "combined_under": 11
    }
    cases = [(row["role"], archive["final66", row["case_id"]]) for row in references]
    cases.extend((f"pair_{pair:02d}", archive["normal20", f"image_pair_{pair:02d}"])
                 for pair in PRIORITY_PAIRS)
    for _, row in cases:
        for name in ("input_path", "old_output_path"):
            assert sha(row[name]) == bindings[row[name]]
        if row["measurement_kind"] == "png":
            assert sha(row["measurement_path"]) == bindings[row["measurement_path"]]

    DEST.mkdir(exist_ok=False)
    write(DEST / "plan_PRIVATE.json", {
        "rule": "One shared gain per image, using rendered RGB8 thresholds in measured, unprotected application pixels.",
        "color_reference": "Exclude pixels already full in the input or the same colour correction at unit gain.",
        "phone_source_sha256": sha(SOURCE), "model_sha256": sha(MODEL),
        "rule_sha256": sha(ROOT / "src/model_training/rgb_exposure_headroom.py"),
        "execution_sha256": sha(Path(__file__)),
        "cases": [dict(role=role, key=row["key"]) for role, row in cases],
        "gate_phone_and_pairs_01_02": "Gain and newly full RGB8 pixels decrease. Phone median brightness lift also decreases.",
        "gate_identities_and_pairs_11_16": "Exact saved output.",
        "gate_underexposure": "Each role's mean RGB and CIEDE2000 no worse than baseline; no baseline improvement vs input lost in either metric.",
        "error_tolerance": TOLERANCE,
        "all_cases_gate": "Exact protected/outside pixels and dimensions, gamma and colour controls retained."
    })

    full = load_image(SOURCE)
    baseline = load_image(PHONE / "primary_correction.png")
    alpha = np.load(PHONE / "original_application_alpha.npy", allow_pickle=False, mmap_mode="r")
    protected = load_image(PHONE / "original_protected_mask.png", True) > 0
    face = load_image(PHONE / "measurement_mask.png", True)
    measured = cv2.resize(face, full.shape[:2][::-1], interpolation=cv2.INTER_NEAREST) > 0
    raw = np.array(phone["controls"])
    trial = cap_facial_rgb_exposure(full, measured, alpha, protected, raw)
    assert np.array_equal(raw[[0, 2, 3, 4]], trial[[0, 2, 3, 4]])
    candidate = render_original_rgb8(full, alpha, protected, trial)
    chosen = (alpha > 0) & ~protected
    assert candidate.shape == baseline.shape == full.shape
    assert np.array_equal(candidate[~chosen], full[~chosen])
    common = chosen & ~np.any(full == 255, axis=-1) & np.any(full != 0, axis=-1)
    start_light = decode(full[common] / 255.0) @ W
    old_lift = float(np.median((decode(baseline[common] / 255.0) @ W) / start_light - 1) * 100)
    new_lift = float(np.median((decode(candidate[common] / 255.0) @ W) / start_light - 1) * 100)
    phone_result = {
        "original_gain": raw[1], "candidate_gain": trial[1],
        "original_new_full_pixels": new_full_count(full, baseline, chosen),
        "candidate_new_full_pixels": new_full_count(full, candidate, chosen),
        "original_median_brightness_lift_percent": old_lift, "candidate_median_brightness_lift_percent": new_lift,
        "dimensions": list(full.shape[:2][::-1]), "outside_and_protected_match": True
    }
    path = DEST / "phone_rgb_headroom_trial.png"
    assert cv2.imwrite(str(path), candidate[..., ::-1])
    assert np.array_equal(load_image(path), candidate)

    result_rows = []
    for role, row in cases:
        with np.load(row["input_path"], allow_pickle=False) as packed:
            image, alpha, protected = (packed[k] for k in ("input", "alpha", "protected"))
            reference = packed["reference"] if role in ("exposure_under", "combined_under") else None
            measured = (packed["measurement"] > 0 if row["measurement_kind"] == "npz"
                        else load_image(row["measurement_path"], True) > 0)
        with np.load(row["old_output_path"], allow_pickle=False) as packed:
            baseline = packed["candidate"]
        raw = np.array(row["controls"])
        trial = cap_facial_rgb_exposure(image, measured, alpha, protected, raw)
        assert np.array_equal(raw[[0, 2, 3, 4]], trial[[0, 2, 3, 4]])
        candidate = render_rgb8(image, alpha, protected, trial)
        chosen = (alpha > 0) & ~protected
        assert candidate.shape == baseline.shape == image.shape
        assert np.array_equal(candidate[~chosen], image[~chosen])
        result = {
            "role": role, "key": row["key"], "original_gain": raw[1], "candidate_gain": trial[1],
            "baseline_exact": bool(np.array_equal(candidate, baseline)),
            "original_new_full_pixels": new_full_count(image, baseline, chosen),
            "candidate_new_full_pixels": new_full_count(image, candidate, chosen)
        }
        if reference is not None:
            result.update(input_error=metrics(image, reference, chosen),
                          baseline_error=metrics(baseline, reference, chosen),
                          candidate_error=metrics(candidate, reference, chosen))
        result_rows.append(result)

    write(DEST / "case_results_PRIVATE.json", result_rows)
    by_role = defaultdict(list)
    for item in result_rows:
        by_role[item["role"]].append(item)
    under = {}
    for role in ("exposure_under", "combined_under"):
        group = by_role[role]
        under[role] = {
            "exact_outputs": sum(row["baseline_exact"] for row in group),
            "cases": len(group),
            "mean_baseline": {k: float(np.mean([row["baseline_error"][k] for row in group])) for k in ("DE", "RGB")},
            "mean_candidate": {k: float(np.mean([row["candidate_error"][k] for row in group])) for k in ("DE", "RGB")},
            "improvements_lost": {
                k: sum((row["baseline_error"][k] < row["input_error"][k] - TOLERANCE
                        and row["candidate_error"][k] >= row["input_error"][k] - TOLERANCE) for row in group)
                for k in ("DE", "RGB")
            }
        }

    def clips_reduced(row):
        return (1 <= row["candidate_gain"] < row["original_gain"]
                and row["candidate_new_full_pixels"] < row["original_new_full_pixels"])

    pairs = {role: by_role[role][0] for role in ("pair_01", "pair_02", "pair_11", "pair_16")}
    gates = dict(
        phone_clipping_and_lift_reduced=clips_reduced(phone_result) and new_lift < old_lift,
        pairs_01_and_02_clipping_reduced=all(clips_reduced(pairs[role]) for role in ("pair_01", "pair_02")),
        pairs_11_and_16_exact=all(pairs[role]["baseline_exact"] for role in ("pair_11", "pair_16")),
        eleven_identities_exact=all(row["baseline_exact"] for row in by_role["identity"]),
        underexposure_reference_recovery=all(
            row["mean_candidate"][key] <= row["mean_baseline"][key] + TOLERANCE
            and not row["improvements_lost"][key] for row in under.values() for key in ("DE", "RGB")
        )
    )
    summary = {
        "gates": gates, "passes_screen": all(gates.values()), "photorender_count": 1 + len(cases),
        "phone": phone_result, "underexposure": under, "priority_pair_results": pairs,
        "all_cases_outside_protected_exact": True, "experimental_only": True
    }
    write(DEST / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
