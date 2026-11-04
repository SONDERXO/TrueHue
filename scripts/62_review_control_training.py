"""Verify fold provenance and render source-held-out control comparison; no fitting."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.evaluation.correction_prototype import apply_correction


def main():
    output=ROOT/'outputs/correction_controls_sourcecv_v1'
    report_path=output/'verification.json'
    if report_path.exists():raise FileExistsError(report_path)
    summary=json.loads((output/'summary.json').read_text())
    with (ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    by_id={r['pair_id']:r for r in rows}
    models={};seen=set()
    for audit in summary['fit_audits']:
        fit=[by_id[p] for p in audit['fit_pair_ids']];evaluate=[by_id[p] for p in audit['evaluated_pair_ids']]
        assert not set(audit['fit_pair_ids'])&set(audit['evaluated_pair_ids'])
        assert not {r['source_image_id'] for r in fit}&{r['source_image_id'] for r in evaluate}
        assert not {r['duplicate_group_id'] for r in fit}&{r['duplicate_group_id'] for r in evaluate}
        assert audit['held_out_group'] not in {r['duplicate_group_id'] for r in fit}
        assert all(r['partition']=='train' and r['table_use']=='train' for r in fit+evaluate)
        if audit['method']=='original_recipe_tree':assert all(r['variant'] not in ['identity_control','mild_bright_exposure'] for r in fit)
        filename=f"fold{audit['fold_id']}_{audit['method']}.joblib";path=output/'fold_models'/filename
        assert hashlib.sha256(path.read_bytes()).hexdigest()==summary['fold_model_sha256'][filename]
        models[(audit['fold_id'],audit['method'])]=load_model(str(path))
        for r in evaluate:seen.add((r['pair_id'],audit['method']))
    assert len(seen)==44 and len(models)==12
    predictions={(p['pair_id'],p['method']):p for p in summary['predictions']}
    assert len(predictions)==66
    for p in summary['predictions']:
        if p['method']=='no_correction':np.testing.assert_array_equal(p['predicted_parameters'],np.ones(3))
        else:
            model=models[(p['fold_id'],p['method'])]
            np.testing.assert_allclose(model.predict(np.asarray(p['features'])[None,:])[0],p['predicted_parameters'],atol=0,rtol=0)
    images=output/'review_boards';images.mkdir()
    links=[]
    for source in sorted({r['source_image_id'] for r in rows}):
        strips=[]
        for row in [r for r in rows if r['source_image_id']==source]:
            pair=row['pair_id'];image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            support=cv2.imread(str(ROOT/row['correction_mask_path']),0)>0
            panels=[]
            for title,pixels in [('Input',image),('Older recipe',apply_correction(image,support,predictions[(pair,'original_recipe_tree')]['predicted_parameters'])),
                                 ('With controls',apply_correction(image,support,predictions[(pair,'controls_tree')]['predicted_parameters'])),('Source reference',reference)]:
                panel=cv2.copyMakeBorder(pixels,34,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,row['variant']+' '+title,(3,14),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
                cv2.putText(panel,'Entire source excluded from fitting',(3,29),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1)
                panels.append(panel)
            strips.append(np.hstack(panels))
        filename=source.replace('/','_')+'_oof.png'
        if not cv2.imwrite(str(images/filename),cv2.cvtColor(np.vstack(strips),cv2.COLOR_RGB2BGR)):raise OSError(filename)
        links.append(f'- [{source}](review_boards/{filename})')
    (output/'review-index.md').write_text('# Source-held-out correction controls comparison\n\nEach source was excluded from its models fitting; selected development evidence only.\n\n'+'\n'.join(links),encoding='utf-8')
    for name,expected in summary['input_sha256'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected
    report=dict(status='passed',fold_models=12,source_group_leakage=False,unique_model_held_pair_predictions=44,
                total_predictions=66,declared_feature_columns=list(FEATURES),target_columns=list(TARGETS),
                original_inputs_unchanged=True,production_model_changed=False,review_boards=6,
                warning='OOF counts22selected sources variants, not independent persons; no all-source candidate exported.')
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
