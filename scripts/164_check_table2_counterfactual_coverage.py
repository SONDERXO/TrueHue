"""All three severities on eight fixed sources; saved-fold replay, never fitting."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.distortion_generation.table2_composite import composite_rgb,SETTINGS
from src.model_training.recovery_targets import fit_recovery_target
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import apply_correction,image_errors

OUT=ROOT/'outputs/table2_counterfactual_coverage_v1'
PARENT=ROOT/'outputs/table2_reviewed_expansion_evaluation_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def save(p,v):
        assert cv2.imwrite(str(p),v)
        assert np.array_equal(cv2.imread(str(p),cv2.IMREAD_UNCHANGED),v)
    def tile(image,label):
        result=cv2.copyMakeBorder(image,25,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(result,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1)
        return result
    plan=read(PARENT/'fit_plan.json');prior=read(PARENT/'summary.json')
    check=read(PARENT/'verification.json')
    assert digest(PARENT/'fit_plan.json')==check['fit_plan_sha256']
    assert digest(PARENT/'summary.json')==check['summary_sha256']
    sources={r['pair_id'].split('__')[0]:r for r in plan['rows'] if r['variant']=='identity'}
    assert set(sources)=={'22211','22454','62331','6236','67583','75027','83205','84364'}
    config=get_config();_,identity=contract(ROOT)
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==plan['rows'][0]['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(im,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    tracked=[Path(__file__),ROOT/'docs/table2-next-coverage-protocol.md',PARENT/'fit_plan.json',PARENT/'summary.json',
        PARENT/'verification.json',PARENT/'user_review.json',artifact,
        ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py']
    tracked+=list(PARENT.glob('fold_*/*'))
    for row in sources.values():tracked += [ROOT/row['reference_path'],ROOT/row['reference_mask_path']]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in tracked}
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'boards').mkdir()
    write(OUT/'plan.json',dict(source_ids=sorted(sources),severities=list(SETTINGS),planned_probes=24,
        role='Counterfactual exposed-development diagnostic; not MST complexion assignment or training admission',
        application='Unchanged saved input measurement mask; no further mask experiments',
        model='Existing held-source fold for each source; no fitting or selection',
        measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes))
    records=[]
    try:
        for name,row in sorted(sources.items()):
            ref=cv2.imread(str(ROOT/row['reference_path']));selected=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            rgb=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB)
            fold=next(f for f in plan['folds'] if row['pair_id'] in f['inner_validation_pair_ids'])
            assert row['source_image_id'] not in fold['train_source_ids']
            tree=PortableTree(read(PARENT/f"fold_{fold['fold_id']}/decision_tree.json"))
            strips=[]
            for group in SETTINGS:
                pair=name+'__'+group
                transformed,_=composite_rgb(rgb,group);generated=rgb.copy();generated[selected]=transformed[selected]
                _,clipping=composite_rgb(rgb[selected][:,None,:],group)
                bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR);current=measure(bgr,detector,masker)
                save(OUT/'images'/(pair+'_input.png'),bgr)
                if current.mask is not None:save(OUT/'images'/(pair+'_mask.png'),current.mask)
                record=dict(pair_id=pair,source_id=name,severity_probe=group,training_admitted=False,
                    status=current.report['status'],measurement=current.report,clipping=clipping,
                    clipping_fraction=clipping['clipped_pixels']/int(selected.sum()),fold_id=fold['fold_id'],
                    reference_path=row['reference_path'],reference_mask_path=row['reference_mask_path'],
                    original_assigned_severity=next(r['variant'].removeprefix('table2_') for r in plan['rows'] if r['pair_id'].startswith(name+'__') and r['variant']!='identity'),
                    no_correction=image_errors(rgb,generated,selected))
                corrected=bgr.copy();oracle=bgr.copy()
                if current.report['status']=='success':
                    mask=current.mask>0
                    features={**current.report['features'],'input_mst_index':lookup.label(current.report['features']['input_ita_degrees'])-1}
                    parameters=tree.predict_one([features[k] for k in MST_FEATURES])
                    result=apply_correction(generated,mask,parameters)
                    corrected=cv2.cvtColor(result,cv2.COLOR_RGB2BGR)
                    save(OUT/'images'/(pair+'_learned.png'),corrected)
                    fit=fit_recovery_target(generated,rgb,mask,selected)
                    record.update(features=features,parameters=parameters,target_fit=fit,
                        reference_mask_retention=float((mask&selected).sum()/selected.sum()),
                        learned=image_errors(rgb,result,selected))
                    if fit['parameters'] is not None:
                        result=apply_correction(generated,mask,fit['parameters']);oracle=cv2.cvtColor(result,cv2.COLOR_RGB2BGR)
                        save(OUT/'images'/(pair+'_oracle.png'),oracle)
                        record['oracle']=image_errors(rgb,result,selected)
                    # Original severity must reproduce the previous experiment exactly.
                    if group==record['original_assigned_severity']:
                        old=next(r for r in prior['records'] if r['pair_id']==name+'__table2_'+group)
                        np.testing.assert_allclose(parameters,old['parameters'],rtol=0,atol=1e-12)
                        assert record['learned']==old['learned']
                strips.append(np.hstack([tile(ref,'Photographic reference'),tile(bgr,group+' '+record['status']),
                    tile(corrected,'Saved-fold prediction' if record['status']=='success' else 'Unavailable; input shown'),
                    tile(oracle,'Fitted oracle; not learned')]))
                records.append(record);print(pair,record['status'],flush=True)
            save(OUT/'boards'/(name+'.png'),np.vstack(strips))
        aggregate={}
        for group in SETTINGS:
            subset=[r for r in records if r['severity_probe']==group]
            paired=[r for r in subset if 'oracle' in r and 'learned' in r]
            aggregate[group]=dict(attempts=len(subset),successful_measurements=sum(r['status']=='success' for r in subset),
                available_targets=len(paired),paired_metric_count=len(paired),
                mean_clipping_fraction=float(np.mean([r['clipping_fraction'] for r in subset])),
                mean_reference_mask_retention=float(np.mean([r['reference_mask_retention'] for r in paired])) if paired else None,
                **{m+'_ciede2000':float(np.mean([r[m]['ciede2000_source_mask'] for r in paired])) if paired else None for m in ['no_correction','learned','oracle']})
        assert hashes=={p:digest(ROOT/p) for p in hashes}
        write(OUT/'summary.json',dict(status='complete_diagnostic_only',records=records,aggregate=aggregate,input_sha256=hashes,
            measurement_contract_sha256=identity,lookup_sha256=digest(artifact),training_admitted=0,models_fitted=0,runtime_replaced=False))
        (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Table 2 coverage diagnostic</title><style>body{font:16px sans-serif;margin:25px;background:#17191e;color:#eee}img{max-width:100%}</style><h1>All-severity diagnostic on eight accepted sources</h1><p>Counterfactual probes, not complexion labels or new training admissions. Same frozen measurement method and original held-source predictor. Oracle uses reference-informed fitted parameters; it is not learned performance. Failures remain in the ledger.</p>'+''.join(f'<h2>{n}</h2><img src="boards/{n}.png">' for n in sorted(sources)),encoding='utf-8')
        print(json.dumps(aggregate,indent=2))
    except Exception as error:
        write(OUT/'failure.json',dict(error=str(error),completed=len(records)));raise


if __name__=='__main__':main()
