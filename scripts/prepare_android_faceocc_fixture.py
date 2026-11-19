"""Export pinned FaceOcc for local Android tests and stage saved reference logits."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import onnx
import segmentation_models_pytorch as smp
import torch
from safetensors.torch import load_file


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
WEIGHTS = ROOT / "models/faceocc_candidate_v1/model.safetensors"
WEIGHT_SHA = "5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    output = parser.parse_args().output_dir.resolve()
    if OUTPUTS.resolve() not in output.parents:
        raise ValueError("Use a new private directory under outputs")
    if sha(WEIGHTS) != WEIGHT_SHA:
        raise ValueError("Pinned FaceOcc checkpoint required")

    output.mkdir()
    for name in ("test1", "test2"):
        source = OUTPUTS / "wb314_user_photo_check_v1" / name
        receipt = json.loads((source / "inference.json").read_text(encoding="utf-8"))
        request = source / "inference_request.json"
        request_data = json.loads(request.read_text(encoding="utf-8"))
        aligned = source / "aligned.png"
        saved_logits = source / "faceocc_logits.npy"
        if (sha(request) != receipt["request_sha256"]
                or sha(saved_logits) != receipt["logits_sha256"]
                or sha(aligned) != request_data["input_sha256"][request_data["aligned_path"]]):
            raise ValueError(f"Saved inference bindings changed for {name}")
        logits = np.load(saved_logits, allow_pickle=False)
        if logits.shape != (256, 256) or logits.dtype != np.float32 or not np.isfinite(logits).all():
            raise ValueError(f"Invalid reference logits for {name}")
        shutil.copyfile(aligned, output / f"{name}.png")
        logits.astype(">f4").tofile(output / f"{name}.bin")

    # Match the architecture in 420_run_preview_faceocc.py without altering that frozen runner.
    torch.set_num_threads(2)
    model = smp.Unet(encoder_name="resnet18", encoder_depth=5, encoder_weights=None,
                    decoder_use_norm="batchnorm", decoder_channels=(256, 128, 64, 32, 16),
                    decoder_attention_type=None, decoder_interpolation="nearest",
                    in_channels=3, classes=1, activation=None)
    model.load_state_dict(load_file(str(WEIGHTS), device="cpu"), strict=True)
    model.eval()
    graph = output / "faceocc.onnx"
    with torch.inference_mode():
        torch.onnx.export(model, (torch.zeros(1, 3, 256, 256),), str(graph),
                          input_names=["input"], output_names=["logits"],
                          opset_version=13, dynamo=False, external_data=False)
    onnx.checker.check_model(str(graph), full_check=True)
    receipt = {"weights_sha256": WEIGHT_SHA, "torch": torch.__version__, "onnx": onnx.__version__,
               "files": {p.name: sha(p) for p in sorted(output.iterdir())}}
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(receipt["files"][graph.name])


if __name__ == "__main__":
    main()
