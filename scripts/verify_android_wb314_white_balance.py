"""Verify Android WB_sRGB coefficients using the pinned local research assets."""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from wb_cue_equivalent_ties import extract, load_model

HARNESS = """
import com.example.skintonecorrection.ml.Wb314WhiteBalance;
import java.io.*;
public class WhiteBalanceParity {
    private static float[] floats(DataInputStream input, int length) throws IOException {
        float[] data = new float[length];
        for (int i = 0; i < length; i++) data[i] = input.readFloat();
        return data;
    }
    public static void main(String[] args) throws IOException {
        Wb314WhiteBalance wb;
        try (var assets = new DataInputStream(new BufferedInputStream(new FileInputStream(args[0])))) {
            int rows = assets.readInt();
            wb = new Wb314WhiteBalance(floats(assets, 10800), floats(assets, 10800 * 55),
                    floats(assets, rows * 55), floats(assets, rows * 33), floats(assets, rows));
        }
        var in = new DataInputStream(new BufferedInputStream(System.in));
        var out = new DataOutputStream(new BufferedOutputStream(System.out));
        int count = in.readInt();
        for (int i = 0; i < count; i++) {
            for (float value : wb.extract(in.readNBytes(256 * 256 * 3))) out.writeFloat(value);
        }
        out.flush();
        try {
            wb.extract(new byte[256 * 256 * 3]);
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("Flat image should have no histogram support");
    }
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    outputs = ROOT / "outputs"
    destination = args.output_dir.resolve()
    if not destination.is_relative_to(outputs):
        raise ValueError("Keep derived research assets in the ignored outputs directory")
    saved = outputs / "wb314_normal_photo_preview_v1"
    read = lambda p: json.loads(p.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    predictions = read(saved / "predictions_sealed.json")
    assert sha(outputs / "wb314_final_training_v1/model.json") == predictions["model_sha256"]
    model, normalize, receipt = load_model()
    norms = np.einsum("ij,ij->i", model.features, model.features)
    records = predictions["records"]
    assert len(records) == 20
    images, expected = [], []
    for row in records:
        path = saved / "evaluation" / (row["pair_id"] + ".npz")
        assert sha(path) == row["evaluation_sha256"]
        with np.load(path, allow_pickle=False) as pack:
            images.append(pack["input"].tobytes())
        expected.append(row["features"][281:])
    rng = np.random.default_rng(314)
    for lo, hi in ((0, 256), (15, 200)):
        rgb = rng.integers(lo, hi, (256, 256, 3), dtype=np.uint8)
        coefficients, _, _, _ = extract(model, normalize, rgb)
        images.append(rgb.tobytes())
        expected.append(np.asarray(coefficients, np.float32))

    destination.mkdir(parents=True, exist_ok=False)
    assets = destination / "wb_srgb_PARITY_ONLY.bin"
    with assets.open("xb") as handle:
        handle.write(struct.pack(">i", len(norms)))
        for value in (model.encoderBias, model.encoderWeights, model.features, model.mappingFuncs, norms):
            handle.write(np.asarray(value, dtype=">f4").tobytes())
    harness = destination / "WhiteBalanceParity.java"
    harness.write_text(HARNESS, encoding="utf-8")
    source = ROOT / "android-app/app/src/main/java/com/example/skintonecorrection/ml/Wb314WhiteBalance.java"
    subprocess.run([str(args.jdk / "bin/javac.exe"), "--release", "11", "-d", str(destination),
                    str(source), str(harness)], check=True)
    p = subprocess.run([str(args.jdk / "bin/java.exe"), "-cp", str(destination),
                        "WhiteBalanceParity", str(assets)],
                       input=struct.pack(">i", len(images)) + b"".join(images), capture_output=True)
    (destination / "jvm-stderr.txt").write_bytes(p.stderr)
    p.check_returncode()
    target = np.asarray(expected, np.float32)
    actual = np.frombuffer(p.stdout, dtype=">f4").reshape(target.shape)
    summary = {
        "saved_cases": 20, "generated_cases": 2, "coefficients_compared": target.size,
        "exact_coefficients": int(np.count_nonzero(actual == target)),
        "maximum_absolute_difference": float(np.max(np.abs(target - actual))),
        "rows_with_differences": np.flatnonzero(np.any(actual != target, axis=1)).tolist(),
        "flat_image_rejected": True, "asset_revision": receipt["revision"], "asset_bank_sha256": sha(assets),
        "ran_on_android_device": False,
    }
    (destination / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    if not np.array_equal(target, actual):
        raise AssertionError("White-balance coefficient mismatch")


if __name__ == "__main__":
    main()
