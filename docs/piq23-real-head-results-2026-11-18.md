# Received PIQ23: first real quality head completed

18November2026, Asia/Manila. Dataset verified and the previously approved **one real exposure-quality head** fitted. This is real portrait/expert-annotation evidence, separate from prior mock engineering and synthetic11source heads. **Held ranking is positive; the complete predeclared quality screen fails on loss, so no correction fit/adoption follows.**

| Evidence | Result |
|---|---|
| Received archive | `C:\Users\NYTHAN\Downloads\PIQ2023-Dataset.zip`,4,412,843,501bytes |
| Archive SHA256 | `5fac8093a42720cc30aeacd921407efaf57753daed845556d163de65e35729ae` |
| Exposure admission | All5116paths/IDs/JOD/CIs/scenes match public roster;0missing/extras/decode failures |
| Partitions |3630Train/35scenes;1486Test/15scenes |
| Exact duplicates |22pairs/44files, all within one scene and partition;0crosspartition/0strict-CIcontradictions; retained |
| Real features |5116frozen4096float32vectors,1generatedcontractreplay; input/model immutable |
| Actual fit |1head,50epochs/7000Adamupdates,71178training pairs;0correction fits |
| Held pairs |24725/27981correct,0ties; pooled88.36%,equal-scene85.51% |
| Held scene accuracy |All15above50%; range56.29%–98.05% |
| Training accuracy/loss |Equal-scene99.54%/0.01672 |
| Held loss |Equal-scene1.45248, pooled1.14705; tied baseline0.69315 |

The model learned useful within-scene ordering on unseen scenes. Its confident held errors and training/held gap remain substantial: eight of15scenes have loss worse than the tied baseline. The [predeclared screen](piq23-real-head-evaluation-2026-11-18.md) required equal-scene accuracy>.5 **and** loss<log2. Accuracy passes; loss fails. Preserve both observations. No retuning of epochs/regularization/scales, post-result temperature normalization or automatic feature/probe/correction-fit queue. Failure of this score screen does not establish universal feature uselessness, nor can ordering alone establish natural correction or preservation.

Dataset owner's user-supplied citation/acknowledgment request retained; archive contains scoreCSVs and images, no added README/licence. Proceeded with access provided for requested noncommercial thesis assessment, without public redistribution/commercial rights claims. Details/Overallpixels not decoded. EveryExposureimage is1350x1700RGB;1571ICCprofiles and twoorientation6tags recorded. Fixed declared decoding does not apply profile conversion/EXIFrotation;256BICUBIC/existingencoder128view contract unchanged. These are framing/colour-management limitations, not silently corrected variants. Person overlap and officialMSTlabels unknown, no demographic labels inferred.

Reused completed generated optimizer QA and frozen encoder. The final feature receipt hit a `versions` dictionary-call typo **after** all5116vectors, input/state checks and records were completed. Original code/failure/partial and complete records preserved; `finalize_piq23_feature_receipt.py` verified saved vectors and bindings and wrote the receipt with0newencoder/image calls. No scientific setting or output changed, no repeated extraction. Dependencies/environment unchanged.

Independent actual audit passed8192Train-onlyscaler values, exact3630training IDs/35scenes,71178pairIDs,7000seededbatch hashes,50scene results,58run-artifact hashes. All5116scores independently checked across4096terms; maxdifference6.04e-14. Frozenhead hash sealed beforeTestscoring; no held normalization/fitting/epoch selection. Full traces/epoch states are diagnostic receipts, not an epoch-selection set.

Artifacts: `outputs/piq23_actual_archive_v1`, `piq23_actual_admission_v1`, `piq23_actual_features_v1`, `piq23_actual_head_v1`. Actual head: `outputs/piq23_actual_head_v1/head.json` (`generated_fixture=false`). Generatedhead remains mock/neveractualinference. Supporting code: `admit_received_piq23.py`, `piq23_actual_features.py`, `finalize_piq23_feature_receipt.py`, `fit_actual_piq23_head.py`, `verify_actual_piq23_head.py`.

**Approved single-head stage fulfilled; fixed quality screen NOTADVANCED; no next correction fit selected.** No further fits, extraction reruns, datasets/models, user review or runtime integration selected. PPRfullpipeline remains deferred at its downloadedLUT checkpoint, with its separate approval preserved; do not restart it automatically. Every prior closed study/rating/manual ear preserved. This is a disclosed external quality-supervision extension to proposal63/65, not the original traditional-tree method, final combined model, per-tone qualification, expertMOS or Android completion. Full goal/Fridayexpert-paper sequence/manuscript pause/raw-original/lockedcontents-and-manifests/no-contact/adviserformatonly remain; no completion promise.
