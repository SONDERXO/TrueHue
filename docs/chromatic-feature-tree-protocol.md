# Fixed facial chromatic distribution comparison

30 October 2026. Facial Lab means cannot describe color spread or asymmetric
outliers. Test one fixed extension: masked a* median/IQR and b* median/IQR,
using the existing OpenCV 8-bit Lab convention and linear quartiles. These are
input-only facial statistics compatible with the proposal's feature category;
the particular four statistics are an engineering choice, not a paper quote.

Compare five existing Lab/ITA/experimental-MST features with those five plus
these four statistics. Use the exact 41 previously admitted rows, 26 source/
duplicate-held folds, ordinary direct gamma/R/B targets, depth 3, seed 42,
minimum leaf size 1 and fitting-control protection. All fitting rows exclude
the held source and variants. No feature subset, percentile, threshold, depth
or target-weight search. No brightness features are added.

Report historical 30, historical clean 15, distorted 15, additional clean 11
and combined 41 separately. Require zero held-clean changes and benefit versus
unchanged, and assess distorted utility against the matched five-feature
comparator. This reused exposed cohort cannot establish final validation.
No automatic demo promotion, even on a development gate pass.

Verify exact baseline parity, independently reconstructed masked statistics,
52 raw-tree refits, fitting-only leaf protection/membership, source separation,
82 output pixel/metric replays and aggregate/gate consistency. Keep measurement
masks, ITA, lookup, calibration, targets and reserved data unchanged. No new
mask approval or human review request is inferred.
