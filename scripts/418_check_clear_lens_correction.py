"""Fixed clear-lens/rim comparison on all12 saved FFHQ cases; no inference."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.clear_lens_correction import protect_with_clear_lenses
from src.correction.seamless_blend import apply_blended

BASE=ROOT/'outputs/ffhq_mask_support_v1'
PREVIOUS=ROOT/'outputs/ffhq_object_protection_v1'
OUT=ROOT/'outputs/ffhq_clear_lens_correction_v1'
CLEAR={'16061','59807'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,value):p.write_text(json.dumps(value,indent=2),encoding='utf-8')
def save(p,array):
    if not cv2.imwrite(str(p),array):raise IOError(str(p))
def overlay(image,mask,color):
    result=image.copy();sel=mask>0
    result[sel]=np.rint(.6*image[sel]+.4*np.array(color)).astype(np.uint8)
    return result


def main():
    if OUT.exists():raise FileExistsError(OUT)
    hashes=read(PREVIOUS/'plan.json')['input_sha256']
    for package in [BASE,PREVIOUS]:
        hashes.update({str(package/p):h for p,h in read(package/'sha256.json').items()})
        hashes[str(package/'sha256.json')]=sha(package/'sha256.json')
    for p in [Path(__file__),ROOT/'src/skin_masking/clear_lens_correction.py',
              ROOT/'tests/test_clear_lens_correction.py',ROOT/'docs/clear-lens-correction-protocol-2026-11-05.md']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    OUT.mkdir()
    write(OUT/'plan.json',dict(status='recorded_before_mask_processing',input_sha256=hashes,
        explicit_clear_lens_ids=sorted(CLEAR),designation='assistant_visual_from_previously_inspected_originals_not_auto_classification',
        rim_width=2,new_inference=0,training_admitted=False))
    rows=read(BASE/'results.json')['records'];records=[];sheets=[];cards=[]
    for row in rows:
        sid=row['id'];source=BASE/sid;previous=PREVIOUS/sid;folder=OUT/sid;folder.mkdir()
        rec=dict(id=sid,status='failed',transparent_glasses=sid in CLEAR,training_admitted=False,MST=None)
        try:
            image=cv2.imread(str(source/'input.png'))
            mask=lambda name:cv2.imread(str(source/(name+'.png')),0)
            old=FaceNeckSupport(mask('support_measurement_mask'),mask('neck_mask'),mask('correction_mask'),row['support_report'])
            categories=mask('categories');visible=cv2.imread(str(previous/'visible_face.png'),0)
            points=np.load(source/'landmarks.npy',allow_pickle=False)
            outline=build_face_coverage(image,points).face_outline
            revised,veto,lenses,rims=protect_with_clear_lenses(old,categories,visible,outline,transparent_glasses=sid in CLEAR)
            previous_mask=cv2.imread(str(previous/'correction_mask.png'),0)
            restored=(revised.correction_mask>0)&(previous_mask==0)
            assert not restored[lenses==0].any()
            if sid not in CLEAR:assert np.array_equal(revised.correction_mask,previous_mask)
            baseline=mask('baseline_mask');_,xx=np.nonzero(baseline);width=int(xx.max()-xx.min()+1)
            demo,alpha,blend=apply_blended(image,revised.correction_mask,[.85,1.05,.95],face_width=width,protected=veto)
            neutral,_,_=apply_blended(image,revised.correction_mask,[1.,1.,1.],face_width=width,protected=veto)
            assert np.array_equal(neutral,image)
            assert np.array_equal(revised.measurement_mask,old.measurement_mask)
            assert not revised.correction_mask[old.correction_mask==0].any()
            assert not alpha[veto].any() and not alpha[rims>0].any()
            assert np.array_equal(demo[veto],image[veto])
            assert np.array_equal(demo[revised.correction_mask==0],image[revised.correction_mask==0])
            distance=cv2.distanceTransform((revised.correction_mask>0).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
            t=np.clip(distance/max(2,int(np.ceil(width*.03))),0,1).astype(float)
            expected=t*t*(3-2*t);expected[revised.correction_mask==0]=0
            assert np.array_equal(alpha,expected)
            rgb=image[:,:,::-1].astype(float)/255
            target=np.clip(rgb**.85*np.array([1.05,1.,.95]),0,1)
            independent=np.rint((rgb*(1-alpha[:,:,None])+target*alpha[:,:,None])*255).astype(np.uint8)[:,:,::-1]
            assert np.array_equal(demo,independent)
            for name,array in [('input',image),('correction_mask',revised.correction_mask),('neck_mask',revised.neck_mask),
                ('protected_mask',veto.astype(np.uint8)*255),('lens_interiors',lenses),('approximate_rims',rims),('operator_demo',demo)]:
                save(folder/(name+'.png'),array)
            np.save(folder/'alpha.npy',alpha)
            detail=overlay(image,lenses,[0,255,0]);detail=overlay(detail,rims,[255,0,255])
            board=np.hstack([image,overlay(image,previous_mask,[0,255,0]),overlay(image,revised.correction_mask,[0,255,0]),detail,demo])
            save(folder/'board.png',board)
            label=np.full((26,board.shape[1],3),255,np.uint8)
            cv2.putText(label,sid+' clear='+str(sid in CLEAR)+' restored='+str(int(restored.sum())),(6,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            sheets.append(np.vstack([label,board]))
            if sid in CLEAR:save(OUT/(sid+'_detail.png'),np.vstack([label,board]))
            rec.update(status='technical_success',report=revised.report,blend_report=blend,
                independently_checked=True,measurement_unchanged=True,
                zero_protected_alpha=True,neutral_identity=True,
                restored_pixels=int(restored.sum()),lens_alpha_positive=int(((lenses>0)&(alpha>0)).sum()),
                lens_alpha_full=int(((lenses>0)&(alpha==1)).sum()))
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        rec['file_sha256']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        records.append(rec)
        cards.append('<h2>'+sid+(' — clear lenses designated' if sid in CLEAR else ' — unchanged opaque/unknown policy')+'</h2><img src="'+sid+'/board.png">')
    for i in range(0,len(sheets),3):save(OUT/f'contact_{i//3+1}.png',np.vstack(sheets[i:i+3]))
    assert all(sha(p)==h for p,h in hashes.items())
    result=dict(records=records,total=len(rows),technical_successes=sum(r['status']=='technical_success' for r in records),
        clear_lens_cases=2,other_cases_unchanged=10,new_inference=0,target_fits=0,tree_fits=0,MST_fits=0,
        training_admissions=0,parent_packages_and_pinned_inputs_unchanged=True)
    write(OUT/'results.json',result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Clear lenses: correction through glasses</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Clear lenses: correct the visible face, protect rims</h1><p>Panels: input; previous all-glasses exclusion; revised correction; '+
        'lens interiors green/approximate rims pink; fixed illustrative operator. Two clear-lens examples designated by visual inspection; '+
        'sunglasses remain excluded. Two-pixel parser-envelope band approximates rims/bridge; it is not exact frame segmentation. '+
        'Eyes inside lens interiors are corrected. No automatic glasses-type classification, new inference or training.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Original attribution and limitations</a></p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':main()
