# Thesis 2 Implementation Plan

## Objective

Develop a smartphone-based, post-capture skin tone correction application that uses ITA-based skin tone estimation and a decision-tree model to improve exposure and color across Monk Skin Tone categories.

## Fixed Scope

- Platform: Android, on-device only
- Input: Gallery image (single face)
- Pipeline: face detection → skin mask → ITA → MST → decision-tree correction → corrected image
- Model: decision-tree regression (gamma, red gain, blue gain)
- Datasets: FairFace + SCIN (training), MST-E (evaluation only)
- Evaluation: MAE, CIEDE2000 ΔE, inference time, expert MOS (2 photographers)
- Out of scope: iOS, live camera, cloud processing, full-body correction, ISP modification

## Milestones

1. Python prototype (face + mask + ITA + MST)
2. Synthetic distortion generator
3. Baseline and decision-tree model
4. Android integration
5. System testing
6. Quantitative + expert evaluation
7. Thesis documentation
