"""Run the compiled Android WB314 loader against saved local development vectors."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HARNESS = """
import com.example.skintonecorrection.ml.PortableTreeAsset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Scanner;
import java.util.Locale;
public class Wb314TreeParity {
    public static void main(String[] args) throws Exception {
        byte[] model = Files.readAllBytes(Path.of(args[0]));
        var loader = PortableTreeAsset.INSTANCE;
        var tree = loader.parseWb314(model, args[1]);
        expectRejection(() -> loader.parseWb314(model, "0".repeat(64)));
        expectRejection(() -> tree.predict(new double[313]));
        double[] invalid = new double[314];
        invalid[0] = Double.NaN;
        expectRejection(() -> tree.predict(invalid));
        Scanner in = new Scanner(System.in).useLocale(Locale.ROOT);
        while (in.hasNextDouble()) {
            double[] vector = new double[314];
            for (int i = 0; i < vector.length; i++) vector[i] = in.nextDouble();
            System.out.println(tree.leafId(vector) + ":" + Arrays.toString(tree.predict(vector)));
        }
    }
    private static void expectRejection(Runnable action) {
        try { action.run(); }
        catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("Invalid input accepted");
    }
}
"""


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--jdk", type=Path, required=True)
    cli.add_argument("--output-dir", type=Path, required=True)
    args = cli.parse_args()
    build = ROOT / "android-app/app/build"
    cache = ROOT / "outputs/android_toolchain/gradle/caches/modules-2/files-2.1"
    classpath = [
        build / "tmp/kotlin-classes/debug",
        build / "intermediates/javac/debug/compileDebugJavaWithJavac/classes",
        next((cache / "org.json/json/20240303").glob("*/*.jar")),
        next((cache / "org.jetbrains.kotlin/kotlin-stdlib/2.0.21").glob("*/*.jar")),
    ]
    if not all(path.exists() for path in classpath):
        raise FileNotFoundError("Build the debug app and run its JVM unit tests first.")
    training = ROOT / "outputs/wb314_final_training_v1"
    saved_model = training / "model.json"
    read = lambda p: json.loads(p.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    digest = sha(saved_model)
    assert digest == read(training / "model_seal.json")["model_sha256"]
    nodes = read(saved_model)["nodes"]
    previous = {row["case_id"]: row for row in read(training / "training_predictions.json")}
    normal = read(ROOT / "outputs/wb314_normal_photo_preview_v1/predictions_sealed.json")
    assert digest == normal["model_sha256"]
    inputs = read(ROOT / "outputs/wb_feature_direct_prediction_v1/rows.json")
    assert len(inputs) == len(previous) == 66 and len(normal["records"]) == 20
    vectors = [row["x314"] for row in inputs] + [row["features"] for row in normal["records"]]
    expected = [(previous[row["case_id"]]["leaf"], previous[row["case_id"]]["controls"])
                for row in inputs] + [(row["leaf"], row["controls"]) for row in normal["records"]]
    # For each split, perturb a fitting vector that reaches it across the float32 boundary.
    witnesses = {}
    for vector in vectors[:66]:
        index = 0
        while nodes[index]["kind"] == "split":
            witnesses[index] = vector
            node = nodes[index]
            feature = float(np.float32(vector[node["feature"]]))
            index = node["left" if feature <= node["threshold"] else "right"]
    assert len(witnesses) == sum(node["kind"] == "split" for node in nodes)
    for index, vector in witnesses.items():
        node = nodes[index]
        center = np.float32(node["threshold"])
        for value in (np.nextafter(center, np.float32(-np.inf)), center,
                      np.nextafter(center, np.float32(np.inf))):
            variant = vector.copy()
            variant[node["feature"]] = float(value)
            leaf = 0
            while nodes[leaf]["kind"] == "split":
                split = nodes[leaf]
                feature = float(np.float32(variant[split["feature"]]))
                leaf = split["left" if feature <= split["threshold"] else "right"]
            vectors.append(variant)
            expected.append((leaf, nodes[leaf]["values"]))

    args.output_dir.mkdir(parents=True, exist_ok=False)
    harness = args.output_dir / "Wb314TreeParity.java"
    harness.write_text(HARNESS, encoding="utf-8")
    cp = os.pathsep.join(map(str, classpath))
    subprocess.run([str(args.jdk / "bin/javac.exe"), "--release", "11", "-cp", cp,
                    "-d", str(args.output_dir), str(harness)], check=True)
    run = subprocess.run([str(args.jdk / "bin/java.exe"), "-cp",
                          cp + os.pathsep + str(args.output_dir), "Wb314TreeParity",
                          str(saved_model), digest],
                         input="\n".join(" ".join(map(str, row)) for row in vectors),
                         text=True, capture_output=True)
    (args.output_dir / "jvm-stderr.txt").write_text(run.stderr, encoding="utf-8")
    run.check_returncode()
    actual = [(int(i), json.loads(values)) for i, values in
              (line.split(":", 1) for line in run.stdout.splitlines())]
    assert actual == expected, "WB314 leaf or control mismatch"
    summary = {"saved_development_vectors": 86, "float32_boundary_vectors": len(vectors) - 86,
               "exact_leaf_and_control_matches": len(vectors), "invalid_inputs_rejected": 3,
               "model_sha256": digest, "apk_inference_run": False}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
