# Fixed five-feature conservative leaf comparison

28 October2026. Transfer the already defined training-control leaf policy to the
five-feature model that improved on matched original inputs. Freeze this
comparison before scoring. Same15sources/30pairs/15folds and existing baseline5
splits; no fitting,depth/feature/threshold search or source/mask edits. Use only
the28fitting rows per fold to identify leaves with any unchanged control and
set those outputs to identity. Other outputs stay unchanged. Retain ITA/MST,
all accepted contamination concerns,7rejectedIDs and74holds. Assess all/clean/
distorted reconstruction and every changed prediction. Existing strict overall
improvement and zero held-clean-harm gates remain. This is a separate output
policy experiment, not ordinary regression or automatic model promotion; it
cannot guarantee preservation of unseen clean inputs in distortion-only leaves.
