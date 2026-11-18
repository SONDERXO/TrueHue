"""Bind exhaustive five-board visual review and fixed failed disposition."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/segface_fixed_mask_comparison_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=OUT/'review_receipt_PRIVATE.json';assert not p.exists()
    v=json.loads((OUT/'verification_PRIVATE.json').read_text())
    assert v['passed'] and not v['all_requirements_pass'] and v['result_sha256']==sha(OUT/'results_PRIVATE.json')
    boards=[OUT/f'review_0{i}'/'board.png' for i in range(1,6)]
    worker=ROOT/'outputs/segface_fixed_masks_v1'
    receipt=dict(completed=True,selection='All five predicted reviewed cases; sixth landmark failure retained without prediction.',
        visual_review='Primary assistant viewed every review_01..review_05 comparison board using view_image on 9 November 2026.',
        observations='Substantial additional facial measurement coverage, especially reviews01-04. Final masks remain partial. Four newly included hair/beard points preclude adoption; no dense beard/glasses protection claim.',
        board_sha256={str(p):sha(p) for p in boards},
        worker_output_sha256={str(p):sha(p) for p in worker.rglob('*') if p.is_file()},
        result_sha256=sha(OUT/'results_PRIVATE.json'),verification_sha256=sha(OUT/'verification_PRIVATE.json'),
        disposition='Fails zero-new-unwanted-point screen; not adopted. No automatic masking rescue or correction fitting.',
        private_forwards=5,synthetic_loader_forwards=2,holdout_image_reads=0,adopted=False)
    p.write_text(json.dumps(receipt,indent=2));print('Recorded all5boards; protection failure retained.')
if __name__=='__main__':main()
