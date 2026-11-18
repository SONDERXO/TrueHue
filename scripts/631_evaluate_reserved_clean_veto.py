"""Same fixed 756 prepared attempts, separately before/after the reserved-clean veto."""
from pathlib import Path
import runpy,json,sys,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    stage=sys.argv[1];assert stage in ('pre','final')
    out=ROOT/('outputs/reserved_clean_veto_pre_comparison_v1' if stage=='pre' else 'outputs/reserved_clean_veto_comparison_v1')
    model=ROOT/'outputs/reserved_clean_veto_models_v1'/('pre_veto_models_PRIVATE.json' if stage=='pre' else 'models_PRIVATE.json')
    ns=runpy.run_path(str(ROOT/'scripts/614_evaluate_expanded_correction.py'));fn=ns['main'];fn.__globals__.update(OUT=out,M=model);fn()
    p=out/'results_PRIVATE.json';d=json.loads(p.read_text());d['comparison']='Reserved development groups excluded: '+stage+' clean veto; aligned parent remains acceptance comparator'
    for path in d['boards']:
        im=cv2.imread(path);im[:28]=255
        cv2.putText(im,Path(path).parent.name+' ref|input|aligned parent|'+stage+' veto',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1);assert cv2.imwrite(path,im)
    for start in range(0,len(d['boards']),4):assert cv2.imwrite(str(out/'contact_sheets'/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in d['boards'][start:start+4]]))
    p.write_text(json.dumps(d,indent=2))
    p=out/'input_sha256_PRIVATE.json';b=json.loads(p.read_text());b[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(b,indent=2))
if __name__=='__main__':main()
