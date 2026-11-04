# Fixed material-boundary guard follow-up

26 October 2026. Declared after the A/F/C experiment, before this follow-up.
The initial chroma veto recovers the cheek but leaves/adds painted-area pixels.
This is an adaptive development follow-up, not predeclared independent testing.

Test one conservative guard on C, without changing its material seeds, color
thresholds, model classes or anatomical rules: remove pixels within Euclidean
distance<=2 native pixels of an A pixel rejected by C's chroma-material rule.
The two-pixel safety margin reuses the existing experimental support guard's
native exclusion-distance convention; it is not chosen by a radius sweep.
Outliers are material-rejected pixels inside A, not manual painted regions.
No reference/paint labels enter inference. Call the result C2. No further margin
search is authorized by this protocol.

Use all53 core cases and all90 historical source/input cases already processed,
unchanged native224/256 frames. Removal-only from C; no added pixels, no new
inference or exposure. Protect all generation/measurement/correction stages
consistently. Retain previous A/F/C artifacts and historical review decisions.

Score full/interior reference skin and feature/paint exclusions, newly selected
exclusions relative to ORIGINAL masks,48 sparse points, cheek202/124, finite
measurement/brightness features and both generation-retention denominators.
Inspect every source/input board and the paint transition regions. Independently
replay distance filtering with a radius2 disk dilation and verify all recorded
original hashes. Record losses/failures, not just contamination reduction.

If labeled paint additions/contamination remain or skin loss is material, do
not regenerate/admit/fit. Preserve the useful parser contour evidence and record
the precise unresolved material-protection limitation. No automatic paint,
final evaluation, user-workflow change or proposal amendment follows. This
guard adds another implementation detail to the thesis method distinction.
