# Re-IQA input-feature feasibility review

11 November 2026. User authorized assessment of one learned input representation before downloading weights, training or touching photos. **Outcome: technically compatible with a correction tree, but not ready for a correction fit or Android adoption. A substantive hybrid-method choice is needed before a weight/inference pilot.** No weights, model execution, photo reads, new correction predictions, fits or final/locked accesses occurred.

## Relevant evidence and its limits

The authors' paper studies content and quality representations for image-quality prediction. Its augmentation bank includes brighten/darken, mean shifts, contrast and colour distortions. This provides a specific distortion-representation rationale beyond our failed handcrafted summaries. It does not demonstrate gamma/red/blue restoration, skin-tone conditioning, separation of illumination from complexion, or passing TrueHue's identity/colour checks. Their nonlinear brightness and chroma corruptions are not our exact gamma/red-gain recipes. IQA scores or perceptual naturalness must not become skin-tone ground truth or our correction target. [Paper, sections 3, 4 and appendix 7.1](https://arxiv.org/html/2304.00451).

## Exact implementation finding

Pinned repository commit: 8d00fc5a5d50a678f8bf3ffde160353f29a3e030. Public source files were fetched as text and hashed, not imported or executed. The quality demo calls only the encoder at original and half scale, concatenating 2048 pooled features from each into4096. Its128-dimensional contrastive MLP output is NOT the feature used by the released demo. Do not select that smaller head merely to avoid the dimensionality issue. The demo uses RGB ToTensor without standard ImageNet mean/std normalization. It accepts a single photo and does not require an original reference at inference. [Pinned demo](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/demo_quality_aware_feats.py).

For TrueHue the possible layout would be frozen quality encoder ->4096features plus unchanged16inputs -> one three-output decision tree -> existing gamma/red/blue renderer. Do not append the failed36spatialNSSfeatures. No content encoder, MOS regressor, quality score, second correction head, decoder, best-of-renders selection or reference-derived feature would be included. This layout preserves one final correction predictor but changes the overall method to a pretrained-deep-feature/traditional-tree hybrid. That is a declared departure from the proposal's traditional-ML-only scope, not a purely traditional pipeline because the last estimator is a tree.

## Release, terms and provenance

The repository has an MIT software licence, requiring preservation of its notices. No separate checkpoint-specific restriction was located in the inspected files; this is not a claim of a complete independent review of every pretraining image's rights. The https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD advertises a quality checkpoint on Google Drive; its public view identifies quality_aware_r50.pth. No weight bytes, integrity hash, actual checkpoint size, checkpoint keys or model output were verified. A sparse Drive sign-in view does not establish that download requires an account or that access is blocked. [Licence](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/LICENSE). [https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD).

The https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD names KADIS originals, AVA, COCO, CERTH-Blur and VOC for quality pretraining; the separate content encoder uses ImageNet and is not proposed here. The paper and repository differ in some training quantities/schedules (e.g.25versus40epochs and CERTH subset counts), so the advertised checkpoint cannot be assumed to reproduce every paper setting. The published40MBtraining-path CSV exists but was not downloaded. Listed dataset names do not prove no shared image with TrueHue sources, many of which can share internet-photo origins. No overlap finding or identity clearance is claimed. Unknown pretraining overlap is a final-independence limitation to investigate/disclose; it does not automatically forbid explicitly exposed exploratory development. No locked-photo bytes should be opened to resolve it. [https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD).

## Static resource estimate, not a benchmark

| Item | Source-derived estimate |
|---|---:|
| Width1ResNet50 encoder parameters, excluding projection head |23,508,032|
| Float32 parameter bytes only |94,032,128 (89.68MiB)|
| Two-scale256+128 convolution multiply-accumulates |6,672,875,520|
| Encoder output coordinates, two scales |4096|
| Total with retained old16inputs |4112|
| Available diagnostic fitting data per fold |40rows from10sourcephotos|

Calculated from the pinned bottleneck topology, excluding activation memory, BN buffers, checkpoint optimizer/projection/momentum states and preprocessing overhead. Multiply-accumulates are not milliseconds and are not interchangeable with every source's FLOP convention. Independent parameter arithmetic matches the encoder count; adding a1000-class head reproduces Torchvision's published25,557,032parameter count. Our256/128MACestimate is a static calculation, not a phone measurement or proof that Android cannot run it. [Pinned backbone](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/networks/build_backbone.py), [pinned ResNet](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/networks/resnet.py), [Torchvision reference](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html).

The repository documents Linux/Python3.9/PyTorch1.13.1/torchvision0.14.1/CUDA11.7 testing. It supplies no verified TrueHue Android export/timing path in the inspected files. This does not make CPU inference impossible. No dependencies were installed/downgraded, no CUDA/training script executed and no remote checkpoint deserialized. A later isolated engineering pilot must verify actual runtime/export behaviour rather than copy the whole research training stack. [https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD](https://github.com/avinabsaha/ReIQA/blob/8d00fc5a5d50a678f8bf3ffde160353f29a3e030/README.MD).

4112coordinates with only40rows/10sources creates a serious risk of source-specific splits. Dimension greater than row count is not a mathematical impossibility or a new numeric adoption boundary. Arbitrary truncation, PCA fitted on all44inputs, feature ranking using held outcomes or replacing the head with a pretrained quality score would add unapproved changes or leakage. The current44-case task still has constantblue targets and no independentMSTlabels. An encoder does not fix those claim limitations by itself.

## Recommendation and bounded next option

Do not train a correction tree or add Re-IQA to the app now. The feasibility review establishes a plausible but untested representation mechanism and tangible engineering costs. It does not establish that it is the best or successful way to finish the model.

If the researchers accept a frozen neural feature extractor as an explicit method amendment, the next concrete step is ONE engineering/representation pilot, not another dataset/model grid:

1. Resolve actual public checkpoint metadata/transfer bound and preserve its hash/notices; do not download all training data or a second encoder. Inspect a checkpoint safely before use; do not execute its training code. Access failure stops that route without mirror/retry loops.
2. In an isolated environment, test only that frozen encoder on generated arrays first. Establish declared preprocessing,4096dimensions, finite/deterministic output and actual CPU memory/time. Check gamma/colour response descriptively; do not call response magnitude accuracy or select feature subsets from it. Export/phone feasibility remains a separate measured question. Preserve the original128head/full4096 distinction; no size rescue variant.
3. Only if operationally feasible and specifically justified, prepare an input-only cached-development diagnostic. No tree fit follows automatically. Any new correction comparison needs a frozen prospective protocol, unchanged controls/renderer/ITA-MST and grouped roles, all harms/identity accounting and a stop rule. Pretraining uncertainty must remain disclosed; final24/older locks remain byte-unread.

A researcher choice to keep feature extraction lightweight means not pursuing this particular Re-IQA candidate. It would not establish that all learned features or decision trees fail. It also would not leave an evidence-backed new fitting run ready under the currently tested inputs. Do not substitute a negative-results thesis for the requested working-model goal or impose adviser approval. No new mask reviews, camera, PPR download or model-family replacement is requested.

## Verification and disposition

Ten pinned source-text hashes and source facts were checked; the network code was parsed but not imported. Encoder parameter count independently recalculated. Findings/receipts are in outputs/reiqa_feature_feasibility_v1. Downloaded material consists of public source/metadata only, not photo data, weights or scientific fixtures. No code was integrated into TrueHue, no runtime/Android changes, contact, upload, commit or push. All earlier failed comparisons remain closed and preserved.
