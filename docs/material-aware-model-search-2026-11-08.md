# Focused local material-model search — 8 November 2026

User explicitly authorised a renewed focused public-source search. **No candidate was verified as ready for a local comparison with clear access, complete weights and reuse terms.** This is a bounded search result, not a claim that no suitable model exists.

## Leads checked

| Candidate / primary source | What was established | Unresolved requirement |
| --- | --- | --- |
| [jseobyun/FaceParsing](https://github.com/jseobyun/FaceParsing) | A full parser with explicit skin, beard, hair, glasses and facewear classes; README supplies a decoder link and requires a separate DINOv3 backbone | Its licence section addresses DINOv3, without clearly establishing separate code/decoder permission. Backbone access remains gated. No complete package acquired |
| [Official DINOv3 backbone](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m) | Official page requires login and agreement to share account information | Account approval/terms were not accepted or bypassed. Access was not established |
| [kaganozturk/Effects-of-Facial-Hair-on-Face-Recognition](https://github.com/kaganozturk/Effects-of-Facial-Hair-on-Face-Recognition) | Author-associated research lead; current README links facial-hair annotations | No trained checkpoint download or explicit reuse licence was established from the inspected repository. An annotation link is not a runnable model |
| [IFrajtag/Facial_hair_segmentation_analysis](https://github.com/IFrajtag/Facial_hair_segmentation_analysis) | Corrected repository address located through the [paper's search-indexed data statement](https://www.mdpi.com/2227-7080/14/7/452); current visible root lists a data directory | README requests returned missing/unavailable content; a complete model package and model terms were not verified. Direct paper opening was rate-limited. Do not interpret this as a complete recursive inventory |
| [Charlie2802/Beard-Segmentation-Final](https://github.com/Charlie2802/Beard-Segmentation-Final) | Inspectable root lists a project README describing training experiments | No downloadable trained checkpoint or explicit reuse terms established in checked material. A reported metric is not qualification on TrueHue |
| [HkKhan/beard](https://github.com/HkKhan/beard) | Newly inspected SAM-based beard application; documentation names base and fine-tuned checkpoints. Its loader accepts local checkpoints and uses prompt-based SAM inference | The inspected documentation does not establish a downloadable, hashed beard checkpoint with clear reuse terms. No model accepted. It is not a skin/object parser or a lens/rim separator |

The author repository above corresponds to the later FG 2025 paper; it is not automatically the release of every artifact promised in the earlier [2023 preprint](https://arxiv.org/abs/2308.15740). No linked annotations were downloaded or admitted as training data.

Existing general 19-class BiSeNet/SegFormer and portrait-segmentation search results do not establish an explicit facial-hair distinction. The already tested larger BiSeNet and EasyPortrait auxiliary models remain unadopted; this search does not reopen their failed rules. Roboflow's previously observed cloud-only deployment does not satisfy local-weight access and was not used for private inference.

## Recommendation

The best **semantic fit among the inspected full-parser leads** is DINO FaceParsing because its documented classes directly match the missing material distinctions. That is a label-schema judgment, **not** demonstrated accuracy, access clearance or a selected executable candidate.

The concrete prerequisite is to establish permitted access to its original backbone plus decoder and clarify code/decoder research-use terms. The author-associated beard model is an alternative checkpoint-availability lead, but a beard-only model would still require a separately justified skin-coverage strategy. No author contact is authorised or sent by this search.

Do not download from unverified mirrors, substitute base SAM for fine-tuned beard weights, infer a licence from public visibility, accept account terms on the user's behalf, or upload dataset photos. No checkpoint downloads, remote/local inference, dependency changes or fitting occurred. The final 24-photo holdout remains byte-unread.

Once a complete permitted package actually exists, inspect and hash it, fix one comparison and preserve existing reviews/failures/protections before inference. Until then there is no qualified new mask model to run. A new search or renewed failed access attempts are not automatically the next experiment.

## Search scope and limits

Checked primary project repositories, author model documentation and the official backbone page. Search-result snippets helped locate leads but were not treated as verified checkpoint availability. Some GitHub tree/API requests could not be fetched by the web tool, and the corrected IFrajtag paper returned HTTP 429. These are access/inspection limits, not proof of absent files. Public pages may change; links and the check date are recorded here. No new dataset search, images, annotation round, app integration or scientific admission.
