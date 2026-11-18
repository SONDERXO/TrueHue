# Exposure versus colour: saved training audit

9 November 2026. **The harmful correction pattern already appears in fitting data.** The current summed-error objective permits a colour-only example to be harmed when many underexposed examples improve. This supplies a specific training-side reason for a constrained-objective comparison; it does not establish that the proposed constraint will generalise.

## Full-fit data and source pairing

The unchanged full fitting matrix has 890 conditions from 82 originals: 82 clean, 228 exposure-only, 222 colour-only and 358 combined. Source variants were paired with their own fitting clean original; no split or identity assumption changed. No evaluation features or errors were used to choose thresholds or fit a discriminator.

All 72 available core underexposure pairs lower both facial L* and scene median brightness relative to their own clean original. All 71 core overexposure pairs raise both. But colour-only conditions also often lower facial L*: 67/73 cool, 47/78 warm and 65/71 stress-colour pairs. The corresponding scene median never rises, and sometimes stays equal. Brightness change alone therefore does not uniquely identify exposure distortion.

Across colour-only pairs, facial L* changes range from −5.95 to +3.56; a* from −5.10 to +0.39 and b* from −11.85 to +2.53. These intervals overlap those of exposure-only pairs. Range overlap is not proof of multivariate inseparability. Facial changes include changes in actual-input mask selection as well as transformed pixels, so they are not pure fixed-pixel photometric effects. Same-source clean differences are unavailable to normal inference and must not become leaked features.

## Fitting harm behind the stress decision

The previously traced full-fit leaf has 68 rows: 67 underexposure conditions and one colour-only stress condition. Its gamma≈0.700 action harms that fitting colour condition: saved RGB MAE 6.67 with identity versus 28.15 after correction. Yet summed error over the leaf falls from 1,978.15 to 389.00, so the current objective prefers the action. No clean fitting row is present to prevent it.

This is one harmed colour-only row among 222 in the full pre-veto fit. The analogous evaluation harm is a separate already-exposed case; it was not fitted. Repeated synthetic conditions and folds are not independent people. No new accuracy result or parser improvement is claimed.

## Proposed single intervention

Add a fitting feasibility condition: **every colour-only fitting row must receive an action whose saved RGB cost is no greater than identity**. Preserve exact clean feasibility, source/group roles, reserved-clean veto, frozen facial exception, depth four, features, actions, costs and calibrated MST. Recipe membership supplies a training constraint only; it must not be supplied to inference.

The [fixed comparison protocol](colour-only-nonharm-protocol-2026-11-09.md) specifies exactly 11 fits and unchanged acceptance. It is a proposal, not an automatically started fit. This may reduce useful exposure recovery, may miss unseen colour failures and does not directly solve the mixed clean/overexposed identity branches or incomplete masks.

Scripts 656–657 verify source-paired deltas and saved colour costs. No model training, predictions, inference, rendering, new photos, annotation or holdout access occurred. Private output: `outputs/training_exposure_colour_audit_v1`. DINO remains unused while permission clarification is awaited; the final 24-photo holdout remains byte-unread.
