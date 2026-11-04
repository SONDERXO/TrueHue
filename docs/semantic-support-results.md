# MediaPipe skin/hair comparison — 23 October 2026

Integrated follow-up: [versioned correction option](integrated-correction-option.md)
provides a single-image command and checks all existing controlled attempts.

The **semantic hair veto** is the preferred next correction-mask development
candidate. It removes two of three remaining clean-image hair selections while
keeping all 12 reviewed skin points. Using the semantic face-skin mask alone
includes all three reviewed paint points, so it is not a replacement default.
Neither candidate has been adopted into the production/approved thesis pipeline.

## Fixed setup and model provenance

The official SelfieMulticlass 256x256 float32 model, version1, was downloaded
locally into ignored `models/selfie_segmenter/`. No dataset images were uploaded.
Its 16,371,837-byte file has SHA256
`c6748b1253a99067ef71f7e26ca71096cd449baefa8f101900ea23016507e0e0`.
The adjacent provenance JSON records pinned URL, checksum, ETag and download time.

The [official model guide](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter)
documents background, hair, body-skin, face-skin, clothes and others. The installed
model's label metadata was checked against that exact order. The
[Python guide](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter/python)
provides the ImageSegmenter API used here. Paint is not a dedicated model category.

Two rules were specified before scoring, without a confidence sweep:

- **Semantic face skin:** full-input category argmax equals3, restricted to the
  existing face box and excluding eyes, brows and complete mouth.
- **Semantic hair veto:** remove category1 from the previous material-checked
  correction support. It may remove baseline hair as well as new additions, but
  cannot add missing skin or reject non-hair material by itself.

The model processes the full input image; MediaPipe returns native-resolution
categories. Estimation masks, input Lab/ITA features, correction tree and its
predicted parameters remain fixed. Frozen human labels enter scoring only.

## Your 24-point regression results

| Input | Mask | Skin retained /12 | Hair selected /4 | Paint selected /3 |
| --- | --- | ---: | ---: | ---: |
| Clean | Previous material check | 12 | 3 | 0 |
| Clean | Semantic face skin | 12 | 1 | 3 |
| Clean | Semantic hair veto | 12 | 1 | 0 |
| Color shifted | Previous material check | 10 | 1 | 0 |
| Color shifted | Semantic face skin | 12 | 1 | 3 |
| Color shifted | Semantic hair veto | 10 | 1 | 0 |

All methods in this table exclude the five reviewed Other points. All96 new
semantic point observations were available. These selected points are known
development regressions, not image-area accuracy or independent validation.

The hair veto fixes baseline clean-hair P05 (29962) and P15 (val/10480). Hair P06
(29962) remains selected in both clean and shifted variants. The prior shifted
skin misses P14 (val/10480) and P19 (62331) remain: a removal-only filter cannot
recover them. The semantic face-skin mask recovers those skin points, but also
includes paint P09–P11. No human labels were changed to accommodate a candidate.

## Fixed-model image results

| Mean CIEDE2000, lower is better | Development:3 variants,1 source | Clipped stress:4 pairs |
| --- | ---: | ---: |
| Original mask | 7.609 | 13.916 |
| Previous material check | 6.622 | 13.967 |
| Semantic face skin | 6.648 | 13.305 |
| Semantic hair veto | 6.643 | 13.741 |

All seven pairs completed. The hair veto is primarily a material-support
improvement, not a new color-error win on the one-source development set.
Its development generation-region coverage is92.9% versus93.4% previously;
outside-region RGB MAE is0.00104 versus0.00109. Stress cases are nonindependent
and still expose model prediction failures. Source-mask overlap does not tell
whether removed pixels are genuine skin or previously included hair.

## Broader mask diagnostics and timing

All92 source/variant attempts were recorded (46 development sources, clean and
fixed color shift), with per-method availability kept separate:

- Original and semantic face-skin masks:90 available, two landmark failures.
- Material check and hair veto:83 available, inheriting those two failures plus
  seven insufficient-color-seed cases. A semantic-only result is not silently
  dropped merely because the older color candidate is unavailable.

On the same37 shifted inputs where every method is available, mean generation-
region coverage is72.2% for the material check and70.5% for the veto; extra-region
pixels decrease603 to496. On46 clean inputs, overlap with the baseline generation
region falls100% to97.4%. This region includes known baseline hair mistakes, so
less overlap is not automatically lost genuine skin. Clean100% is tautological,
not a skin-accuracy result. Matched averages and all excluded cases are preserved.

Visual checks covered all three source19 model comparisons, broad clean29962,
shifted16798, clean76841, shifted6236 and the review board including clean10480.
Hair trimming is visible without the previous GrabCut collapse. Pure face-skin
also includes paint and can include other unwanted facial materials. Narrow
seams, incomplete coverage and existing geometry failures remain. Most broader
sheets received automated checks only; no full new human approval is claimed.

Median warmed segmentation-call time is about165ms on this desktop. It excludes
face detection, landmarks, feature extraction, correction and model startup;
it is not an Android end-to-end latency result. The model introduces another
16.4MB float32 weight file; deployment suitability still needs separate testing.

## Reproducibility and verification

```text
venv/Scripts/python.exe scripts/36_download_selfie_segmenter.py
venv/Scripts/python.exe scripts/37_test_selfie_segmentation.py --output-name semantic_support_channels_v1
venv/Scripts/python.exe scripts/38_summarize_semantic_support.py
```

Existing weights/runs are protected from overwrite. Download requires network
access; inference is local. Final artifacts are in
`outputs/semantic_support_channels_v1/`: comparisons, category maps, masks,
per-input availability, metrics, timings, frozen-point scores and hashes.
`hair_filter_review_board.png` compares input / previous mask / hair veto.

An initial compatibility run in `outputs/semantic_support_v1/` rejected every
semantic output because installed MediaPipe1.0.1 returns categories as H×W×1.
The adapter was corrected to remove only that singleton channel (no resizing or
policy change), and a separate full run completed. Initial unavailable outputs
were preserved and are not treated as algorithm-performance evidence.

431 tests passed. Tests cover category order assumptions, class selection,
anatomical exclusions, face bounds, hair-only removal, invalid inputs and native
singleton-channel normalization. The real model was also exercised on the full
run. Prior baseline images/features reproduced exactly, saved model and human
label hashes remained unchanged, and final run input hashes were checked.

## Decision

Keep semantic hair veto as a versioned development candidate; do not replace the
estimation mask or silently adopt the raw semantic face-skin mask. Next assess
the candidate's actual corrected images and residual boundary errors before
using it for a larger controlled run. Retain P06/P14/P19 as unresolved regression
cases rather than tuning thresholds until these known points pass.

Adding a segmentation model is a separately documented implementation/methodology
decision if adopted. No Android files, final MST mapping, approved methodology,
training eligibility or final-test set changed here. These exploratory results
do not establish fairness, generalization, calibrated skin color or final thesis
performance.
