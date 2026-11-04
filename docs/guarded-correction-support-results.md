# Limiting unwanted correction — 22 October 2026

Follow-up: [input-relative color check](material-check-results.md) tests
paint/hair rejection and documents the tradeoff with recovered skin.

The guarded fill reduces unwanted expansion in the original example while
retaining most of its improvement. Broader checks still show hair/face-paint
inclusion, so neither geometric fill is ready as the default correction mask.

The user's visual review found the previous fill much better but requested less
expansion. This run tests that concern; it does not change previous human review
decisions, training eligibility or the approved thesis method.

## Candidate and fixed comparison

The original mask is preserved. New pixels must be inside its convex hull,
more than 3% of the smaller face-crop dimension from the hull boundary, and more
than 2% from anatomical exclusions (each distance has a minimum of two pixels).
These rules were fixed before this run; no sweep or score-based selection was
performed. The input image's geometry alone determines the fill. Existing errors
in the original mask are not repaired by restricting additions.

Estimation masks, Lab/ITA features, tree and predictions remain unchanged.
Seven earlier pairs were compared with no refitting. On the three development
variants of source 19:

| Mean metric | Original | Unrestricted fill | Guarded fill |
| --- | ---: | ---: | ---: |
| Color error, lower is better | 7.609 | 6.483 | 6.621 |
| Coverage of generation region | 75.6% | 96.4% | 93.4% |
| Pixels outside generation region | 350 | 673 | 355 |
| Outside-region RGB MAE | 0.00109 | 0.00199 | 0.00110 |

For the problem color-shift image specifically, guarded coverage is 89.0%
versus 35.6% originally and 97.2% unrestricted. Extra pixels return from 327
to the baseline 179; color error is 5.272 versus 8.227 originally and 4.898
unrestricted. The guard preserves most, but not all, of the recovered skin.

On four separate, nonindependent clipped stress pairs, mean color error is
13.916 originally, 13.969 unrestricted and 13.968 guarded. Outside-region RGB
MAE is 0.00156, 0.00463 and 0.00240 respectively. Model overcorrection persists;
the mask guard does not solve prediction errors. No new seven-pair failures.

## Broader development check

All 45 originally accepted development sources plus rejected hair case 29962
were used for mask diagnostics only. Known geometry case 83184 is already among
the 45. No reserved-test sources were used. Each source was checked clean and
with the same fixed color shift (red gain 0.85, blue gain 1.15, gamma 1) applied
on its clean baseline mask. The shifted input's masks were inferred independently.
The clean mask never guides completion; it is only generation/scoring support.
These sources are not newly approved clean references or training candidates.

Of 92 attempted mask cases, 90 succeeded: 46 clean and 44 shifted. Shifted
21241 and 83184 failed landmark detection and remain in `failures.csv`.
On the common 44 shifted cases, mean coverage was 52.1% originally, 64.7%
unrestricted and 61.5% guarded. Mean extra pixels were 314, 1,111 and 814.
Thus gains and reduced expansion coexist with substantial unresolved coverage
loss. There are no broader learned-model correction scores in this check.

For clean inputs, original coverage is 100% by construction: it is the generation
region itself. Neither this nor the shifted coverage is a human skin-accuracy
measurement. Added pixels can be valid skin or unwanted material. Pixel counts
alone cannot distinguish them.

Visual checks covered the original color-shift pair, stress pair 22454,
shifted broad cases 16798, 10480 and 29962, and clean 83184. Face paint in 16798
and hair in 29962 still receive new support. Case 83184 remains a geometry
concern and its shifted landmark failure is not hidden. Most broader sheets
have only automated checks; no full new human approval is claimed.

## Verification, artifacts and next step

418 tests passed, including preservation of original support, subset-of-hull
bounds, exclusion margins, recovery in the interior and explicit invalid-support
failure. Previous hard-correction images reproduced exactly; input features and
model hashes were checked. All original review decisions remain intact.

Run `venv/Scripts/python.exe scripts/31_guard_correction_support.py` from the
project root. It refuses to overwrite an existing run. Artifacts are under
`outputs/guarded_correction_support_v1/`: `pairs/` has before/after images;
`broader/` has mask overlays; CSVs preserve metrics, diagnostics and failures.
Pair sheets: reference/input/additions above original/unrestricted/guarded.
Orange marks additions blocked by the guard; cyan marks retained additions.
Broader sheets: input/original above unrestricted/guarded, with additions cyan.

Keep this as an optional development candidate, not a replacement default.
The next implementation issue is distinguishing skin from hair, paint and other
material inside the face, with explicit failure handling. Additional edge
smoothing cannot make that distinction. Retain these failures as regression
examples and compare any input-based material filter against them and ordinary
faces before wider training. These post-validation experiments do not establish
generalization or a final thesis score; no automatic reference-color copying,
new MST mapping, Android integration or final-test evaluation was introduced.
