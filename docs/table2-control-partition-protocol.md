# Fixed control-aware partition training experiment

28 October2026. Photographer opinions are deferred until the correction model is
finished, using the user's existing Google Form. The local photographer package
is unused and is not a prerequisite for this model experiment.

Hypothesis: regression squared-error splits prioritize parameter magnitudes over
clean/distorted separation. Test a separate single-tree training objective:
use Gini classification splits for fitting identity-versus-distortion labels,
then assign exact identity parameters to any leaf containing a fitting control;
distortion-only leaves get the mean of their fitting gamma/red/blue targets.
Export the result as one ordinary feature-test/three-output portable tree.
No auxiliary classifier is evaluated at inference time. This is experimentally
different from ordinary decision-tree regression, not an adopted thesis amendment.

Retain exactly the9inputfeatures including Lab/ITA/MST,20reviewedpairs,10fixed
source/duplicate-group outer folds,depth3/seed42/minimumleaf1/unweighted settings,
targetfits,masks/scoring support,5rejectedIDs,21heldsources andacceptedconcerns.
Fit exactly10trees using18fittingpairs each. Only fitting labels determine splits
and leaf outputs; no held label/reference/target or source ID enters inference.
No depth sweep,feature selection,class weighting,new sources,gate changes or
special handling of75027. Preserve incomplete runs and every outcome.

Compare on identical held inputs with the existing9feature regression and
clean-leaf policies. Report no-correction,all/clean/distorted reconstruction,
per-case changes and untouched distortions. Gates remain strict overall
improvement against no correction AND zero held-clean harm. No runtime promotion
from a passing exposed-development result alone. If this experiment fails, do
not tune the partition or purity rule from the same outcomes. MST/calibration,
clipping,reference/person/category and final-evaluation limitations remain.
