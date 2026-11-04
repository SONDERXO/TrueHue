# Input-mask robustness under fixed Table2 distortions

29 October 2026. Run a fixed two-by-two diagnostic on the 20 technically usable
human-accepted original-mask training references and their already generated
Table2 inputs. Preserve all original approvals and concerns, especially16033
hair inclusion. Exclude failed43909, rejected sources and every reserved,
development-validation and final-test source. No new photo review requested.

Factors: existing HSV AND YCrCb versus detailed-method YCrCb-only using the
already implemented Cr133..173/Cb77..127 bounds; original component selection
versus face-oval restriction before component selection. Keep all morphology,
single-face detection results, first-success margin landmarks and complete
eye/brow/mouth exclusions unchanged. Do not lower detector confidence, rescue
missing geometry, change severity settings, invert or enhance inputs, introduce
a parser, tune color thresholds or fill extra holes.

Process both saved reference and actual distorted frames using that frame's
own detection/landmarks. Features, geometry and masks may never be copied from
reference to distorted input. Check exact parity of the reconstructed original
HSV/YCrCb arm with each saved baseline mask. Geometry failure stays explicit.

Report all four arms' selected counts, existing whole/quadrant support-retention
screen against the same original reference generation mask, mask change between
reference/input and pixels outside each input's oval. Outside-oval counts are
anatomical diagnostics, not human-labeled contamination. Original reference
mask is not pixel ground truth. The .5/.8/100 screen is the existing exploratory
screen, not a new validated acceptance threshold. Candidate reference masks
have no transferred human acceptance. Record identity-frame changes too.

No candidate MST mapping, new calibration, target optimization, tree fits or
automatic source admission. All changed masks require distinct measurement
contracts before calibration. Nineteen inputs remain clipped regardless of
mask area or retention, and cannot silently enter an unclipped primary set.
Do not select a mask policy solely for more pixels or a higher retention count.
Save masks/geometry, complete attempt records, policy/dependency hashes and
replay verification. All conclusions are development-only.
