"""Prepare the frozen post-quarantine training queue; never admit or fit a tree."""
import hashlib
import html
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.training_manifest import LABEL_TO_GROUP
from src.ita_estimation.square_measurement import contract, measure, MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.table2_composite import composite_rgb
from src.model_training.recovery_targets import fit_recovery_target

OUT = ROOT/'outputs/correction_training_preparation_v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    frozen = ROOT/'outputs/correction_data_redesign_v1'
    audit = ROOT/'outputs/correction_duplicate_audit_v1'
    verification = read(audit/'verification.json')
    assert verification['status']=='pass'
    for name, sha in verification['evidence_sha256'].items():
        assert digest(audit/name)==sha
    selection, policy = read(frozen/'selection.json'), read(frozen/'access_policy.json')
    assert digest(frozen/'selection.json')==read(audit/'summary.json')['selection_sha256']
    dispositions = {r['image_id']:r for r in read(audit/'candidate_dispositions.json')}
    queue = read(audit/'verified_training_queue.json')
    selected = []
    for batch in queue['batches']:
        for image_id in batch['image_ids']:
            row = training_candidate(image_id, selection, policy)
            assert dispositions[image_id]['status']=='screen_clear_unreviewed'
            assert row['training_batch']==batch['batch']
            selected.append(dict(row, duplicate_group_id=dispositions[image_id]['duplicate_group']))
    assert len(selected)==len({r['image_id'] for r in selected})==418
    config = get_config()
    spec, identity = contract(ROOT)
    assert identity=='051dfb175e1356776ea59ebb5c3d63a7e1130de49d5787a7e75b7c0fa135db73'
    artifact = ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)=='3e3f3635ed860f68ab664c86f9ac985c7c3e8e461a16475156ebcd0eafe0cd7e'
    lookup = DevelopmentMonotoneLookup(read(artifact), identity)
    tracked = [Path(__file__),artifact,frozen/'selection.json',frozen/'access_policy.json',audit/'verification.json',
               audit/'verified_training_queue.json',audit/'candidate_dispositions.json',
               ROOT/'data/manifests/development_exposure_additions.jsonl',
               ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py']
    hashes = {p.relative_to(ROOT).as_posix():digest(p) for p in tracked}
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'boards').mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_training_preprocessing',selected=selected,
          measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes,
          policy='Existing reference-estimated-MST Table2 severity; unchanged control plus one distortion; no fitting/admission.',
          held_out_access='No development-validation/final-test preprocessing in this stage.'))
    write(OUT/'run_status.json',dict(status='running'))
    prepare = importlib.import_module('11_prepare_training_manifests')
    detector = lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(im, box):
        x,y,w,h = box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    def save(path, im):
        if not cv2.imwrite(str(path),im):raise OSError(path)
    def tile(im, label, mask=None):
        shown = im.copy()
        if mask is not None:
            support = mask>0
            shown[support] = np.rint(.65*shown[support]+.35*np.array([0,255,0])).astype(np.uint8)
        shown = cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1)
        return shown
    records = []
    try:
        for row in selected:
            name = Path(row['image_id']).stem
            path = ROOT/row['relative_image_path']
            # Record each actual attempt before reading its image.
            with (OUT/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=row['image_id'],role='train',phase='reference_and_distortion_preparation',visual_review='pending'))+'\n')
            source_hash = digest(path)
            ref = measure(cv2.imread(str(path)),detector,masker)
            record = dict(image_id=row['image_id'],source_id=name,training_batch=row['training_batch'],
                duplicate_group_id=row['duplicate_group_id'],source_path=row['relative_image_path'],source_sha256=source_hash,
                status='reference_failed',reference_measurement=ref.report,training_eligible=False,
                user_decision='pending',source_reference_suitability='pending',mask_scene_suitability='pending')
            panels = []
            if ref.image is not None:
                save(OUT/'images'/f'{name}_reference.png',ref.image)
                panels = [tile(ref.image,name+' reference'),tile(ref.image,'Reference support',ref.mask)]
            if ref.mask is not None:save(OUT/'images'/f'{name}_reference_mask.png',ref.mask)
            if ref.report['status']=='success':
                label = lookup.label(ref.report['features']['input_ita_degrees'])
                group = LABEL_TO_GROUP[label]
                rgb = cv2.cvtColor(ref.image,cv2.COLOR_BGR2RGB);support = ref.mask>0
                transformed,_ = composite_rgb(rgb,group)
                generated = rgb.copy();generated[support] = transformed[support]
                _,clipping = composite_rgb(rgb[support][:,None,:],group)
                bgr = cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
                current = measure(bgr,detector,masker)
                save(OUT/'images'/f'{name}_input.png',bgr)
                if current.mask is not None:save(OUT/'images'/f'{name}_input_mask.png',current.mask)
                record.update(status='distorted_failed',reference_mst_estimate=label,assigned_severity=group,
                    official_mst_label=None,group_assignment_source='experimental_reference_ita_lookup',
                    identity_target=[1.,1.,1.],identity_features={**ref.report['features'],'input_mst_index':label-1},
                    clipping=clipping,clipping_fraction=clipping['clipped_pixels']/int(support.sum()),input_measurement=current.report)
                panels.extend([tile(bgr,group+' Table2 input'),tile(bgr,'Input support: '+current.report['status'],current.mask)])
                if current.report['status']=='success':
                    fit = fit_recovery_target(generated,rgb,current.mask>0,support)
                    record.update(target_fit=fit,input_features={**current.report['features'],
                        'input_mst_index':lookup.label(current.report['features']['input_ita_degrees'])-1},
                        reference_mask_retention=float(((current.mask>0)&support).sum()/support.sum()),
                        status='pending_review' if fit['parameters'] is not None else 'target_unavailable')
            assert digest(path)==source_hash
            if panels:save(OUT/'boards'/f'{name}.png',np.hstack(panels))
            records.append(record)
            with (OUT/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            print(f'{len(records)}/418 {name}: {record["status"]}',flush=True)
        assert contract(ROOT)[1]==identity
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
        summary = dict(status='complete_pending_review',attempted_sources=len(records),
            statuses=dict(Counter(r['status'] for r in records)),
            severity_counts=dict(Counter(r.get('assigned_severity','unavailable') for r in records)),
            training_admitted=0,correction_models_fitted=0,reference_target_optimizer_calls=sum('target_fit' in r for r in records),
            measurement_contract_sha256=identity,lookup_sha256=digest(artifact),input_sha256=hashes)
        write(OUT/'summary.json',summary)
        intro = '<!doctype html><meta charset="utf-8"><style>body{font:17px system-ui;background:#17191e;color:#eee;margin:28px}img{max-width:100%}section{border-top:1px solid #777;margin:24px 0}a{color:#9cf}</style>'
        links = []
        for batch in queue['batches']:
            sections = []
            for r in records:
                if r['training_batch']!=batch['batch']:continue
                name = r['source_id']
                sections.append(f'<section><h2>{name}: {html.escape(r["status"])}</h2><p>Experimental reference MST: {r.get("reference_mst_estimate","unavailable")}; severity: {r.get("assigned_severity","unavailable")}; clipped support: {100*r.get("clipping_fraction",0):.1f}%.</p><img loading="lazy" src="boards/{name}.png"></section>')
            filename = f'batch_{batch["batch"]}.html'
            (OUT/filename).write_text(intro+f'<h1>Training review batch {batch["batch"]}</h1><p>Review reference lighting/detail and both displayed masks. Green marks selected pixels, not accuracy. Photos are reconstruction references, not calibrated skin truth. Reply by ID: accept / reject / uncertain, with concerns. No tree fitted; no automatic admission. Failures remain recorded.</p>'+''.join(sections),encoding='utf-8')
            links.append(f'<li><a href="{filename}">Batch {batch["batch"]}: {len(sections)} candidates</a></li>')
        (OUT/'review.html').write_text(intro+'<h1>418 training candidates: preprocessing review</h1><p>Two quarantined training IDs excluded without replacement. Validation and final test excluded. Review all eligible displayed processing before fitting; numerical success is not approval.</p><ul>'+''.join(links)+'</ul>',encoding='utf-8')
        write(OUT/'run_status.json',dict(status='complete_pending_review'))
        print(json.dumps(summary,indent=2),flush=True)
    except Exception as error:
        write(OUT/'run_status.json',dict(status='failed',completed=len(records),error=str(error)))
        raise


if __name__=='__main__':
    main()
