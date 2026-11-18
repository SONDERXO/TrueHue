# Existing labelled brightness coverage review — 10 November 2026

The saved real measurements do not close the photographic brightness gap. The
current 30 reviewed measurements span L*=8.6235–43.8131. The 82 historical real
clean fitting measurements span 10.5254–47.9678; twelve of the fourteen reviewed
photographic roles remain outside either range (photographic range
37.6508–71.8763). Historical masks use an older pipeline and are not newly
admitted calibration data. Synthetic brightened variants and reserved rows are
excluded from the real-coverage comparison.

There is a concrete local candidate: thirty front-facing 1200-illumination
captures, comprising F_cool/H_warm/L_warm for exactly the same ten reviewed
Stellenbosch subjects. Exact publisher decimal labels match the current thirty
rows. All candidate files exist and match inherited byte sizes. Their historical
inventory hashes and 224×224 RGB geometry are recorded; image hashes were not
recomputed and image bytes were not opened. The ten subjects are disjoint from
the eight closed final-holdout groups. No holdout image was opened or hashed.

The condition name does not prove greater measured skin brightness, adequate
support, or transfer to photographic inputs. These are new captures; current
600-condition masks, strokes and face boxes cannot be transferred to them.
The small original image dimensions remain a limitation.

Script 755 prepares the exact thirty-row roster and a bounded screen proposal
under `outputs/labelled_brightness_coverage_review_v1`. Metadata bindings and
independent roster counts pass verification: ten subjects each have three rows,
three conditions each have ten, thirty unique paths, unchanged labels, and all
admission flags false. Verification establishes metadata consistency, not pixel
integrity or skin validity.

The next recommended step is the prepared thirty-capture measurement screen:
first verify the exact inherited hashes, then apply the existing fixed native
pipeline, retain all thirty outcomes including failures, and inspect support and
actual Lab/ITA coverage. No replacements, threshold/crop/parser rescue, fits,
MST predictions or automatic annotation admission are proposed. This screen is
prepared but **not executed**. No user mask review is needed at this stage.

This review used metadata and cached scalar measurements only: zero photograph
bytes, model calls or fits. It preserves the completed contextual comparison,
existing annotations, decision-tree requirement and current demo behavior.
