"""Aggregate meeting notes; no private images, model loading or inference."""

BRIEF_PATH = 'docs/adviser-progress-brief-2026-11-07.md'
PROGRESS_TITLE = 'TrueHue research progress | 7 November 2026'
PROGRESS_TEXT = """WORKING PROTOTYPE; CORRECTION MODEL STILL IN DEVELOPMENT

This demo uses current masks with older baseline5 / fold1 correction controls.
Newer correction models/gates remain unadopted. MST uses the older mask only.

WHAT WE BUILT
Local photo input, face detection, skin selection, Lab/ITA measurement,
experimental MST estimation, gamma/red/blue correction, comparison and export.
The desktop now adds face/neck support, blending, object protection and clear-lens
handling. Switch the green overlay between correction and facial measurement.
Choose clear for transparent lenses, opaque for sunglasses, or uncertain to
keep glasses protected. Approximate rims and mask errors remain limitations.
Continuous MST and the newer correction/no-correction gates are research only.

CHANGES FROM THE PROPOSAL
- Pretrained face parsing and occlusion checking replace colour-only thresholds.
- Separate skin measurement from wider face/neck correction and blending.
- Added FFHQ source checks and Stellenbosch development experiments.
- Tested ITA + Lab continuous MST, separate predictors and correction gates.
- Revised distortion recipes and grouped development comparisons.
Experimental model changes are not adopted or formally panel-approved.

RECENT FINDINGS
Exploratory continuous MST: ITA + Lab MAE 0.73, versus ITA-only 2.37 and
median baseline 2.97; 29 available photos from 10 held publisher groups.
These are score errors, not percentage accuracy or independent validation.

Latest correction comparison (lower RGB error is better):
                            Retained    Signed    Constrained
Development clean edits       3/29      27/29        7/29
Development core RGB MAE      13.51       9.63       11.26
Later clean edits              1/23      23/23        3/23
Later fallback core MAE       17.43      11.65       14.06

The constrained gate protects fitting clean examples but still changes unseen
clean photos. It failed the required zero-change screen and was not adopted.
The retained research gate is also separate from the older live demo model.

WHAT REMAINS
Preserve unseen clean photos while correcting distorted inputs; improve mask
coverage and boundaries; evaluate actual-input masks and object protection;
complete independent assessment, professional feedback and later app integration.
Small exposed cohorts, synthetic distortions, 224px source images and imperfect
masks limit the findings. RGB reconstruction error is not perceived naturalness.
Repeated conditions are not independent people. No fairness claim is established.

PLAN AND DATES (PROVISIONAL)
Nov 8: agree on one justified next step; saved-trace diagnosis is proposed.
Nov 9-11: one bounded intervention only if justified and authorized.
Nov 12: reassess model readiness and conference scope.
Nov 13: target conference evidence/draft readiness; Nov 14: submission deadline.
Nov 28: low-confidence project planning target, conditional on model results,
integration and real reviewer availability. No fixed validated-model date yet.

MEETING DEMO
Use your own or otherwise permitted photo. Explain that the green mask and MST
are estimates and the result can be wrong. Show failures as well as successes.
Restricted dataset images and private review boards are not included here.
Open the full adviser briefing for the development history and evidence links.
"""
