"""Compare the Android Java WB314 pixel renderer with Python on generated RGB8."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.luminance_chroma_operator import render_rgb8

HARNESS = """
import com.example.skintonecorrection.ml.Wb314PixelRenderer;
import java.util.Scanner;
import java.util.Locale;
public class RendererParity {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in).useLocale(Locale.ROOT);
        while (in.hasNextInt()) {
            int count = in.nextInt();
            var renderer = new Wb314PixelRenderer(in.nextDouble(), in.nextDouble(),
                    in.nextDouble(), in.nextDouble(), in.nextDouble());
            for (int i = 0; i < count; i++) {
                int pixel = in.nextInt();
                double alpha = in.nextDouble();
                boolean protect = in.nextInt() != 0;
                System.out.println(renderer.render(pixel, alpha, protect));
            }
        }
        var renderer = new Wb314PixelRenderer(1, 1, 1, 1, 1);
        boolean rejected = false;
        try { renderer.render(0xff000000, 0.5, true); }
        catch (IllegalArgumentException expected) { rejected = true; }
        if (!rejected) throw new AssertionError("accepted protected nonzero alpha");
    }
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jdk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    harness = args.output_dir / "RendererParity.java"
    harness.write_text(HARNESS, encoding="utf-8")
    source = ROOT / "android-app/app/src/main/java/com/example/skintonecorrection/ml/Wb314PixelRenderer.java"
    subprocess.run([str(args.jdk / "bin/javac.exe"), "--release", "11", "-d",
                    str(args.output_dir), str(source), str(harness)], check=True)

    rng = np.random.default_rng(314)
    image = rng.integers(0, 256, (80, 80, 3), dtype=np.uint8)
    image[0] = np.tile([[0, 0, 0], [255, 255, 255], [255, 0, 0],
                        [0, 255, 0], [0, 0, 255]], (16, 1))
    alpha = rng.choice([0., 0.125, 0.5, 0.875, 1.], image.shape[:2])
    protected = rng.random(alpha.shape) < 0.2
    alpha[protected] = 0
    control_sets = ([1, 1, 1, 1, 1], [1, 2**0.5, 1, 1, 1],
                    [1, 2**-0.5, 1.15, 0.85, 1], [0.7, 1.25, 1.2, 0.9, 1.5],
                    [4, 0.25, 4, 0.25, 0.25])
    # Use signed packed ints like Android Bitmap.getPixels.
    def packed(rgb):
        r, g, b = (int(x) for x in rgb)
        return (r << 16 | g << 8 | b) - (1 << 24)

    lines, expected = [], []
    samples = [f"{packed(rgb)} {a!r} {int(p)}" for rgb, a, p in
               zip(image.reshape(-1, 3), alpha.flatten().tolist(), protected.flat)]
    for controls in control_sets:
        lines.append(f"{len(samples)} " + " ".join(map(str, controls)))
        lines.extend(samples)
        reference = render_rgb8(image, alpha, protected, controls)
        assert np.array_equal(reference[alpha == 0], image[alpha == 0])
        expected.extend(map(packed, reference.reshape(-1, 3)))
    process = subprocess.run([str(args.jdk / "bin/java.exe"), "-cp",
                              str(args.output_dir), "RendererParity"],
                             input="\n".join(lines), text=True, capture_output=True, check=True)
    actual = [int(v) for v in process.stdout.splitlines()]
    if actual != expected:
        mismatches = sum(a != b for a, b in zip(actual, expected))
        raise AssertionError(f"Pixel mismatch: {mismatches}; lengths {len(actual)}/{len(expected)}")
    summary = {"exact_rgb8_pixels": len(expected), "control_sets": len(control_sets),
               "protected_nonzero_alpha_rejected": True, "generated_inputs": True,
               "android_native_pipeline_run": False}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
