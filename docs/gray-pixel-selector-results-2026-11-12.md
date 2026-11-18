# Gray-pixel selector: generated-only results and disposition

12 November 2026, Asia/Manila. **Specified and implemented; engineering checks pass, readiness to advance does not. No cached-photo screen or correction training follows.** This closes this particular generated engineering candidate, not every gray-pixel method or traditional feature family. User's working-model objective remains unfinished.

## Source and frozen implementation

The published2015article was captured (8,704,346bytes), hashed, extracted and PDFpages4/6 rendered and visually inspected. Source figures were read as literature; no TrueHue dataset or holdout photographs were read. The paper specifies3x3log-channel standard deviations, equation6gray-index,7x7averaging with inverse mean-RGB weighting,0.01percentselection and mean RGB pooling. Crucially equation6is sqrt(var(channelstd)/mean(channelstd)), not the coefficient of variation std/mean. The former denominator is inside the square root. This corrects any inference that the prior simplified necessary-condition diagnostic was the full published algorithm. [Yang, Gao and Li2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/html/Yang_Efficient_Illuminant_Estimation_2015_CVPR_paper.html).

The protocol was written before implementation/fixture results. Independently written module src/model_training/gray_pixel_context.py follows these equations with explicit numerical support conventions. No authorGPLcode/ZIP was copied or executed. This is not author-code or MATLAB parity. Reflected boundaries, no logepsilon, complete positive3x3support, exact nonflat criterion and complete7x7score support are declared adaptations; invalid scores are not padded as attractive zeros or partially averaged. Positive dark values remain included with inverse-L weighting; saturated255values are retained/count-reported. Empty candidate sets return unavailable with no features. This is an extractor outcome, not a correction safety gate or identity success.

Select ceil(0.0001*H*W), capped to available candidates, minimumone; rank by computed score then row-majorindex. Pool mean RGB and output two natural-log ratios R/G and B/G. At64x64this is one selected pixel; at256x256it is seven. No percentile, channel, window or black-level sweep. The tree, existing16inputs, ITA/MST, supports, correction operator and runtime were not edited.

A PDF renderer was absent, so pypdfium2 was installed only under this assessment's render_tools directory. It rendered the literature pages; no project/runtime dependency installation or change was made.

## Engineering verification

Final14generated-only tests pass, including an independent scalar complete-pipeline replay; equation6denominator; flat/black/zero-channel unavailability; positive dark/saturated handling; exact neutral ties;256pxseven-pixelpooling; RGB permutation; invalid input; determinism and nonmutation. An initialrun had12pass/1fail: rounding a cross-channel mean of identical values made tiny false gray scores, selecting index40rather than0on a neutral fixture. The failure is preserved in initial_test_failure_PRIVATE.json. Centering deviations before averaging fixed the implementation without changing frozen parameters. A final256pxcount/pooling test was added after the fixture run; both test-file hashes are explicitly preserved by the verifier.

The separate scalar verifier recomputes49,152local windows and49,152final windows across12fixtures, verifies candidate availability, pooled codes and descriptors, fixture material membership and source hashes. It passes numerical score/output checks. Exact scalar selected-index agreement is ONLY5/12. The greatest independent selected-score gap is6.47e-17; these are floating-point near-ties, not comparable gaps in correction quality. A1e-12numeric verification tolerance is reported, never used by the selector to combine ties. We do not claim bitwise scalar ranking parity. Treat location sensitivity as a limitation, not a reason to add a tie/score tolerance selected after results.

## Full fixed generated check

Three64x64textured scene constructions: neutral material, coloured material, and a mixedscene with a known-generated neutralhalf. Each uses the existing four diagnostic transformations (identity, gamma1/.7under, gamma.7over, red245/255cool). RGB8rint applied, no continuous clipping.12arrays are separately named generated_fixtures_ONLY.npz and have generated_fixture=true; none enters source manifests, annotations, fitting, MST evaluation or scientific sample counts. Material labels are known only by construction, not inferred neutrality for real photos.

