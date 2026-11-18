# Official PPR mirror readiness check - 11 November 2026

The frozen additional 16-pair batch remains unacquired. This check read publisher documentation and a small public access page only. It did not retry the Google archive endpoint.

The official README links Google Drive and Baidu for data. Baidu returned HTTP 200 with an extraction-code page; the README publishes code `mrwn`. The page does not establish the selected archive listing, member availability, or HTTP range support. Those remain unverified, rather than proven unavailable. The next concrete access check is the official Baidu share using that published code, followed by listing and bounded-range verification. No account requirement is inferred.

The official data-preparation guide links OneDrive under RAW/XMP preparation. The web fetch returned 404. This is not evidence of an available mirror of the same rendered source/target-A pairs. The README's other OneDrive link concerns pretrained models and would not supply correction training pairs.

No photos, archive members, models, fits, annotations, or final-holdout bytes were read. All previous failures and the frozen roster and transfer limits remain unchanged. An alternative host must still supply those exact pairs within the existing cap; RAW conversion, a pretrained model, or a different roster would require a separate justified design.

This is an access finding only. It supplies no evidence of improved correction, and the correction model remains unfinished. The paper can report the completed development failures honestly; no successful final model or completed final evaluation is claimed.

Sources:
- https://github.com/csjliang/PPR10K
- https://github.com/csjliang/PPR10K/blob/master/docs/dataset_usage.md

Receipt and captured public documents: `outputs/ppr_official_mirror_readiness_v1/`.

Follow-up within this check: submitting the publisher-provided Baidu extraction code returned HTTP 200 but application error `errno=105`; no accepted share session or file listing was established. No CAPTCHA/account requirement or error meaning is inferred. Receipt: `baidu_code_check_PRIVATE.json`. Stop automated access attempts; further access requires a normal interactive check of the official share.
