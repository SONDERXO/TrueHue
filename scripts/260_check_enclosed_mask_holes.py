"""Topology completion on exposed contour candidates; no model or label changes."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.contour_ycrcb_measurement import build_mask
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.enclosed_hole_support import complete_enclosed_holes,VERSION


def main():
    out=ROOT/'outputs/enclosed_mask_holes_v1';parent=ROOT/'outputs/postcheck_contour_development_v1'
    frames=ROOT/'outputs/ycrcb_training_check20_v1/images'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    verification=read(parent/'verification.json')
    for path,digest in verification['evidence_sha256'].items():assert sha(parent/path)==digest
    rows=read(parent/'attempts.json')
    paths=[Path(__file__),ROOT/'docs/enclosed-hole-mask-protocol.md',ROOT/'src/skin_masking/enclosed_hole_support.py',parent/'verification.json']
    paths.extend(parent/p for p in verification['evidence_sha256'])
    paths.extend(frames/f'{r["source_id"]}_{f}.png' for r in rows for f in ('reference','color'))
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    out.mkdir();(out/'images').mkdir();(out/'boards').mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_completion',version=VERSION,input_sha256=hashes,
        frames=40,existing_reviews_preserved=True,model_calls=0,measurement_features_changed=False,active_demo_changed=False))
    records=[];boards=[]
    for row in rows:
        name=row['source_id']
        for frame in ('reference','color'):
            image=cv2.imread(str(frames/f'{name}_{frame}.png'))
            old=cv2.imread(str(parent/'images'/f'{name}_{frame}_new_mask.png'),0)>0
            points_path=parent/'geometry'/f'{name}_{frame}_landmarks.npy'
            base=dict(source_id=name,frame=frame,prior_decision=row['prior_check_decision'],exact_original_notes=row['exact_original_notes'])
            if not points_path.exists():
                assert not old.any();records.append(dict(base,status='missing_geometry_no_fallback',added_pixels=0));continue
            x,y,w,h=row['frames'][frame]['new_report']['face_box'];points=np.load(points_path)
            result=build_mask(image[y:y+h,x:x+w],points)
            np.testing.assert_array_equal(result.mask>0,old[y:y+h,x:x+w])
            _,oval=restrict_to_face_outline(np.full((h,w),255,np.uint8),points)
            exclusions=np.zeros_like(old);exclusions[y:y+h,x:x+w]=result.exclusion_mask>0
            outline=np.zeros_like(old);outline[y:y+h,x:x+w]=oval>0
            candidate=complete_enclosed_holes(old,exclusions,outline)
            added=candidate&~old
            assert not np.any(old&~candidate) and not np.any(added&(~outline|exclusions))
            np.testing.assert_array_equal(candidate,complete_enclosed_holes(old,exclusions,outline))
            path=out/'images'/f'{name}_{frame}_mask.png';assert cv2.imwrite(str(path),candidate.astype(np.uint8)*255)
            np.testing.assert_array_equal(cv2.imread(str(path),0)>0,candidate)
            count,labels=cv2.connectedComponents((~old).astype(np.uint8),connectivity=8)
            added_labels=set(labels[added].tolist())
            for label in added_labels:
                component=labels==label
                assert not component[0].any() and not component[-1].any() and not component[:,0].any() and not component[:,-1].any()
                assert not np.any(component&(exclusions|~outline)) and np.all(added[component])
            records.append(dict(base,status='completed_geometry_diagnostic',old_pixels=int(old.sum()),added_pixels=int(added.sum()),
                components_added=len(added_labels),candidate_pixels=int(candidate.sum()),new_mask_sha256=sha(path),human_approval_inferred=False))
            before=image.copy();before[old]=(.5*before[old]+np.array([0,150,0])).astype(np.uint8)
            after=before.copy();after[added]=[0,0,255]
            board=np.hstack((image,before,after))
            header=np.full((30,board.shape[1],3),245,np.uint8)
            cv2.putText(header,f'{name} {frame}: photo | existing contour | red = added {int(added.sum())}',(8,21),cv2.FONT_HERSHEY_SIMPLEX,.47,(20,20,20),1)
            board=np.vstack((header,board));cv2.imwrite(str(out/'boards'/f'{name}_{frame}.png'),board)
            if added.any():boards.append((int(added.sum()),board))
    assert len(records)==40
    if boards:
        largest=[b for _,b in sorted(boards,key=lambda p:p[0],reverse=True)[:4]]
        cv2.imwrite(str(out/'largest_additions.png'),np.vstack(largest))
    comparisons=[]
    for row in rows:
        name=row['source_id'];a=out/'images'/f'{name}_reference_mask.png';b=out/'images'/f'{name}_color_mask.png'
        if not(a.exists() and b.exists()):continue
        reference=cv2.imread(str(a),0)>0;color=cv2.imread(str(b),0)>0
        original_color=cv2.imread(str(parent/'images'/f'{name}_color_new_mask.png'),0)>0
        original_reference=cv2.imread(str(parent/'images'/f'{name}_reference_new_mask.png'),0)>0
        comparisons.append(dict(source_id=name,missed_original_reference_before=int((original_reference&~original_color).sum()),
            missed_original_reference_after=int((original_reference&~color).sum()),
            color_additions_outside_original_reference=int((color&~original_color&~original_reference).sum()),
            note='support agreement only; reference candidate is not ground truth'))
    assert all(sha(ROOT/path)==digest for path,digest in hashes.items())
    write('summary.json',dict(status='diagnostic_complete_no_promotion',frames=40,geometry_frames=sum(r['status']=='completed_geometry_diagnostic' for r in records),
        changed_frames=sum(r['added_pixels']>0 for r in records),added_pixels=sum(r['added_pixels'] for r in records),records=records,paired_support_diagnostics=comparisons,
        active_demo_changed=False,new_training_admissions=0,existing_reviews_preserved=True))
    write('verification.json',dict(status='pass',frames_accounted=40,geometry_reconstructed=37,
        independent_component_addition_checks=True,deterministic_saved_masks=True,
        evidence_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}))
    print(json.dumps({k:v for k,v in read(out/'summary.json').items() if k not in ('records','paired_support_diagnostics')}))


if __name__=='__main__':main()
