"""Upgrade only review HTML; retain original verified pages and all image bytes."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/correction_training_preparation_v1'


def main():
    backup=OUT/'original_review_pages_v1'
    if backup.exists():raise FileExistsError('Original page backup already exists')
    rows=[json.loads(line) for line in (OUT/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    verification=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
    # Verify frozen evidence before preserving/replacing presentation files.
    for relative,sha in verification['evidence_sha256'].items():
        assert hashlib.sha256((OUT/relative).read_bytes()).hexdigest()==sha
    template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
    manifest_sha=hashlib.sha256((OUT/'attempts.jsonl').read_bytes()).hexdigest()
    backup.mkdir()
    for p in [OUT/'review.html',*(OUT/f'batch_{n}.html' for n in range(1,8))]:shutil.copy2(p,backup/p.name)
    shutil.copy2(ROOT/'scripts/review_tools/training_review.js',OUT/'training_review.js')
    for batch in range(1,8):
        records=[]
        for r in rows:
            if r['training_batch']!=batch:continue
            records.append(dict(image_id=r['image_id'],source_id=r['source_id'],status=r['status'],
                reference_mst_estimate=r.get('reference_mst_estimate'),assigned_severity=r.get('assigned_severity'),
                clipping_fraction=r.get('clipping_fraction'),panel_count=4 if 'input_measurement' in r else 2,
                failure_reason=r.get('input_measurement',{}).get('reason') or r['reference_measurement'].get('reason') or r.get('target_fit',{}).get('status')))
        data=json.dumps(dict(batch=batch,manifest_sha256=manifest_sha,records=records)).replace('<','\\u003c')
        links=' · '.join(f'<a href="batch_{n}.html">{n}</a>' for n in range(1,8))
        page=template.replace('__BATCH__',str(batch)).replace('__BATCH_LINKS__',links).replace('__DATA__',data)
        (OUT/f'batch_{batch}.html').write_text(page,encoding='utf-8')
    # Keep the existing index links; add guidance for the upgraded pages.
    index=(backup/'review.html').read_text(encoding='utf-8')
    index=index.replace('<ul>','<p>Each batch now has one-image review, enlarged panels, filters, decisions and notes. Progress saves in your browser; export a JSON backup for sharing and recovery. Imported decisions are annotations only, not automatic training admission.</p><ul>',1)
    (OUT/'review.html').write_text(index,encoding='utf-8')
    changed=[OUT/'review.html',OUT/'training_review.js',*(OUT/f'batch_{n}.html' for n in range(1,8))]
    (OUT/'review_presentation_update.json').write_text(json.dumps(dict(
        version='training_review_ui_v1',original_pages='original_review_pages_v1',
        original_verification='verification.json refers to original HTML now preserved in original_review_pages_v1; scientific files unchanged',
        manifest_sha256=manifest_sha,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in changed}),indent=2),encoding='utf-8')
    print('Upgraded seven batches; original pages preserved; scientific artifacts unchanged.')


if __name__=='__main__':main()
