# Planned primary-data comparison completed; candidate not adopted

30 October 2026. Imported the finished primary-mask review: **58 accepts,
3 rejects, no missing or uncertain decisions**. Fourteen accepted masks have
notes, preserved verbatim. Ran the one predeclared comparison without changing
features, tree settings, targets, mask rules or gates. Normal-case reconstruction
improves, but clean safety and stress behavior worsen. The candidate is not
adopted, and the small-model experiment cycle is now stopped as agreed.

## Review import and training data

All three rejects are source 6236: color, gamma lightening and gamma darkening.
The exact note on each is “Background is in face mask, but good facial coverage”.
These three inputs stay out of candidate fitting. Its separately approved
original clean control remains; reference approval and variant decisions are
different scopes. No accepted note is removed or converted into a rejection
to improve the result.

The 58 eligible accepted inputs span 25 sources: 24 lightening, 24 darkening,
nine original color components and one original exposure component. The model
uses these plus the 26 original controls: 84 rows before held-source exclusion.
These remain only 26 source groups, not 84 independent people. Existing clipped
stress inputs and mask-screen holds are retained separately.

Script 282 checks schema/manifest identity, frozen review/source evidence,
source-group/reference lineage, input and mask hashes, input-only Lab/ITA/MST/
endpoint features and recipe-specific targets. Gamma-only targets reproduce
the declared power recipe; fitted color/exposure targets reproduce saved fit
residuals. Supplemental gamma data remain explicitly separate from the complete
Table 2 recipe. No calibration or original measurement contract changes.

## The single fixed comparison

The [predeclared protocol](primary-training-single-comparison-protocol.md) is
unchanged: eleven endpoint-model features, direct gamma/R/B targets, depth 3,
seed 42, minimum leaf 1, unweighted rows and fitting-control identity protection.
Each source and every one of its variants are held out together in 26 folds.
The baseline is the frozen endpoint model for that same source-held fold, not
a refit or a selected favorable model.

Both methods are evaluated on the exact same 105 inputs: original 47 plus
58 accepted primary cases. All 105 saved inputs have successful preparation
measurements. This comparison reuses their exact reviewed masks; it does not
claim a new detector/mask robustness test. No reserved source is opened.

Lower CIEDE2000 is better.

| Scope | Cases | Frozen endpoint baseline | Primary-data candidate | Unchanged input |
|---|---:|---:|---:|---:|
| All primary distortions | 58 | 8.312 | **6.629** | 8.362 |
| Lightening | 24 | 10.023 | **8.252** | 9.548 |
| Darkening | 24 | 8.533 | **5.889** | 9.128 |
| Color components | 9 | **3.929** | 4.853 | 3.929 |
| Original exposure component | 1 | 1.412 | 1.412 | 1.412 |
| Earlier clipped stress | 21 | **11.279** | 18.000 | 20.511 |
| Original 47 | 47 | **5.300** | 8.712 | 9.165 |
| Matched total | 105 | **6.964** | 7.561 | 8.721 |
| Clean photos changed | 26 | **1** | 3 | 0 |

The normal-case mean improves about 20% versus the baseline, but the matched
total is about 8.6% worse. Source-equal summaries tell the same direction:
primary 8.686 to 6.902; full matched set 6.957 to 7.475. Color correction does
not improve, so the primary pooled gain must not be described as a color-gain
solution. Candidate stress error also worsens substantially.

The candidate changes three held clean photos: 83205 (11.277 error), 29880
(10.136) and 68073 (10.047). Inspected all three output boards; each shows a
visible unwanted brightening/mask-shaped correction. These are not merely
rounding-only pixel differences. The old 68453 clean failure is unchanged by
the new model, but fixing that one case does not compensate for three new
failures. No source exceptions or threshold changes are introduced.

Open [all 105 comparisons](../outputs/reviewed_primary_comparison_v1/review.html).
The gallery includes every case and prioritizes clean failures from either
method. It requests no additional user labels. Earlier mask notes are shown
where applicable. All image links/hashes are checked; live browser testing is
not claimed. The three candidate clean-failure boards were inspected locally.

## Verification and stopping decision

`scripts/283_run_primary_training_comparison.py --verify` independently checks
105 input feature vectors, refits all **26 candidate trees**, reconstructs
fitting-only protected memberships, replays **210 output images and metrics**,
checks held-source separation and outside-mask preservation, and reproduces
all 47 original frozen baseline predictions exactly. Script 284 preserves the
gallery and a machine-readable `stopping_decision.json`.

No core library changed. The last full-suite result remains 798 passing tests;
this run uses the independent admission/tree/pixel verification, not a claim of
another full-suite run. All datasets, decisions, targets, source roles and notes
remain retained. No photographer work, reserved-data access or demo replacement.

The clean-safety gate fails for both models, and the primary candidate is not
an overall upgrade to the previous research candidate. **Do not launch another
feature, depth, weight, threshold, source-exception or recipe trial in response.**
The agreed comparison is complete and the failed outcome is preserved. Continue
only after a documented source-data or method decision, as described in the
[post-comparison decision checkpoint](primary-comparison-decision-checkpoint.md).
