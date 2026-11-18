"""Saved-record anchor geometry diagnosis: no images, scores or new forwards."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'outputs/ppr10k_new_group_comparison_v1'
SCREEN=ROOT/'outputs/ppr10k_automatic_support_v1'
OUT=ROOT/'outputs/ppr10k_anchor_diagnosis_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Preserve prior/partial diagnosis')
    bound={}
    def read(p):
        bound[str(p.relative_to(ROOT))]=sha(p)
        return json.loads(p.read_text(encoding='utf-8'))
    screen=read(SCREEN/'results_PRIVATE.json');verification=read(SCREEN/'verification_PRIVATE.json')
    assert verification['passed'] and verification['results_sha256']==sha(SCREEN/'results_PRIVATE.json')
    historical=read(OLD/'sha256.json')
    audit=read(OLD/'image_audit.json');regions=read(OLD/'source_regions.json')
    for name in ['image_audit.json','source_regions.json']:
        assert sha(OLD/name)==historical[name]
    shape={a['frame']:a['shape'] for a in audit if a['role']=='source'}
    rows=[]
    for r in screen['records']:
        frame=r['frame'];height,width,_=shape[frame];poly=regions[frame]['polygon']
        x=[p[0] for p in poly];y=[p[1] for p in poly]
        pw=max(x)-min(x)+1;ph=max(y)-min(y)+1
        sx=256/width;sy=256/height
        rows.append(dict(frame=frame,previous_status=r['status'],native_width=width,native_height=height,
            historical_polygon_bbox_native=[min(x),min(y),pw,ph],
            polygon_size_on_square256=[pw*sx,ph*sy],horizontal_scale=sx,vertical_scale=sy,
            aspect_width_over_height_multiplier=sx/sy,
            anchors=r['anchors_256'],candidate_confidences_saved=False,
            limitation='Manual polygon is a diagnostic face-size proxy, not detector truth or an inference crop.'))
        assert abs(sx/sy-height/width)<1e-12
    for name in ['scripts/703_screen_existing_ppr10k_support.py','src/face_detection/detect_faces.py',
                 'scripts/705_diagnose_ppr10k_anchor_misses.py']:
        bound[name]=sha(ROOT/name)
    summary=dict(attempts=8,available=4,zero_anchor_failures=4,
        confidences_available=False,all_inputs_anisotropically_resized=True,
        causal_diagnosis='Unresolved: geometry/scale/pose may contribute; confidence rejection vs candidate absence cannot be recovered from saved boxes.',
        selected_test='Single detector-only native-resolution/aspect-preserving input comparison at unchanged .85 threshold on all8; NOT executed.',
        new_image_reads=0,new_forwards=0,new_fits=0,holdout_reads=0)
    assert all(sha(ROOT/p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(dict(summary=summary,rows=rows,input_sha256=bound),indent=2),encoding='utf-8')
    for r in rows:print(r['frame'],r['previous_status'],*[round(x,2) for x in r['polygon_size_on_square256']],round(r['aspect_width_over_height_multiplier'],3))
    print('PASS: 8 saved geometry rows; source/receipt bindings unchanged; zero new forwards.')
if __name__=='__main__':main()
