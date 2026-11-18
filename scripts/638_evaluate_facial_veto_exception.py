"""Fixed756 prepared evaluation, frozen facial exception only."""
from pathlib import Path
import runpy,json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/facial_veto_exception_comparison_v1';M=ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json'
def main():
    assert json.loads((M.parent/'verification_PRIVATE.json').read_text())['passed']
    ns=runpy.run_path(str(ROOT/'scripts/614_evaluate_expanded_correction.py'));fn=ns['main'];fn.__globals__.update(OUT=OUT,M=M);fn()
    p=OUT/'results_PRIVATE.json';d=json.loads(p.read_text());d['comparison']='Frozen raw facial-range exception to reserved clean veto; zero fits'
    for path in d['boards']:
        im=cv2.imread(path);im[:28]=255;cv2.putText(im,Path(path).parent.name+' ref|input|aligned parent|facial exception',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);assert cv2.imwrite(path,im)
    for start in range(0,len(d['boards']),4):assert cv2.imwrite(str(OUT/'contact_sheets'/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in d['boards'][start:start+4]]))
    p.write_text(json.dumps(d,indent=2))
    p=OUT/'input_sha256_PRIVATE.json';b=json.loads(p.read_text());b[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(b,indent=2))
if __name__=='__main__':main()
