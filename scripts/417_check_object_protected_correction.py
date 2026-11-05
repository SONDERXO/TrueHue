"""Compare removal-only object protection on all12 saved FFHQ cases; no inference."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.skin_masking.object_protected_correction import protect_correction_objects
from src.correction.seamless_blend import apply_blended

PARENT=ROOT/'outputs/ffhq_mask_support_v1'
OUT=ROOT/'outputs/ffhq_object_protection_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def write(p,data):p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def save(p,data):
    if not cv2.imwrite(str(p),data):raise IOError(str(p))
def overlay(image,mask,color):
    result=image.copy();sel=mask>0
    result[sel]=np.rint(.6*image[sel]+.4*np.array(color)).astype(np.uint8)
    return result


def main():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=read(PARENT/'sha256.json')
    assert all(sha(PARENT/p)==h for p,h in manifest.items())
    hashes=read(PARENT/'inference_plan.json')['input_sha256']
    hashes.update({str(PARENT/p):h for p,h in manifest.items()})
    hashes[str(PARENT/'sha256.json')]=sha(PARENT/'sha256.json')
    for p in [Path(__file__),ROOT/'docs/object-protected-correction-protocol-2026-11-05.md',
              ROOT/'src/skin_masking/object_protected_correction.py',ROOT/'tests/test_object_protected_correction.py']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    OUT.mkdir()
    write(OUT/'plan.json',dict(input_sha256=hashes,policy='user_requested_object_exclusion',
          status='recorded_before_mask_processing',new_inference=0,training_admitted=False))
    prior=read(PARENT/'results.json');pred={r['image_id']:r for r in read(PARENT/'inference.json')['records']}
    records=[];sheets=[];cards=[]
    for row in prior['records']:
        source=PARENT/row['id'];folder=OUT/row['id'];folder.mkdir()
        rec=dict(id=row['id'],status='failed',training_admitted=False,MST=None)
        try:
            image=cv2.imread(str(source/'input.png'))
            mask=lambda name:cv2.imread(str(source/(name+'.png')),0)
            old=FaceNeckSupport(mask('support_measurement_mask'),mask('neck_mask'),mask('correction_mask'),row['support_report'])
            cats=mask('categories');points=np.load(source/'landmarks.npy',allow_pickle=False)
            logits=np.load(PARENT/pred[row['id']]['logits_path'],allow_pickle=False)
            visible=map_visible_mask((logits>0).astype(np.uint8)*255,image.shape[:2],np.array(row['matrix']))
            outline=build_face_coverage(image,points).face_outline
            revised,veto=protect_correction_objects(old,cats,visible,outline)
            parentmask=mask('baseline_mask');_,xx=np.nonzero(parentmask);width=int(xx.max()-xx.min()+1)
            demo,alpha,blend=apply_blended(image,revised.correction_mask,[.85,1.05,.95],face_width=width,protected=veto)
            neutral,_,_=apply_blended(image,revised.correction_mask,[1.,1.,1.],face_width=width,protected=veto)
            assert np.array_equal(neutral,image)
            assert np.array_equal(revised.measurement_mask,old.measurement_mask)
            assert not revised.correction_mask[old.correction_mask==0].any()
            assert not revised.correction_mask[veto].any() and not alpha[veto].any()
            outside=revised.correction_mask==0
            assert np.array_equal(demo[outside],image[outside])
            # Independent rendering and alpha-equation checks, without calling the wrapper.
            distance=cv2.distanceTransform((revised.correction_mask>0).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
            t=np.clip(distance/max(2,int(np.ceil(width*.03))),0,1).astype(float)
            expected=t*t*(3-2*t);expected[outside]=0
            assert np.array_equal(alpha,expected)
            rgb=image[:,:,::-1].astype(float)/255
            target=np.clip(rgb**.85*np.array([1.05,1.,.95]),0,1)
            expected_demo=np.rint((rgb*(1-alpha[:,:,None])+target*alpha[:,:,None])*255).astype(np.uint8)[:,:,::-1]
            assert np.array_equal(expected_demo,demo)
            for name,array in [('input',image),('correction_mask',revised.correction_mask),
                ('neck_mask',revised.neck_mask),('protected_mask',veto.astype(np.uint8)*255),
                ('visible_face',visible),('operator_demo',demo),('measurement_mask',revised.measurement_mask)]:
                save(folder/(name+'.png'),array)
            np.save(folder/'alpha.npy',alpha)
            board=np.hstack([image,overlay(image,old.correction_mask,[0,255,0]),
                overlay(image,revised.correction_mask,[0,255,0]),
                overlay(image,(veto&(old.correction_mask>0)).astype(np.uint8),[255,0,255]),demo])
            save(folder/'board.png',board)
            label=np.full((26,board.shape[1],3),255,np.uint8)
            cv2.putText(label,row['id']+' removed='+str(revised.report['removed_pixels']),
                (6,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            sheets.append(np.vstack([label,board]))
            rec.update(status='technical_success',report=revised.report,blend_report=blend,
                zero_protected_alpha_verified=True,unchanged_protected_pixels_verified=True,
                neutral_identity_verified=True,measurement_unchanged_verified=True,
                independent_alpha_and_RGB8_verified=True)
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        rec['file_sha256']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        records.append(rec)
        cards.append('<h2>'+row['id']+'</h2><p>'+html.escape(rec['status'])+'</p><img src="'+row['id']+'/board.png">')
    for i in range(0,len(sheets),3):save(OUT/f'contact_{i//3+1}.png',np.vstack(sheets[i:i+3]))
    assert [r['id'] for r in records]==[r['id'] for r in prior['records']]
    assert all(sha(p)==h for p,h in hashes.items())
    result=dict(records=records,total=len(records),technical_successes=sum(r['status']=='technical_success' for r in records),
        new_inference=0,target_fits=0,MST_fits=0,tree_fits=0,training_admissions=0,
        parent_package_unchanged=True,source_hashes_unchanged=True,measurement_features_unchanged=True)
    write(OUT/'results.json',result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Object-protected correction</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Correction with object protection</h1><p>All12 retained, no new inference/training. Panels: input; previous correction green; '+
        'object-protected correction green; newly protected pixels pink; fixed illustrative operator. '+
        'Predictions can miss objects or remove useful skin. Face-only visibility does not establish neck object protection.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Original attribution and source limitations</a></p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':main()
