# Face-parser code and decoder permission check

8 November 2026. **No explicit research-use permission for the separate face-parser code or decoder was located in the checked material.** This is an evidence finding, not a legal opinion or proof that no permission exists elsewhere.

## Checks actually completed

- Retrieved the complete, nontruncated GitHub tree at commit `bb649e99424ea988ca2bec8b5a3c8e8ca33f3f2e` and repository metadata. GitHub's detected licence field is null. The only filename matching licence/readme/notice/copying/permission patterns is `README.md`.
- Retrieved and hashed 19 project-owned source/documentation/configuration files, excluding images and the vendored DINOv3 subtree. Keyword inspection found the README licence section referring to DINOv3 weights, and Meta/DINOv3 notices in the backbone hub file. These statements do not explicitly identify reuse terms for the separate face decoder.
- Queried all existing issues, open and closed, through the API. One issue exists, with zero comments, asking about face versus neck labels. It contains no permission statement.
- Checked local Downloads and the copied candidate package. The included README and `LICENSE.md` belong to the downloaded Meta backbone package; no separate decoder permission document was supplied. The checkpoint inventory is not a licence document.
- Attempted the author-linked Google Drive preview through the web tool. It was inaccessible. No claim is made that the Drive interface, file description or account-specific view contains no further terms.

Primary links: [pinned README](https://github.com/jseobyun/FaceParsing/blob/bb649e99424ea988ca2bec8b5a3c8e8ca33f3f2e/README.md), [repository](https://github.com/jseobyun/FaceParsing), [existing issue](https://github.com/jseobyun/FaceParsing/issues/1), [decoder link](https://drive.google.com/file/d/15ypMgTcP29Bhk0w1mCxDPzJC2FNJeeTy/view).

The newly fetched commit is stronger evidence than the earlier cached web snippets. Future implementation must use a pinned inspected revision, rather than assume cached source pages and current master are identical. No upstream code was executed.

## Next action

Ask the author to identify the applicable licence or explicitly confirm university research use for **both code and the decoder checkpoint**. Suggested text:

> May we use your FaceParsing code and pretrained decoder checkpoint for our university thesis, TrueHue, studying facial skin-colour measurement and photographic correction? Inference would run locally, and we would not redistribute the weights. Could you identify the applicable licence and citation requirements, or confirm permission for this research use?

This is a draft only. No issue, email, comment or other author contact was sent. No model was run or integrated, and no new dependency, fitting or image upload occurred. Backbone approval remains recorded separately; the final 24-photo holdout remains byte-unread.

## Evidence record

Script 651; ignored `outputs/decoder_permission_evidence_v1` holds repository/tree/issue metadata, inert source text snapshots, source SHA-256 values and the summary. Read-only network requests were authorised for this check. No images, private dataset information or credentials were sent.
