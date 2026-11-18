"""Import actual local six-case export; refuse substitution or repeated overwrite."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
from src.evaluation.reference_point_review import validate_export,compare_points
PARENT=ROOT/'outputs/stellenbosch_reference_points_v1'
OUT=ROOT/'outputs/stellenbosch_reference_points_import_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('export',type=Path);args=parser.parse_args()
    if OUT.exists():raise FileExistsError('Actual import exists; no overwrite')
    bound=read(PARENT/'input_sha256_PRIVATE.json')
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    raw=args.export.read_bytes();value=json.loads(raw)
    manifest=read(PARENT/'manifest.json');rows=validate_export(value,manifest,sha(PARENT/'manifest.json'))
    bindings=read(PARENT/'prediction_bindings_PRIVATE.json');predictions={}
    for row in rows:
        binding=bindings[row['review_id']];path=binding['native_grid_path']
        if path is None:predictions[row['review_id']]=None;continue
        assert sha(path)==binding['native_grid_sha256']
        grid=cv2.imread(path,0);x0,y0,x1,y1=binding['native_bounds'];predictions[row['review_id']]=grid[y0:y1,x0:x1]>0
        expected=next(r for r in manifest['rows'] if r['review_id']==row['review_id'])
        assert predictions[row['review_id']].shape==(expected['height'],expected['width'])
    result=compare_points(rows,predictions)
    result.update(reviewer=value['reviewer'],export_sha256=hashlib.sha256(raw).hexdigest(),
        manifest_sha256=sha(PARENT/'manifest.json'),independent_or_blinded=False,new_forwards=0,new_fits=0)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'actual_export_PRIVATE.json').write_bytes(raw)
    (OUT/'comparison_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':main()
