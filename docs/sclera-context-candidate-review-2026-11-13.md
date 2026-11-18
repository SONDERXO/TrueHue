# A distinct colour-context candidate: sclera measurements

13 November 2026. **Literature/code feasibility review only. No feature extractor, photo read or fit selected.** User asked to continue finding solutions while staying aligned with the paper. The latest22input candidate remains FAIL/CLOSED/NOTADOPTED; exposure success and approved ear coverage are preserved.

## Paper requirements remain clear

Rechecked cached proposal pages13?14,63,65. Distorted-input restoration toward original processed photos is primary; unchanged-photo preservation is supplementary engineering evidence rather than a verbatim primary success criterion. The candidate still fails distorted-colour mean improvement, independently of the normal-photo checks. No physicalskintruth, perfectlyneutral scene, calibration chart, newcamera or adviser approval is imposed. We cannot make this candidate pass by removing normalcontrols or increasing strength. The accepted future operating preferences and oldfailedresults remain unchanged.

## Primary evidence and scope

[Males, Hedi and Grgic, Colour balancing using sclera colour, IET Image Processing12(3),416?421](https://www.vcl.fer.hr/papers_pdf/Colour%20balancing%20using%20sclera%20colour.pdf), DOI10.1049/iet-ipr.2017.0182, studies average sclera colour as an illuminant cue. Its algorithm detects eyes, localizes iris, excludes iris/skin and uses a measured canonical sclera reference before chromatic adaptation. The authors require clearly visible eyes and discuss natural sclera-colour variation. Their reference was established using raw/calibrated chart photographs; reported results are not proof on our processed256pixelcache. (Sections2?4.) No author code/calibration data are downloaded or reproduced. A second proceedings link timed out and supplies no additional verified evidence.

Our candidate is NOT adopting that correction algorithm, illuminant truth or numerical canonical colour. It is to investigate a small set of automatically extracted eye-white colour measurements as EXTRAinputcontext to the retained decision tree. The tree alone would still predict gamma/red/blue controls; ITA/MST and facial skin statistics stay. This would be a documented feature-method extension, not a claim that the submitted paper already specifies non-skin eye statistics. The user's earlier permission for justified lightweight traditional feature redesign applies; no neural encoder or manual correction-type oracle is smuggled in.

The distinct rationale is semantic material information: skincolour varies across people, whereas a successfully isolated sclera region can provide a different source of chromatic context. This is not another whole-image brightness threshold or quantization-footprint formula. It could help distinguish colour casts from individual skin colour, but source-eye variation, prior edits and illumination differences can defeat that inference. The literature supplies a hypothesis, not a completed repair or a guarantee before tomorrow's deadline.

## Concrete implementation/availability gap

The current cached19classparser has left_eye/right_eye/glasses but NOdedicated sclera label. Existing eye-region polygons do not by themselves isolate eye whites from iris, lashes, eyelids, reflections or lenses. Therefore taking class4/5meanRGB and calling it sclera would be an invalid shortcut. Small256workingimages, closed eyes, sunglasses and occlusion may leave no usable sclera. No eye-pixel accuracy or cohort availability was checked in this image-unread stage.

If pursued, the next bounded engineering specification must define ONEtraditional selection method using existing eye geometry, explicit availability/missing handling and generated contamination/occlusion tests before any real extraction. Keep eyecontext separate from immutable facial measurement/ITA/MST and from correction/protection masks. Reading a possible contextual region does not authorize correcting protected eyes or changing glasses handling. Missing/ambiguous eye whites cannot be labelled neutral, inferred from the reference or replaced by a fabricated perfect patch; a future fixed missing-feature convention is part of the design, not a new quality-veto gate. A feature is not required to exist in every image, but its absence must be handled and evaluated honestly.

A later small existing-cache availability check would need a fixed exposed-only roster and no new annotation/capture requirement. It must not demand calibration charts or open final24/olderlocks. No userreview queue is issued now. Any future fitting needs separately bound data/feature/targets/sourceheldprotocol and positive evidence that the selector supplies meaningful measurements; it must not reopen failedmodels or reuse their ratings as newcandidateevidence.

## Deadline and disposition

This is a specific candidate for engineering review, not a selected training campaign or a change to the app's input requirements. It is not qualified for real fitting yet. With completepaper/model/development targeted for14November(timeunspecified), no claim is made that sclera segmentation, transfer validation, final/MOS/Android or the paper will be completed by then. No deadline-driven acceptance relaxation or automatic switch to exposure-only/prototype scope. Model-first/paperpaused priority remains until the user changes it.

The current task used primary-paper text and local code/metadata only. Bound hashes unchanged; no dataset/cache/face/eye/mask/NPZ, raworiginal, final24/olderlocked bytes, fits, candidate predictions, installs/weights, runtime/Androidchanges or contacts/uploads/commitpush. One finaltree/ITA/MST/traditional/singlephoto/face-neck/manualrefinement/approvedears retained.
