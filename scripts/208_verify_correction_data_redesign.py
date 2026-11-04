"""Independent metadata selection, role locks and unchanged historical allocations."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate


def main():
    out=ROOT/'outputs/correction_data_redesign_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def csvrows(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    selection=read(out/'selection.json');policy=read(out/'access_policy.json');queue=read(out/'training_queue.json')
    for p,h in selection['input_sha256'].items():assert digest(ROOT/p)==h
    master=csvrows(ROOT/'data/manifests/controlled_development_v1/source_audit.csv')
    assert len(master)==650
    from collections import Counter
    assert Counter(r['partition'] for r in master)==dict(train=450,development_validation=126,reserved_test=74)
    excluded={r['image_id'] for r in master}
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
    excluded|={json.loads(line)['image_id'] for line in ledger.read_text(encoding='utf-8').splitlines() if line}
    for path in sorted((ROOT/'data/manifests').glob('*processed_manifest.csv')):
        excluded|={r['image_id'] for r in csvrows(path) if r.get('image_id','').startswith('fairface__')}
    assert excluded==set(selection['excluded_ids'])
    expected={}
    for split,folder,labelpath,salt,count in [('train','train','train_labels.csv','train_seed42',510),('validation','val','val_labels.csv','test_seed42',90)]:
        available={p.name for p in (ROOT/'data/raw/FairFace'/folder).iterdir() if p.is_file()}
        eligible=[]
        for r in csvrows(ROOT/'data/raw/FairFace'/labelpath):
            name=r['file'].strip().replace('\\','/');image_id='fairface__'+name
            if name.split('/')[-1] in available and image_id not in excluded:eligible.append(image_id)
        selected=sorted(eligible,key=lambda image_id:(hashlib.sha256(('truehue_redesign600_v1/'+salt+'/'+image_id).encode()).hexdigest(),image_id))[:count]
        if split=='train':expected['train']=selected[:420];expected['development_validation']=selected[420:]
        else:expected['final_test']=selected
    all_ids=set()
    for role,ids in expected.items():
        records=[r for r in selection['selected'] if r['role']==role]
        assert ids==[r['image_id'] for r in records]
        csv_records=csvrows(out/(role+'_candidates.csv'));assert len(csv_records)==len(ids)
        assert [r['image_id'] for r in csv_records]==ids
        assert not all_ids&set(ids) and not set(ids)&excluded;all_ids|=set(ids)
        for r in records:
            assert r['pixel_access']=='not_opened_in_this_stage' and r['eligibility']=='unreviewed_candidate'
            assert r['duplicate_audit']=='pending' and r['subject_separation']=='not_verified' and r['mst_label'] is None
            assert r['relative_image_path']=='data/raw/FairFace/'+r['image_id'].split('__',1)[1]
            assert r['original_split']==('validation' if role=='final_test' else 'train')
            if role=='train':assert training_candidate(r['image_id'],selection,policy)==r
            else:
                try:training_candidate(r['image_id'],selection,policy)
                except PermissionError:pass
                else:raise AssertionError('Locked candidate accepted by new training guard')
    assert len(all_ids)==600 and len(queue['batches'])==7
    queued=[p for b in queue['batches'] for p in b['image_ids']]
    assert len(queued)==len(set(queued))==420 and set(queued)==set(expected['train'])
    assert all(len(b['image_ids'])==60 for b in queue['batches'])
    assert read(out/'access_ledger.json')==dict(status='metadata_only',raw_image_opens=0,feature_extractions=0,model_fits=0,pixel_review_exposures_added=0)
    # All read_bytes calls here target metadata/artifact files, never raw images.
    target.write_text(json.dumps(dict(status='pass',independently_reproduced_candidate_ids=600,verified_train_authorizations=420,
        verified_validation_test_denials=180,verified_training_batches=7,historical_650_allocations_unchanged=True,
        explicit_exposure_ledger_unchanged=True,metadata_only_no_raw_image_bytes_read=True,
        selection_sha256=digest(out/'selection.json'),evidence_sha256={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:600candidate IDs,420train authorizations,180locked-role denials,7batches; no image bytes read')


if __name__=='__main__':main()
