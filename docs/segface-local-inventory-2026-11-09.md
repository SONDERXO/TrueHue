# SegFace local checkpoint inventory — 9 November 2026

The user supplied the selected checkpoint. **Its exact size and SHA256 match
the author metadata recorded during route selection.** The earlier failed
network acquisition is preserved separately.

- Path: `models/segface_mobilenet_candidate_v1/model_299.pt`.
- Size: 84,928,824 bytes.
- SHA256: `4d67ea7d8c33849272b293b421fa3d20d54d9987f1bca8c1ef0eebe4534993e8`.
- ZIP: 1,309 entries; CRC checks passed.
- Pickle metadata: 154,960 bytes; 44,242 opcodes inspected without execution.
- The expected `state_dict_backbone` name is present. Observed globals are
  OrderedDict, Counter, FloatStorage, LongStorage and `_rebuild_tensor_v2`.

Script 694 performed no unpickling, tensor loading, remote-code import, model
forward, dependency install or private-image access. Metadata/global names and
CRC checks are not security certification or evidence of complete parameter
shapes, successful strict loading or segmentation quality. Source MIT notice
was copied alongside the checkpoint and verified against the pinned snapshot.

Private artifacts: `outputs/segface_local_inventory_v1/inventory_PRIVATE.json`
and `verification_PRIVATE.json`. The author hash comparison is now a local
verification, superseding the acquisition status's missing-file state. The
selection record itself remains preserved as historical evidence.

Next is isolated interface/loader preparation: establish compatible dependencies,
prevent automatic pretrained-backbone downloads, restrict checkpoint loading,
verify exact keys/shapes and all nineteen class IDs, then freeze the existing
coverage/protection comparison before any private-photo forward. No new
annotation, parser promotion, correction fit or final-holdout access follows
automatically. The candidate has no explicit beard or frame/lens labels.

The active masks, demo and correction candidates are unchanged. DINO remains
unused; all 24 final holdout photos remain byte-unread. No contact, upload,
publication, commit or push occurred.
