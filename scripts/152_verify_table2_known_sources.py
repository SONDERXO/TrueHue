"""Verify saved diagnostic evidence and score oracle correction on fixed support."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    folder=ROOT/'outputs/table2_known_source_feasibility_v1'
    target=folder/'fixed_support_verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    source=folder/'summary.json';summary=json.loads(source.read_text())
    verification=json.loads((folder/'verification.json').read_text())
    assert digest(source)==verification['summary_sha256']
    for path,value in summary['input_sha256'].items():assert digest(ROOT/path)==value
    for path,value in summary['evidence_sha256'].items():assert digest(folder/path)==value
    records=[]
    for row in summary['records']:
        name=Path(row['source_path']).stem;group=row['severity_probe']
        def rgb(suffix):return cv2.cvtColor(cv2.imread(str(folder/f'{name}_{suffix}.png')),cv2.COLOR_BGR2RGB)
        reference=rgb('reference');image=rgb(group+'_input')
        scoring=cv2.imread(str(folder/f'{name}_reference_mask.png'),0)>0
        report=dict(source=name,severity=group,status=row['status'],reference_skin_pixels=int(scoring.sum()),
            clipping_fraction=row['clipping']['clipped_pixels']/int(scoring.sum()),
            no_correction=image_errors(reference,image,scoring),oracle=None)
        if row['status']=='success':
            mask=cv2.imread(str(folder/f'{name}_{group}_mask.png'),0)>0
            fitted=row['target_fit'];support=scoring&mask
            assert int(support.sum())==fitted['selected_pixels']
            params=fitted['parameters']
            if params is not None:
                corrected=apply_correction(image,mask,params)
                assert np.array_equal(corrected[~mask],image[~mask])
                report.update(reference_mask_retention=float(support.sum()/scoring.sum()),
                    oracle=image_errors(reference,corrected,scoring),
                    intersection_oracle=image_errors(reference,corrected,support))
        records.append(report)
    aggregate=[]
    for group in ['light','medium','dark']:
        planned=[r for r in records if r['severity']==group]
        paired=[r for r in planned if r['oracle'] is not None]
        aggregate.append(dict(severity=group,planned=len(planned),available=len(paired),
            clipped=len([r for r in planned if r['clipping_fraction']>0]),
            mean_reference_mask_retention=float(np.mean([r['reference_mask_retention'] for r in paired])),
            paired_no_correction_ciede2000=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in paired])),
            paired_oracle_ciede2000=float(np.mean([r['oracle']['ciede2000_source_mask'] for r in paired])),
            paired_intersection_oracle_ciede2000=float(np.mean([r['intersection_oracle']['ciede2000_source_mask'] for r in paired]))))
    output=dict(status='pass',summary_sha256=digest(source),records=records,aggregate=aggregate,
        limitation='Reference-informed oracle capacity on exposed development sources, not learned performance. Fixed reference mask is a pipeline mask, not expert skin truth.',
        training_admitted=0)
    target.write_text(json.dumps(output,indent=2));print(json.dumps(aggregate,indent=2))


if __name__=='__main__':main()
