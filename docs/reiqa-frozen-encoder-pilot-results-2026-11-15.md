# Frozen neural encoder: generated feasibility results

15 November2026. **GENERATED_MECHANICS_PASS_ONLY.** User explicitly approved a bounded frozen-feature assessment after reconsidering the previous neural-feature decline. One Re-IQA quality-aware encoder was assessed. This is substantive hybrid-method research, not adoption into the paper, correction model or Android app.

Protocol: [frozen pilot](reiqa-frozen-encoder-pilot-protocol-2026-11-15.md). All six generated cases and preprocessing were fixed before encoder execution. No project photographs or masks were opened.

## Checkpoint and reproducibility

Official pinned README: https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD . Its advertised quality-aware Drive checkpoint transferred successfully through the official large-file confirmation. No mirror or second checkpoint was used.

- Download:369,850,481bytes,48.68seconds,within512MiB/600second bound.
- SHA256:`aef5e85843ba502206c726da78500ead5ff705da8b4a335d3b25466c93f1f2fb`.
- Archive:810members; metadata117,772bytes. Static pickle inspection found only OrderedDict and PyTorch storage/tensor reconstruction globals.
- Restricted `torch.load(weights_only=True,map_location='cpu')` succeeded, without arbitrary-global additions or unrestricted pickle fallback. Top-level entries:model,contrast,optimizer,epoch,model_ema. Only `model` encoder weights were used; no optimizer or training state was resumed, no EMA/content/projection head substituted.
- All model-state entries were finite tensors. Every encoder key/shape loaded strictly into both architectures. Encoder parameters:23,508,032.
- MIT notice retained beside the downloaded checkpoint. No checkpoint-specific additional restrictions were found in the previously inspected source; pretraining-image rights/overlap clearance is not claimed.

Environment is isolated at `.venv-reiqa-pilot`, excluded from Git. Python3.13.17,torch2.15.0+cpu,torchvision0.29.2+cpu,numpy2.5.4,Pillow13.0.0. Full frozen dependency list saved. The first combined install request stopped because psutil was absent from the CPU wheel index; no package was installed by that failed resolution. A subsequent install omitted the unnecessary psutil and used native Windows memory accounting. Existing project dependencies were not changed. This modern environment differs from the authors' original setup; exact original-environment reproduction is not claimed.

## Generated checks

RGB8 input at256x256 plus Pillow-default half128 scale; float32 /255, no ImageNet normalization. Two-scale pooled encoder outputs concatenated to4096, not the128-dimensional contrastive projection. Two CPU threads, deterministic algorithms, eval mode and frozen parameters.

The pinned architecture was instantiated by extracting only four audited definitions from its cached source AST, avoiding research training imports and unrelated model dependencies. An independently installed torchvision ResNet50, with final layer replaced by Identity, loaded the same encoder weights strictly. The full4096-value identity outputs matched EXACTLY, max difference0. This is same-library implementation parity on one generated base, not a universal implementation proof.

| Generated case | Feature L2 change from generated identity | Two-scale extraction seconds |
|---|---:|---:|
|Identity repeat|0|0.279|
|Gamma1.4|11.164|0.352|
|Gamma0.7|5.084|0.281|
|Redgain1.1|3.684|0.303|
|Bluegain0.9|2.476|0.309|
|Gamma1.4/red1.1/blue0.9|8.916|0.300|

All24,576 saved feature values are finite. Repeated identity is exact and all encoder weights AND buffers remain unchanged. First-call extraction0.377seconds. These are single desktop timings, not stable benchmarks or Android latency. Process peak working set1,006,006,272bytes (~959MiB), including checkpoint, two models, cloned-state verification and dependencies; this is neither isolated deployed-encoder footprint nor a phone measurement.

Independent saved-vector accounting, without importing torch/model code, verified all six shapes/dtypes, finiteness, response norms/maxima and bound hashes. Scalar float64 vs torch float32 reduction differences are checked with declared1e-6relative/absolute arithmetic tolerance; encoder parity and identity repeat remain EXACT with no tolerance relaxation. The saved-vector verifier does not independently execute a second neural engine.

## Meaning and next bounded step

This clears checkpoint access and basic desktop mechanics. Exposure AND colour changes are visible to this representation on the fixed generated base. It does NOT establish that the encoder distinguishes an added cast from naturally photographed complexion, lighting, background or content; feature distance is not correction accuracy, preference, physical colour or fairness. No favourable coordinate selection or feature threshold was made. High dimension with only11current sources remains a transfer/overfitting risk.

The next justified stage is a prospectively fixed **input-only representation assessment on the already exposed66 cached development inputs**, retaining all11sources/sixroles and frozen4096features. Before reading any pixels, specify exact allowed input-key/hash bindings, all-case failure handling, preprocessing and descriptive source-versus-edit accounting; exclude photographic references, target controls and held error labels from extraction. The present generated responses are enough to justify investigating representation availability, not enough to authorize a correction tree fit. No feature selection, PCA, alternate encoder, new source acquisition or model fit follows automatically. A later prediction test needs its own source-held design and preserved appearance gates.

The old November11 layout of4096+16/44cases is historical, not an adopted current recipe. Whether to combine these features with current281inputs, which renderer/output scope to retain, and how to test correction-family transfer must be fixed separately before fitting. ITA/MST are retained; the five-control operator remains experimental. Do not quietly change both representation and correction model and attribute any result to the encoder alone.

Darker-skin bias reduction remains the primary thesis aim. These generated probes have no skin-tone assignments. Current FFHQ lacks official independent tone labels; the MST mapper is an unvalidated development transfer. Pretraining overlap is unresolved. A successful development representation/prediction experiment would still not establish darker-skin qualification.

## Artifacts and preservation

`scripts/prepare_reiqa_checkpoint_pilot.py`, `scripts/check_reiqa_frozen_generated.py`, `scripts/verify_reiqa_frozen_generated.py`; syntax checks passed. Evidence at `outputs/reiqa_checkpoint_pilot_v1` (checkpoint, transfer receipt, official confirmation page, licence, isolated dependencies) and `outputs/reiqa_frozen_generated_v1` (full generated vectors, weight inventory, provenance, mechanics and independent accounting). Output directories refuse overwrite; failures preserve partial evidence.

Zero dataset/cache photograph or NPZ reads, correction-tree fits, correction predictions, renders, ratings, locked final24/older contents OR manifests, runtime/Android/manuscript edits. The new generated NPZ is explicitly synthetic and was replayed only by its verifier. Existing artifacts, failed-branch closures, ratings, approved59807manual and desktop ears remain intact. No candidate adopted; model unfinished, paper paused, November25 and model-ASAP priority retained.
