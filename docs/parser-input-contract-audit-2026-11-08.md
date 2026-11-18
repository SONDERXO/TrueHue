# Parser input audit — 8 November 2026

No implementation mismatch was found in the checked preprocessing or coordinates.
This completes the authorised saved-input audit. No model was run, fitted or
changed, and no application change was made.

## Checks completed

- Verified the parser asset and archived author inference source against their
  recorded hashes.
- For all 54 clean inputs, exactly reconstructed the native crop from the source
  scene, then its bilinear 256-pixel processing image.
- Compared the local preprocessing tensor with an independent transcription of
  the archived author's BGR-to-RGB, 512-pixel bilinear resize, float32 scaling,
  ImageNet normalization and channel-first batch conversion. All matched exactly;
  input pixels remained unchanged.
- Checked saved category-map dimensions against their processing images.
- Used synthetic logits to verify argmax followed by nearest-neighbour restoration
  to the requested output coordinates.

These checks do not run the network or establish OpenCV/ONNXRuntime numerical
equivalence. They do not prove that the model recognizes these faces correctly.

## What differs from earlier experiments

The current aligned candidate deliberately uses raw parser inputs. The earlier
5 November experiment applied one fixed Lab-L CLAHE transform only to a parser
copy. Its technical passes increased from 18 to 21 of 30, but fragmented masks
and visibility failures remained; it was not adopted.

All 30 overlapping source cases have different saved crop bounds and different
256-pixel input images between those experiments. Therefore the earlier category
maps cannot serve as a controlled appearance comparison on the current geometry.
Reusing those maps as though their pixels aligned would be incorrect. This audit
does not establish that either framing is better.

The 6 November larger-parser comparison also remains relevant: it included more
skin points (54 to 77 of 113), but included more unwanted material (9 to 15 of 94).
Changing to the larger model is not a demonstrated solution to both coverage and
protection.

## Proposed next bounded comparison — not run

Use only the five previously traced clean images with saved landmarks, categories
and FaceOcc logits. Apply the already specified parser-only Lab-L CLAHE transform
(clip limit 2, grid 8×8) to their exact current saved 256-pixel images.

This requires exactly five new parser forwards, no new detector, landmark or
FaceOcc forwards and no fitting. Retain the sixth landmark-failed photo as a
failure. Compare against the cached raw parser categories, keeping coordinates,
class list, component association, anatomical/nostril guards, cached visibility,
minimum-pixel rule and correction model fixed. Measure original pixels only.

Report marked-patch coverage before and after the existing filters, technical
failures and agreement with the already completed sparse skin/hair/object points
where source coordinates match. Show both added and lost support. Neck-containing
patches and sparse points remain limited references, not full mask ground truth.
More selected skin alone cannot justify adoption. No threshold tuning, transform
sweep, larger batch, correction refit or automatic runtime integration follows.

The purpose is to isolate whether the previously studied input transform helps
on the current framing, not to repeat the earlier experiment under an accuracy
claim. A matching MST/correction retraining cycle is outside this proposed check.

## Reproduction

Script `scripts/580_audit_parser_input_contract.py`; private outputs
`outputs/parser_input_contract_audit_v1`. All 256 bound source/input hashes were
checked. Earlier model, dataset and experiment artifacts are preserved.
