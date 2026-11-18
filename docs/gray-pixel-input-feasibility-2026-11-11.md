# Gray-pixel colour-cast cue: assumptions and readiness

11 November 2026. User requested an assessment before any implementation/training selection. **Distinct lightweight mechanism, but no correction fit justified yet.** This is a completed source-and-equation assessment plus generated analytical examples, not a complete gray-pixel algorithm test, source-photo screen or failed correction comparison.

## What the published method supplies

Yang, Gao and Li (CVPR2015) seek approximately achromatic textured patches through similarity of local contrast in log RGB, then estimate illuminant chromaticity. It assumes suitable detectable near-gray regions and locally uniform illumination. Flat/isolated gray pixels are unsuitable for its local-difference test. The authors explicitly describe their equal-log-contrast condition as necessary, not sufficient: some coloured pixels satisfy it. Their benchmark results do not establish TrueHue correction controls or performance on our rendered photographs. [Original paper, sections2.1-2.3](https://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Yang_Efficient_Illuminant_Estimation_2015_CVPR_paper.pdf).

Later primary work analyzes false gray detections and uses a different reflection model; it discusses linear, black-level-corrected, unsaturated inputs. That supports treating the physical interpretation carefully, not silently replacing the2015algorithm with a2019variant. [Qian et al.,2019, sections2-3](https://arxiv.org/html/1901.03198).

## Difference from our closed features

Our failed chromaIQR/covariance features describe whole selected distributions. The failed p6scene cue describes channel moments; the recent spatialNSSdescriptor describes locally normalized luma distributions and products. Gray-pixel selection instead uses cross-channel relationships of local log contrast to identify candidate regions before pooling colour. No full gray-pixel implementation was located in the scoped docs/src search. Distinct computations do not imply useful correction information or justify a tree fit by themselves.

If tested later, only a contextual R/G and B/G summary of automatically selected scene candidates could feed the retained16inputs and one correction tree. No grayness score would certify neutral material, label skin tone, gate correction, alter facial masks or supply gamma/red/blue directly. Do not overwrite the existing statistics, MST map or nominal inverse controls. The current tree remains the only correction-control predictor; no gray-world/white-balance pre-correction stage is selected.

## Generated analytical checks: what is and is not identifiable

For a positive textured patch T(x), let I_c(x)=a_c*T(x), with constant channel factors a_c. Then log I_c=log a_c+log T. Every channel has exactly the same nonzero local log standard deviation, whether a=[1,1,1] (neutral) or [1.4,.8,.6] (coloured). Equal log contrasts therefore do not distinguish material chromaticity from a diagonal cast in this example. The same observed pixels can be factored as a coloured surface under neutral illumination or a neutral surface under coloured illumination. This is an analytical ambiguity, not a new claim of physical-truth requirements for the paper.

Apply the existing controlled transformation J_c=I_c**g*k_c without clipping. Local log standard deviations become g*std(log T), still equal across channels. A normalized cross-channel spread of those deviations remains zero. This necessary-condition diagnostic alone therefore does not identify exposure direction. It is NOT the complete published gray-index ranking, which has additional processing/selection; no claim that all its selected pixels stay unchanged under gamma is made.

For the coloured patch, pooled R/G equals (a_R/a_G)**g*(k_R/k_G). It changes under common gamma even without a red/blue cast. For a truly neutral patch, R/G remains k_R/k_G. Thus correct candidate selection matters to the proposed cast-versus-exposure use. A plausible near-neutral-selection statistic cannot automatically be treated as an independently observed cast value. An additive code offset also breaks log-gain cancellation; unknown image processing can matter.

Script838 verifies these identities on two generated3x3patch types under identity/under/over/red-attenuation, eight patch conditions, with independent scalar arithmetic for24logvariances and27exact product identities. No selection percentage, grayness threshold, smoothness, black cutoff or classifier was tuned. Fixtures are not photos, scientific rows, independent people, learned predictions or new annotations. This confirms a mathematical limitation already allowed by the original paper, not measured failure of the full algorithm.

## Compatibility with TrueHue's actual inputs

The available working inputs are processed RGB8 photographs, not verified linear camera-sensor data. Encoded-RGB gamma/gain operations are useful controlled engineering transforms, but an estimated scene chromaticity is not a measured illuminant. Applying the standard sRGB inverse transfer function would define another processing convention; it would not undo unknown original white balance, tone mapping, local edits or clipping. No inverse-camera calibration or RAW acquisition is required or selected here.

At256px, resizing/quantization can erase local texture or introduce cross-channel differences. Log zero and flat-patch handling require explicit definitions. Scene candidates may be clothing, backgrounds, skin or textured coloured objects; none becomes a validated neutral ROI. Differing local illuminants mean scene candidates need not describe the face's illumination. Do not invent true neutral labels from white-looking objects or ask the user for another mask review to supply them. Conversely, absence of neutral ground-truth labels does not universally ban exploratory input features; it limits what can be claimed about them.

## Implementation terms and resources

Author repository pinned at 21cbfaf8f7cece657c3e3276c9bc80958d22831d. Its README identifies a2015MATLABrelease ZIP; repository licence is GPL-3.0. Only public README/licence/tree metadata were fetched; neither the11.5MBZIP nor other bundled files/data were downloaded or executed. No GPLsource is copied into TrueHue's runtime. Reusing that implementation would require retaining its applicable terms; a published-equation implementation would need its own explicit numerical convention and attribution, not a claim of author-code parity. [Author repository](https://github.com/kaifuyang/Gray-Pixel).

Local window filters, logs, ranking and pooling are traditional operations compatible in principle with lightweight single-photo extraction. No CPU/phone benchmark, final parameter choices or output availability is established. There is no pretrained encoder, neural feature source, checkpoint or new dataset requirement. Existing segmentation and optional manual support remain unchanged.

## Decision and specific next evidence

Do not start another correction fit, cached-photo feature screen, threshold variant or new user annotation under this assessment. The method remains a possible contextual feature family, not a qualified repair. It is not rejected as universally incapable and it has no new model-comparison failure result.

If pursuing this family, the next concrete deliverable is ONE complete, frozen selector/extractor engineering specification from the published algorithm: settle exact gray-index formula, neighborhood/border treatment, positive/flat/dark/saturated handling, ranking/pooling, deterministic ties and an explicit unavailable outcome. Use published settings where verified, not a grid chosen on our held outcomes. Demonstrate its complete behavior on generated neutral, coloured and mixed patches under the same fixed transforms, including false candidates and RGB8quantization, before selecting any cached-data extraction. The current necessary-condition calculation does not meet that full-method verification requirement. Such a specification must explain why region selection could add information beyond our failed summaries and how it will report its known ambiguities. Do not add runtime thresholds or universal admission boundaries.

Only a complete operational descriptor could be considered for a later bounded44cached-input readiness screen with unchanged16inputs/targets/MST/folds/masks. That would still not prove better correction or authorize automatic training. If the descriptor only reproduces existing scene ratios or confounds exposure/cast in those cases, stop it without window/percentile/channel rescue. No switch to a newer gray-pixel variant follows automatically.

Keep the main paper's synthetic-original restoration objective, one tree, ITA/MST, lightweight traditional features, face/visible-neck scope and optional manual refinement. Existing failures stay closed, neural feature extraction remains declined and PPRoptional/paused. No physical-colour study, perfect-neutral detection requirement, new capture or adviser approval is imposed. The correction model is unfinished; this assessment supplies no deployed improvement.

## Preservation and receipts

outputs/gray_pixel_feasibility_v1 contains source metadata and generated analytical results. No local photo, reference, mask, final24 or older locked image bytes read. No model/target/calibration fits, correction predictions, original-photo acquisition, contact, upload, commit/push, runtime or Android changes. Original artifacts/reviews preserved.
