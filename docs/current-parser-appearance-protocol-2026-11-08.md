# Fixed current-framing parser comparison — 8 November 2026

User approved the five-input comparison proposed in the parser input audit.
Exactly five new ResNet18 parser forwards: the current saved clean inputs for
review_01 through review_05. Review_06 remains a landmark failure, with no forward.
The sole change is the existing parser-only Lab-L CLAHE clip2/grid8 transform.
Use original input pixels for measurements. Keep all geometry, classes, component
selection, anatomical and nostril exclusions, 1000-pixel guard and cached raw
FaceOcc logits fixed. Verify reused alignment exactly. No fitting or other model
forwards, no parameter search, no runtime change or automatic adoption.

Compare raw cached categories and final measurements with the candidate. Report
all six cases, diagnostic versus technically usable patch overlap, and completed
sparse skin/unwanted point inclusion after mapping their original crop coordinates
to the common full native scene. Unavailable predictions remain unavailable;
also report paired availability rather than treating failures as correct exclusions.
Show all five fixed original/candidate/change boards. Existing patches include
neck and are not complete facial ground truth. More selected skin alone does not
justify adoption; report additional unwanted inclusions. Stop after this comparison.
