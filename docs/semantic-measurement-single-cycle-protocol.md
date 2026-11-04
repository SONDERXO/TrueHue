# Fuller-face measurement: one controlled cycle

31 October 2026. The user authorized moving forward with the fuller-face mask,
matching ITA/MST work, and recording changes and results. The user clarified
that implementation can proceed before reporting changes through the appeal.
This records the user's direction, not an independent institutional ruling.

We will reuse the existing parser and exclusions without tuning them. Separate
beard/mustache models remain on hold. Neither desktop nor Android correction
will change during this cycle. ITA, MST and decision-tree correction remain.

## Fixed work and data

1. Bind the existing semantic mask to a new measurement contract: whole-frame
   256×256 INTER_LINEAR, YuNet .85/exactly one face, required existing landmarks,
   pinned existing 19-class parser, associated skin/nose and hard exclusions.
   Measure the binary full-frame mask, not its feathered display alpha. Keep the
   existing 1000-pixel minimum and Lab/ITA formula/rounding. No fallback to the
   old mask or old ITA. Record masked RGB endpoint statistics separately.
2. Attempt exactly the same 418 previously exposed MST-E development images
   listed in reviewed_included_rows.csv. Preserve every failure. Hash sources,
   code, models and memberships before processing. No new source selection,
   reserved correction-evaluation pixels, old review approval transfer or
   correction-tree fitting. MST-E remains mapping/evaluation data only.
3. Fit the same decreasing, subject-balanced isotonic/interpolation recipe once
   per held subject, with every photo of that subject excluded from fitting.
   Derive fitting membership from successful NEW measurements; never reuse old
   success membership blindly. Save IDs, weights, knots and predictions. Compare
   with the fitting-subject median baseline on the same rows; show shared-row
   old/new results separately from changed processing availability.
4. Report support by category/subject and lighting, processing availability,
   ordinal MAE/exact/within-one accuracy, unsupported folds and prior exposure.
   Subject separation here is development evaluation, not an untouched test.
   No extra masks, thresholds, weights or calibration recipes will be tried in
   response to this outcome. Do not force a category-10 endpoint.

## Meaning and stopping point

Technical success and exclusion of predicted non-skin classes are not human
mask-quality approval, correct reference lighting or intrinsic skin color.
New masks remain unreviewed. This cycle can establish a reproducible candidate
measurement and matching development calibration evidence, not final validity.
Do not adopt a lookup merely because mean error improves. Identify the minimum
remaining mask/reference judgments and independent-subject support before asking
for review or another correction fit. Old distortion masks/targets cannot simply
be relabelled as a new, consistently prepared training set.

The final mapping/export and correction cycle need a separate recorded decision
based on these results; neither is automatic. No professional opinions are
requested before a good initial correction model exists.
