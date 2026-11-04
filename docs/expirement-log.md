# Experiment Log

## Format

For each experiment, record:

- Date
- Goal
- What was changed
- Dataset / sample size
- Key results (numbers + observations)
- Decision
- Next action
- Git commit hash

## Example

### 2026-09-08 – Skin mask threshold tuning

- Goal: Improve skin mask for medium/dark tones
- Change: Adjusted YCcan you rCb thresholds
- Sample: 30 images from FairFace (MST 04–09)
- Result: Better coverage for MST 06–08; more noise for MST 09
- Decision: Keep new thresholds; add morphological cleanup
- Next: Test with erosion/dilation
- Commit: `abc1234`

### 2026-09-20 – Batch face detection and facial skin-mask pilot test

- Goal:
  Test YuNet face detection and HSV/YCrCb facial skin masking on 15 pilot images1
  before beginning ITA computation.

- Input:
  15 local pilot images stored in `data/raw/pilot_images/`.
  Images were not committed to Git.

- Implementation:
  - Face detector: YuNet ONNX using OpenCV `cv2.FaceDetectorYN`
  - Face processing: largest detected face only
  - Skin masking: HSV + YCrCb thresholding applied only within the face crop
  - Output artifacts:
    - Face crops: `outputs/pilot_face_crops/`
    - Binary masks: `outputs/pilot_masks/`
    - Visual overlays: `outputs/pilot_visualizations/`
    - Summary CSV: `outputs/metrics/pilot_face_skin_results.csv`

- Results:
  - Total images: 15
  - Successful face detections: <fill in>
  - Failed face detections: <fill in>
  - Masks passing the 1,000-pixel rule: <fill in>
  - Skin-ratio range: <lowest>% to <highest>%
  - Main observed false positives: <fill in>
  - Main observed false negatives: <fill in>

- Decision:
  - <Example: Keep YuNet face detection.>
  - <Example: Modify mask cleanup and retain only the largest connected component.>
  - <Example: Continue to ITA computation only after visually acceptable masks are obtained.>

- Next action:
  Implement CIELAB conversion and ITA computation only for images with
  acceptable facial masks.

- Commit:
  <paste commit hash>


  ### 2026-09-22 – Skin-mask pilot review and identified limitations

- Goal:
  Manually review the V1 facial skin masks generated using YuNet face
  detection, HSV/YCrCb thresholding, morphology, and largest connected
  component filtering.

- Findings:
  - The mask frequently included eye-area pixels, excluding primarily the pupils.
  - The mask included eyebrow regions in some images.
  - The mask inconsistently excluded valid cheek areas for lighter skin under
    some imaging conditions.
  - The mask performed poorly in low-light conditions, particularly for
    darker skin, where valid facial skin pixels were often missed.

- Interpretation:
  HSV/YCrCb color thresholding alone cannot reliably distinguish facial skin
  from nearby anatomical regions such as eyelids, eyebrows, and lips. Its
  sensitivity to illumination also introduces a potential skin-tone-related
  reliability concern.

- Decision:
  Preserve V1 as the baseline skin-mask implementation. Develop V2 by adding
  landmark-based exclusion masks for eyes, eyebrows, and mouth/lips after the
  HSV/YCrCb candidate mask and largest-component filtering stages.

- ITA handling:
  ITA must be computed from pixels in the original facial image selected by
  the final V2 mask. Any illumination-normalized image, if used, will be used
  only to assist segmentation and not as the source of CIELAB values for ITA.

- Next action:
  Implement landmark-based facial-feature exclusion and rerun the same pilot
  image set to compare V1 and V2 masks.


  ### 2026-09-22 – V2 masked CIELAB and ITA pilot computation

- Goal:
  Compute mean CIELAB statistics and Individual Typology Angle (ITA) using
  only facial-skin pixels selected by the chosen Skin Mask V2 pipeline.

- Input:
  16 pilot images from `data/raw/pilot_images/`.

- Pipeline:
  YuNet face detection → Skin Mask V2 → selected skin pixels from original
  BGR face crop → OpenCV Lab conversion → conversion to conventional CIELAB
  values → mean L*, mean a*, mean b* → ITA computation.

- Validity rule:
  Images with fewer than 1,000 selected skin pixels are excluded from ITA
  computation.

- Result:
  - Images processed: 16
  - Valid ITA calculations: 16
  - Excluded images: 0
  - Skin-pixel range: 12,086 to 37,063
  - Mask-coverage range: 31.25% to 88.40%
  - Mean L* range: 22.0228 to 71.6681
  - ITA range: -79.2380° to 50.9661°
  - Output CSV: `outputs/metrics/v2_pilot_ita_results.csv`

- Interpretation:
  The pipeline generated valid numerical ITA outputs for all pilot images.
  Results remain dependent on the quality of V2 skin masks and image lighting.
  The pilot values are image-derived estimates and are not treated as clinical,
  racial, ethnic, or permanent labels.

- Next action:
  Review selected masks and ITA outputs for plausibility, then construct a
  documented MST-E-calibrated ITA-to-MST mapping procedure.


  ### 2026-10-13 – SCIN metadata subset selection

- Dataset:
  SCIN official metadata.

- Selection method:
  Reproducible metadata-only sampling using seed 42 and official estimated
  Monk Skin Tone (eMST) labels.

- Broad groups:
  - Light: eMST 01–03
  - Medium: eMST 04–07
  - Dark: eMST 08–10

- Requested subset:
  75 candidate images per broad group.

- Result:
  - Light: 75 selected
  - Medium: 75 selected
  - Dark: 34 selected from 17 unique cases
  - Total: 184 selected candidates

- Interpretation:
  SCIN contained insufficient official eMST 08–10 cases to meet the requested
  dark-group target. No duplicated cases were introduced merely to force
  balance.

- Decision:
  Use all 184 selected SCIN candidates as a supplemental training source.
  Address dark-group balance using the combined FairFace + SCIN candidate pool,
  while preserving the distinction between official SCIN eMST labels and
  FairFace image-derived estimates.

- Next action:
  Test-download one SCIN image from the selected candidate list, validate the
  source path, then download only the selected candidate images.