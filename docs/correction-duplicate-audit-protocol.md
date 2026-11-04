# Frozen candidate duplicate audit

This phase permits computational duplicate screening of the 600 frozen new
candidates and all excluded historical sources, without visual review, face
processing, ITA/MST extraction, correction predictions or model fitting.
It does not open development-validation or final-test evaluation.

Before running the audit, freeze these rules: decode each source with OpenCV,
hash decoded shape and BGR pixel bytes, and compute the existing 64-bit grayscale
difference hash (9 by 8 thumbnail, adjacent horizontal comparisons). Exact
decoded matches or Hamming distance at most 4 create undirected candidate links.
Connected components propagate conflicts. This threshold is a conservative
duplicate screen, not a face identity detector.

Quarantine every new candidate in a component containing a historical source
or multiple new roles. Quarantine unreadable sources. Within-role candidate
links retain a shared group for any later group-separated resampling. No role
is reassigned and no replacement is selected. A screen-clear source remains
unreviewed and is not automatically eligible for fitting. Absence of a link
does not establish person separation or rule out other duplicates.

Store a separate access ledger and complete fingerprints, failures, links and
dispositions under a new audit output directory. Preserve the original frozen
selection, its metadata-stage ledger and the historical exposure ledger.
Subsequent reporting must disclose computational pixel access to held-out
sources; it must not call those images never opened. Quality and model-outcome
inspection of development-validation and final test remain locked.
