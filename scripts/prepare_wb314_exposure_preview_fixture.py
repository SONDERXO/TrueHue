"""Create private saved-mask fixtures for the Android exposure preview test."""
import hashlib
import shutil

import cv2
import numpy as np

from assess_wb314_rgb_exposure_headroom import ARCHIVE, MODEL, OUT, PHONE, SOURCE, load_image, read, sha, write
from assess_wb314_local_rgb_highlights import DEST as LOCAL, save_rgb
from assess_wb314_widespread_exposure import DEST as WIDESPREAD

DEST = OUT / "wb314_widespread_android_v1" / "fixture"


def eligible_count(image, measurement, alpha, protected):
    return int(np.count_nonzero((measurement > 0) & (alpha > 0) & ~protected & ~np.any(image == 255, axis=-1)))


def save_masks(name, measurement, alpha, protected):
    assert measurement.shape == alpha.shape == protected.shape == (256, 256)
    assert measurement.dtype == np.uint8 and protected.dtype == bool
    with (DEST / f"{name}.bin").open("xb") as handle:
        handle.write(measurement.tobytes())
        handle.write(alpha.astype(">f8").tobytes())
        handle.write(protected.astype(np.uint8).tobytes())


def main():
    checked = read(WIDESPREAD / "summary.json")
    plan = read(WIDESPREAD / "plan_PRIVATE.json")
    assert checked["technical_pass"] and sha(MODEL) == plan["model_sha256"] and sha(SOURCE) == plan["source_sha256"]
    audit = read(ARCHIVE / "verification.json")
    for name in ("bindings.json", "controls_sealed.json", "results_PRIVATE.json"):
        assert sha(ARCHIVE / name) == audit["artifacts"][name]
    binding = read(ARCHIVE / "bindings.json")
    seals = {(x["group"], x["key"]):x for x in read(ARCHIVE / "controls_sealed.json")["records"]}
    variants = {(x["group"], x["key"]):x for x in read(ARCHIVE / "results_PRIVATE.json")}
    measured = {(x["role"], x["key"]):x for x in read(LOCAL / "case_results_PRIVATE.json")}
    assessed = read(WIDESPREAD / "cases_PRIVATE.json")

    group_names = ("pair_01", "pair_02", "pair_11", "pair_16", "identity", "exposure_under", "combined_under")
    selected = [max((r for r in assessed if r["role"] == role),
                    key=lambda r: measured[role, r["key"]]["changed_pixels"]) for role in group_names]
    DEST.mkdir(parents=True, exist_ok=False)

    manifest = read(PHONE / "manifest.json")
    for name in ("normalized_input.png", "measurement_mask.png", "application_alpha.npy", "protected_mask.png", "report.json"):
        assert sha(PHONE / name) == manifest["artifacts"][name]
    original = load_image(SOURCE)
    normalization = load_image(PHONE / "normalized_input.png")
    measurement = load_image(PHONE / "measurement_mask.png", True)
    alpha = np.load(PHONE / "application_alpha.npy", allow_pickle=False)
    protected = load_image(PHONE / "protected_mask.png", True) > 0
    save_masks("portrait", measurement, alpha, protected)
    shape = original.shape[1::-1]
    upright_measurement = cv2.resize(measurement, shape, interpolation=cv2.INTER_NEAREST)
    full_alpha = np.load(PHONE / "original_application_alpha.npy", mmap_mode="r", allow_pickle=False)
    full_protected = load_image(PHONE / "original_protected_mask.png", True) > 0
    eligible = eligible_count(original, upright_measurement, full_alpha, full_protected)
    raw = read(PHONE / "report.json")["controls"]
    expected = raw.copy()
    expected[1] = checked["phone"]["candidate_exposure_gain"]
    shutil.copyfile(SOURCE, DEST / "portrait-input.png")
    shutil.copyfile(WIDESPREAD / "phone_widespread_exposure_trial.png", DEST / "portrait-expected.png")
    clipped = read(LOCAL / "summary.json")["phone"]["changed_pixels"]
    cases = [dict(name="portrait", method=checked["phone"]["method"], raw=raw, effective=expected,
                  clipped=clipped, eligible=eligible,
                  normalized_rgb_sha256=hashlib.sha256(normalization.tobytes()).hexdigest())]
    del original, upright_measurement, full_alpha, full_protected

    for row in selected:
        role, key = row["role"], row["key"]
        group = "normal20" if role.startswith("pair_") else "final66"
        source = seals[group, key]
        for name in ("input_path", "old_output_path"):
            assert sha(source[name]) == binding[source[name]]
        with np.load(source["input_path"], allow_pickle=False) as packed:
            image, alpha, protected = (packed[k] for k in ("input", "alpha", "protected"))
            if source["measurement_kind"] == "npz":
                measurement = packed["measurement"]
            else:
                path = source["measurement_path"]
                assert sha(path) == binding[path]
                measurement = load_image(path, True)
        controls = source["controls"]
        effective = controls
        output = source["old_output_path"]
        if row["method"] == "facial_luminance":
            variant = variants[group, key]
            output = variant["output_path"]
            assert sha(output) == variant["output_sha256"]
            effective = variant["facial_guard"]["effective_controls"]
        else:
            assert row["method"] == "original" and row["exact_baseline"]
        with np.load(output, allow_pickle=False) as saved:
            save_rgb(DEST / f"{role}-expected.png", saved["candidate"])
        save_rgb(DEST / f"{role}-input.png", image)
        save_masks(role, measurement, alpha, protected)
        cases.append(dict(name=role, method=row["method"], raw=controls, effective=effective,
                          eligible=eligible_count(image, measurement, alpha, protected),
                          clipped=measured[role, key]["changed_pixels"],
                          normalized_rgb_sha256=hashlib.sha256(image.tobytes()).hexdigest()))
    write(DEST / "cases.json", cases)
    print(f"Prepared {len(cases)} private cases with saved expectations.")


if __name__ == "__main__":
    main()
