"""Independent saved-curve and target-residual verification for admitted pairs."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.paper_gamma import transform_rgb


def main():
    folder=ROOT/'outputs/distorted_mask_review11_import_v1';target=folder/'target_verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    rows=read(folder/'accepted_pairs.json');reviews={r['image_id']:r for r in read(folder/'reconciled_reviews.json')}
    audit=read(folder/'verification.json')
    for path,digest in audit['evidence_sha256'].items():assert sha(folder/path)==digest
    results=[]
    for r in rows:
        assert reviews[r['source_image_id']]['decision']=='accept'
        assert reviews[r['source_image_id']]['notes']==r['exact_review_notes']
        image=cv2.cvtColor(cv2.imread(str(ROOT/r['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        selected=mask&score;fit=r['target_fit'];legacy=fit['parameters'];params=r['paper_target']
        assert int(selected.sum())==fit['selected_pixels'] and fit['converged'] and fit['jacobian_rank']==3
        assert params==[1/legacy[0],*legacy[1:]]
        raw=np.clip(np.power(image.astype(float)/255,1/legacy[0])*[legacy[1],1,legacy[2]],0,1)
        direct=transform_rgb(image.astype(float)/255,*params)
        np.testing.assert_array_equal(np.rint(raw*255).astype(np.uint8),np.rint(direct*255).astype(np.uint8))
        residual=float(np.sqrt(np.mean((raw[selected]-reference[selected].astype(float)/255)**2)))
        quantized=float(np.mean(np.abs(np.rint(raw[selected]*255)-reference[selected].astype(float)))/255)
        assert abs(residual-fit['float_rgb_rmse'])<1e-12 and abs(quantized-fit['quantized_rgb_mae'])<1e-12
        results.append(dict(pair_id=r['pair_id'],selected_pixels=int(selected.sum()),verified_rgb_rmse=residual,
            exact_notes_preserved=True,clipping_fraction=r['clipping_fraction']))
    assert len(results)==6
    target.write_text(json.dumps(dict(status='pass',verified_accepted_targets=6,records=results,
        accepted_pairs_sha256=sha(folder/'accepted_pairs.json'),source_export_sha256=sha(folder/'original_user_export.json'),
        producer_sha256=sha(Path(__file__)),note='RGB-fitted approximate reference-informed targets, not runtime access to references or proof of global optimum'),indent=2),encoding='utf-8')
    print('PASS: six accepted masks, exact notes, direct/legacy curves and saved target residuals independently checked.')


if __name__=='__main__':main()
