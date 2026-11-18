"""Reuse fixed evaluator; original aligned parent remains acceptance comparator."""
from pathlib import Path
import runpy,json
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/depth_four_correction_comparison_v1'
def main():
    ns=runpy.run_path(str(ROOT/'scripts/614_evaluate_expanded_correction.py'))
    fn=ns['main'];fn.__globals__.update(OUT=OUT,M=ROOT/'outputs/depth_four_correction_models_v1/models_PRIVATE.json');fn()
    p=OUT/'results_PRIVATE.json';d=json.loads(p.read_text());d['comparison']='Depth four only versus frozen expanded depth three; aligned parent acceptance comparator'
    old=json.loads((ROOT/'outputs/expanded_correction_comparison_v1/results_PRIVATE.json').read_text())
    d['expanded_depth_three_summary']=old['summary']
    for path in d['boards']:
        im=cv2.imread(path);im[:28]=255
        cv2.putText(im,Path(path).parent.name+' ref|input|aligned parent|depth four',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1)
        assert cv2.imwrite(path,im)
    for start in range(0,len(d['boards']),4):
        assert cv2.imwrite(str(OUT/'contact_sheets'/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in d['boards'][start:start+4]]))
    p.write_text(json.dumps(d,indent=2))
if __name__=='__main__':main()
