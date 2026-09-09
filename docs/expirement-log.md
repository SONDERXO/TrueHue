# Experiment Log

## Format

For each experiment, record:

- Date
- Goal
- What was changed
- Dataset / sample size
- Key results (numbers + observations)
- Decision
- Next action
- Git commit hash

## Example

### 2026-09-08 – Skin mask threshold tuning

- Goal: Improve skin mask for medium/dark tones
- Change: Adjusted YCrCb thresholds
- Sample: 30 images from FairFace (MST 04–09)
- Result: Better coverage for MST 06–08; more noise for MST 09
- Decision: Keep new thresholds; add morphological cleanup
- Next: Test with erosion/dilation
- Commit: `abc1234`
