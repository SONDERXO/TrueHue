# Downloaded DINOv3 package inventory

8 November 2026. User reports backbone access approved and downloaded five files into `Downloads/dinov3`. All five were inspected and copied, without moving or overwriting the originals, into ignored `models/dinov3_face_parser_candidate_v1`.

The config identifies DINOv3 ViT-B/16: 12 layers, width 768, patch size 16 and four register tokens. The 342,662,192-byte safetensors file contains 211 float32 tensors and 85,660,416 parameter elements. Header dimensions, tensor byte lengths, contiguous nonoverlapping data offsets and total payload length pass structural checks. Every copied file matches its source SHA-256.

Weights SHA-256: `9a21ac3df0c63839d62612dda6f454d816c25611cc7a52966ed5a5a94921dc8b`. This records local file integrity; a remote official digest has not independently been matched. Config, processor config, original README and licence were preserved alongside the weights. This inventory does not provide a legal opinion or clear a separate decoder's terms.

## Compatibility remains unresolved

This is the Hugging Face format, with names such as `embeddings.patch_embeddings.weight` and separate attention projection tensors. The [face-parser loader](https://github.com/jseobyun/FaceParsing/blob/master/src/face_parsing/predictor.py) instead uses its local `torch.hub` DINOv3 constructor and original backbone checkpoint, plus a separate decoder checkpoint. The [author README](https://github.com/jseobyun/FaceParsing) specifies that original `.pth` asset and decoder separately.

The file must not simply be renamed to `.pth`. A verified key/shape conversion or an equivalent Hugging Face encoder adapter would be needed if retaining this format. Neither has been implemented or validated. Transformers is not installed in the current venv; no new dependency was installed by this inventory. The downloaded 224-pixel processor default must not silently replace the face-parser's 512-pixel inference contract.

## Next steps

1. Inspect the face-parser decoder and its exact encoder feature interface, code dependencies and reuse terms before executing third-party code or a pickle-based checkpoint.
2. Establish a compatible backbone-loading route, with complete key/shape coverage and numerical feature parity if conversion/adaptation is used. Do not silently load missing keys or random layers.
3. Only after the complete package and permissions are established, freeze one masking comparison with existing actual-input references and object-protection requirements.

No inference, tensor-model deserialisation, decoder download, fitting or app integration occurred. Safetensors metadata was read as bounded JSON rather than executing model code. The final 24-photo holdout remains byte-unread. Script 649 and private `outputs/dinov3_package_inventory_v1/inventory_PRIVATE.json` record the inventory. Original Downloads files remain intact; all weights and private receipts are Git-ignored.
