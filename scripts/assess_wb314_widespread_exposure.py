"""Check one exposure decision on the existing WB314 development cases."""
from collections import Counter
import json
from pathlib import Path

import cv2
import numpy as np

from assess_wb314_rgb_exposure_headroom import (
    ARCHIVE, DEST as GLOBAL, MODEL, OUT, PHONE, ROOT, SOURCE,
    load_image, new_full_count, read, sha, write,
)
from assess_wb314_local_rgb_highlights import DEST as LOCAL, save_rgb
from src.correction.original_resolution import render_original_rgb8
from src.model_training.luminance_chroma_operator import W, decode, render_rgb8
from src.model_training.widespread_exposure_headroom import cap_widespread_exposure

DEST = OUT / "wb314_widespread_exposure_v1"


def main():
    previous = read(LOCAL / "plan_PRIVATE.json")
    assert sha(MODEL) == previous["model_sha256"]
    assert sha(SOURCE) == previous["phone_source_sha256"]
    assert not read(GLOBAL / "summary.json")["passes_screen"]
    reviewed = read(LOCAL / "appearance_review_PRIVATE.json")
    assert reviewed["technical_summary_sha256"] == sha(LOCAL / "summary.json")
    old_local = read(LOCAL / "summary.json")
    assert old_local["appearance_review_required"]

    audit = read(ARCHIVE / "verification.json")
    for name in ("bindings.json", "controls_sealed.json", "results_PRIVATE.json"):
        assert sha(ARCHIVE / name) == audit["artifacts"][name]
    archives = {(r["group"], r["key"]): r for r in read(ARCHIVE / "controls_sealed.json")["records"]}
    results = {(r["group"], r["key"]): r for r in read(ARCHIVE / "results_PRIVATE.json")}
    bindings = read(ARCHIVE / "bindings.json")
    upstream = read(PHONE / "manifest.json")
    for name in ("original_application_alpha.npy", "original_protected_mask.png", "report.json",
                 "primary_correction.png", "normalized_input.png", "measurement_mask.png",
                 "application_alpha.npy", "protected_mask.png"):
        assert sha(PHONE / name) == upstream["artifacts"][name]
    phone_report = read(PHONE / "report.json")
    assert phone_report["model_sha256"] == sha(MODEL) and phone_report["source_sha256"] == sha(SOURCE)
    before = {(r["role"], r["key"]):r for r in read(LOCAL / "case_results_PRIVATE.json")}
    assert len(previous["case_membership"]) == len(before) == 37

    DEST.mkdir(exist_ok=False)
    write(DEST / "plan_PRIVATE.json", {
        "case_membership": previous["case_membership"],
        "model_sha256": sha(MODEL), "source_sha256": sha(SOURCE),
        "rule_sha256": sha(ROOT / "src/model_training/widespread_exposure_headroom.py"),
        "runner_sha256": sha(Path(__file__)),
        "trigger": "At least a quarter of originally non-full, measured, unprotected application pixels are full in the baseline due to positive exposure.",
        "threshold_basis": "One fixed development cutoff within the observed gap. The cutoff was informed by these exposed cases. No independent validation or cutoff search.",
        "adjustment": "Use the established analysis-size facial luminance cap if it reduces exposure with other controls intact. Otherwise apply RGB headroom on the rendering grid.",
        "targets": "The two earlier softened outputs must match exactly. The original-size portrait must reduce clipping and median brightness lift. All other cases must preserve the saved output exactly.",
        "all_cases": "Original dimensions and protected/outside-support pixels exact.",
        "appearance_review_still_required": True,
    })

    image = load_image(SOURCE)
    baseline = load_image(PHONE / "primary_correction.png")
    alpha = np.load(PHONE / "original_application_alpha.npy", allow_pickle=False, mmap_mode="r")
    protected = load_image(PHONE / "original_protected_mask.png", True) > 0
    face = load_image(PHONE / "measurement_mask.png", True)
    measured = cv2.resize(face, image.shape[:2][::-1], interpolation=cv2.INTER_NEAREST) > 0
    analysis = (load_image(PHONE / "normalized_input.png"), face,
                np.load(PHONE / "application_alpha.npy", allow_pickle=False),
                load_image(PHONE / "protected_mask.png", True) > 0)
    raw = np.array(phone_report["controls"])
    decision = cap_widespread_exposure(image, baseline, measured, alpha, protected, raw, analysis=analysis)
    assert decision["exposure_clipped_pixels"] == old_local["phone"]["changed_pixels"]
    controls = decision["controls"]
    assert np.array_equal(controls[[0, 2, 3, 4]], raw[[0, 2, 3, 4]])
    candidate = baseline if np.array_equal(raw, controls) else render_original_rgb8(image, alpha, protected, controls)
    support = (alpha > 0) & ~protected
    assert candidate.shape == baseline.shape == image.shape
    assert np.array_equal(candidate[~support], image[~support])
    matched = support & ~np.any(image == 255, axis=-1) & np.any(image != 0, axis=-1)
    reference_light = decode(image[matched] / 255.) @ W
    phone = {
        "method": decision["method"],
        "affected_fraction": decision["exposure_clipped_pixels"] / decision["eligible_pixels"],
        "original_exposure_gain": raw[1], "candidate_exposure_gain": controls[1],
        "newly_full_baseline": new_full_count(image, baseline, support),
        "newly_full_candidate": new_full_count(image, candidate, support),
        "baseline_lift": float(100 * np.median((decode(baseline[matched] / 255.) @ W) / reference_light - 1)),
        "candidate_lift": float(100 * np.median((decode(candidate[matched] / 255.) @ W) / reference_light - 1)),
        "dimensions": list(image.shape[:2][::-1]),
        "matches_previous_rgb_preview": bool(np.array_equal(candidate, load_image(GLOBAL / "phone_rgb_headroom_trial.png"))),
    }
    save_rgb(DEST / "phone_widespread_exposure_trial.png", candidate)
    del image, baseline, alpha, protected, measured, candidate, support, matched, reference_light

    cases = []
    for item in previous["case_membership"]:
        role, key = item["role"], item["key"]
        group = "normal20" if role.startswith("pair_") else "final66"
        row = archives[group, key]
        for name in ("input_path", "old_output_path"):
            assert sha(row[name]) == bindings[row[name]]
        with np.load(row["input_path"], allow_pickle=False) as pack:
            image, alpha, protected = (pack[k] for k in ("input", "alpha", "protected"))
            if row["measurement_kind"] == "npz":
                measured = pack["measurement"] > 0
            else:
                path = row["measurement_path"]
                assert sha(path) == bindings[path]
                measured = load_image(path, True) > 0
        with np.load(row["old_output_path"], allow_pickle=False) as pack:
            baseline = pack["candidate"]
        raw = np.array(row["controls"])
        decision = cap_widespread_exposure(image, baseline, measured, alpha, protected, raw)
        assert decision["exposure_clipped_pixels"] == before[role, key]["changed_pixels"]
        controls = decision["controls"]
        assert np.array_equal(controls[[0, 2, 3, 4]], raw[[0, 2, 3, 4]])
        candidate = baseline if np.array_equal(raw, controls) else render_rgb8(image, alpha, protected, controls)
        outside = (alpha == 0) | protected
        assert candidate.shape == image.shape == baseline.shape
        assert np.array_equal(candidate[outside], image[outside])
        matches_prior_softening = None
        if role in ("pair_01", "pair_02"):
            older = results[group, key]
            assert sha(older["output_path"]) == older["output_sha256"]
            with np.load(older["output_path"], allow_pickle=False) as pack:
                matches_prior_softening = bool(np.array_equal(candidate, pack["candidate"]))
        cases.append(dict(role=role, key=key, method=decision["method"],
                          exact_baseline=bool(np.array_equal(candidate, baseline)),
                          matches_prior_softening=matches_prior_softening))

    mandatory = {
        "phone_brightness_and_clipping_reduced": (
            phone["candidate_lift"] < phone["baseline_lift"]
            and phone["newly_full_candidate"] < phone["newly_full_baseline"]
        ),
        "two_preferred_softened_results_exact": all(
            case["matches_prior_softening"] for case in cases if case["role"] in ("pair_01", "pair_02")
        ),
        "other_outputs_exact": all(
            case["exact_baseline"] for case in cases if case["role"] not in ("pair_01", "pair_02")
        ),
    }
    summary = {
        "technical_pass": all(mandatory.values()), "gates": mandatory,
        "phone": phone, "cases": 1 + len(cases),
        "unchanged_result_count": sum(case["exact_baseline"] for case in cases),
        "identity_count": sum(case["role"] == "identity" and case["exact_baseline"] for case in cases),
        "underexposure_preserved": sum(case["role"].endswith("_under") and case["exact_baseline"] for case in cases),
        "methods": dict(Counter(case["method"] for case in cases)),
        "appearance_review_required": True,
    }
    write(DEST / "summary.json", summary)
    write(DEST / "cases_PRIVATE.json", cases)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
