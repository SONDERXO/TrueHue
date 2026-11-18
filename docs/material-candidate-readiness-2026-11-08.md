# Material-model readiness check — 8 November 2026

No complete locally runnable candidate was verified. The existing access and reuse
dependencies remain; another parser comparison has not started.

## Existing leads checked

- **[DINO FaceParsing](https://github.com/jseobyun/FaceParsing):** the public
  README documents skin, beard, hair, glasses and facewear. It provides a decoder
  link and requires a separate DINOv3 backbone. Its license section addresses
  DINOv3 weights but does not clearly establish separate code/decoder reuse terms.
  The [official backbone page](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m)
  still asks users to log in and agree to information sharing before access.
  This check did not accept terms or establish account-specific access.
- **[Roboflow facial_hair-8quxg/1](https://universe.roboflow.com/phd-witpb/facial_hair-8quxg):**
  the public page lists beard, mustache, eyebrow and hair instance segmentation.
  It shows authenticated API use, but this does not establish that this account
  can download local weights. The displayed CC BY 4.0 dataset notice is not
  confirmation of model-weight reuse terms. The earlier authenticated-endpoint
  requirement remains unresolved; failed unauthenticated artifact calls were not
  repeated. This is a potential facial-hair veto, not a replacement skin parser
  or a transparent-lens/rim model.
- The earlier IFrajtag and Charlie2802 repository leads were opened, but the web
  tool did not expose enough current repository content to verify new assets.
  Do not interpret this as proof that no assets exist. Their previous unready
  findings remain historical, not newly confirmed complete-tree inventories.

No decoder, DINO backbone or explicit-facial-hair candidate export was found in
the checked local model paths. No credentials were inspected or printed. No
model weights, source packages, datasets or dependencies were downloaded.

## Concrete next action

Use the already documented Roboflow account route: in the user's own account,
check whether version1 offers a **local instance-segmentation weight export** and
model reuse terms. A dataset export or hosted API demo does not satisfy this.
If available, save the original weights, class mapping, export/preprocessing
settings and supplied terms under `models/explicit_facial_hair_candidate_v1/`.
No API key needs to be pasted into chat. See the existing
[acquisition instructions](facial-hair-checkpoint-acquisition.md).

After receipt, inspect/hash the files and verify the output contract before
selecting a fixed diagnostic. The current six-photo plan's coverage and unwanted
inclusion checks still apply. A beard-only veto cannot recover skin missing from
the base parser; it cannot by itself meet the full coverage objective. No automatic
combination with a larger parser or enhanced input is authorised here.

If local export is unavailable, record that answer and stop this access route.
Do not repeatedly rerun public access checks, purchase access, contact authors,
submit account forms, upload photographs or begin a broad model search.

## Scope and disposition

This is a public documentation/local-file readiness check following the user's
approval to continue candidate verification. It supplies no performance results.
No model was selected, run, fitted or integrated. Existing images, labels and
artifacts remain private. The correction model and four unwanted clean-photo
edits remain unchanged. A completion date is not supported by this check.
