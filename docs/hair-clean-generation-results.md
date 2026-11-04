# Hair contamination fix: generation-mask experiment

23 October 2026. Follow-up to [mask-quality screening](square-mask-quality-screen.md).

## What changed in the experiment

Applied the existing MediaPipe hair veto to each clean source's generation
mask before making synthetic inputs. This only removes predicted hair; it
cannot expand generation support into new skin, hair or paint. All eight
sources and all 38 existing parameter settings were checked, including retained,
held, development, stress and excluded cases. No thresholds were widened.

Fresh distorted images, estimation masks and correction support are saved
separately in `outputs/hair_clean_generation_v1/`. No production policy,
training manifest, review label, feature schema or correction model changed.
The experiment does not replace the paper's threshold method or approve using
an additional learned model in final preprocessing.

## Findings and disposition

For source12288, 2,524 predicted-hair pixels were removed from the generation
region (40,045 to 37,521 pixels). The removal overlay shows the principal
contamination at the hairline. Across all sources the cleanup is removal-only;
saved-image recipes reproduce exactly and clipping never increases.

The unchanged quantitative screen passes 25 training candidates rather than22.
Three previously held source12288 examples (dark, unchanged, mild brightening)
no longer fail after correcting the generation reference. **This is not a
demonstrated segmentation improvement:** the unchanged input and both of its
output masks are identical, and all three old masks already pass when scored
against the cleaned denominator. Report changed denominators explicitly.

Five training cases still fail:

- Source12288/color-shift.
- Source22211/dark and color-shift.
- Source22454/dark.
- Source62331/color-shift.

Keep those five held; do not force expansion from sparse seeds or loosen
thresholds until the same examples pass. Source19/color-shift still fails the
screen and remains development-only. The original excluded source22454/color
still fails the pixel minimum (393 pixels in this experiment).

The three reference-related holds are classified as candidates for later
review under a separately versioned generation policy. They have **not** been
promoted into the existing22-row screen-pass training manifest. The original
eight held rows, original30 candidate rows and all historical partitions remain
unchanged. No training comparison has been run on the candidate25.

## Labeled hair/paint regression

Script55 checks the original24 reviewed pixels on their six original224 images
at exact original coordinates. No resized label transfer or new annotations.

| Labeled material | Reviewed points | Original generation selects | Cleaned generation selects | Existing clean correction support selects |
| --- | ---: | ---: | ---: | ---: |
| Skin | 12 | 11 | 11 | 12 |
| Hair | 4 | 3 | 1 | 1 |
| Paint | 3 | 0 | 0 | 0 |
| Other | 5 | 0 | 0 | 0 |

The removal did not lose any previously selected reviewed skin points or add
any reviewed paint points. One reviewed hair point remains selected. This is
a small, development-selected clean-image regression, not area accuracy,
universal paint protection or a new shifted-image/corrected-output evaluation.
The generation mask remains distinct from the correction mask. The existing
material check is preserved; no raw semantic skin replacement was introduced.

## Verification and review

- Eight generation masks verified as subsets of originals, with no predicted
  hair remaining under the clean-source category maps.
- All38 saved image recipes and clipping counts independently checked.
- Input/table/model/review hashes unchanged; existing **454 tests passed**.
- Codex inspected the eight-source removal overlay and source12288's full
  baseline/candidate comparison board. Other candidate pair boards are saved
  but not all were visually inspected in this experiment.

[Generation-mask removal overlay](../outputs/hair_clean_generation_v1/generation_removal_review.png)
uses red for removed pixels and green for retained generation support.
[Pair comparison boards](../outputs/hair_clean_generation_v1/review-index.md),
[full evidence](../outputs/hair_clean_generation_v1/summary.json), and
[labeled-point results](../outputs/hair_clean_generation_v1/labeled_generation_regression.json)
are preserved for later thesis editing.

Reproduction: scripts54 and55, using their existing output names only when
those directories/files do not already exist. Both refuse overwrite.

## Recommendation

Follow-up: [YCrCb-only fixed comparison](ycrcb-estimation-ablation.md) recovered
two held cases experimentally and preserved reviewed paint exclusion, but
introduced broader support that still needs material/boundary review. Not adopted.

Keep hair-clean generation as the isolated candidate fix for reference-mask
contamination. Keep the five true mask-loss cases held. Do not treat these
experiments or an easier screened subset as final-method approval. Further
masking work must test retained and held cases together and retain hair/paint
regressions; repeated tuning on these reviewed cases is development evidence.
Before any final training, the unresolved MST mapping, dataset roles and
additional-model decision in [the thesis record](thesis-method-alignment.md)
still need resolution.
