"""Prepare a private two-case Android fixture using existing normalized photos and masks."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.correction.original_resolution import lift_analysis_support, render_original_rgb8

MODEL_SHA = "7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f"
MAP_SHA = "6863575e284a6495e71e7445c88445d4215300db95f2b9111a43cd2191fe6be3"
read = lambda path: json.loads(path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    store = ROOT / "outputs"
    out = args.output_dir.resolve()
    if not out.is_relative_to(store):
        raise ValueError("Research fixture must stay under outputs/")
    model = store / "wb314_final_training_v1/model.json"
    mapping = store / "shared_core_mst_features_v1/mapping_PRIVATE.json"
    bank = store / "wb314_android_white_balance_v1/wb_srgb_PARITY_ONLY.bin"
    bank_receipt = read(bank.with_name("summary.json"))
    assert sha(model) == MODEL_SHA and sha(mapping) == MAP_SHA
    assert bank_receipt["exact_coefficients"] == bank_receipt["coefficients_compared"] == 726
    assert sha(bank) == bank_receipt["asset_bank_sha256"]
    history = store / "wb314_normal_photo_preview_v1"
    predictions = read(history / "predictions_sealed.json")
    assert predictions["model_sha256"] == MODEL_SHA

    out.mkdir(parents=True, exist_ok=False)
    for path, name in [(model, "model.json"), (mapping, "mapping.json"), (bank, "wb_srgb.bin")]:
        shutil.copyfile(path, out / name)
        assert sha(path) == sha(out / name)
    manifest = {"schema": "truehue_wb314_android_research_v1", "tree_sha256": MODEL_SHA,
                "mapping_sha256": MAP_SHA, "bank_sha256": sha(bank)}
    (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    done = set()
    for row in predictions["records"]:
        cache = history / "evaluation" / (row["pair_id"] + ".npz")
        assert sha(cache) == row["evaluation_sha256"]
        with np.load(cache, allow_pickle=False) as loaded:
            rgb, prior, measure, alpha, protected = [loaded[k] for k in
                                                     ("input", "candidate", "measurement", "alpha", "protected")]
        name = "preserved" if np.array_equal(prior, rgb) else "adjusted"
        if name in done:
            continue
        # Integer replication gives a non-square render input with the same exact area-normalized image.
        original = rgb.repeat(3, axis=0).repeat(2, axis=1)
        assert np.array_equal(cv2.resize(original, (256, 256), interpolation=cv2.INTER_AREA), rgb)
        a, p = lift_analysis_support(alpha, protected, original.shape)
        output = render_original_rgb8(original, a, p, row["controls"])
        assert np.array_equal(output[p | (a == 0)], original[p | (a == 0)])
        assert np.array_equal(output, original) == (name == "preserved")
        for tag, image in (("input", original), ("output", output)):
            assert cv2.imwrite(str(out / f"{name}_{tag}.png"), image[:, :, ::-1])
        with (out / f"{name}.bin").open("xb") as handle:
            handle.write(hashlib.sha256(rgb.tobytes()).hexdigest().encode("ascii"))
            handle.write(measure.tobytes())
            handle.write(alpha.astype(">f8").tobytes())
            handle.write(protected.astype(np.uint8).tobytes())
            handle.write(struct.pack(">319di", *(row["features"] + row["controls"]), row["leaf"]))
        done.add(name)
        if len(done) == 2:
            break
    assert done == {"adjusted", "preserved"}
    print(json.dumps({"cases": len(done), "manifest_sha256": sha(out / "manifest.json"),
                      "size": [512, 768], "new_model_predictions": 0, "new_mask_inferences": 0}))


if __name__ == "__main__":
    main()
