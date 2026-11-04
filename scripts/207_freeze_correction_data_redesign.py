"""Metadata-only600candidate freeze with separate validation/test locks."""
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/correction_data_redesign_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def readcsv(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    master_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv';master=readcsv(master_path)
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl';before=ledger.read_bytes()
    explicit=[json.loads(line) for line in before.decode('utf-8').splitlines() if line]
    excluded={r['image_id'] for r in master}|{r['image_id'] for r in explicit}
    registries=sorted((ROOT/'data/manifests').glob('*processed_manifest.csv'))
    for path in registries:
        for r in readcsv(path):
            name=r.get('image_id','')
            if name.startswith('fairface__'):excluded.add(name)
    train_path=ROOT/'data/raw/FairFace/train_labels.csv';val_path=ROOT/'data/raw/FairFace/val_labels.csv'
    metadata={'train':readcsv(train_path),'validation':readcsv(val_path)}
    # Directory entries only; do not open image files or compute pixel/file hashes.
    local={split:{p.name for p in (ROOT/'data/raw/FairFace'/folder).iterdir() if p.is_file()} for split,folder in [('train','train'),('validation','val')]}
    pools={};availability={}
    for split,records in metadata.items():
        prefix='train/' if split=='train' else 'val/';seen=set();pool=[];missing=0
        for record in records:
            file=record['file'].replace('\\','/').strip()
            if not file.startswith(prefix) or '..' in Path(file).parts:raise ValueError('Unexpected original metadata path')
            image_id='fairface__'+file
            if image_id in seen:raise ValueError('Duplicate original metadata ID')
            seen.add(image_id)
            if file.split('/')[-1] not in local[split]:missing+=1;continue
            if image_id in excluded:continue
            pool.append(dict(image_id=image_id,relative_image_path='data/raw/FairFace/'+file,original_split=split))
        pools[split]=pool;availability[split]=dict(metadata_rows=len(records),local_directory_files=len(local[split]),missing_metadata_paths=missing,eligible_outside_exclusion_registry=len(pool))
    assert len(pools['train'])>=510 and len(pools['validation'])>=90
    train=sorted(pools['train'],key=lambda r:(hashlib.sha256(('truehue_redesign600_v1/train_seed42/'+r['image_id']).encode()).hexdigest(),r['image_id']))[:510]
    test=sorted(pools['validation'],key=lambda r:(hashlib.sha256(('truehue_redesign600_v1/test_seed42/'+r['image_id']).encode()).hexdigest(),r['image_id']))[:90]
    selected=[]
    for role,records in [('train',train[:420]),('development_validation',train[420:]),('final_test',test)]:
        for index,r in enumerate(records,1):selected.append(dict(**r,role=role,role_index=index,
            training_batch=((index-1)//60+1) if role=='train' else None,pixel_access='not_opened_in_this_stage',
            eligibility='unreviewed_candidate',duplicate_audit='pending',subject_separation='not_verified',mst_label=None))
    assert len(selected)==600 and len({r['image_id'] for r in selected})==600
    assert not {r['image_id'] for r in selected}&excluded
    paths=[Path(__file__),ROOT/'docs/correction-data-redesign-protocol.md',master_path,ledger,train_path,val_path,*registries]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir()
    for role in ['train','development_validation','final_test']:
        records=[r for r in selected if r['role']==role]
        with (OUT/(role+'_candidates.csv')).open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,list(records[0]));w.writeheader();w.writerows(records)
    write(OUT/'selection.json',dict(status='metadata_frozen_no_image_access',selected=selected,excluded_ids=sorted(excluded),availability=availability,
        counts=dict(train=420,development_validation=90,final_test=90),input_sha256=hashes,
        caveats=['Candidate counts,not accepted/eligible counts','All historical650IDs excluded;metadata exposure is disclosed',
            'Not MST-stratified,not verified person-disjoint','No duplicate audit or image processing performed','SCIN and MST coverage unfinished']))
    write(OUT/'access_policy.json',dict(status='frozen_before_preprocessing',permitted_current_role='train',
        locked_roles=['development_validation','final_test'],validation_opening='Only after model/data-policy freeze and recorded phase transition',
        final_test_opening='Only after all method/model/reporting choices frozen',duplicate_audit='Execution protocol and disclosed image access required before fitting',
        automatic_unlock=False,automatic_candidate_admission=False))
    write(OUT/'training_queue.json',dict(status='candidate_preparation_only',batches=[dict(batch=i,image_ids=[r['image_id'] for r in selected if r['role']=='train' and r['training_batch']==i]) for i in range(1,8)],
        validation_or_test_included=False,model_fits_authorized_by_this_manifest=False))
    write(OUT/'access_ledger.json',dict(status='metadata_only',raw_image_opens=0,feature_extractions=0,model_fits=0,pixel_review_exposures_added=0))
    assert hashes=={p:digest(ROOT/p) for p in hashes} and ledger.read_bytes()==before
    print(json.dumps(dict(counts=dict(train=420,development_validation=90,final_test=90),availability=availability,historical_excluded=len(excluded),raw_images_opened=0),indent=2))


if __name__=='__main__':main()