| Generated scene | Role | Selected R/G log | Selected B/G log | Selected material |
|---|---|---:|---:|---|
| neutral | identity | 0.000000 | 0.000000 | neutral |
| neutral | exposure_under | 0.000000 | 0.000000 | neutral |
| neutral | exposure_over | 0.000000 | 0.000000 | neutral |
| neutral | colour_cool | -0.048009 | 0.000000 | neutral |
| coloured | identity | 0.405465 | -0.693147 | coloured |
| coloured | exposure_under | 0.574629 | -0.976915 | coloured |
| coloured | exposure_over | 0.285101 | -0.480366 | coloured |
| coloured | colour_cool | 0.365800 | -0.693147 | coloured |
| mixed | identity | 0.000000 | 0.000000 | neutral |
| mixed | exposure_under | 0.000000 | 0.000000 | neutral |
| mixed | exposure_over | 0.000000 | 0.000000 | neutral |
| mixed | colour_cool | 0.365800 | -0.693147 | coloured |

All12arrays return a descriptor; availability is not a quality pass. The selected material is coloured in5/12conditions (fourfrom the all-coloured scene, onefrom mixedscene). The mixedscene's identity and both exposure variants select neutral material, but its mildcool variant selects coloured material even though the neutralhalf remains present. Selectedlocations change in7/9base-versus-transformed comparisons. Quantized content and ranking sensitivity are both present; the results do not causally separate them.

For the neutral-only scene, exposure variants yield zero ratios; the mildred reduction yields logR/G=-.048009 instead of the ideal unquantized log(245/255)approximately-0.040005. For the all-coloured scene, cast-free gamma changes shift logR/G from.405465to.574629or.285101, and shift B/G too. Thus these feature values alone do not establish colour-cast direction independently of material/exposure. This is the expected ambiguity from the earlier analytical check, now present with the full fixed implementation and quantization.

The mixed result is an observed counterexample to treating this descriptor as a trusted neutral/cast measurement. It is NOT proof the full published method never works, that all gray-pixel variants fail, or that these generated outcomes predict error on portraits. A downstream tree could potentially learn with imperfect descriptors; this test supplies no evidence that it does so. No numerical neutralfraction/response/harm threshold was invented to declare an accuracy benchmark. Maximum observed64pxdescriptor call8.4ms on this desktop, not Android latency or memory certification.

## Disposition

Do not advance this fixed candidate automatically to44cached-photo extraction, another correction fit or runtime integration. Its proposed value was avoiding confusion between colour cast and natural material/exposure; generated outcomes do not establish that value, and exact ranking remains sensitive to arithmetic near-ties. The assessment is complete and the candidate stops here. No changing selectionfraction/window/channel/linearization/border/tie policy, masking coloured backgrounds, newergray-indexvariant or extra selection classifier follows as a rescue.

No new review task, neutral-region annotation, dataset/capture/RAW requirement or physical-colour target is imposed. Keep lightweight traditional input features, one final decision tree, ITA/MST, face/visible-neck scope, optional manual refinement, uncorrected baseline and the paper's synthetic-original restoration task. ReIQA remains declined, PPRpaused and all historical failed trials closed. No supported replacement intervention is selected in this result; further work must offer distinct inference-available information and a correction-specific rationale, rather than another formula trial. This is not substitution of a limitations-only thesis or adviser approval for the user's model goal.

## Artifacts and preservation

Protocol: docs/gray-pixel-selector-protocol-2026-11-12.md. Generated runner839, independent verifier840, test_gray_pixel_context.py. Source/fixtures/results/hashes/verification in outputs/gray_pixel_selector_engineering_v1. Paper PDF/PNGs are reference-reading artifacts; generatedarrays are not real dataset evidence. No development/cache/original/final24/olderlocked photograph reads, masks, fits, correction predictions, MSTfits, acquisition of photos, contact, uploads, commit/push, runtime or Android changes. All earlier user decisions and artifacts preserved.
