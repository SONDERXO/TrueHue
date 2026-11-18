# Synthetic probe features: fixed correction comparison failed

17 November 2026, Asia/Manila. **Complete / FAILED COMBINED REQUIREMENTS / CLOSED / NOT ADOPTED.** The user requested the next step after the eleven-head ranking diagnostic, under the preceding instruction "Whatever it takes to finish the correction model". The [prospective protocol](synthetic-probe-correction-protocol-2026-11-17.md) fixed one two-probe/316feature comparison before actual extraction or correction fits. No head, loss, EV, depth, mask, control, baseline or gate tuning followed the result.

## Result that determines the decision

All eleven source-held correction trees used the new cue inputs (13cue-based branches across the eleven models). Underexposure improved, including previously neutral predictions, but colour restoration failed and six acceptable-original inputs received exposure changes. Passing some exposure means is not a combined model pass.

| Role | WB314 RGB MAE | New316 RGB MAE | WB314 DE | New316 DE |
|---|---:|---:|---:|---:|
|Identity|3.726|10.826|1.471|3.800|
|Colour-only|2.476|9.531|0.901|3.187|
|Underexposure|11.251|8.606|4.552|3.136|
|Overexposure|1.597|1.597|0.811|0.811|
|Combined-under|7.570|5.661|3.743|3.383|
|Combined-over|1.249|12.840|0.535|4.178|

The fixed screen required every nonidentity role to beat input AND fitting-only constant on both RGB/DE, underexposure to improve overWB314, and colour to be no worse thanWB314. Four exposure roles beat input/constant, and the under-improvement condition passes. **Colour fails:** newRGB9.531 is worse than uncorrected6.564 and constant3.996, while newDE3.187 is worse than constant2.410 and WB314.901. Colour nonregression fails. Combined-over also regresses sharply versusWB314; preserve this despite its input/constant mean pass.

Five colour-only cases have RGB error worse than input:16061,29617,32685,39568,46795. New meanRGB/development errors are numerical reference-restoration evidence, not invented human judgments. Six identity outputs change:16061,29617,39568,46795,49131,59807. All receive exposuregain approximately1.4142;29617also receives colour-balance changes. No user harm labels or old acceptance transfer are manufactured.

The three earlier exact no-ops now receive gain1.4142:16061under RGB21.615=>1.211,48879under25.379=>1.472,48879combined-under26.347=>8.836. That resolves those specific neutral predictions numerically but does NOT rescue the aggregate colour/preservation failures. Do not retain only these three favourable cases or claim visible usefulness from these numbers.

## Probe evidence and what was actually tested

The completed ranking stage remains29/44held comparisons and its narrow positive result remains historical. Its severe overconfidence (loss12.032 versus tied.693) was not hidden or temperature-scaled.

The follow-on read exactly66existing cached256RGB8 `input` arrays, after hashing all declared containers. No reference/support pixels were decoded during probe extraction. Exactly132new minus/plus0.5EV probe arrays were encoded, plus one GENERATED encoder-contract call. Base4096vectors were reused. Independent scalar512code mappings checked every probe array; all22identity probe vectors match the corresponding prior camera under/over vectors EXACTLY. Every new score was scalar checked (maxerror2.84e-13), input bytes immutable, encoder weights/buffers unchanged. No head training or new image acquisition.

Descriptive best-option counts out of11: identity/base5, colour-only/base3, under/plus7, over/minus5, combined-under/plus8, combined-over/minus6. No ties. Thus the score is not a safe direct exposure selector. These counts were NOT used as a universal necessary feature gate: the separate direct control test assessed actual feature usefulness, preserving the WB proxy/direct-assessment distinction.

For each outer held sourceS, its existing headS was used for ALL60fitting cases AND6held cases. HeadS excludes sourceS entirely. Using each training row's own leave-source-out head would leak the outer held source into features; that shortcut was explicitly rejected. HeadS training responses are in-sample supervised features, with overfitting risk disclosed. The actual end-to-end test held sourceS out of both head fitting and correction fitting.

Exact314float32prefix plus two raw score differences, cast once tofloat32, no scaling/clipping/subset/weights. All11fold-specific66x316matrices and2178scores independently verified before fitting. Same fixed depth4/seed42CART and controls/operator/support/targets asWB314. **Exactly11new real correction fits**,660fitting proofs and66native/export/scalar held controls. All eleven models verified BEFORE held predictions; all66controls sealed BEFORE any reference/support pixel scoring. Baseline/constant outputs reused,0head/target/mapper/baseline refits.

After sealing,66candidate outputs received exact independent scalar RGB8render checks, protection/unchanged-region checks, primary/core/feather/whole RGB/DE accounting and parent-asset joins. All48primary summary values/gates independently recounted. Final separate audit verified87current artifact hashes,660fit66held routes,227,964prefix values and1,452scalar cue values; outer-head exclusions and held-target absence passed. Engineering correctness does not change scientific failure.

## Engineering preflight history retained

Probe-v1 preflight compared saved generated shape(1,4096) with flattened(4096,), so it stopped before any real input decode. Its bindings/original workflow/failure record remain under `outputs/synthetic_exposure_probe_v1`. V2applies the same reshape(-1) used by the original camera workflow; exact equality remains required. No tolerance, encoder, preprocessing or scientific parameter changed. Actual132probe vectors are in `synthetic_exposure_probe_v2`; new generated adapter QA there passed.

Correction generated QA versions1/2remain;v3adds stricter held-target projection and a target-poison guard before real fitting. The real fold files contain no held target values. The final generated workflow passed11trees/660fit66held/66scalar pixel replays, bad-width/nonfinite/wrong-head/source-leak rejection before fitting, missing-seal/no-overwrite and failure preservation. Repeated generated QA did not create extra real fits.

Existing encoder environment Python3.13.17/NumPy2.5.4/Pillow13.0.0/torch2.15.0CPU/torchvision0.29.2CPU retained. Correction tree environment Python3.14.7/NumPy2.5.3/scipy1.18.1/sklearn1.9.1/skimage0.26.0 exactly matches the earlier tree study. No installation, upgrade or silent environment replacement.

## Boundary and retained objective

This fixed316candidate is closed without a new review batch or deployment. No depth/leaf/loss/score-scale/head/feature/probe-strength/source rescue queue. Existing eleven-head study remains completed; no more synthetic head fits are selected. No supported subsequent correction fit is established by this outcome. It does not prove all ranking/feature/control approaches impossible.

Full automatic exposure AND colour with acceptable complexion/identity remains the objective. PriorWB314identity/colour acceptances and its exposure feedback stay intact and candidate-specific. Darker-skin benefit, independent tone qualification, expertMOS and current-model Android readiness remain unfulfilled. Source-held development is repeatedly inspected, not untouched confirmation. PIQ23 access/use is separately pending with0realPIQ heads; no SICE/other-source work, contact or new portraits. No raw originals or locked contents/manifests, manuscript/runtime/Android changes, new ratings or final adoption. Friday submission/expert sequence unchanged, no completion promise.

## Artifacts

- `outputs/synthetic_exposure_probe_v2`:132vectors/cues/bindings/access/scalar verification.
- `outputs/synthetic_probe_correction_design_v1`:fold-specific matrices/head exclusions/source bindings.
- `outputs/synthetic_probe_correction_prediction_v1`:eleven models, sealed controls,66evaluation packs, case records, summary, verification and independent audit.
- Reused scorer labels this new candidate `joint` internally; in THIS output directory that key means the new synthetic316candidate, not the closed4410joint model. Old4410artifacts were not changed or rescored.
