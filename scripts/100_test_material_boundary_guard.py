"""One fixed removal-only C2 follow-up, all core and historical cases."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.skin_masking.material_boundary_guard import guard_material_boundary
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mask(path):
    a=cv2.imread(str(path),0);assert a is not None
    return a>0


def main():
    output=ROOT/'outputs/parser_material_boundary_v1'
    if output.exists():raise FileExistsError(output)
    loader=importlib.import_module('96_test_dense_face_parser');scoring=importlib.import_module('90_score_face_boundary_references')
    brightness=importlib.import_module('72_audit_brightness_features');witnesses=importlib.import_module('82_inspect_accepted_mask_notes').WITNESSES
    cases={r['key']:r for r in json.loads((ROOT/'outputs/anatomical_contour_v1/summary.json').read_text())['records']}
    refs={i:cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(i+'_labels.png')),0) for i in ['40048','60162','16798']}
    export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text());paint=np.zeros(refs['16798'].shape,bool)
    for p in export['images'][1]['polygons'][:6]:paint|=scoring.polygon_pixels(p['points'],paint.shape[1],paint.shape[0])
    paint &= refs['16798']==3
    hashes={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),ROOT/'src/skin_masking/material_boundary_guard.py',
        ROOT/'docs/parser-material-boundary-protocol.md',ROOT/'scripts/82_inspect_accepted_mask_notes.py']}
    output.mkdir()
    for folder in ['masks','boards']:(output/folder).mkdir()
    (output/'protocol.md').write_bytes((ROOT/'docs/parser-material-boundary-protocol.md').read_bytes())
    all_records=[];all_points=[];boards={};witness_results=[];replayed=0;feature_count=0
    for phase,folder in [('core','parser_material_core_v1'),('historical','parser_material_historical_v1')]:
        parent=ROOT/'outputs'/folder;previous=json.loads((parent/'summary.json').read_text());generations={}
        hashes.update(previous['input_sha256'])
        hashes.update({str(p.relative_to(ROOT)):digest(p) for p in [parent/'summary.json',parent/'verification.json']})
        hashes.update({str(p.relative_to(ROOT)):digest(p) for name in ['ingredients','masks'] for p in (parent/name).iterdir() if p.is_file()})
        record_lookup={}
        for row in previous['records']:
            key,ident=row['key'],row['image_id'];record=dict(phase=phase,key=key,image_id=ident,status=row['status'],stages={},training_eligible=False)
            if row['status']!='available':record['reason']=row['reason'];all_records.append(record);continue
            if phase=='core':image,original,generation=loader.load_case(cases[key])
            else:
                old=ROOT/'outputs/training_source60_variants_v1/images'
                if key.endswith('_source'):
                    image=cv2.imread(str(old/(ident+'_reference.png')));original={'generation':mask(old/(ident+'_generation.png'))};generation=None
                else:
                    image=cv2.imread(str(old/(key+'_input.png')));original={'measurement':mask(old/(key+'_baseline_estimate.png')),'correction':mask(old/(key+'_support.png'))};generation=mask(old/(ident+'_generation.png'))
            full_stage='correction' if 'correction' in row['stages'] else 'generation'
            base=mask(parent/'masks'/(key+'_'+full_stage+'_A.png'));chroma=mask(parent/'masks'/(key+'_'+full_stage+'_C.png'))
            candidate,outliers=guard_material_boundary(base,chroma)
            yy,xx=np.mgrid[-2:3,-2:3];disk=(xx*xx+yy*yy<=4).astype(np.uint8)
            independent=chroma & ~(cv2.dilate(outliers.astype(np.uint8),disk)>0)
            np.testing.assert_array_equal(candidate,independent)
            record['outlier_pixels']=int(outliers.sum())
            stage_masks={}
            for stage,old_mask in original.items():
                prior_c=mask(parent/'masks'/(key+'_'+stage+'_C.png'));current=prior_c & candidate
                np.testing.assert_array_equal(current,prior_c & independent);replayed+=1
                assert not (current & ~prior_c).any()
                path=output/'masks'/(phase+'_'+key+'_'+stage+'_C2.png');assert cv2.imwrite(str(path),current.astype(np.uint8)*255)
                value=dict(pixels=int(current.sum()),removed_from_C=int((prior_c&~current).sum()),added_to_original=int((current&~old_mask).sum()))
                if phase=='core' and ident in refs:
                    labels=refs[ident];value.update(reference=scoring.score(current,labels),interior_reference=scoring.score(current,labels,True),added_excluded=int((current&~old_mask&(labels==3)).sum()))
                    if ident=='16798':value['paint']=dict(selected=int((current&paint).sum()),added=int((current&~old_mask&paint).sum()))
                if phase=='core' and ident=='40048':value['cheek_202_124']=bool(current[124,202])
                record['stages'][stage]=value;stage_masks[stage]=current
                if ident in witnesses:
                    x0,y0,x1,y1=witnesses[ident]['bounds'];witness_results.append(dict(phase=phase,key=key,stage=stage,material=witnesses[ident]['material'],bounds=witnesses[ident]['bounds'],
                        original=int(old_mask[y0:y1,x0:x1].sum()),A=int(mask(parent/'masks'/(key+'_'+stage+'_A.png'))[y0:y1,x0:x1].sum()),
                        F=int(mask(parent/'masks'/(key+'_'+stage+'_F.png'))[y0:y1,x0:x1].sum()),C=int(prior_c[y0:y1,x0:x1].sum()),C2=int(current[y0:y1,x0:x1].sum())))
                panels=[]
                for title,support in [('Original',old_mask),('C chroma',prior_c),('C2 margin2',current)]:
                    shown=image.copy();shown[support]=np.rint(.55*shown[support]+[0,99,0]).astype(np.uint8);shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
                    cv2.putText(shown,key+' '+stage,(3,11),cv2.FONT_HERSHEY_SIMPLEX,.25,(255,255,255),1);cv2.putText(shown,title,(3,23),cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1);panels.append(shown)
                boards.setdefault(phase+'_'+ident,[]).append(np.hstack(panels))
            if 'generation' in stage_masks:generations[ident]=stage_masks['generation']
            if 'measurement' in stage_masks:
                measurement=stage_masks['measurement'];stats=compute_masked_lab_statistics(image,measurement.astype(np.uint8)*255,1000);bf=brightness.brightness_features(image,measurement)
                record['measurement_statistics']=dict(statistics=stats,brightness=bf)
                # Independent conventional-Lab/ITA and brightness calculation.
                encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);encoded[:,:,0]*=100/255;encoded[:,:,1:]-=128
                pixels=encoded[measurement];assert len(pixels)>=1000
                means=[round(float(pixels[:,i].mean()),4) for i in range(3)];ita=round(float(np.degrees(np.arctan((means[0]-50)/means[2]))),4)
                np.testing.assert_allclose([stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']],means+[ita],atol=1e-4,rtol=0)
                y,x=np.nonzero(measurement);xm,ym=(x.min()+x.max())/2,(y.min()+y.max())/2;L=encoded[:,:,0][measurement]
                p10,p25,p50,p75,p90=np.percentile(L,[10,25,50,75,90],method='linear')
                values=[p10,p50,p90,p75-p25,float(L[x<=xm].mean())-float(L[x>xm].mean()),float(L[y<=ym].mean())-float(L[y>ym].mean())]
                assert bf['valid'];np.testing.assert_allclose(list(bf['features'].values()),values,atol=1e-4,rtol=0);feature_count+=1
            if generation is not None:
                record['retention_old_generation_denominator']=support_retention(generation,stage_masks['measurement'],stage_masks['correction'])
                record['retention_prospective_generation_denominator']=support_retention(generations[ident],stage_masks['measurement'],stage_masks['correction']) if ident in generations and generations[ident].any() else None
            record_lookup[key]=stage_masks;all_records.append(record)
        if phase=='core':
            point_spec=json.loads((ROOT/'data/manifests/material_review_v1/review_manifest.json').read_text())['points']
            for point in previous['point_observations']:
                spec=next(p for p in point_spec if p['point_id']==point['point_id']);ident=Path(spec['image_id']).stem;key=ident+'_regression_'+point['variant'];x,y=spec['x'],spec['y']
                all_points.append(dict(point_id=point['point_id'],variant=point['variant'],label=point['label'],stages={stage:bool(value[y,x]) for stage,value in record_lookup[key].items()}))
    for ident,rows in boards.items():
        for page,offset in enumerate(range(0,len(rows),4),1):assert cv2.imwrite(str(output/'boards'/f'{ident}_page{page}.png'),np.vstack(rows[offset:offset+4]))
    assert len(all_records)==143 and replayed==268 and feature_count==119 and len(all_points)==48
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_followup_no_adoption_no_regeneration_no_fitting',records=all_records,points=all_points,witness_observations=witness_results,input_sha256=hashes,
        verification=dict(status='pass',mask_disk_replays=replayed,independent_measurement_feature_sets=feature_count,input_hashes_unchanged=True),models_fitted=0,
        sentinel_status='Prior83184 rejection preserved; no unsupported geometry fallback or new admission',limitations='Adaptive fixed development follow-up; margin2 not searched. Material consistency/neighbor protection is not paint recognition. Inputs still old generation policy.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary['verification']))


if __name__=='__main__':main()
