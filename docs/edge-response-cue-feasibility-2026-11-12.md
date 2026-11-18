# Edge-based response cue: specific feasibility assessment

12 November 2026. **Not qualified as a standalone added-gamma repair; no real-data fit or extractor selected.** User authorized finding a concrete inference-available traditional cue for source transfer. The candidate investigated here was gamma/response information from edge profiles, which differs from pooled Lab/lightness and a quality-score predictor. The decision tree, ITA/MST and traditional single-photo scope would remain if a usable extractor were eventually justified.

## Primary literature actually checked

[Lin and Zhang, CVPR2005, Determining the Radiometric Response Function from a Single Grayscale Image](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/grayscale.pdf) estimates the camera radiometric response from edge-region intensity distributions, using selected edges and a response-function prior. Its goal is mapping measured intensities to irradiance, not preserving a photographer's acceptable rendering. The method depends on an edge-mixture distribution assumption; the paper also discusses limitations of treating arbitrary camera response as a simple gamma. (Sections1?2.)

[Ng, Chang and Tsui, CVPR2007, Using Geometry Invariants for Camera Response Function Estimation](https://www.ee.columbia.edu/ln/dvmm/publications/07/cvpr07_TTNG_final.pdf) uses image derivatives and locally planar irradiance constraints to estimate camera response. It explicitly discusses detection ambiguity, derivative stability and physical assumptions for single-image estimation. Its geometry-based cue is relevant to response shape rather than average skin brightness, but it does not claim to identify an unknown extra edit relative to an unknown original. (Sections1?3.)

These are author/institution-hosted primary papers. No author code, response priors, neural weights, archives or packages were downloaded or executed. No reproduction/performance claim is made. Other search hits were not adopted as candidates in this assessment.

## Mismatch with our actual target

Inference for TrueHue sees the processed photograph. Our primary task restores a distorted image toward its acceptable encoded photographic original, not toward linear scene irradiance. Write an idealized acceptable rendering as F(L), with added synthetic gamma D_d(z)=z**d. The observed input is D_d(F(L)). Even exact knowledge of the combined response does not, by itself, separate the acceptable source response F from added d.

For a simple admissible response F(L)=L**r, the observed exponent is r*d. Source-response exponent r=.7 with no added edit d=1 and source-response r=1 with added d=.7 have the same total response. Yet their required nominal correction gamma differs:1versus1/.7. The same ambiguity holds for the existing1/.7distortion direction. A response-linearizing feature cannot be assumed to signal a bad photograph merely because its estimated curve is nonlinear.

Script857 verifies two GENERATED scalar ramp-edge pairs with21samples each. The inputs match exactly as RGB8-code sequences, while their acceptable reference sequences and inverse-gamma targets differ. In worldA the acceptable source is quantized after its own response; in worldB the original ramp is already integer-coded and then gamma-processed, matching our transform/round sequence. No photo or actual dataset collision is claimed. The construction proves a non-unique explanation within the stated source models, not universal impossibility of learned photographic correction.

The missing relation is whether actual acceptable sources have sufficiently predictable baseline response/processing for this cue to distinguish additional distortion across sources. Neither the papers nor this algebra establishes that relation. Known source rendering, metadata or a useful learned prior could change the assessment, but no such new requirement, acquisition or prior is imposed on the user. Keeping a physical scene-radiance target is not necessary for the study; in fact substituting one would change it.

## Disposition and limits

Do not install a response estimator, append a guessed gamma feature to the16inputs or launch another44case tree fit merely because this cue has a physical derivation. Its standalone extra-edit interpretation is not justified. This is narrower than declaring every edge feature, CRFmethod or traditional model impossible. The check also does not prove actual source transfer failure is caused by response ambiguity. It rules out using total response as if it were the known added recipe.

No further candidate, fitting campaign or review task is selected. The approved desktop ear coverage stays incorporated; measurement/protection and controls unchanged. Oblique and all prior trials remain closed. Preserve the user's model-first priority; paper paused, model unfinished. No return to neural features, capture, adviser approval, source-ID/MSTcutoffs or final access.

Artifacts: outputs/edge_response_cue_feasibility_v1/generated_counterexamples_ONLY.json and verification_PRIVATE.json. Independent replay confirms42matching observed codes across two21sample comparisons, distinct reference targets and unchanged bound input hashes. Generated examples never enter scientific rows. Zero dataset/source/cache/mask/final24/olderlocked image reads, real fits, predictions, runtime/Android changes, contacts/uploads/commitpush.
