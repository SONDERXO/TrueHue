"""Check Java feature arithmetic using hash-bound, already measured WB314 inputs."""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.blue_axis_preparation import features281

HARNESS = """
import com.example.skintonecorrection.ml.Wb314ImageFeatures;
import java.io.*;
public class FeatureParity {
    public static void main(String[] args) throws IOException {
        var input = new DataInputStream(new BufferedInputStream(System.in));
        var output = new DataOutputStream(new BufferedOutputStream(System.out));
        int cases = input.readInt(), knots = input.readInt();
        double[] x = new double[knots], y = new double[knots];
        for (int i = 0; i < knots; i++) x[i] = input.readDouble();
        for (int i = 0; i < knots; i++) y[i] = input.readDouble();
        for (int i = 0; i < cases; i++) {
            byte[] rgb = input.readNBytes(3 * 65536), lab = input.readNBytes(3 * 65536);
            byte[] mask = input.readNBytes(65536);
            for (float value : Wb314ImageFeatures.extract(rgb, lab, mask, x, y)) output.writeFloat(value);
        }
        output.flush();
    }
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    local = ROOT / "outputs"
    saved = local / "wb314_normal_photo_preview_v1"
    read = lambda p: json.loads(p.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    frozen = read(saved / "predictions_sealed.json")
    assert sha(local / "wb314_final_training_v1/model.json") == frozen["model_sha256"]
    bindings = read(local / "wb314_final_training_v1/bindings.json")
    schema = local / "wb_feature_direct_prediction_v1/feature_schema.json"
    assert sha(schema) == bindings[schema.relative_to(ROOT).as_posix()]
    names = read(schema)["314"][:281]
    mapping_path = local / "shared_core_mst_features_v1/mapping_PRIVATE.json"
    assert sha(mapping_path) == "6863575e284a6495e71e7445c88445d4215300db95f2b9111a43cd2191fe6be3"
    mapping = read(mapping_path)
    xs, ys = mapping["ita_knots"], mapping["mst_score_knots"]
    records = frozen["records"]
    assert len(records) == 20
    chunks = [struct.pack(">ii", len(records) + 2, len(xs)),
              struct.pack(">" + "d" * (2 * len(xs)), *(xs + ys))]
    expected = []

    def add(rgb, mask, reference):
        lab = cv2.cvtColor(np.ascontiguousarray(rgb[:, :, ::-1]), cv2.COLOR_BGR2LAB)
        chunks.extend([rgb.tobytes(), lab.tobytes(), mask.tobytes()])
        expected.append(reference)

    for record in records:
        path = saved / "evaluation" / (record["pair_id"] + ".npz")
        assert sha(path) == record["evaluation_sha256"]
        with np.load(path, allow_pickle=False) as pack:
            add(pack["input"], pack["measurement"], record["features"][:281])
    mask = np.full((256, 256), 255, np.uint8)
    rng = np.random.default_rng(314)
    generated = [rng.integers(0, 256, (256, 256, 3), dtype=np.uint8),
                 np.broadcast_to(np.array([180, 100, 0], np.uint8), (256, 256, 3))]
    for rgb in generated:
        add(rgb, mask, features281(rgb, mask, mapping, names)[0])

    args.output_dir.mkdir(parents=True, exist_ok=False)
    harness = args.output_dir / "FeatureParity.java"
    harness.write_text(HARNESS, encoding="utf-8")
    source = ROOT / "android-app/app/src/main/java/com/example/skintonecorrection/ml/Wb314ImageFeatures.java"
    subprocess.run([str(args.jdk / "bin/javac.exe"), "--release", "11", "-d",
                    str(args.output_dir), str(source), str(harness)], check=True)
    p = subprocess.run([str(args.jdk / "bin/java.exe"), "-cp", str(args.output_dir), "FeatureParity"],
                       input=b"".join(chunks), capture_output=True, check=True)
    target = np.asarray(expected, np.float32)
    actual = np.frombuffer(p.stdout, dtype=">f4").reshape(target.shape)
    errors = np.argwhere(target != actual)
    summary = {"saved_cases": 20, "generated_cases": 2, "compared_features": target.size,
               "exact_features": target.size - len(errors),
               "maximum_absolute_difference": float(np.max(np.abs(target - actual))),
               "android_lab_conversion_checked": False, "mismatched_feature_indices": sorted(set(errors[:, 1].tolist()))}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    if len(errors):
        raise AssertionError("Feature arithmetic mismatch")


if __name__ == "__main__":
    main()
