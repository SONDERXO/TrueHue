# Smartphone-Based Post-Capture Skin Tone Correction Using ITA Estimation and Machine Learning

**Thesis 2 – Implementation Project**  
Department of Computer, Information Sciences, and Mathematics  
University of San Carlos  
Bachelor of Science in Computer Science

## Purpose

This repository contains the implementation of a smartphone-based, post-capture skin tone correction application that:

- Detects the face and isolates the facial skin region (HSV + YCrCb)
- Estimates skin tone using the Individual Typology Angle (ITA)
- Maps ITA to Monk Skin Tone (MST) categories
- Uses a decision-tree model to predict gamma and red/blue correction gains
- Runs entirely on-device on Android

## Repository Structure

```text
skin-tone-correction/
├── README.md
├── docs/
│   ├── implementation-plan.md
│   ├── experiment-log.md
│   ├── test-cases.md
│   └── decision-log.md
├── data/
│   ├── raw/
│   ├── processed/
│   ├── train/
│   ├── validation/
│   └── test/
├── notebooks/
├── src/
│   ├── data_preparation/
│   ├── face_detection/
│   ├── skin_masking/
│   ├── ita_estimation/
│   ├── distortion_generation/
│   ├── model_training/
│   ├── evaluation/
│   └── utilities/
├── models/
├── outputs/
│   ├── masks/
│   ├── corrected_images/
│   ├── metrics/
│   └── figures/
├── android-app/
└── tests/
```

## Team Members & Roles

| Name                | Primary Responsibilities                                     |
|---------------------|--------------------------------------------------------------|
| Nythan John Rivera  | Android app, on-device correction engine, integration, docs  |
| Oceane Rim Dardare  | Data/ML pipeline, ITA/MST logic, model training, evaluation  |

## Setup Instructions

### Python Environment (ML Pipeline)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Android App

- Android Studio (latest stable)
- Minimum SDK: API 24+ (adjust as needed)
- Language: Kotlin (recommended) or Java

## Datasets

- **FairFace** – primary training dataset  
- **SCIN** – secondary training dataset  
- **MST-E** – evaluation benchmark only  

Access and usage must comply with each dataset’s license. Do not upload raw datasets to this repository.

## Branching Strategy

- `main` – stable, demonstrable versions only  
- `develop` – integrated work in progress  
- `ml-pipeline` – Python/ML development  
- `android-ui` – Android application development  
- `testing-documentation` – tests, docs, and evaluation scripts  
