"""One saved-input assessment of a local RGB highlight adjustment."""
from collections import Counter
import json
from pathlib import Path

import cv2
import numpy as np

from assess_wb314_rgb_exposure_headroom import (
    ARCHIVE, DEST as GLOBAL, MODEL, OUT, PHONE, ROOT, SOURCE, TOLERANCE,
    load_image, metrics, new_full_count, read, sha, write,
)
from src.model_training.local_rgb_highlights import soften_local_rgb_highlights
from src.model_training.luminance_chroma_operator import W, decode

DEST = OUT / "wb314_local_rgb_highlights_v1"


def compare(image, baseline, measured, alpha, protected, controls):
    output = soften_local_rgb_highlights(image, baseline, measured, alpha, protected, controls)
    support = (alpha > 0) & ~protected
    changed = np.any(output != baseline, axis=-1)
    eligible = support & measured & ~np.any(image == 255, axis=-1) & np.any(baseline == 255, axis=-1)
    assert output.shape == baseline.shape == image.shape
    assert np.array_equal(output[~support], image[~support])
    assert not np.any(changed & ~eligible)
    assert not np.any(output[changed] == 255)
    return output, {
        "changed_pixels": int(changed.sum()),
        "newly_full_baseline": new_full_count(image, baseline, support),
        "newly_full_candidate": new_full_count(image, output, support),
    }


def save_rgb(path, image):
    assert cv2.imwrite(str(path), image[..., ::-1])
    assert np.array_equal(load_image(path), image)


