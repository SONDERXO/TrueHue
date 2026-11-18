# Downloaded face-decoder checkpoint inventory

8 November 2026. The user downloaded `Downloads/dinov3/decoder.ckpt`. It was inspected without unpickling, importing the author code or running a network, then copied into ignored `models/dinov3_face_parser_candidate_v1/decoder.ckpt`. The Downloads original remains intact.

## What is present

The 193,588,922-byte file is a PyTorch-style ZIP checkpoint with 896 entries. Its bounded pickle metadata can be parsed as inert opcodes. It contains 319 distinct observed weight-name strings: 84 under `encoder.cnn` and 235 under `decoder` groups. Names include the CNN's early convolution and batch-normalisation buffers, multiscale adaptation/fusion blocks, auxiliary heads and final segmentation head. No `encoder.dinov3` weight-name strings were found. This is consistent with the described separate CNN/decoder package.

ZIP CRC checks passed and the copied file's SHA-256 matches the original. The hash and full observed name list are in private `outputs/dinov3_decoder_inventory_v1/inventory_PRIVATE.json`.

## What is not established yet

- Observed key names do not prove exact tensor dimensions, complete expected state coverage or trained quality. No model was instantiated or state dictionary loaded.
- Opcode inspection and CRC checks are not a security certification. No unrestricted pickle deserialization was used. A later load must use restrictive tensor loading and reject unexpected checkpoint objects rather than bypass an error.
- A local hash establishes identity for future checks, not independent verification against an author-published digest.
- User-supplied DINOv3 backbone approval remains distinct from permission for the separate parser code/decoder. No additional terms or permission statement was supplied with this download.
- The Hugging Face backbone still needs the verified loading route described in the [interface audit](dino-decoder-interface-audit-2026-11-08.md). Renaming it is not a solution.

## Next prerequisite

Obtain or locate an explicit research-use statement for the parser code and decoder. Meanwhile the inert package inventory is complete. After that requirement is resolved, prepare a pinned, isolated inference adapter with complete key/shape checks, no automatic VGG downloads and a verified backbone feature interface before proposing the fixed masking run.

No dependencies installed, conversion, fitting, inference, images processed or runtime changes. The separate 24-photo holdout remains byte-unread. Script 650 preserves prior artifacts and private-model Git exclusions.
