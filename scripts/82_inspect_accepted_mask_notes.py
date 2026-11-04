"""Audit seven accepted-note cases using explicit visual witness regions only."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

# Half-open pixel rectangles in saved256 images, visually inspected by Codex.
# Witness regions demonstrate specific contamination, not complete annotations.
WITNESSES={'31154':dict(bounds=[10,205,50,235],material='hair/background beside lower-left jaw'),
           '60162':dict(bounds=[225,160,248,220],material='background beside right jaw'),
           '63870':dict(bounds=[0,0,20,40],material='light head-covering fabric at upper-left border')}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'outputs/source60_note_inspection_v1'
    tables=ROOT/'data/manifests/source60_note_inspection_v1'
    if (output/'summary.json').exists() or tables.exists():raise FileExistsError('Inspection exists')
    output.mkdir(exist_ok=True);tables.mkdir()
    review_path=ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json'
    review=json.loads(review_path.read_text())['pairs']
    selected=[r for r in review if r['human_decision']=='accept' and r['technical_followup']]
    assert len(selected)==7
    parent=ROOT/'outputs/training_source60_variants_v1/images'
    brightness=importlib.import_module('72_audit_brightness_features')
    tracked=[Path(__file__),review_path,ROOT/'data/manifests/source60_user_review_v1/original_user_export.json',
             ROOT/'data/manifests/development_exposure_additions.jsonl',ROOT/'models/correction_prototype_v1/decision_tree.joblib',
             ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json']
    for r in selected:
        ident=Path(r['image_id']).stem;stem=r['pair_id']
        tracked += [parent/(ident+'_reference.png'),parent/(ident+'_generation.png')]
        tracked += [parent/(stem+s) for s in ['_input.png','_baseline_estimate.png','_support.png']]
    hashes={str(p):digest(p) for p in tracked};records=[];boards={}
    for row in selected:
        stem=row['pair_id'];ident=Path(row['image_id']).stem;spec=WITNESSES[ident]
        image=cv2.imread(str(parent/(stem+'_input.png')));reference=cv2.imread(str(parent/(ident+'_reference.png')))
        masks={k:cv2.imread(str(parent/f),0)>0 for k,f in dict(generation=ident+'_generation.png',measurement=stem+'_baseline_estimate.png',correction=stem+'_support.png').items()}
        x0,y0,x1,y1=spec['bounds'];witness=np.zeros(image.shape[:2],bool);witness[y0:y1,x0:x1]=True
        counts={k:int((m&witness).sum()) for k,m in masks.items()}
        original=compute_masked_lab_statistics(image,masks['measurement'].astype(np.uint8)*255,1000)
        removed=compute_masked_lab_statistics(image,(masks['measurement']&~witness).astype(np.uint8)*255,1000)
        # Counterfactual sensitivity only; never substitute into a training table.
        original_brightness=brightness.brightness_features(image,masks['measurement'])
        removed_brightness=brightness.brightness_features(image,masks['measurement']&~witness)
        assert original['valid'] and removed['valid']
        record=dict(pair_id=stem,image_id=row['image_id'],human_decision=row['human_decision'],human_notes=row['human_notes'],
            witness=spec,witness_selected_pixels=counts,
            changed_input_pixels_in_witness=int((witness&np.any(image!=reference,axis=2)).sum()),
            diagnostic_lab_change_after_witness_removal={k:removed[k]-original[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']},
            diagnostic_brightness_change_after_witness_removal={k:removed_brightness['features'][k]-original_brightness['features'][k] for k in original_brightness['features']} if removed_brightness['valid'] else None,
            technical_status='hold_pending_mask_policy_or_source_regeneration_review',training_eligible=False)
        records.append(record);panels=[]
        for name,mask in [('Input',None)]+list(masks.items()):
            shown=image.copy()
            if mask is not None:shown[mask]=np.rint(.55*shown[mask]+.45*np.asarray([0,220,0])).astype(np.uint8)
            cv2.rectangle(shown,(x0,y0),(x1-1,y1-1),(0,0,255),1)
            shown=cv2.copyMakeBorder(shown,34,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,row['variant']+' '+name,(3,14),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
            cv2.putText(shown,'Witness selected: '+str(counts.get(name,0)),(3,29),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1)
            panels.append(shown)
        boards.setdefault(ident,[]).append(np.hstack(panels))
    for ident,rows in boards.items():assert cv2.imwrite(str(output/(ident+'_layers.png')),np.vstack(rows))
    assert hashes=={p:digest(Path(p)) for p in hashes}
    (tables/'technical_findings.json').write_text(json.dumps(dict(status='inspection_only_user_decisions_unchanged',witness_definition='Codex visually selected diagnostic rectangles; not user/pixel ground truth or exhaustive contamination counts',pairs=records),indent=2),encoding='utf-8')
    summary=dict(status='complete_no_repairs_no_fitting',cases=7,user_acceptances_preserved=True,technical_holds=7,
        witness_counts=[dict(pair_id=r['pair_id'],**r['witness_selected_pixels'],changed_input_pixels=r['changed_input_pixels_in_witness']) for r in records],
        input_sha256=hashes,limitation='Removing a witness rectangle is a sensitivity probe, not an adopted mask fix, anatomical annotation or proof that remaining pixels are clean. No new mask/features used for training.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (output/'review-index.md').write_text('# Accepted-note layer inspection\n\nRed rectangle: visually identified non-skin witness, not exhaustive annotation. Green: selected mask.\n\n'+'\n'.join(f'- [{ident}: input/generation/measurement/correction]({ident}_layers.png)' for ident in boards),encoding='utf-8')
    print(json.dumps(summary['witness_counts'],indent=2))


if __name__=='__main__':main()
