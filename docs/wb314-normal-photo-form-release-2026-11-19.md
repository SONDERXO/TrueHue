# Normal-photo development-feedback package

## Subsequent instrument update

A later read-only public Form capture verifies that the user inserted 20 image items and added 20 consistent four-option preference questions, alongside the existing 20 overall quality ratings and comments. The user subsequently supplied the updated normal-photo comparison introduction directly in chat; that introduction change is user-reported, not a fresh network verification. Consent retention was requested. Image-item presence is verified, but the uploaded image pixels were not independently rebound to the local PNG hashes. No invitations, completed reviewer participation or received responses are confirmed. The agent sent no invitations and accessed no response data.

The preference item is a categorical comparison; report its counts/percentages separately from the overall 1-5 quality ratings/MOS. Do not average option codes or count “unable to judge” as a tie or approval. The original export's `questions_changed=False` and `live_Form_updated=False` describe the agent's release action at that checkpoint; they do not deny these later user-made changes. Preserve that historical receipt and use this later instrument stage when describing collection. The model and selected local PNGs remain fixed.

The current development-feedback selection is the 20 normal-input/main-output pairs from the non-replacing advisory preview. The local upload package copies only the main correction images; separate protected alternatives are excluded. This is a procedural release for feedback, not 20 individual appearance ratings, expert acceptance or final model adoption.

## Pairing and instrument

The left panel is the uncorrected, undistorted dataset photograph. The right panel is the unchanged frozen WB314 primary result. No synthetic exposure or colour distortion is added in this round. Some inputs already look adequate; unchanged output can be appropriate. The input is not calibrated physical skin-colour ground truth.

The same 20 source photos of 13 previously exposed people cover publisher MST categories 1-10, two pairs each. Labels are evaluation metadata and never predictor inputs. No model training uses MST-E. These well-lit photographs are not an independent final cohort or representative naturally faulty phone captures.

The existing 20 MST sections, consent and evaluator items, 20 overall 1-5 rating questions with their original anchors, and 20 comments remain unchanged. A cached read-only HTTP 200 response from the public respondent Form confirms the section headings and complete existing question definitions match the earlier instrument. The initial local comparison failed because Windows default decoding was used for cached UTF-8 JSON; an explicit UTF-8 comparison passes. Both receipts are preserved. No repeat network fetch was needed to resolve that encoding issue.

Only the comparison instructions need clarification: normal input left, main result right, no added synthetic distortion, and a visible change is not automatically better. The prepared text supplements the comparison instructions; retain existing participation, privacy and consent information. The questionnaire still produces one overall score per pair, not four separate criterion scores.

## Export and verification

`scripts/release_wb314_normal_form_packet.py` copies the approved main PNG bytes without inference, correction rendering, original-JPEG decoding, resampling or fitting. It verifies:

- 20 exact primary PNG copies against both the advisory preview hashes and earlier normal-photo files.
- 20 official catalogue subject/MST joins and matching existing Form slots.
- 20 embedded PNG byte checks and valid image payloads.
- 20 ZIP member hashes and archive CRC.
- The frozen model SHA remains `7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`.

Local delivery: `output/wb314-normal-photo-expert-form-2026-11-19/START_HERE.html` and `WB314-normal-photo-expert-form.zip`. The ZIP contains only the 20 primary PNGs and upload/instruction files. Per-image bindings and authorization remain private in `outputs/wb314_normal_photo_expert_form_release_v1/`; the public aggregate summary reports export status only.

Round ID: `wb314_mste_normal_primary_development_round1_2026_11_19`. Use one fixed image/model version throughout the round. Preserve any actual earlier responses under their actual version; do not pool or relabel synthetic-round responses as normal-photo feedback. Earlier synthetic packages remain historical and are superseded only for this current image selection.

## Live status and limits

No connected document editor was available. The agent has inserted zero Form images, made zero live edits, accessed no response data, submitted no responses and sent no invitations. Image insertion, comparison-introduction clarification and respondent preview remain pending manual steps. No additional permission or image-approval round is required to use this prepared selection.

Images retain the exact existing enlarged face views from 256-pixel whole-frame processing; no additional HD detail is created. Known mask, hair/beard, jewellery, neck/collar and foreground limitations remain. The main output retains its previous highlight behaviour; separate headroom alternatives are not silently applied. Earlier failed cap screens remain failed. Normal-photo reliability, independent final MST evaluation and device qualification remain incomplete. This export does not finish the correction model or establish expert MOS.
