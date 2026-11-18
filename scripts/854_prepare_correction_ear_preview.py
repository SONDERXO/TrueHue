"""Existing three exposed reviewed caches only; no failed-model prediction."""
from pathlib import Path
import hashlib,json,sys,html
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.correction_ear_preview import add_associated_ears
from src.correction.seamless_blend import apply_blended
OUT=ROOT/'outputs/correction_coverage_preview_v1'

def main():
    target=OUT/'preview_receipt_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve completed preview')
    frozen=json.loads((OUT/'inspection_inputs_PRIVATE.json').read_text())
    records=[];sections=[]
    for item in frozen['sources']:
        ident=item['id'];folder=Path(item['annotation']);old=ROOT/'outputs/ffhq_mask_support_v1'/ident
        for p,h in item['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
        image=cv2.imread(str(folder/'photo_used.png'));c=cv2.imread(str(folder/'correction_mask.png'),0)
        m=cv2.imread(str(folder/'measurement_mask.png'),0);p=cv2.imread(str(folder/'protected_mask.png'),0)>0
        automatic=cv2.imread(str(folder/'automatic_correction_mask.png'),0)
        removed=(automatic>0)&(c==0)
        cat=cv2.imread(str(old/'categories.png'),0);r=json.loads((folder/'report.json').read_text())
        candidate,measure,report=add_associated_ears(c,m,p,cat,manual_removed=removed)
        assert np.array_equal(measure,m) and np.array_equal(candidate[p],c[p]) and not candidate[removed].any()
        alpha=np.load(folder/'correction_alpha.npy',allow_pickle=False)
        before,check,_=apply_blended(image,c,(1.15,1.,1.),face_width=r['face_width'],protected=p)
        assert np.array_equal(check,alpha)
        after,newalpha,_=apply_blended(image,candidate,(1.15,1.,1.),face_width=r['face_width'],protected=p)
        assert np.array_equal(after[p],image[p]) and np.array_equal(after[newalpha==0],image[newalpha==0])
        dest=OUT/ident;dest.mkdir()
        overlay=image.copy();existing=c>0;added=(candidate>0)&~existing
        overlay[existing]=np.rint(.65*overlay[existing]+.35*np.array([0,200,0])).astype(np.uint8)
        overlay[added]=[0,220,255];overlay[p]=[0,0,255]
        for name,array in [('original.png',image),('selection.png',overlay),('before.png',before),('after.png',after),('candidate_correction.png',candidate),('measurement_UNCHANGED.png',measure)]:
            assert cv2.imwrite(str(dest/name),array)
        np.save(dest/'candidate_alpha.npy',newalpha,allow_pickle=False)
        report.update(id=ident,diagnostic_controls=[1.15,1.,1.],original_manifest_sha256=item['annotation_manifest_sha256'],
            automatic_correction_sha256=hashlib.sha256((folder/'automatic_correction_mask.png').read_bytes()).hexdigest(),
            output_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in dest.iterdir()})
        records.append(report)
        sections.append('<section><h2>'+html.escape(ident)+'</h2><div>'+''.join('<figure><img src="'+ident+'/'+n+'"><figcaption>'+label+'</figcaption></figure>' for n,label in [('original.png','Original'),('selection.png','Green: retained / yellow: added ear / red: protected'),('before.png','Old support, fixed diagnostic darkening'),('after.png','Ear preview, SAME diagnostic darkening')])+'</div><p>Added '+str(report['added_pixels'])+' ear pixels. Forehead unchanged.</p></section>')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Correction coverage preview</title><style>body{font:16px system-ui;margin:24px}section div{display:flex;flex-wrap:wrap;gap:16px}figure{margin:0;max-width:256px}img{width:256px;height:256px}figcaption{max-width:256px}</style><h1>Ear coverage preview — not model correction</h1><p>Three existing development images. Fixed gamma 1.15 is a visibility test, not a proposed correction. Measurement and protections are unchanged. The failed model is not used.</p><p>Check whether the yellow additions cover visible ears without touching hair, earrings or background, and whether the transition looks continuous. Forehead additions need separate inspection; no scalp hair was added. This page has no painting or save controls: just report any concern with the source number.</p>'+''.join(sections),encoding='utf-8')
    for item in frozen['sources']:
        for p,h in item['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    target.write_text(json.dumps(dict(status='ISOLATED_PREVIEW_NOT_ADOPTED',records=records,measurement_unchanged=True,
        original_exports_unchanged=True,model_calls=0,fits=0,raw_original_reads=0,locked_reads=0),indent=2)+'\n')
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
