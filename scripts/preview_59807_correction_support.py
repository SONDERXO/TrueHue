"""One-source manual polygon proposal; isolated diagnostic preview, never runtime."""
from pathlib import Path
import hashlib
import html
import json
import math
import sys
import webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.correction.seamless_blend import apply_blended

OUT=ROOT/'outputs/correction_support_59807_preview_v1'
# Explicit image-coordinate manual proposals, not an automatic skin detector.
FOREHEAD=[[[92,94],[94,84],[99,81],[102,77],[108,76],[111,73],[113,75],[113,82],
           [118,84],[122,83],[125,89],[125,101],[113,105],[98,104],[91,100]],
          [[111,71],[116,67],[120,67],[123,71],[125,76],[123,82],[119,86],[113,84]]]
NECK=[[54,205],[63,199],[74,204],[86,232],[86,249],[75,249],[67,232],[55,230]]
MICROPHONE=[[132,190],[141,187],[151,188],[160,192],[165,199],[169,211],[172,223],
            [173,233],[168,241],[163,246],[158,255],[136,255],[133,247],[129,238],
            [126,226],[124,214],[124,204],[127,196]]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def polygon(shape,points):
    mask=np.zeros(shape,np.uint8);cv2.fillPoly(mask,[np.array(points,np.int32)],255);return mask>0

def propose(correction,measurement,protection,manual_removed,categories):
    shape=correction.shape
    if any(a.shape!=shape for a in [measurement,protection,manual_removed,categories]):raise ValueError('Matching arrays required')
    additions=np.zeros(shape,bool)
    for points in FOREHEAD:additions|=polygon(shape,points)
    neck=polygon(shape,NECK)&(categories==14)
    additions|=neck
    additions&=~protection&~manual_removed
    new_protected=protection|polygon(shape,MICROPHONE)
    selected=((correction>0)|additions)&~new_protected&~manual_removed
    return selected.astype(np.uint8)*255,measurement.copy(),new_protected,dict(
        forehead_polygons=FOREHEAD,neck_polygon=NECK,neck_intersection='cached_class14_only',microphone_polygon=MICROPHONE,
        manual_proposal_source='agent visual inspection of exact59807 cached image, not user-approved anatomy',
        additions=int((selected&~(correction>0)).sum()),removals=int(((correction>0)&~selected).sum()),
        newly_protected=int((new_protected&~protection).sum()),neck_proposal_pixels=int(neck.sum()))

