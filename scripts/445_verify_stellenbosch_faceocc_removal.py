"""Independent raster accounting and completed private removal assessment."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
PARENT=ROOT/'outputs/stellenbosch_faceocc_removal_v1'
OUT=ROOT/'outputs/stellenbosch_faceocc_removal_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NOTES={
 1:'Mainly hairline/boundary removal, including hair lock; not all removed pixels are unwanted skin loss.',
 2:'Mostly boundary trim; some upper forehead/temple skin appears removed; central parser gaps remain distinct.',
 3:'Warmest condition removes substantial apparently visible lower-face/chin skin; other conditions have boundary/chin variation.',
 4:'Mostly boundary/hairline trimming; some forehead/jaw skin may be removed, not a dense annotation.',
 5:'Broad apparent cheek/chin skin loss in warm conditions, as well as uncertain lower-face/neck and hairline areas.',
 6:'Glasses/reflections ambiguous; middle warm condition removes most forehead/cheek support leaving tiny cheek patch. Mapping-domain loss contributes but model rejection dominates; final warm condition also trims forehead.',
 7:'First parent unavailable; middle available forehead/side-face support entirely removed; last leaves only sparse forehead/cheek islands despite apparently visible facial skin.',
 8:'Primarily contour trim; incomplete central mask remains a parser-stage issue, not solely FaceOcc.',
 9:'All three have available parent support. Forehead or broader facial support removed almost entirely; three final failures. Very dim pixels limit certainty but removal overlaps apparent visible skin, not just objects.',
 10:'All three unavailable at parent/detector stages; no FaceOcc rejection fabricated.'}

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json')
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(Path(p))==h for p,h in bound.items())
    data=read(PARENT/'results_PRIVATE.json');rows=data['records'];available=[r for r in rows if r['available']]
    assert len(rows)==30 and len(available)==25 and len({r['subject_key'] for r in rows})==10
    for r in available:
        masks={k:cv2.imread(str(PARENT/(r['case_id']+'_'+k+'.png')),0)>0 for k in ['parent','kept','removed','mapping_loss','model_loss']}
        assert np.array_equal(masks['parent'],masks['kept']|masks['removed'])
        assert not (masks['kept']&masks['removed']).any()
        assert np.array_equal(masks['removed'],masks['mapping_loss']|masks['model_loss'])
        assert not (masks['mapping_loss']&masks['model_loss']).any()
        for mask,field in [('parent','parent_pixels'),('kept','kept_pixels'),('removed','removed_pixels'),('mapping_loss','mapping_domain_loss'),('model_loss','model_prediction_loss')]:
            assert int(masks[mask].sum())==r[field]
    for field in ['parent_pixels','kept_pixels','removed_pixels','mapping_domain_loss','model_prediction_loss']:
        assert sum(r[field] for r in available)==data['summary'][field]
    notes=dict(all30_boards_assistant_inspected=True,source_scores_hidden_on_boards=True,
        notes_by_subject_index=NOTES,saved_partition_checks=25,aggregate_checks=5,
        model_share_of_removed_pixels=data['summary']['model_prediction_loss']/data['summary']['removed_pixels'],
        observation='Apparent visible-skin loss as well as plausible boundary/object removal; no dense truth/accuracy.',
        selected_repair_direction='One fixed segmentation-only appearance preprocessing comparison for FaceOcc, keeping original alignment and original-pixel statistics; not activated.',
        no_veto_disable_or_threshold_change=True,new_forwards=0,new_fits=0,admissions=0,
        parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(Path(__file__)))
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(notes,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in notes.items() if k!='notes_by_subject_index'},indent=2))

if __name__=='__main__':main()
