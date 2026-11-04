"""Fixed dense-parser versus removal-only veto on known saved cases; no fitting."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.face_parsing_experiment import DenseFaceParser,facial_skin,LABELS
from src.distortion_generation.generate_distortions import transform_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mask(path):
    raw=cv2.imread(str(path),0)
    assert raw is not None and set(np.unique(raw)).issubset({0,255})
    return raw>0


def load_case(record):
    """Resolve exact known original image/masks; never read a new source."""
    config=get_config();key,ident=record['key'],record['image_id']
    if key.endswith('_source'):
        candidates=[ROOT/'outputs'/folder/'images' for folder in ('non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1')]
        parent=next(p for p in candidates if (p/(ident+'_reference.png')).exists())
        image=cv2.imread(str(parent/(ident+'_reference.png')))
        return image,{'generation':mask(parent/(ident+'_generation.png'))},None
    if '_regression_' in key:
        split='val' if ident=='10480' else 'train';variant=record['variant'];image_id='fairface__'+split+'/'+ident+'.jpg'
        image=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace'/split/(ident+'.jpg')))
        if variant!='clean':image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
        cats=np.load(ROOT/'outputs/landmark_framing_v1/geometry'/(key+'_categories.npy'));skin=np.isin(cats,[2,3])
        stem=image_id.replace('/','_')+'_'+variant
        measurement=mask(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')) & skin
        stages={'measurement':measurement,'correction':mask(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')) & skin}
        if variant=='clean':stages['generation']=measurement.copy()
        return image,stages,None
    candidates=[ROOT/'outputs'/folder/'images' for folder in ('non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1')]
    parent=next(p for p in candidates if (p/(key+'_input.png')).exists())
    image=cv2.imread(str(parent/(key+'_input.png')))
    return image,{'measurement':mask(parent/(key+'_baseline_estimate.png')),'correction':mask(parent/(key+'_support.png'))},mask(parent/(ident+'_generation.png'))


def main():
    config=get_config();output=ROOT/config.OUTPUTS_ROOT/'dense_face_parser_v1'
    if output.exists():raise FileExistsError(output)
    baseline_path=ROOT/'outputs/anatomical_contour_v1/summary.json';baseline=json.loads(baseline_path.read_text())
    audit_path=ROOT/'outputs/semantic_reference_audit_v1/summary.json';audit=json.loads(audit_path.read_text())
    model=ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx';provenance=model.with_suffix('.provenance.json')
    metadata=json.loads(provenance.read_text());assert digest(model)==metadata['sha256']
    hashes=dict(audit['input_sha256'])
    tracked=[Path(__file__),model,provenance,ROOT/'scripts/95_download_face_parser.py',
        ROOT/'src/skin_masking/face_parsing_experiment.py',ROOT/'docs/face-parsing-protocol.md',baseline_path,audit_path]
    hashes.update({str(p.relative_to(ROOT)):digest(p) for p in tracked})
    assert metadata['protocol_sha256']==digest(ROOT/'docs/face-parsing-protocol.md')
    assert all(digest(ROOT/p)==h for p,h in hashes.items())
    points=json.loads((ROOT/'data/manifests/material_review_v1/review_manifest.json').read_text())['points']
    label_map={p['point_id']:p['label'] for p in json.loads((ROOT/'data/manifests/material_review_v1/material_review_labels.json').read_text())['labels']}
    references={i:cv2.imread(str(ROOT/'outputs/face_boundary_reference_v1/labels'/(i+'_labels.png')),0) for i in ('40048','60162','16798')}
    polygons=json.loads((ROOT/'data/manifests/face_boundary_reference_v1/original_export.json').read_text())
    roles=audit['subgroup_description']['roles'];regions={}
    scoring=importlib.import_module('90_score_face_boundary_references');brightness=importlib.import_module('72_audit_brightness_features')
    for a in polygons['images']:
        ident=Path(a['image_id']).stem;labels=references[ident];paint=np.zeros_like(labels,bool)
        for index in roles[ident]['paint']:
            paint|=scoring.polygon_pixels(a['polygons'][index-1]['points'],labels.shape[1],labels.shape[0])
        paint &= labels==3;regions[ident]=dict(features=(labels==3)&~paint,paint=paint)
    output.mkdir()
    for name in ('categories','masks','boards','references'):(output/name).mkdir()
    (output/'protocol.md').write_bytes((ROOT/'docs/face-parsing-protocol.md').read_bytes())
    (output/'run_status.json').write_text('{"status":"running"}')
    started=time.perf_counter();parser=DenseFaceParser(model);load_seconds=time.perf_counter()-started
    records,observations,timings,boards=[],[],[],{}
    def predict(image,key):
        start=time.perf_counter();categories=parser.categories_bgr(image);elapsed=time.perf_counter()-start
        timings.append(elapsed);assert cv2.imwrite(str(output/'categories'/(key+'.png')),categories)
        dense=facial_skin(categories);assert cv2.imwrite(str(output/'masks'/(key+'_D.png')),dense.astype(np.uint8)*255)
        return dense,categories,elapsed
    for prior in baseline['records']:
        key,ident=prior['key'],prior['image_id'];image,old,generation=load_case(prior)
        try:
            dense,categories,elapsed=predict(image,key)
        except (cv2.error,ValueError) as error:
            records.append(dict(key=key,image_id=ident,status='unavailable',reason=str(error),stages={}));continue
        record=dict(key=key,image_id=ident,status='available',inference_seconds=elapsed,stages={},training_eligible=False,
                    category_counts={name:int((categories==i).sum()) for i,name in enumerate(LABELS)})
        if ident in references:
            labels=references[ident];assert dense.shape==labels.shape
            record['dense_reference']=scoring.score(dense,labels);record['dense_interior_reference']=scoring.score(dense,labels,True)
            record['dense_exclusion_groups']={name:dict(pixels=int(region.sum()),selected=int((dense&region).sum())) for name,region in regions[ident].items()}
        if ident=='40048':record['dense_cheek_202_124']=bool(dense[124,202])
        vetoes={}
        for stage,original in old.items():
            veto=original & dense;vetoes[stage]=veto
            assert not (veto & ~original).any()
            assert cv2.imwrite(str(output/'masks'/(key+'_'+stage+'_V.png')),veto.astype(np.uint8)*255)
            value=dict(before_pixels=int(original.sum()),after_pixels=int(veto.sum()),removed_pixels=int((original&~veto).sum()))
            if ident in references:
                value.update(original_reference=scoring.score(original,references[ident]),reference=scoring.score(veto,references[ident]),interior_reference=scoring.score(veto,references[ident],True),
                    exclusion_groups={name:dict(pixels=int(region.sum()),selected=int((veto&region).sum())) for name,region in regions[ident].items()})
            if ident=='40048':value['cheek_202_124']=bool(veto[124,202])
            record['stages'][stage]=value
            panels=[]
            for title,selected in [('Original',original),('D dense diagnostic',dense),('V old AND dense',veto)]:
                shown=image.copy();shown[selected]=np.rint(.55*shown[selected]+[0,99,0]).astype(np.uint8)
                shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(shown,key+' '+stage,(3,11),cv2.FONT_HERSHEY_SIMPLEX,.25,(255,255,255),1)
                cv2.putText(shown,title,(3,23),cv2.FONT_HERSHEY_SIMPLEX,.29,(255,255,255),1);panels.append(shown)
            boards.setdefault(ident,[]).append(np.hstack(panels))
        if 'measurement' in vetoes:
            measurement=vetoes['measurement'];stats=compute_masked_lab_statistics(image,measurement.astype(np.uint8)*255,1000)
            record['measurement_statistics']=dict(statistics=stats,brightness=brightness.brightness_features(image,measurement))
        if generation is not None:
            record['retention_old_generation_denominator']=support_retention(generation,vetoes['measurement'],vetoes['correction'])
        if prior.get('regression'):
            for point in (p for p in points if Path(p['image_id']).stem==ident):
                x,y=point['x'],point['y'];assert dense.shape==(point['height'],point['width'])
                observations.append(dict(point_id=point['point_id'],variant=prior['variant'],label=label_map[point['point_id']],dense=bool(dense[y,x]),
                    stages={name:dict(original=bool(original[y,x]),veto=bool(vetoes[name][y,x])) for name,original in old.items()}))
        if ident in references:
            panels=[image]
            for selected in [dense,vetoes.get('correction',vetoes.get('generation',vetoes.get('measurement')))]:
                shown=image.copy();shown[selected & (references[ident]==3)]=[0,0,255];shown[~selected & (references[ident]==1)]=[255,100,0];panels.append(shown)
            assert cv2.imwrite(str(output/'references'/(key+'.png')),np.hstack(panels))
        records.append(record);print(key,flush=True)
    sentinel_results=[]
    for variant in ('clean','global_color_shift'):
        image=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace/train/83184.jpg'))
        if variant!='clean':image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
        try:
            dense,categories,elapsed=predict(image,'83184_sentinel_'+variant)
            sentinel_results.append(dict(variant=variant,status='diagnostic_only_not_geometry_approved',selected_pixels=int(dense.sum()),inference_seconds=elapsed))
            shown=image.copy();shown[dense]=np.rint(.55*shown[dense]+[0,99,0]).astype(np.uint8)
            assert cv2.imwrite(str(output/'boards'/('83184_'+variant+'.png')),np.hstack([image,shown]))
        except (cv2.error,ValueError) as error:sentinel_results.append(dict(variant=variant,status='unavailable',reason=str(error)))
    for ident,rows in boards.items():
        for page,offset in enumerate(range(0,len(rows),4),1):assert cv2.imwrite(str(output/'boards'/f'{ident}_page{page}.png'),np.vstack(rows[offset:offset+4]))
    assert len(records)==53 and all(digest(ROOT/p)==h for p,h in hashes.items())
    summary=dict(status='complete_diagnostic_only_no_adoption_no_regeneration_no_fit',records=records,point_observations=observations,sentinels=sentinel_results,
        model=dict(bytes=metadata['bytes'],sha256=metadata['sha256'],load_seconds=load_seconds,source_revision=metadata['source_revision']),
        desktop_cpu_timing=dict(count=len(timings),first_seconds=timings[0],median_seconds=float(np.median(timings)),min_seconds=min(timings),max_seconds=max(timings),opencv=cv2.__version__,note='OpenCV CPU target requested; desktop timings are not Android benchmarks'),
        input_sha256=hashes,models_fitted=0,limitations='D raw support is not a final mask, and has no paint class. V preserves legacy gaps and may lose skin; no expansive replacement. Internal512 inference restores exact native saved coordinates. All prior decisions/holds/sentinel rejection remain unchanged.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (output/'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps(dict(available=sum(r['status']=='available' for r in records),total=len(records),timing=summary['desktop_cpu_timing'])))


if __name__=='__main__':main()