def build():
    if OUT.exists():raise FileExistsError('Preserve complete/partial preview')
    saved=ROOT/'outputs/histogram_gap_source_held_comparison_v1/supports/59807'
    source=ROOT/'outputs/ffhq_mask_support_v1/59807'
    oldreceipt=read(saved/'manifest_PRIVATE.json');inventory=read(source.parent/'sha256.json')
    plan=read(ROOT/'outputs/histogram_gap_source_held_design_v1/plan_PRIVATE.json')
    item=next(s for s in plan['support_sources'] if s['source']=='ffhq_source_59807')
    annotation=Path(item['annotation'])
    bindings={}
    for name,digest in oldreceipt['files'].items():
        p=saved/name;assert sha(p)==digest;bindings[str(p.relative_to(ROOT))]=digest
    for name in ['input.png','categories.png']:
        p=source/name;assert sha(p)==inventory['59807/'+name];bindings[str(p.relative_to(ROOT))]=sha(p)
    for name in ['automatic_correction_mask.png','correction_mask.png']:
        p=annotation/name;assert sha(p)==item['declared_files'][name]['sha256'];bindings[str(p.relative_to(ROOT))]=sha(p)
    code=['scripts/preview_59807_correction_support.py','src/correction/seamless_blend.py','src/distortion_generation/paper_gamma.py']
    bindings.update({n:sha(ROOT/n) for n in code})
    OUT.mkdir()
    (OUT/'execution_plan_PRIVATE.json').write_text(json.dumps(dict(input_sha256=bindings,
        ordered_source=['59807'],diagnostic_gammas=[1.15,1/1.15],method='explicit_manual_polygon_preview',
        forehead=FOREHEAD,neck=NECK,microphone=MICROPHONE,model_calls=0,runtime_adoption=False),indent=2)+'\n')
    image=cv2.imread(str(source/'input.png'));cat=cv2.imread(str(source/'categories.png'),0)
    c=cv2.imread(str(saved/'correction_mask.png'),0);m=cv2.imread(str(saved/'measurement_mask.png'),0)
    p=cv2.imread(str(saved/'protected_mask.png'),0)>0
    prior=cv2.imread(str(annotation/'correction_mask.png'),0)>0;automatic=cv2.imread(str(annotation/'automatic_correction_mask.png'),0)>0
    removed=automatic&~prior
    candidate,measurement,protected,details=propose(c,m,p,removed,cat)
    assert np.array_equal(measurement,m) and not candidate[protected].any() and not candidate[removed].any()
    overlay=image.copy();kept=(candidate>0)&(c>0);added=(candidate>0)&(c==0)
    overlay[kept]=np.rint(.7*image[kept]+.3*np.array([0,200,0])).astype(np.uint8)
    overlay[added]=np.rint(.25*image[added]+.75*np.array([0,230,255])).astype(np.uint8)
    overlay[protected]=np.rint(.4*image[protected]+.6*np.array([230,0,210])).astype(np.uint8)
    def save(name,data):assert cv2.imwrite(str(OUT/name),data)
    save('original.png',image);save('selection.png',overlay);save('candidate_correction.png',candidate)
    save('candidate_protected.png',protected.astype(np.uint8)*255)
    (OUT/'measurement_UNCHANGED.png').write_bytes((saved/'measurement_mask.png').read_bytes())
    oldalpha=np.load(saved/'alpha.npy',allow_pickle=False)
    for tag,gamma in [('dark',1.15),('bright',1/1.15)]:
        before,baseline,_=apply_blended(image,c,(gamma,1.,1.),face_width=123,protected=p)
        after,alpha,_=apply_blended(image,candidate,(gamma,1.,1.),face_width=123,protected=protected)
        assert np.array_equal(baseline,oldalpha)
        assert np.array_equal(after[protected],image[protected]) and np.array_equal(after[alpha==0],image[alpha==0])
        # Independent per-channel blend arithmetic, without calling apply_blended.
        direct=np.empty_like(image)
        for ch in range(3):
            u=image[:,:,ch].astype(float)/255
            direct[:,:,ch]=np.rint(255*(u*(1-alpha)+np.power(u,gamma)*alpha)).astype(np.uint8)
        assert np.array_equal(after,direct)
        save(tag+'_old.png',before);save(tag+'_preview.png',after)
        np.save(OUT/'candidate_alpha.npy',alpha,allow_pickle=False) if tag=='dark' else None
    save('old_alpha.png',np.rint(oldalpha*255).astype(np.uint8));save('candidate_alpha.png',np.rint(alpha*255).astype(np.uint8))
    sections=[]
    for title,names in [('Support selection',[('original.png','Original cached photo'),('selection.png','Green retained / yellow added / magenta protected')]),
                        ('Fixed diagnostic darkening',[('dark_old.png','Existing support'),('dark_preview.png','Proposed support')]),
                        ('Fixed diagnostic brightening',[('bright_old.png','Existing support'),('bright_preview.png','Proposed support')]),
                        ('Alpha coverage',[('old_alpha.png','Existing alpha'),('candidate_alpha.png','Proposed alpha')])]:
        sections.append('<h2>'+title+'</h2><div>'+''.join('<figure><img src="'+n+'"><figcaption>'+label+'</figcaption></figure>' for n,label in names)+'</div>')
    page='''<!doctype html><meta charset="utf-8"><title>59807 correction-support preview</title>
<style>body{font:16px system-ui;max-width:1100px;margin:24px auto;padding:0 16px;color:#222;background:#fafafa}div{display:flex;gap:20px;flex-wrap:wrap}figure{margin:0 0 20px}img{width:512px;max-width:100%;image-rendering:pixelated}figcaption{padding:6px 0}h2{margin-top:30px}p{max-width:950px;line-height:1.5}</style>
<h1>59807 — isolated correction-support preview</h1><p>This is a manual coverage proposal for this photo only, not an automatic mask fix or a trained correction. Yellow shows proposed forehead/neck additions. Magenta protects the microphone. The measurement mask is unchanged.</p><p>Both fixed diagnostic directions use the SAME controls for old and proposed support. Judge the coverage and transitions, not whether the photo needed that correction. Pixelated enlargement adds no image detail.</p><p>Check upper forehead skin versus fine hair, the narrow neck strip, and the microphone edge. Glasses remain as in the existing support. This page has no painting or save task; report whether these specific changes look appropriate. Nothing is adopted yet.</p>'''+''.join(sections)
    (OUT/'preview.html').write_text(page,encoding='utf-8')
    # A compact inspection sheet for the agent, identical source pixels.
    panels=[]
    for name in ['original.png','selection.png','dark_old.png','dark_preview.png','bright_old.png','bright_preview.png']:
        tile=np.full((280,256,3),255,np.uint8);tile[24:]=cv2.imread(str(OUT/name));cv2.putText(tile,name,(3,16),cv2.FONT_HERSHEY_SIMPLEX,.38,(0,0,0),1);panels.append(tile)
    save('inspection.png',np.vstack([np.hstack(panels[:2]),np.hstack(panels[2:4]),np.hstack(panels[4:])]))
    assert all(sha(ROOT/n)==digest for n,digest in bindings.items())
    receipt=dict(status='ISOLATED_PREVIEW_NOT_ADOPTED',source='59807',details=details,measurement_byte_unchanged=True,
        original_inputs_unchanged=True,manual_removals_preserved=True,protected_and_zero_alpha_unchanged=True,
        independent_channel_render_passed=True,model_calls=0,fits=0,raw_original_reads=0,locked_reads=0,
        file_sha256={p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    (OUT/'preview_receipt_PRIVATE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(details))

def main():
    if sys.argv[1:]==['--build']:build()
    elif sys.argv[1:]==['--open']:
        receipt=read(OUT/'preview_receipt_PRIVATE.json')
        for name,h in receipt['file_sha256'].items():assert sha(OUT/name)==h
        webbrowser.open((OUT/'preview.html').resolve().as_uri())
    else:raise SystemExit('Use --build once, or --open existing preview')

if __name__=='__main__':main()
