"""Run the frozen semantic candidate on reviewed references only."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.focused_semantic_mask import semantic_supports, VERSION


def main():
    out=ROOT/'outputs/focused_semantic_mask_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/correction_training_preparation_v1'
    annotations=ROOT/'outputs/focused_mask_review24_import_v1'
    for name,sha in read(annotations/'verification.json')['evidence_sha256'].items():assert digest(annotations/name)==sha
    reviews=read(annotations/'reconciled_reviews.json')
    rows={r['image_id']:r for r in (json.loads(line) for line in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    config=get_config();model=ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx'
    assert digest(model)==read(model.with_suffix('.provenance.json'))['sha256']
    paths=[Path(__file__),ROOT/'docs/focused-semantic-mask-protocol.md',model,model.with_suffix('.provenance.json'),
        ROOT/'src/skin_masking/focused_semantic_mask.py',ROOT/'src/skin_masking/face_parsing_experiment.py',
        annotations/'reconciled_reviews.json',parent/'attempts.jsonl',
        ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json']
    old_hashes=read(parent/'verification.json')['evidence_sha256']
    reserved={r['image_id'] for r in read(paths[-1])['sources']}
    assert len(reviews)==24 and not reserved&{r['image_id'] for r in reviews}
    for review in reviews:
        name=review['source_id']
        paths.append(parent/'images'/f'{name}_reference.png')
        mask=parent/'images'/f'{name}_reference_mask.png'
        if mask.exists():paths.append(mask)
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for name in ['categories','masks','boards']:(out/name).mkdir()
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    write('plan.json',dict(version=VERSION,protocol='docs/focused-semantic-mask-protocol.md',
        selected_ids=[r['image_id'] for r in reviews],input_sha256=hashes,existing_mst_lookup_applicable=False,
        reserved_training_check_access=False,training_admitted=0,models_fitted=0))
    write('run_status.json',dict(status='running'))
    parser=DenseFaceParser(model);records=[]
    def save(path,image):
        if not cv2.imwrite(str(path),image):raise OSError(path)
    def tile(image,title,mask=None):
        shown=image.copy()
        if mask is not None:
            support=mask>0;shown[support]=np.rint(.65*shown[support]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1)
        return shown
    try:
        for review in reviews:
            name=review['source_id'];prior=rows[review['image_id']]
            image_path=parent/'images'/f'{name}_reference.png'
            assert digest(image_path)==old_hashes[f'images/{name}_reference.png']
            image=cv2.imread(str(image_path));mask_path=parent/'images'/f'{name}_reference_mask.png'
            if mask_path.exists():
                assert digest(mask_path)==old_hashes[f'images/{name}_reference_mask.png']
                baseline=cv2.imread(str(mask_path),0)
            else:baseline=np.zeros(image.shape[:2],np.uint8)
            removal=np.zeros_like(baseline);candidate=np.zeros_like(baseline)
            ref=prior['reference_measurement'];available=False
            record=dict(image_id=review['image_id'],source_id=name,baseline_user_decision=review['decision'],
                baseline_exact_notes=review['notes'],baseline_processing_status=prior['status'],
                status='unavailable',training_eligible=False,candidate_review='pending')
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=review['image_id'],phase='reviewed_training_reference_candidate',reserved_check=False))+'\n')
            start=time.perf_counter()
            try:
                if ref.get('face_count')!=1 or 'face_box' not in ref:raise ValueError('Exactly one fixed-detector face required')
                categories=parser.categories_bgr(image)
                save(out/'categories'/f'{name}.png',categories)
                removal,candidate=semantic_supports(categories,baseline,[ref['face_box']])
                available=True
                record.update(status='available' if np.count_nonzero(candidate)>=1000 else 'insufficient_candidate_support')
            except (ValueError,RuntimeError,cv2.error) as error:record['reason']=str(error)
            record.update(parser_supports_available=available,seconds=time.perf_counter()-start,
                baseline_pixels=int(np.count_nonzero(baseline)),removal_only_pixels=int(np.count_nonzero(removal)),
                candidate_pixels=int(np.count_nonzero(candidate)),
                added_pixels=int(np.count_nonzero((candidate>0)&(baseline==0))),
                removed_pixels=int(np.count_nonzero((baseline>0)&(candidate==0))))
            for arm,mask in [('removal',removal),('candidate',candidate)]:save(out/'masks'/f'{name}_{arm}.png',mask)
            board=np.hstack([tile(image,name+' reference'),tile(image,'Saved baseline',baseline),
                tile(image,'Removal-only diagnostic',removal),tile(image,'Semantic candidate',candidate)])
            save(out/'boards'/f'{name}.png',board);records.append(record)
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            print(name,record['status'],record['baseline_pixels'],'->',record['candidate_pixels'],flush=True)
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
        summary=dict(version=VERSION,status='complete_pending_candidate_review',sources=24,
            statuses=dict(Counter(r['status'] for r in records)),
            baseline_accepted_cases=sum(r['baseline_user_decision']=='accept' for r in records),
            accepted_baseline_cases_changed=sum(r['baseline_user_decision']=='accept' and (r['added_pixels'] or r['removed_pixels'])>0 for r in records),
            measured_improvement='not_established_without_candidate_annotations',reserved_training_check_attempts=0,
            candidate_ita_mst_calls=0,correction_models_fitted=0,existing_mst_lookup_applicable=False)
        write('summary.json',summary)
        spec=dict(batch='semantic24',manifest_sha256=digest(out/'plan.json'),
            review_scope='semantic_reference_mask_candidate_only',panel_labels=['Reference','Saved baseline','Removal-only diagnostic','Semantic candidate'],
            review_instructions='Compare the rightmost candidate with the saved baseline. Accept means the candidate mask is suitable; add any concern or regression. Middle removal-only panel is diagnostic. Original decisions remain unchanged.',
            records=[dict(image_id=r['image_id'],source_id=r['source_id'],status='pending_review' if r['status']=='available' else r['status'],
                panel_count=4,selection_reason='Previously reviewed training reference',
                failure_reason=r.get('reason'),comparison_note=f'Baseline decision: {r["baseline_user_decision"]}. Original note: {r["baseline_exact_notes"] or "none"}. Pixels: {r["baseline_pixels"]} → {r["candidate_pixels"]}.') for r in records])
        template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
        page=template.replace('__BATCH__','semantic24').replace('__BATCH_LINKS__','Same 24 photos · candidate comparison').replace('__DATA__',json.dumps(spec).replace('<','\\u003c'))
        page=page.replace('href="review.html"','href="../focused_mask_review24_v1/review.html"',1).replace('All batches','Original review')
        page=page.replace('Training review · batch semantic24','Reference mask candidate comparison · same 24 photos')
        page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',spec['review_instructions'])
        page=page.replace('<header>','<body class="large"><header>',1).replace('<input type="checkbox" id="large">','<input type="checkbox" id="large" checked>')
        (out/'review.html').write_text(page,encoding='utf-8')
        (out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
        write('run_status.json',dict(status='complete_pending_candidate_review'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)));raise


if __name__=='__main__':main()
