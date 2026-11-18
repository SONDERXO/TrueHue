# Next-step review: externally learned portrait-retouching parameters

17 November 2026, Asia/Manila. User: "That's great progress, what's next for us? What can we do to finish the correction model?" The latest synthetic316candidate remains FAILED/CLOSED/NOTADOPTED. Diagnosis and implementation progress do not establish a usable combined model.

## Recommendation and present limit

Investigate whether a frozen parameter predictor already trained on expert-retouched portraits can provide additional exposure/colour guidance to the retained feature-to-control model. ONE concrete candidate is the official PPR10K pretrained parameter predictor. This is a different learning basis from the local eleven-source synthetic score, not a new source/head/tuning queue. It remains a proposed feature source, not a ready executable correction experiment or demonstrated solution.

PPR10K itself is not a new discovery. Prior local pair/support/representability studies remain closed; none of those images or TIFFs was reopened. The newly considered object is the published pretrained parameter-producing component, rather than another local paired-image fit. A targeted docs/source search found no matching completed pretrained-PPR-parameter assessment; not an exhaustive novelty claim.

The recommendation is a hypothesis: externally learned portrait editing preferences might add information beyond generic quality features and locally fitted synthetic rankings. More pretraining data alone does not guarantee appropriate exposure, acceptable identity or darker-skin benefit. A retouching style can also alter already acceptable photographs or favour lighter appearance, so preservation and tone qualification cannot be assumed.

## Verified source facts

The official PPR10K repository describes11,161portraits, three expert retouch versions, and pretrained-model listings (12files/268MB total listing). This establishes actual portrait relevance, unlike the unverified SICE portrait lead. The project source is Apache2.0, while the README separately restricts dataset/derived-data exploitation to noncommercial research. Applicability to specific weights and thesis/model distribution still needs binding; code licence alone is not blanket model/data permission.

The inspected official `validation.py` uses `resnet18_224(out_dim=5)` and loads a `classifier_%d.pth` state separately from five LUT states. Its five outputs weight the five LUT-transformed images. These are mixing coefficients, not exposure categories, signedEV, gamma/RB controls, expert quality scores or universal skin-brightness targets. The unrelated three-output `Classifier` class in `models_x.py` is NOT the selected validation architecture.

The parameter-producing forward path is separately identifiable in source. A possible parameter-only adaptation would read those five outputs as input features while retaining ITA/MST and the final control predictor/renderer. It would not establish author end-to-end parity or independently validate our use of the coefficients. No external output pixels, LUT interpolation or trilinear extension are proposed for the feature-only feasibility stage. `models_x.py` imports the trilinear module at top level, so importing the entire upstream module merely to read coefficients would be inappropriate; any isolated architecture adaptation must be explicit and generated/parity checked. No such adaptation has been implemented here.

## Access checks actually completed

Official README-linked Google Drive and OneDrive model locations returned404through the web reader. This is not proof the files are unavailable in an ordinary browser. Browser skill was read and the available connector surface queried (no Drive/OneDrive connector); browser setup/discovery found no available browser. No login, account, terms acceptance, post or contact. The public GitHub issue API could not be fetched, so no issue/comment claims were made.

No checkpoint, source archive or dataset was downloaded. No particular pretrained file size/hash, successful access, safe tensor structure, strict load, real inference or readiness is established. The validation default names `mask_noglc_a` and epoch-1, implying the intended first candidate path `mask_noglc_a/classifier_-1.pth`; file existence has NOT been verified. No switch among retouchers/model variants is selected if that resource fails.

The previously documented ECPD/PEN article was also rechecked. No official public pretrained checkpoint was established; no new ECPD data request or claim of immediate usability. ECPD remains optional, user-reported requested, not the universal dependency.

## Concrete boundary before another fit

1. Establish ONE official checkpoint's actual availability, source revision, model-specific terms and filename/size/hash. The default candidate above is only a source-code-derived choice, not an acquired model. Do not download the268MBcollection or training corpus to find a favourable model. A proposed single-file transfer cap would be64MiB; freeze the acquisition/strict-load protocol before any transfer.
2. If accessible and suitable, bind safe weights-only inspection, exact architecture/preprocessing and generated-only repeat/immutability/parameter-output checks in the existing isolated environment. No ImageNet auto-download, arbitrary pickle globals, dependency upgrade, Caffe/MATLAB/trilinear compilation or external RGB correction path. This new pretrained neural component is a method extension; do not silently treat earlier ReIQA-specific permission or pixel-network exclusions as blanket permission for it.
3. Only after that feasibility evidence, discuss/select one bounded input-available cue assessment and, if justified, one prospective control comparison with full combined requirements. No current real inference, correction fit or new review is selected. Do not assume another coefficient feature fixes transfer or invent a new mandatory proxy gate.

## What finishing still requires

One selected candidate must demonstrate useful exposure AND colour with acceptable photographed complexion/identity, including candidate-specific development appraisal. Supported independent tone-group quantitative evidence and actual expert image feedback follow a working initial model, with versioned refinements/re-review as adopted. Then freeze/verify the selected inference pipeline on Android and complete accurate methods/results reporting once manuscript editing is explicitly unpaused and the editable file supplied. Existing demo/build success, single-user ratings or engineering parity cannot substitute for those outcomes.

The immediate recommendation is the bounded parameter-source feasibility question above. No guaranteed repair or Friday completion date is established. Do not restart failed fits, loosen gates, adopt a colour-only/prototype-only fallback or refer technical decisions to the adviser. All old results/ratings/manual ears, locked contents/manifests/raw-original prohibitions, manuscript/runtime/Android and no-contact boundaries remain.

Primary sources inspected:

- https://github.com/csjliang/PPR10K
- https://github.com/csjliang/PPR10K/blob/master/code_3DLUT/models_x.py
- https://raw.githubusercontent.com/csjliang/PPR10K/master/code_3DLUT/validation.py
- https://raw.githubusercontent.com/csjliang/PPR10K/master/code_3DLUT/datasets_evaluation.py
- https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/ipr2.12464

Paper check: cached proposal13/63/65/66 and current authorized extensions. Retained single-photo feature-to-control purpose; externally supervised neural parameter features would add a disclosed component beyond the original traditional single-tree inputs. No manuscript or panel approval inferred.
