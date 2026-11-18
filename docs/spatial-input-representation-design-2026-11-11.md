# Input redesign: spatial natural-scene statistics feasibility

11 November 2026. The user authorizes a justified input-feature redesign while retaining the final decision tree, ITA/MST, single-photo input, face/visible-neck support and optional manual refinement. This specification selects ONE representation family for generated-only engineering feasibility, not a new correction fit or a validated illumination estimator.

## Rationale and primary sources

The tested absolute summaries misroute distinguishable source variants even after fitting loss improves. They omit pixel-neighborhood statistics. Earlier left/right and top/bottom brightness, quantiles/IQR, chromatic covariance, endpoints, green distributions and the p6 bright-scene cue were tested and remain closed. A literature/repository check found no BRISQUE/MSCN/AGGD implementation in reviewed docs/src. This is a scoped local finding, not novelty.

Mittal, Moorthy and Bovik (2012) describe locally normalized luminance and neighboring coefficient products for no-reference image-quality assessment. Their result motivates an input representation that responds to local spatial distortions instead of absolute brightness alone. It does NOT prove gamma direction prediction, complexion independence, skin-colour accuracy or correction generalization. Treat any such benefit as our untested hypothesis. Local normalization may suppress a gamma signal as well as suppressing content variation. BRISQUE quality is not the study's restoration target.

- Authors' original paper: https://live.ece.utexas.edu/publications/2012/TIP%20BRISQUE.pdf
- Authors' laboratory listing: https://live.ece.utexas.edu/research/Quality/index_algorithms.htm
- OpenCV implementation/licence reference: https://github.com/opencv/opencv_contrib/blob/4.x/modules/quality/src/qualitybrisque.cpp

Use an independently written descriptor inspired by the published equations, not a bundled BRISQUE model, pretrained SVM/SVR, learned embedding, score optimizer, correction selector or imported release. No code/weights/package download or installation. Existing NumPy/OpenCV/SciPy suffice in this environment. Mathematical distribution-parameter moment estimation is part of the descriptor, not a fitted correction predictor. No copied third-party code; cite the original method in the paper. Reusing the publisher's software later would require its full notices; no such reuse is selected now.

## Fixed engineering convention

Input is actual RGB8 frame, minimum 16x16, interpreted as delivered encoded RGB. Form code-value luma .299R+.587G+.114B (not linear physical luminance). Use full frame, no skin-only fill, new crops, mask morphology or synthetic borders. Calculate local mean and variance with a 7x7 Gaussian sigma7/6, reflected border, float64. Coefficients are (Y-mean)/(sqrt(max(local variance,0))+1), stabilizer in 8-bit code units. This makes no linear-RAW or illumination-truth claim.

At original scale and one half scale (OpenCV area resampling), extract two symmetric-GGD moment parameters from coefficients and four AGGD parameters from each H/V/D1/D2 neighboring product distribution, 18 per scale, 36 total. Neighbor products use valid pairs without circular wrap. Half-scale resampling and valid-pair boundaries are explicit implementation conventions; do not claim numerical equivalence to the authors' MATLAB code or OpenCV BRISQUE.

GGD shape uses deterministic minimum moment-ratio difference on [.2,10] with step .001; this is fixed numeric density estimation, not an exposure/feature/model sweep or a selected classification threshold. GGD second parameter is empirical variance. AGGD features are shape, distribution-implied mean, left variance and right variance. Zero-energy or single-sided degeneracy must yield defined finite diagnostics, not an admitted correction decision or silent case removal. Record feature names/order and constants. No per-dataset centering or reference/recipe/source metadata enters the extractor.

Retain the existing 16 inputs unchanged in any eventual comparison; this candidate would add 36, for 52 inputs. No feature subset search. That is a substantial dimensionality risk with only 11 source groups, not automatically enough data or authority to fit. The descriptor does not add independently observed information beyond the input pixels; it retains different information than the previous summaries. Luma features do not directly identify red/blue gain, so existing chromatic inputs remain necessary but unproven.

## Current authorized stage and stop rule

Generated-only implementation checks: independent local-window arithmetic; known normal/Laplace moment shape checks; constant/one-sided/invalid inputs; output finiteness and determinism; same-histogram frames with different spatial arrangements; descriptive response to the existing gamma/red recipes on generated textures. Fixtures stay outside scientific records/annotations. Do not call those fixtures portraits, correction data, accuracy, tone groups or learned predictions. Report non-response or confounding rather than changing scale, channel, sigma, moments or dimensionality in response.

After verification, review whether the descriptor contains distinct spatial information and whether its costs/degeneracies are acceptable for bounded cached-development extraction. Do not automatically train. An eventual photo-held comparison needs a separate prospective specification, same targets/operator/masks/MST and explicit dimensionality/overfit risks. No parent refit, target repair, new normality threshold, quality-score gate, independent MST claim, full-task completion or automatic Android integration. PPR remains optional and paused; original/final/older locked bytes stay unread. No new photo acquisition, capture, user mask reviews, calibration fit or contact.