def main():
    prior = read(GLOBAL / "plan_PRIVATE.json")
    assert not read(GLOBAL / "summary.json")["passes_screen"]
    assert sha(SOURCE) == prior["phone_source_sha256"]
    assert sha(MODEL) == prior["model_sha256"]
    archive = read(ARCHIVE / "controls_sealed.json")
    binding = read(ARCHIVE / "bindings.json")
    verification = read(ARCHIVE / "verification.json")
    for name in ("controls_sealed.json", "bindings.json"):
        assert sha(ARCHIVE / name) == verification["artifacts"][name]
    sealed = {(row["group"], row["key"]): row for row in archive["records"]}
    cases = [
        (item["role"], sealed["normal20" if item["role"].startswith("pair_") else "final66", item["key"]])
        for item in prior["cases"]
    ]
    assert Counter(role for role, _ in cases) == {
        "identity": 11, "exposure_under": 11, "combined_under": 11,
        "pair_01": 1, "pair_02": 1, "pair_11": 1, "pair_16": 1,
    }
    for _, row in cases:
        paths = [row["input_path"], row["old_output_path"]]
        if row["measurement_kind"] == "png":
            paths.append(row["measurement_path"])
        assert all(sha(path) == binding[path] for path in paths)
    manifest = read(PHONE / "manifest.json")
    for name in ("report.json", "measurement_mask.png", "original_application_alpha.npy",
                 "original_protected_mask.png", "primary_correction.png"):
        assert sha(PHONE / name) == manifest["artifacts"][name]
    phone = read(PHONE / "report.json")
    assert phone["source_sha256"] == sha(SOURCE) and phone["model_sha256"] == sha(MODEL)

    DEST.mkdir(exist_ok=False)
    write(DEST / "plan_PRIVATE.json", {
        "case_membership": prior["cases"],
        "model_sha256": prior["model_sha256"],
        "phone_source_sha256": prior["phone_source_sha256"],
        "rule_sha256": sha(ROOT / "src/model_training/local_rgb_highlights.py"),
        "script_sha256": sha(Path(__file__)),
        "rule": "Only attenuate the saved positive exposure contribution on eligible newly full measured facial pixels. Use nearest RGB8 quantization boundary.",
        "mandatory_checks": [
            "Exact dimensions and protected/outside support pixels",
            "Exact saved result at every pixel outside targeted highlights",
            "Lower added clipping on phone and pairs 01/02, lower median brightness lift on phone",
            "Exact 11 identities and pair 16",
            "For each underexposure role, no increase in either mean reference error and no lost improvement vs input",
        ],
        "pair_11_rule": "Changes permitted only on targeted highlights. Appearance review required for any later adoption.",
        "appearance_review_required": True,
        "new_predictor_calls": 0,
        "new_fits": 0,
    })

    image = load_image(SOURCE)
    baseline = load_image(PHONE / "primary_correction.png")
    facial = load_image(PHONE / "measurement_mask.png", True)
    measured = cv2.resize(facial, image.shape[:2][::-1], interpolation=cv2.INTER_NEAREST) > 0
    alpha = np.load(PHONE / "original_application_alpha.npy", allow_pickle=False, mmap_mode="r")
    protected = load_image(PHONE / "original_protected_mask.png", True) > 0
    candidate, phone_result = compare(image, baseline, measured, alpha, protected, phone["controls"])
    support = (alpha > 0) & ~protected
    matched = support & np.any(image != 0, axis=-1) & ~np.any(image == 255, axis=-1)
    reference_light = decode(image[matched] / 255.) @ W
    phone_result.update(
        width_height=list(image.shape[:2][::-1]),
        median_lift_baseline=float(100 * np.median((decode(baseline[matched] / 255.) @ W) / reference_light - 1)),
        median_lift_candidate=float(100 * np.median((decode(candidate[matched] / 255.) @ W) / reference_light - 1)),
        application_pixels=int(support.sum()),
    )
    save_rgb(DEST / "phone_local_highlights.png", candidate)
    del image, baseline, candidate, measured, alpha, protected, support, matched, reference_light

    details = []
    for role, row in cases:
        with np.load(row["input_path"], allow_pickle=False) as packed:
            image, alpha, protected = (packed[k] for k in ("input", "alpha", "protected"))
            reference = packed["reference"] if role in ("exposure_under", "combined_under") else None
            measured = (packed["measurement"] > 0 if row["measurement_kind"] == "npz"
                        else load_image(row["measurement_path"], True) > 0)
        with np.load(row["old_output_path"], allow_pickle=False) as saved:
            baseline = saved["candidate"]
        candidate, entry = compare(image, baseline, measured, alpha, protected, row["controls"])
        entry.update(role=role, key=row["key"])
        if role.startswith("pair_") and entry["changed_pixels"]:
            save_rgb(DEST / f"{role}_local_highlights.png", candidate)
        if reference is not None:
            support = alpha > 0
            entry.update(original=metrics(image, reference, support),
                         baseline=metrics(baseline, reference, support),
                         candidate=metrics(candidate, reference, support))
        details.append(entry)

    under = {}
    for role in ("exposure_under", "combined_under"):
        group = [row for row in details if row["role"] == role]
        under[role] = {
            "cases": len(group),
            "exact_outputs": sum(not row["changed_pixels"] for row in group),
            "mean_baseline_error": {k: float(np.mean([r["baseline"][k] for r in group])) for k in ("RGB", "DE")},
            "mean_candidate_error": {k: float(np.mean([r["candidate"][k] for r in group])) for k in ("RGB", "DE")},
            "improvements_lost": {
                k: sum((r["baseline"][k] < r["original"][k] - TOLERANCE
                        and r["candidate"][k] >= r["original"][k] - TOLERANCE) for r in group)
                for k in ("RGB", "DE")
            }
        }
    pairs = {row["role"]: row for row in details if row["role"].startswith("pair_")}
    gates = {
        "phone_clipping_and_brightness_lift_reduced": (
            phone_result["newly_full_candidate"] < phone_result["newly_full_baseline"]
            and phone_result["median_lift_candidate"] < phone_result["median_lift_baseline"]
        ),
        "pairs_01_and_02_clipping_reduced": all(
            pairs[key]["newly_full_candidate"] < pairs[key]["newly_full_baseline"] for key in ("pair_01", "pair_02")
        ),
        "identities_and_pair_16_exact": all(
            not row["changed_pixels"] for row in details if row["role"] in ("pair_16", "identity")
        ),
        "underexposure_reference_recovery": all(
            row["mean_candidate_error"][key] <= row["mean_baseline_error"][key] + TOLERANCE
            and not row["improvements_lost"][key] for row in under.values() for key in ("DE", "RGB")
        ),
    }
    summary = {
        "cases": 1 + len(cases), "technical_gates": gates, "technical_pass": all(gates.values()),
        "exact_outside_targeted_pixels_on_all_cases": True, "appearance_review_required": True,
        "phone": phone_result, "underexposure": under, "priority_pairs": pairs,
    }
    write(DEST / "case_results_PRIVATE.json", details)
    write(DEST / "summary.json", summary)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
