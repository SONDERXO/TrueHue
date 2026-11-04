"""Fixed parser/anatomy/material arms, core then historical cohorts separately."""
import argparse
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
from src.skin_masking.parser_material_experiment import combined_supports
from src.skin_masking.face_parsing_experiment import DenseFaceParser,facial_skin
from src.skin_masking.anatomical_contour_experiment import anatomy
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_mask(path):
    a=cv2.imread(str(path),0);assert a is not None and set(np.unique(a)).issubset({0,255})
    return a>0


def main():
    args=argparse.ArgumentParser();args.add_argument('--historical',action='store_true');args=args.parse_args()
    config=get_config();output=ROOT/config.OUTPUTS_ROOT/('parser_material_historical_v1' if args.historical else 'parser_material_core_v1')
    if output.exists():raise FileExistsError(output)
    scoring=importlib.import_module('90_score_face_boundary_references');brightness=importlib.import_module('72_audit_brightness_features')
    loader=importlib.import_module('96_test_dense_face_parser');prepare=importlib.import_module('11_prepare_training_manifests')
    baseline=json.loads((ROOT/'outputs/anatomical_contour_v1/summary.json').read_text())
    previous=json.loads((ROOT/'outputs/dense_face_parser_v1/summary.json').read_text())
    hashes=dict(previous['input_sha256'])
    tracked=[Path(__file__),ROOT/'src/skin_masking/parser_material_experiment.py',ROOT/'docs/parser-combination-protocol.md',
        ROOT/'data/manifests/parser_combination_v1/user_direction.json',ROOT/'outputs/dense_face_parser_v1/summary.json']
    model=ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx'
    cases=[];parser=None
    if args.historical:
        parent=ROOT/'outputs/training_source60_variants_v1';old_path=parent/'summary.json';old=json.loads(old_path.read_text());tracked.append(old_path)
        reviews=ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json';tracked.append(reviews)
        original_reviews={r['pair_id']:r for r in json.loads(reviews.read_text())['pairs']}
        ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
        exposed={json.loads(line)['image_id'] for line in ledger.read_text().splitlines() if line};tracked.append(ledger)
        for row in old['sources']:
            ident=Path(row['image_id']).stem;assert row['image_id'] in exposed
            cases.append(dict(key=ident+'_source',image_id=ident,kind='source',source_row=row,parent=str(parent/'images')))
        for row in old['attempts']:
            ident=Path(row['image_id']).stem;pair=ident+'_'+row['variant'];assert row['image_id'] in exposed
            cases.append(dict(key=pair,image_id=ident,kind='input',source_row=row,parent=str(parent/'images'),review=original_reviews[pair]))
        assert len(cases)==90
        tracked+=list((parent/'images').glob('*.png'))
        tracked+=list((ROOT/'outputs/non_skin_veto_v1/masks').glob('*.png'))
    else:
        cases=baseline['records']
        tracked+=list((ROOT/'outputs/anatomical_contour_v1/geometry').glob('*.png'))
        tracked+=list((ROOT/'outputs/landmark_framing_v1/geometry').glob('*_categories.npy'))
        tracked+=list((ROOT/'outputs/dense_face_parser_v1/categories').glob('*.png'))
    hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    refs={i:cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(i+'_labels.png')),0) for i in ['40048','60162','16798']}
    export=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text());regions={}
    for a in export['images']:
        ident=Path(a['image_id']).stem;labels=refs[ident];paint=np.zeros(labels.shape,bool)
        if ident=='16798':
            for index in range(6):paint|=scoring.polygon_pixels(a['polygons'][index]['points'],labels.shape[1],labels.shape[0])
        paint&=labels==3;regions[ident]={'features':(labels==3)&~paint,'paint':paint}
    point_spec=json.loads((ROOT/'data/manifests/material_review_v1/review_manifest.json').read_text())['points']
    point_labels={p['point_id']:p['label'] for p in json.loads((ROOT/'data/manifests/material_review_v1/material_review_labels.json').read_text())['labels']}
    output.mkdir()
    for folder in ['ingredients','masks','boards']:(output/folder).mkdir()
    (output/'protocol.md').write_bytes((ROOT/'docs/parser-combination-protocol.md').read_bytes());(output/'run_status.json').write_text('{"status":"running"}')
    if args.historical:parser=DenseFaceParser(model)
    records=[];observations=[];boards={};source_arms={}
    for case in cases:
        key,ident=case['key'],case['image_id'];record=dict(key=key,image_id=ident,status='unavailable',stages={},training_eligible=False)
        if args.historical:
            record['historical_case']=True;record['original_review']=case.get('review');record['historical_variant']=case['source_row'].get('variant')
            parent=Path(case['parent'])
            if case['kind']=='source':
                image=cv2.imread(str(parent/(ident+'_reference.png')));original={'generation':read_mask(parent/(ident+'_generation.png'))};generation=None
                categories=cv2.imread(str(ROOT/'outputs/non_skin_veto_v1/masks'/(ident+'_source_categories.png')),0)
            else:
                image=cv2.imread(str(parent/(key+'_input.png')));original={'measurement':read_mask(parent/(key+'_baseline_estimate.png')),'correction':read_mask(parent/(key+'_support.png'))}
                generation=read_mask(parent/(ident+'_generation.png'));categories=cv2.imread(str(ROOT/'outputs/non_skin_veto_v1/masks'/(key+'_categories.png')),0)
        else:image,original,generation=loader.load_case(case)
        try:
            if args.historical:
                dense_categories=parser.categories_bgr(image);dense=facial_skin(dense_categories)
                boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
                if len(boxes)!=1:raise ValueError('Expected one face')
                box=list(map(int,boxes[0]));points,margin,status=prepare.detect_landmarks_with_margin(image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                if points is None:raise ValueError('Unavailable anatomical landmarks')
                full=points+box[:2];_,excluded,_,details=anatomy(image,full)
                np.save(output/'ingredients'/(key+'_landmarks.npy'),full)
            else:
                dense_categories=cv2.imread(str(ROOT/'outputs/dense_face_parser_v1/categories'/(key+'.png')),0);dense=facial_skin(dense_categories)
                categories=np.load(ROOT/'outputs/landmark_framing_v1/geometry'/(key+'_categories.npy'))
                excluded=read_mask(ROOT/'outputs/anatomical_contour_v1/geometry'/(key+'_expanded_excluded.png'));box=case['geometry']['face_box']
            measurement=original.get('measurement',original.get('generation'))
            arms,details,seeds,full_distance,chroma_distance=combined_supports(image,dense,categories,excluded,box,measurement)
        except (ValueError,cv2.error) as error:
            record['reason']=str(error);records.append(record);print(key+': unavailable '+str(error),flush=True);continue
        for name,value in [('dense',dense),('excluded',excluded),('measurement',measurement),('seeds',seeds)]:
            assert cv2.imwrite(str(output/'ingredients'/(key+'_'+name+'.png')),value.astype(np.uint8)*255)
        assert cv2.imwrite(str(output/'ingredients'/(key+'_categories.png')),categories)
        assert cv2.imwrite(str(output/'ingredients'/(key+'_parser_categories.png')),dense_categories)
        np.save(output/'ingredients'/(key+'_distances.npy'),np.stack([full_distance,chroma_distance]))
        record.update(status='available',material=details,stages={})
        stage_arms={}
        for stage,old in original.items():
            stage_arms[stage]={a:(old&value if stage=='measurement' else value.copy()) for a,value in arms.items()}
            values={}
            for arm,value in stage_arms[stage].items():
                assert not (value&excluded).any()
                assert cv2.imwrite(str(output/'masks'/(key+'_'+stage+'_'+arm+'.png')),value.astype(np.uint8)*255)
                item=dict(pixels=int(value.sum()),added_pixels=int((value&~old).sum()),removed_pixels=int((old&~value).sum()))
                if not args.historical and ident in refs:
                    labels=refs[ident];item.update(reference=scoring.score(value,labels),interior_reference=scoring.score(value,labels,True),
                        added_excluded_pixels=int((value&~old&(labels==3)).sum()),
                        exclusion_groups={name:dict(pixels=int(region.sum()),selected=int((value&region).sum()),added=int((value&~old&region).sum())) for name,region in regions[ident].items()})
                if not args.historical and ident=='40048':item['cheek_202_124_selected']=bool(value[124,202])
                values[arm]=item
            record['stages'][stage]=dict(original_pixels=int(old.sum()),arms=values)
            panels=[]
            for title,value in [('Original',old)]+list(stage_arms[stage].items()):
                shown=image.copy();shown[value]=np.rint(.55*shown[value]+[0,99,0]).astype(np.uint8);shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(shown,key+' '+stage,(3,11),cv2.FONT_HERSHEY_SIMPLEX,.25,(255,255,255),1);cv2.putText(shown,title,(3,23),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(shown)
            boards.setdefault(ident,[]).append(np.hstack(panels))
        if 'generation' in stage_arms:source_arms[ident]=stage_arms['generation']
        if 'measurement' in stage_arms:
            record['measurement_statistics']={a:dict(statistics=compute_masked_lab_statistics(image,value.astype(np.uint8)*255,1000),brightness=brightness.brightness_features(image,value)) for a,value in stage_arms['measurement'].items()}
        if generation is not None:
            record['retention_old_generation_denominator']={a:support_retention(generation,stage_arms['measurement'][a],stage_arms['correction'][a]) for a in arms}
            record['retention_prospective_generation_denominator']={a:support_retention(source_arms[ident][a],stage_arms['measurement'][a],stage_arms['correction'][a]) if source_arms[ident][a].any() else None for a in arms} if ident in source_arms else None
        if not args.historical and case.get('regression'):
            for point in (p for p in point_spec if Path(p['image_id']).stem==ident):
                x,y=point['x'],point['y'];assert image.shape[:2]==(point['height'],point['width'])
                observations.append(dict(point_id=point['point_id'],variant=case['variant'],label=point_labels[point['point_id']],stages={stage:dict(original=bool(original[stage][y,x]),arms={a:bool(value[y,x]) for a,value in vals.items()}) for stage,vals in stage_arms.items()}))
        records.append(record);print(key+': available',flush=True)
    for ident,rows in boards.items():
        for page,offset in enumerate(range(0,len(rows),4),1):assert cv2.imwrite(str(output/'boards'/f'{ident}_page{page}.png'),np.vstack(rows[offset:offset+4]))
    assert len(records)==(90 if args.historical else 53)
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_no_adoption_no_regeneration_no_fitting',historical=args.historical,records=records,point_observations=observations,input_sha256=hashes,models_fitted=0,
        limitations='Fresh prospective generation/correction supports on OLD saved inputs. Original-generation retention contains old non-skin. Material consistency is not paint recognition. Historical decisions and existing sentinel rejection unchanged.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');(output/'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps(dict(total=len(records),available=sum(r['status']=='available' for r in records),point_observations=len(observations))))


if __name__=='__main__':main()
