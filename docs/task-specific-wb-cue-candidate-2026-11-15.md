# Candidate: externally supervised white-balance evidence for control prediction

15 November 2026. The user asks whether the assistant can offer a solution. This is a concrete candidate rationale and initial source-only review, **not a working solution, inference authorization, selected executable fit or model adoption**.

## Paper check

Rechecked cached proposal PDF pages 14 and 63 and the latest alignment re-audit. Retain single-photo feature-to-control inference, ITA/MST and the photographic restoration goal. A possible final ordinary regression tree would retain the written predictor family, but features derived from an externally trained white-balance mapping are a substantive feature/prior extension. They must not be described as only original facial statistics. No alternative pretrained pixel-level correction network, hidden image-correction stage, MSEC revival or real-camera-bias claim is proposed. ECPD is optional.

## Specific hypothesis

Our latest added representation was trained for generic image quality, not explicitly for identifying white-balance error. The local reference prior learned acceptable colour from ten other portraits and showed substantial natural-source mismatch. A frozen prior trained on documented incorrect/correct rendered-white-balance pairs could provide correction-specific evidence that those representations lacked. It may still fail on faces or alter acceptable complexions; external supervision does not prove suitability.

The concrete candidate is to expose the external model's predicted colour-mapping coefficients as input features to one correction-control regressor, alongside the retained traditional features including ITA/MST. The external mapping would NOT be applied to the user's photograph. The sole output renderer would apply the final declared controls under existing alpha/protection. There is no secret external correction followed by another correction, nor any held reference or person ID at inference.

This is an own proposed adaptation, not the published WB_sRGB algorithm or a demonstrated improvement. Its 11-by-3 polynomial mapping cannot be called three red/green/blue gains. A parameter feature design still needs a frozen contract and compatible target/renderer selection before fitting. Do not assume that improvements in the old exposure trials survive a new predictor or that three controls reproduce an arbitrary nonlinear map.

## Source-only findings

[Afifi et al., CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/html/Afifi_When_Color_Constancy_Goes_Wrong_Correcting_Improperly_White-Balanced_Images_CVPR_2019_paper.html) describes a rendered-photo white-balance method learned from over 65,000 paired examples, using nearest-neighbour retrieval to obtain nonlinear colour mappings. It explains why raw illuminant gains alone need not correct already rendered photographs. This supports investigating correction-specific supervised evidence; it does not establish a TrueHue solution or exposure restoration.

Read the official [README](https://github.com/mahmoudnafifi/WB_sRGB/blob/master/README.md) and [Python class](https://github.com/mahmoudnafifi/WB_sRGB/blob/master/WB_sRGB_Python/classes/WBsRGB.py) through the GitHub connector. Observed master: `98340313cc7d1728e286ad9ba03e8f9a0e8b82c5`. The cached texts were fetched from master before resolving that revision; their cache hashes bind the observed text, not a verified pinned-file fetch.

The official Python class computes a colour histogram, uses stored PCA/nearest-neighbour assets, blends stored polynomial functions and applies an 11-by-3 mapping. It is not a pixel-level neural correction network. We do not propose tuning its neighbours, bandwidth, model variant or gamut settings. No assets were loaded or downloaded.

Important compatibility issue: its `im2double` calls OpenCV MINMAX normalization rather than simply dividing by 255. Exposure and feature semantics therefore cannot be assumed to match our inputs. The paper/README do not establish author-environment or MATLAB/Python bitwise parity. Simply copying `correctImage` would not implement the proposed parameter-only interface.

The README describes research-only use and points to a license file. A direct fetch of the guessed root `LICENSE` path returned 404; the actual license document was not located in this initial check. Exact artifact terms, file availability/sizes, camera/scene provenance, portrait applicability and pretraining overlap remain unresolved. No legal or deployment clearance is asserted.

## History distinction and limit

The Rendered WB dataset was already reviewed on November 2 and 9; this is not a new dataset discovery or reopening its portrait acquisition route. The scoped docs check found no completed use of this frozen external mapping as a parameter feature. The external supervised corpus, rather than another fit on our eleven sources, is the proposed additional information basis. Nearest-neighbour machinery alone is not new; the old local 1NN and projection trials remain closed. Gray-pixel, highlight, sclera, conditional-prior, oblique, linear-leaf, target-weighting and generic Re-IQA failures are not reopened.

## Bounded path before any real fit

1. Resolve the exact model-asset terms, sizes, provenance and parameter-only interface from official source metadata. No dataset/image/model downloads follow automatically. Stop if this use is unsuitable or unavailable; no substitute-model queue.
2. If feasible, specify one generated assessment of preprocessing, finite features, coefficient semantics and unchanged final-renderer/protection behavior, including empty/zero histograms and failure cases. Engineering PASS is not colour-quality evidence.
3. Before any portrait inference, freeze one diagnostic on the existing exposed camera-task roster: test colour-error discrimination/control-direction evidence and report all identity responses, not merely nearest family accuracy. No held reference at inference; no source deletion or threshold chosen from the observed outcomes. Failure closes this candidate without a k/feature/normalization rescue sweep.
4. Only supportive results could justify one separately fixed ordinary-tree feature-to-control assessment, all original roles retained, complete exposure AND colour gates and candidate-specific human review. No prior acceptance transfers. Darker-tone qualification and Android remain separate unfinished requirements.

The numerical discrimination statistic and thresholds in step 3 are not specified here, so this note is NOT an executable experiment protocol. No new fit is selected. There is no demonstrated full correction solution or Friday completion promise.

Preserved: model unfinished, manuscript paused, darker-skin priority, Friday November 20 before noon Manila, all ratings/artifacts/manual ears. Zero photos, dataset arrays, correction-model assets, raw originals or locked contents/manifests accessed. Zero fits, predictions, renders, ratings, contacts, runtime/Android/manuscript changes. Public paper abstract, README and source text only; no code execution from the external repository.
