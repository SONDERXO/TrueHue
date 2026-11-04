"""Version the fixed reference cohort for correction supportv2, no inference."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.peribrow_correction import include_features_and_peribrow
from src.ita_estimation.semantic_measurement import contract


def main():
    parent=ROOT/'outputs/preferred_support_cohort_v1';out=ROOT/'outputs/preferred_support_cohort_v2'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    rows=json.loads((parent/'records.json').read_text());identity=contract(ROOT)[1]
    out.mkdir();(out/'references').mkdir()
    hashes={str(p):digest(p) for p in [parent/'records.json',parent/'development_lookup.json',Path(__file__),
        ROOT/'src/skin_masking/peribrow_correction.py']}
    (out/'plan.json').write_text(json.dumps(dict(status='frozen_before_mask_revision',parent='preferred_support_cohort_v1',
        source_membership='unchanged_6anchors_12candidates_2holds',input_sha256=hashes,
        measurement_contract_sha256=identity,correction_support_version='preferred_support_peribrow_v2',
        mapping_fits=0,new_parser_inferences=0,correction_tree_fits=0),indent=2))
    shutil.copyfile(parent/'development_lookup.json',out/'development_lookup.json')
    records=[];changed=0
    for original in rows:
        row=json.loads(json.dumps(original))
        if row['measurement']['status']!='success':records.append(row);continue
        oldfolder=ROOT/Path(row['input_path']).parent
        face=cv2.imread(str(ROOT/row['mask_paths']['face']),0);neck=cv2.imread(str(ROOT/row['mask_paths']['neck']),0)
        combined=cv2.imread(str(ROOT/row['mask_paths']['combined']),0);cats=cv2.imread(str(oldfolder/'categories.png'),0)
        base=FaceNeckSupport(face,neck,combined,{})
        revised=include_features_and_peribrow(base,cats)
        extra=(revised.correction_mask>0)&(combined==0)
        assert np.array_equal(face,revised.measurement_mask)
        masks={k:cv2.imread(str(ROOT/path),0) for k,path in row['mask_paths'].items()}
        masks.update(peribrow=extra.astype(np.uint8)*255,combined=revised.correction_mask)
        folder=out/'references'/Path(row['image_id']).stem;folder.mkdir()
        shutil.copyfile(oldfolder/'input.png',folder/'input.png');shutil.copyfile(oldfolder/'categories.png',folder/'categories.png')
        for k,array in masks.items():assert cv2.imwrite(str(folder/(k+'.png')),array)
        image=cv2.imread(str(folder/'input.png'));overlay=image.copy()
        for k,color in [('face',[0,255,0]),('neck',[255,255,0]),('brows',[255,0,255]),('lips',[255,0,255]),('peribrow',[0,255,255])]:
            selected=masks[k]>0;overlay[selected]=np.rint(.5*image[selected]+.5*np.array(color)).astype(np.uint8)
        assert cv2.imwrite(str(folder/'board.png'),np.hstack((image,overlay,cv2.cvtColor(face,cv2.COLOR_GRAY2BGR),cv2.cvtColor(revised.correction_mask,cv2.COLOR_GRAY2BGR))))
        row.update(input_path=(folder/'input.png').relative_to(ROOT).as_posix(),
            mask_paths={k:(folder/(k+'.png')).relative_to(ROOT).as_posix() for k in masks},
            mask_sha256={k:digest(folder/(k+'.png')) for k in masks},
            region_pixels={k:int((v>0).sum()) for k,v in masks.items()},
            board_path=(folder/'board.png').relative_to(out).as_posix(),
            correction_support_version='preferred_support_peribrow_v2',correction_mask_decision='pending')
        assert row['features']==original['features'] and row['measurement']==original['measurement']
        changed+=bool(extra.any());records.append(row)
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    result=dict(status='version2_references_prepared_unapproved',available=16,technical_holds=2,
        cases_with_new_peribrow_pixels=changed,measurement_masks_and_features_unchanged=True,
        lookup_sha256=digest(out/'development_lookup.json'),lookup_reused_without_refitting=True,
        new_inferences=0,correction_tree_fits=0,new_approvals=0)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
